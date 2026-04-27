"""Installer for alert-rules/* modules."""

from __future__ import annotations

import re
from typing import Any

from ..catalog import Module
from ..clients import Env, GrafanaClient
from ._render import render_str, render_yaml_file


def _slug(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")


def _build_title(module: Module, inputs: dict[str, Any]) -> str:
    template = (module.meta or {}).get("provides", {}).get("title_template")
    if not template:
        rule = render_yaml_file(module.path / "rule.yaml", inputs)
        template = rule.get("title_template") or "{{ service }}_alert"
    return render_str(template, inputs)


def install_alert_rule(module: Module, env: Env, inputs: dict[str, Any]) -> dict[str, Any]:
    """Create or update a Grafana alert rule from a template.

    Idempotent on (folderUID, ruleGroup, title) tuple — finds an existing
    rule with the same title and PUTs to update; otherwise POSTs new.
    """
    rule_def = render_yaml_file(module.path / "rule.yaml", inputs)
    title = _build_title(module, inputs)
    folder_uid = rule_def.get("folderUID") or "sm-alerts-folder"
    folder_title = inputs.get("folder_title", "SM Alerts")
    rule_group = rule_def.get("ruleGroup") or "default"

    client = GrafanaClient(env)
    client.upsert_folder(folder_uid, folder_title)

    payload: dict[str, Any] = {
        "title": title,
        "ruleGroup": rule_group,
        "folderUID": folder_uid,
        "noDataState": rule_def.get("noDataState", "Alerting"),
        "execErrState": rule_def.get("execErrState", "Alerting"),
        "for": rule_def.get("for", "5m"),
        "condition": rule_def.get("condition", "C"),
        "data": rule_def.get("data", []),
        "labels": rule_def.get("labels", {}),
        "annotations": rule_def.get("annotations", {}),
        "isPaused": bool(rule_def.get("isPaused", False)),
    }

    existing = next(
        (r for r in client.list_alert_rules()
         if r.get("title") == title and r.get("folderUID") == folder_uid),
        None,
    )
    if existing:
        result = client.update_alert_rule(existing["uid"], {**existing, **payload})
        action = "updated"
        uid = existing["uid"]
    else:
        result = client.create_alert_rule(payload)
        action = "created"
        uid = (result or {}).get("uid") if isinstance(result, dict) else None

    return {
        "module": module.id,
        "action": action,
        "title": title,
        "uid": uid,
        "result": result,
    }
