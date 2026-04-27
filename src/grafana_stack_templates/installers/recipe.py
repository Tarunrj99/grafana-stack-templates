"""Installer for recipes/* modules.

A recipe bundles other modules and orchestrates per-service application.
"""

from __future__ import annotations

import re
from typing import Any

import yaml

from ..catalog import Module, get_module
from ..clients import Env
from .alert_rule import install_alert_rule
from .slack_template import install_slack_template
from .sm_check import install_sm_check


def _slug(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")


def install_recipe(module: Module, env: Env, inputs: dict[str, Any]) -> dict[str, Any]:
    """Apply a recipe end-to-end."""
    recipe_path = module.path / "recipe.yaml"
    if not recipe_path.is_file():
        raise FileNotFoundError(f"{module.id}: recipe.yaml not found")
    recipe = yaml.safe_load(recipe_path.read_text()) or {}

    defaults = (inputs.get("defaults") or {})
    services = inputs.get("services") or []
    if not services:
        raise ValueError(
            f"recipe {module.id}: no services provided. "
            "Pass --inputs=services.yaml with a `services:` list."
        )

    results: list[dict[str, Any]] = []

    for step in recipe.get("modules", []):
        sub_id = step.get("id")
        sub = get_module(sub_id)
        if sub is None:
            results.append({"module": sub_id, "error": "module not found"})
            continue

        if step.get("apply_once"):
            ctx = {**defaults}
            r = _dispatch(sub, env, ctx)
            results.append(r)
        elif step.get("apply_for_each") == "services":
            for svc_inputs in services:
                ctx = {**defaults, **svc_inputs}
                ctx.setdefault("service_slug", _slug(ctx.get("service", "")))
                r = _dispatch(sub, env, ctx)
                results.append(r)
        else:
            results.append({"module": sub_id, "error": "unknown step shape"})

    return {"module": module.id, "results": results}


def _dispatch(sub: Module, env: Env, ctx: dict[str, Any]) -> dict[str, Any]:
    if sub.category == "slack-templates":
        return install_slack_template(sub, env, ctx)
    if sub.category == "sm-checks":
        return install_sm_check(sub, env, ctx)
    if sub.category == "alert-rules":
        return install_alert_rule(sub, env, ctx)
    raise ValueError(f"recipe dispatch: unsupported sub-category '{sub.category}'")
