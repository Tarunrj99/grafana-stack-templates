"""grafana-stack-templates CLI: `gst <command>`."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import click
import yaml

from . import __version__
from .catalog import get_module, list_modules
from .clients import APIError, Env
from .installers import (
    install_alert_rule,
    install_recipe,
    install_slack_template,
    install_sm_check,
)
from .manifest import ManifestError, fetch_manifest, gate

DEFAULT_SM_URL = "https://synthetic-monitoring-api-prod-us-central-0.grafana.net"


def _load_inputs(path: str | None) -> dict:
    if not path:
        return {}
    p = Path(path)
    if not p.is_file():
        raise click.ClickException(f"--inputs file not found: {path}")
    return yaml.safe_load(p.read_text()) or {}


def _build_env(
    grafana_url: str | None,
    grafana_token: str | None,
    sm_url: str | None,
    sm_token: str | None,
    slack_webhook: str | None,
    dry_run: bool,
) -> Env:
    grafana_url = grafana_url or os.environ.get("GRAFANA_URL")
    grafana_token = grafana_token or os.environ.get("GRAFANA_TOKEN")
    sm_url = sm_url or os.environ.get("SM_URL", DEFAULT_SM_URL)
    sm_token = sm_token or os.environ.get("SM_ACCESS_TOKEN", "")
    slack_webhook = slack_webhook or os.environ.get("SLACK_WEBHOOK")

    if not grafana_url:
        raise click.ClickException("missing --grafana-url (or $GRAFANA_URL)")
    if not grafana_token:
        raise click.ClickException("missing --grafana-token (or $GRAFANA_TOKEN)")

    return Env(
        grafana_url=grafana_url,
        grafana_token=grafana_token,
        sm_url=sm_url,
        sm_token=sm_token,
        slack_webhook=slack_webhook,
        dry_run=dry_run,
    )


@click.group()
@click.version_option(__version__, prog_name="gst")
def main() -> None:
    """Catalog and CLI for Grafana Cloud building blocks."""


@main.command("ls")
@click.argument("category", required=False)
def cmd_ls(category: str | None) -> None:
    """List modules in the catalog."""
    modules = list_modules(category)
    if not modules:
        click.echo("(no modules found)")
        return
    last = None
    for m in modules:
        if m.category != last:
            click.echo()
            click.secho(m.category, fg="cyan", bold=True)
            last = m.category
        click.echo(f"  {m.id:<55} {m.version:<8} {m.name}")


@main.command("show")
@click.argument("module_id")
def cmd_show(module_id: str) -> None:
    """Show details about one module."""
    m = get_module(module_id)
    if m is None:
        click.secho(f"Module not found: {module_id}", fg="red", err=True)
        sys.exit(1)
    click.secho(m.name, bold=True)
    click.echo(f"  id:       {m.id}")
    click.echo(f"  version:  {m.version}")
    click.echo(f"  type:     {m.meta.get('type', '-')}")
    click.echo(f"  target:   {m.meta.get('target', '-')}")
    click.echo()
    click.echo(m.description or "(no description)")
    click.echo()
    if "requires" in m.meta:
        click.secho("requires:", fg="yellow")
        click.echo(json.dumps(m.meta["requires"], indent=2))
    click.echo()
    click.secho("files:", fg="yellow")
    for p in sorted(m.path.iterdir()):
        click.echo(f"  {p.name}")


@main.command("manifest")
def cmd_manifest() -> None:
    """Show the current state of the runtime manifest."""
    try:
        m = fetch_manifest()
    except ManifestError as e:
        click.secho(f"manifest error: {e}", fg="red", err=True)
        sys.exit(2)
    if m is None:
        click.echo("manifest check disabled")
        return
    click.secho(
        f"service_status:        {m.service_status}",
        fg="green" if m.service_status == "active" else "red",
    )
    click.echo(f"schema_version:        {m.schema_version}")
    click.echo(f"min_supported_version: {m.min_supported_version}")
    click.echo(f"deprecated_versions:   {m.deprecated_versions or '(none)'}")
    click.echo(f"projects:              {dict(m.projects) or '(none)'}")
    click.echo(f"deployment_overrides:  {len(m.deployment_overrides)} entries")
    for o in m.deployment_overrides:
        click.echo(f"  - {o}")


_creds_options = [
    click.option("--grafana-url", envvar="GRAFANA_URL", help="Grafana stack URL"),
    click.option("--grafana-token", envvar="GRAFANA_TOKEN", help="Grafana SA token (glsa_...)"),
    click.option("--sm-url", envvar="SM_URL", help="Synthetic Monitoring API URL"),
    click.option("--sm-token", envvar="SM_ACCESS_TOKEN", help="Synthetic Monitoring access token"),
    click.option("--slack-webhook", envvar="SLACK_WEBHOOK", help="Slack incoming webhook URL"),
]


def _add_creds(f):
    for opt in reversed(_creds_options):
        f = opt(f)
    return f


@main.command("plan")
@click.argument("module_id")
@click.option("--deployment-id", required=True, help="Deployment identifier")
@click.option("--inputs", "inputs_path", type=str, default=None, help="YAML file with inputs")
@_add_creds
def cmd_plan(
    module_id: str,
    deployment_id: str,
    inputs_path: str | None,
    grafana_url: str | None,
    grafana_token: str | None,
    sm_url: str | None,
    sm_token: str | None,
    slack_webhook: str | None,
) -> None:
    """Dry-run: show what installing a module would change."""
    _do_install(
        module_id,
        deployment_id,
        inputs_path,
        grafana_url,
        grafana_token,
        sm_url,
        sm_token,
        slack_webhook,
        dry_run=True,
    )


@main.command("install")
@click.argument("module_id")
@click.option("--deployment-id", required=True, help="Deployment identifier")
@click.option("--inputs", "inputs_path", type=str, default=None, help="YAML file with inputs")
@click.option("--dry-run", is_flag=True, help="Show what would happen, don't change anything")
@_add_creds
def cmd_install(
    module_id: str,
    deployment_id: str,
    inputs_path: str | None,
    dry_run: bool,
    grafana_url: str | None,
    grafana_token: str | None,
    sm_url: str | None,
    sm_token: str | None,
    slack_webhook: str | None,
) -> None:
    """Install a module into a Grafana stack."""
    _do_install(
        module_id,
        deployment_id,
        inputs_path,
        grafana_url,
        grafana_token,
        sm_url,
        sm_token,
        slack_webhook,
        dry_run=dry_run,
    )


def _do_install(
    module_id: str,
    deployment_id: str,
    inputs_path: str | None,
    grafana_url: str | None,
    grafana_token: str | None,
    sm_url: str | None,
    sm_token: str | None,
    slack_webhook: str | None,
    *,
    dry_run: bool,
) -> None:
    try:
        gate(__version__, deployment_id=deployment_id)
    except ManifestError as e:
        click.secho(f"refused: {e}", fg="red", err=True)
        sys.exit(2)

    module = get_module(module_id)
    if module is None:
        click.secho(f"Module not found: {module_id}", fg="red", err=True)
        sys.exit(1)

    inputs = _load_inputs(inputs_path)
    env = _build_env(grafana_url, grafana_token, sm_url, sm_token, slack_webhook, dry_run)

    click.secho(
        f"{'PLAN' if dry_run else 'INSTALL'}: {module.id} v{module.version}  →  deployment={deployment_id}",
        fg="cyan",
        bold=True,
    )

    try:
        if module.category == "slack-templates":
            result = install_slack_template(module, env, inputs)
        elif module.category == "sm-checks":
            result = install_sm_check(module, env, inputs)
        elif module.category == "alert-rules":
            result = install_alert_rule(module, env, inputs)
        elif module.category == "recipes":
            result = install_recipe(module, env, inputs)
        else:
            click.secho(f"unsupported module category: {module.category}", fg="red", err=True)
            sys.exit(1)
    except APIError as e:
        click.secho(f"API error: {e}", fg="red", err=True)
        sys.exit(3)

    click.echo(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
