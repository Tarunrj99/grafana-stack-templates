"""Installer for dashboards/* modules.

A dashboard module ships a single ``dashboard.json`` file describing the
dashboard. The installer:

  1. Ensures the target folder exists (default: ``SM Alerts``).
  2. POSTs the dashboard to ``/api/dashboards/db`` with ``overwrite: true``
     so re-runs update in place rather than duplicating.

The dashboard's ``uid`` field in ``dashboard.json`` is the stable
identifier — pick something predictable (e.g. ``sm-overview``) so subsequent
installs target the same dashboard.
"""

from __future__ import annotations

import json
from typing import Any

from ..catalog import Module
from ..clients import Env, GrafanaClient

DEFAULT_FOLDER_UID = "sm-alerts-folder"
DEFAULT_FOLDER_TITLE = "SM Alerts"


def install_dashboard(module: Module, env: Env, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
    inputs = inputs or {}
    json_path = module.path / "dashboard.json"
    if not json_path.is_file():
        raise FileNotFoundError(f"{module.id}: dashboard.json not found")

    dashboard = json.loads(json_path.read_text())

    folder_uid = inputs.get("folder_uid", DEFAULT_FOLDER_UID)
    folder_title = inputs.get("folder_title", DEFAULT_FOLDER_TITLE)

    client = GrafanaClient(env)

    actions: list[dict[str, Any]] = []
    folder = client.upsert_folder(folder_uid, folder_title)
    actions.append({"step": "upsert_folder", "uid": folder_uid, "result": folder})

    payload = {
        "dashboard": dashboard,
        "folderUid": folder_uid,
        "overwrite": True,
        "message": f"upsert via grafana-stack-templates ({module.id})",
    }
    if env.dry_run:
        actions.append({
            "step": "upsert_dashboard",
            "_dry_run": True,
            "uid": dashboard.get("uid"),
            "title": dashboard.get("title"),
        })
    else:
        resp = client._request("POST", "/dashboards/db", json=payload)
        actions.append({
            "step": "upsert_dashboard",
            "uid": dashboard.get("uid"),
            "title": dashboard.get("title"),
            "result": resp,
        })

    return {"module": module.id, "actions": actions}
