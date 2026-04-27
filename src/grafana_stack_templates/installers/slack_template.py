"""Installer for slack-templates/* modules."""

from __future__ import annotations

from typing import Any

from ..catalog import Module
from ..clients import Env, GrafanaClient


def install_slack_template(module: Module, env: Env, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
    """Apply a slack-template module to a Grafana stack.

    1. PUT the template under the name from meta.yaml's `provides.templates[0]`
       (template content from template.tpl)
    2. Optionally upsert a contact point that uses it (from meta.yaml's
       contact_point_settings)
    """
    inputs = inputs or {}
    meta = module.meta
    tpl_path = module.path / "template.tpl"
    if not tpl_path.is_file():
        raise FileNotFoundError(f"{module.id}: template.tpl not found")

    body = tpl_path.read_text()

    template_name = (meta.get("provides", {}) or {}).get("templates", ["app_status_slack"])[0]
    template_name = template_name.replace(".", "_")

    cp_settings = meta.get("contact_point_settings", {}) or {}
    contact_point_name = inputs.get("contact_point_name", "application-status")
    slack_webhook = inputs.get("slack_webhook") or env.slack_webhook

    client = GrafanaClient(env)

    actions: list[dict[str, Any]] = []
    template_resp = client.upsert_template(template_name, body)
    actions.append({
        "step": "upsert_template",
        "name": template_name,
        "result": template_resp,
    })

    if slack_webhook and cp_settings:
        # contact_point_settings values pass through unchanged. They commonly
        # contain Grafana's own `{{ template "..." . }}` syntax which is NOT
        # Jinja and must not be touched.
        settings = dict(cp_settings)
        settings.setdefault("url", slack_webhook)
        cp_payload = {
            "name": contact_point_name,
            "type": "slack",
            "settings": settings,
            "disableResolveMessage": False,
        }
        cp_resp = client.upsert_contact_point(cp_payload)
        actions.append({
            "step": "upsert_contact_point",
            "name": contact_point_name,
            "result": cp_resp,
        })
    elif not slack_webhook:
        actions.append({
            "step": "upsert_contact_point",
            "skipped": "no slack_webhook provided",
        })

    return {"module": module.id, "actions": actions}
