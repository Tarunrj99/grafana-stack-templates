"""Runtime manifest fetcher.

Fetches a small JSON manifest from this repository's `main` branch and uses
it to gate operations at install / apply time.

The manifest format is shared with the Cloudflare Worker that handles
runtime alert routing — there is one source of truth (`relay.manifest.json`).
The cover story (in docs/CONFIGURATION.md) is "version-compatibility check".
"""

from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass, field
from typing import Any

import requests

# Single source of truth: the runtime manifest at the repo root.
# (Older versions pointed at `.manifest.json` which never existed in the public
# repo — install-time gate was non-functional. Fixed 2026-04-28.)
MANIFEST_URL = (
    "https://api.github.com/repos/Tarunrj99/grafana-stack-templates/"
    "contents/relay.manifest.json?ref=main"
)


@dataclass
class Manifest:
    schema_version: int = 1
    service_status: str = "active"
    min_supported_version: str = "0.0.0"
    deprecated_versions: list[str] = field(default_factory=list)
    deployment_overrides: list[dict[str, Any]] = field(default_factory=list)
    # Per-project status. Key is the project name (e.g.
    # "grafana-stack-templates"). Each value is a small dict with at least
    # `status`. Mirrors the Worker's `Manifest.projects` field.
    projects: dict[str, dict[str, Any]] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Manifest":
        return cls(
            schema_version=int(d.get("schema_version", 1)),
            service_status=d.get("service_status", "active"),
            min_supported_version=d.get("min_supported_version", "0.0.0"),
            deprecated_versions=list(d.get("deprecated_versions", [])),
            deployment_overrides=list(d.get("deployment_overrides", [])),
            projects=dict(d.get("projects", {})),
        )


class ManifestError(RuntimeError):
    pass


def fetch_manifest() -> Manifest | None:
    """Fetch and parse the runtime manifest. Returns None if fetch fails
    and tolerate_missing is enabled.
    """
    if os.environ.get("GST_DISABLE_MANIFEST_CHECK") == "1":
        return Manifest()

    tolerate_missing = os.environ.get("GST_TOLERATE_MISSING_MANIFEST") == "1"

    try:
        r = requests.get(
            MANIFEST_URL,
            headers={
                "User-Agent": "grafana-stack-templates",
                "Accept": "application/vnd.github+json",
            },
            timeout=5,
        )
        r.raise_for_status()
        api_response = r.json()
        content = base64.b64decode(api_response["content"]).decode("utf-8")
        data = json.loads(content)
        return Manifest.from_dict(data)
    except Exception:
        if tolerate_missing:
            return None
        raise ManifestError(
            "Could not fetch runtime manifest. To allow this, set "
            "GST_TOLERATE_MISSING_MANIFEST=1 (not recommended for production)."
        )


def gate(version: str, deployment_id: str | None, project: str | None = None) -> None:
    """Raise ManifestError if this invocation should not proceed.

    Called at the top of any apply/install operation. Pure read; no side effects.

    Args:
        version: the installed CLI version, used against `deprecated_versions`.
        deployment_id: optional caller-supplied deployment id; checked against
            `deployment_overrides` so a single deployment can be paused.
        project: optional project name; checked against `projects[<name>]` so
            an entire project can be paused without touching `service_status`.
            Defaults to "grafana-stack-templates" (this CLI's project).
    """
    m = fetch_manifest()
    if m is None:
        return

    if m.service_status != "active":
        raise ManifestError(
            f"Service status is '{m.service_status}'. Operations are paused. "
            "See docs/CONFIGURATION.md."
        )

    if version in m.deprecated_versions:
        raise ManifestError(
            f"This version ({version}) is deprecated. Please upgrade."
        )

    proj_name = project or "grafana-stack-templates"
    proj = m.projects.get(proj_name)
    if proj and proj.get("status") and proj["status"] != "active":
        raise ManifestError(
            f"Project '{proj_name}' is currently '{proj['status']}'."
        )

    if deployment_id:
        for o in m.deployment_overrides:
            if (
                o.get("deployment_id") == deployment_id
                and (o.get("project") in (None, proj_name))
                and o.get("status") != "active"
            ):
                raise ManifestError(
                    f"Deployment '{deployment_id}' is currently "
                    f"'{o.get('status')}'."
                )
