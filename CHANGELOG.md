# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

_No changes yet — open a PR to add an entry here._

---

## [0.1.0] — 2026-04-28

First public release. The catalog is small but functional end-to-end and
has been validated against a live Grafana Cloud stack and a Cloudflare-Worker
relay running in front of Slack.

### Added

#### CLI (`gst`)
- `gst ls` — list all modules and recipes in the catalog.
- `gst show <module>` — print a module's metadata, required inputs, and the
  resource it would produce.
- `gst install <module-or-recipe>` — apply a module or a recipe to a Grafana
  Cloud stack via the provisioning APIs. Supports `--dry-run`,
  `--deployment-id`, `--inputs <yaml>`.
- `gst manifest` — print the current runtime manifest state.
- Runtime manifest gate (`src/grafana_stack_templates/manifest.py`) consulted
  at the top of every `install` invocation. Fail-closed unless
  `GST_TOLERATE_MISSING_MANIFEST=1`. Bypass with `GST_DISABLE_MANIFEST_CHECK=1`
  for offline / air-gapped use.

#### Catalog modules
- `dashboards/synthetic-monitoring-overview` — one-pager dashboard listing
  every SM check, its current `probe_success`, and last-failure timestamp.
- `alert-rules/sm-http-healthcheck` — fires after 5 min of `probe_success == 0`,
  carries the labels notification policies route on (`team`, `service`,
  `severity`, `alertgroup`).
- `sm-checks/http-healthz` — generic HTTP `/healthz` Synthetic Monitoring
  check. Defaults to 10-minute frequency, 5-second timeout, single Ohio probe.
- `slack-templates/app-status-rich` — default Slack notification template
  (block-kit style with colored bar, per-alert fields, inline link buttons).
  Mobile-friendly. Variant A — currently deployed against the reference
  stack.
- `slack-templates/app-status-compact` — single-line per service. For
  high-volume noise channels.
- `slack-templates/app-status-detailed` — extra context (description,
  labels, UTC + viewer-localized timestamps via Slack's native `<!date^>`
  token). For incident-review channels.
- `recipes/synthetic-monitoring-pack` — bundles SM check + alert rule +
  Slack template, applied per service in `examples/services.yaml`.

#### Runtime manifest
- `relay.manifest.json` at repo root. One source of truth consumed by both
  the CLI's install-time gate and the optional `cloud-relay-hub`
  Cloudflare Worker that sits between Grafana and Slack.
- Schema documented in [`docs/CONFIGURATION.md`](docs/CONFIGURATION.md):
  `service_status` (global kill-switch), `projects` (per-project pause),
  `deployment_overrides` (per-deployment pause), `min_supported_version`,
  `deprecated_versions`.

#### Documentation
- `README.md` — overview, requirements, architecture diagram, repository
  layout, 5-minute quick start, module catalog, recipe walkthrough,
  CLI-vs-UI comparison, kill-switch, dev setup, extending guide, doc index.
- [`docs/QUICKSTART.md`](docs/QUICKSTART.md) — full end-to-end tutorial.
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — design rationale.
- [`docs/MODULES.md`](docs/MODULES.md) — every module, its inputs, and what
  it produces.
- [`docs/MANUAL_INSTALL.md`](docs/MANUAL_INSTALL.md) — UI walkthrough for
  each module type, no CLI required.
- [`docs/RECIPES.md`](docs/RECIPES.md) — operational playbook (rotate
  webhook, pause one project, switch templates, add a service to the pack,
  cut over to the relay).
- [`docs/CONFIGURATION.md`](docs/CONFIGURATION.md) — runtime manifest
  schema, env vars, defaults.
- [`docs/SAMPLE_OUTPUT.md`](docs/SAMPLE_OUTPUT.md) — rendered Slack messages
  for every template variant, both firing and resolved states.
- [`docs/DEBUG.md`](docs/DEBUG.md) — troubleshooting checklist, common API
  errors, dry-run + offline modes.

#### Community files
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — dev setup, PR checklist, commit
  style, module-add walkthrough, recipe-add walkthrough, release process.
- [`SECURITY.md`](SECURITY.md) — disclosure policy, supported versions,
  secret-handling design summary.
- [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) — Contributor Covenant 2.1.
- [`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE/) — bug, feature, and
  module-request templates.
- [`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md).

#### Build / dev hygiene
- `Makefile` — `make venv install / test / lint / clean`.
- `.env.example` — starter env file with all four required vars + the two
  manifest-gate toggles.
- `pyproject.toml` — installable as `grafana-stack-templates` with `[dev]`
  extras (pytest, ruff).
- `tests/` — pytest suite covering catalog reader, manifest fetcher, and
  install dry-runs (no real network calls).

### Live deployment
- Validated against a live Grafana Cloud stack: 79 SM checks created
  (76 HTTP + 3 newly added — 2 HTTP + 1 TCP for WebSocket), 71 alert rules
  conforming 100% to the standard (`for: 5m`, `severity: critical`,
  `team: devops`, `alertgroup: appstatus`), one canonical
  `application-status` contact point routed via the kill-switch-gated
  Cloudflare Worker relay.
- End-to-end Slack alert-latency measured: ~6 m at probe = 60 s,
  ~10–20 m at probe = 600 s. Documented timeline + render samples included.
- Kill-switch validated: editing `relay.manifest.json` →
  `service_status: paused` suppresses Slack delivery within ~60 s. Flipping
  back to `active` resumes within ~60 s.

[Unreleased]: https://github.com/Tarunrj99/grafana-stack-templates/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Tarunrj99/grafana-stack-templates/releases/tag/v0.1.0
