"""Installer for sm-checks/* modules."""

from __future__ import annotations

from typing import Any

from ..catalog import Module
from ..clients import Env, SMClient
from ._render import render_yaml_file


def _build_payload(module: Module, inputs: dict[str, Any]) -> dict[str, Any]:
    rendered = render_yaml_file(module.path / "check.yaml", inputs)
    if rendered.get("frequency"):
        rendered["frequency"] = int(rendered["frequency"])
    if rendered.get("timeout"):
        rendered["timeout"] = int(rendered["timeout"])
    if rendered.get("probes") and isinstance(rendered["probes"], list):
        rendered["probes"] = [int(p) for p in rendered["probes"]]
    return rendered


def install_sm_check(module: Module, env: Env, inputs: dict[str, Any]) -> dict[str, Any]:
    """Create or update a Synthetic Monitoring check.

    Idempotent: looks up by (target, job) and updates if found.
    Returns the resulting check (with `id`) so downstream installers can
    reference it (e.g. alert rules need the job/target to query metrics).
    """
    payload = _build_payload(module, inputs)
    client = SMClient(env)

    existing = client.find_by_target_and_job(payload["target"], payload["job"])
    if existing:
        update_payload = dict(existing)
        for k in ("frequency", "timeout", "enabled", "labels", "probes",
                  "alertSensitivity", "basicMetricsOnly", "settings"):
            if k in payload:
                update_payload[k] = payload[k]
        update_payload.pop("created", None)
        update_payload.pop("modified", None)
        result = client.update_check(update_payload)
        action = "updated"
    else:
        result = client.create_check(payload)
        action = "created"

    return {
        "module": module.id,
        "action": action,
        "target": payload["target"],
        "job": payload["job"],
        "check": result,
    }
