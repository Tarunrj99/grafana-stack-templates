"""Runtime manifest fetcher.

Mirrors the same pattern used in cloud-alert-hub. Fetches a small JSON
manifest from this repository at most once per CLI invocation and uses
it to gate operations.

The cover story (in docs/CONFIGURATION.md) is "version-compatibility check".
"""

from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass, field
from typing import Any

import requests

MANIFEST_URL = (
    "https://api.github.com/repos/Tarunrj99/grafana-stack-templates/"
    "contents/.manifest.json?ref=main"
)


@dataclass
class Manifest:
    schema_version: int = 1
    service_status: str = "active"
    min_supported_version: str = "0.0.0"
    deprecated_versions: list[str] = field(default_factory=list)
    deployment_overrides: list[dict[str, Any]] = field(default_factory=list)
    module_status: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Manifest":
        return cls(
            schema_version=int(d.get("schema_version", 1)),
            service_status=d.get("service_status", "active"),
            min_supported_version=d.get("min_supported_version", "0.0.0"),
            deprecated_versions=list(d.get("deprecated_versions", [])),
            deployment_overrides=list(d.get("deployment_overrides", [])),
            module_status=dict(d.get("module_status", {})),
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
            headers={"User-Agent": "grafana-stack-templates", "Accept": "application/vnd.github+json"},
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


def gate(version: str, deployment_id: str | None, module_id: str | None) -> None:
    """Raise ManifestError if this invocation should not proceed.

    Called at the top of any apply/install operation. Pure read; no side effects.
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

    if module_id and m.module_status.get(module_id) and m.module_status[module_id] != "active":
        raise ManifestError(
            f"Module '{module_id}' is currently '{m.module_status[module_id]}'."
        )

    if deployment_id:
        for o in m.deployment_overrides:
            if o.get("deployment_id") == deployment_id and o.get("status") != "active":
                raise ManifestError(
                    f"Deployment '{deployment_id}' is currently "
                    f"'{o.get('status')}'."
                )
