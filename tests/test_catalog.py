"""The catalog walker reads modules from disk; tests verify shape and
discovery without hitting any network."""

from __future__ import annotations

import pytest

from grafana_stack_templates.catalog import CATEGORIES, get_module, list_modules


def test_list_modules_finds_at_least_one_per_category():
    modules = list_modules()
    assert modules, "no modules found at all"
    cats_seen = {m.category for m in modules}
    # Every category we ship a module under must be represented at least
    # once. A new empty category is fine; this test catches accidental
    # deletion of all modules under a category.
    for shipping_cat in ("alert-rules", "sm-checks", "slack-templates", "recipes", "dashboards"):
        assert shipping_cat in cats_seen, f"no modules under {shipping_cat}/"


def test_every_module_has_required_meta_fields():
    for m in list_modules():
        assert m.id, f"empty id on {m.path}"
        assert "/" in m.id, f"module id should be 'category/name': {m.id}"
        assert m.version, f"missing version on {m.id}"
        assert m.description or m.category == "recipes", f"missing description on {m.id}"


def test_categories_are_an_allowlist():
    for m in list_modules():
        assert m.category in CATEGORIES, f"unknown category {m.category!r} on {m.id}"


def test_get_module_returns_none_for_unknown():
    assert get_module("does-not-exist/at-all") is None


def test_get_module_roundtrips_for_each_listed_module():
    for m in list_modules():
        again = get_module(m.id)
        assert again is not None and again.id == m.id


@pytest.mark.parametrize(
    "module_id",
    [
        "alert-rules/sm-http-healthcheck",
        "sm-checks/http-healthz",
        "slack-templates/app-status-rich",
        "slack-templates/app-status-compact",
        "slack-templates/app-status-detailed",
        "dashboards/synthetic-monitoring-overview",
        "recipes/synthetic-monitoring-pack",
    ],
)
def test_shipped_modules_load(module_id):
    m = get_module(module_id)
    assert m is not None, f"shipped module {module_id} did not load"
