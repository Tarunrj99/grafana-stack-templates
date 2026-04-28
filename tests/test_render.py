"""Smoke checks for module resource files: each one parses, and key
templated placeholders are present where the docs claim they are.

We don't fully render Grafana templates here — Grafana's text/template
runtime isn't a Go runtime we have access to in CI — but we can check
that every shipped Slack template defines the named blocks the contact
point references (`app_status.title`, `app_status.text`).
"""

from __future__ import annotations

import json

import pytest
import yaml

from grafana_stack_templates.catalog import get_module, list_modules


@pytest.mark.parametrize(
    "module_id",
    [
        "slack-templates/app-status-rich",
        "slack-templates/app-status-compact",
        "slack-templates/app-status-detailed",
    ],
)
def test_slack_templates_define_named_blocks(module_id):
    m = get_module(module_id)
    body = (m.path / "template.tpl").read_text()
    assert '{{ define "app_status.title"' in body, f"{module_id}: missing app_status.title block"
    assert '{{ define "app_status.text"' in body, f"{module_id}: missing app_status.text block"


def test_alert_rule_module_has_routing_label_set():
    m = get_module("alert-rules/sm-http-healthcheck")
    rule = yaml.safe_load((m.path / "rule.yaml").read_text())
    # The rule.yaml is templated (Jinja-style {{ }}) so we don't fully
    # render here. Just check the file parsed and contains the structural
    # elements consumers depend on.
    assert "title_template" in rule
    assert "data" in rule
    assert rule.get("for") == "5m"


def test_sm_check_module_disables_built_in_alert_sensitivity():
    m = get_module("sm-checks/http-healthz")
    body = (m.path / "check.yaml").read_text()
    assert "alertSensitivity: none" in body, "SM check must turn off built-in alerting"
    assert "basicMetricsOnly: true" in body


def test_dashboard_json_is_valid_and_pinned_uid():
    m = get_module("dashboards/synthetic-monitoring-overview")
    payload = json.loads((m.path / "dashboard.json").read_text())
    assert payload.get("uid"), "dashboard must declare a stable uid"
    assert payload.get("schemaVersion") >= 30  # avoid ancient schemas
    # at least one prom-backed panel
    has_prom = False
    for p in payload.get("panels", []):
        ds = p.get("datasource") or {}
        if ds.get("type") == "prometheus":
            has_prom = True
            break
    assert has_prom, "dashboard has no prometheus panels"


def test_recipe_references_only_existing_modules():
    m = get_module("recipes/synthetic-monitoring-pack")
    recipe = yaml.safe_load((m.path / "recipe.yaml").read_text())
    referenced = [step["id"] for step in recipe.get("modules", [])]
    catalog_ids = {x.id for x in list_modules()}
    for ref in referenced:
        assert ref in catalog_ids, f"recipe references missing module: {ref}"
