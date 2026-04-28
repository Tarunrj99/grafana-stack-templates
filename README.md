<!-- -*- markdown -*- -->

<h1 align="center">grafana-stack-templates</h1>

<p align="center">
  <b>A curated catalog of ready-to-apply Grafana Cloud building blocks.</b><br>
  Dashboards, alert rules, Synthetic Monitoring checks, Slack notification
  templates, and full recipes that bundle them together — installable with
  one command.
</p>

<p align="center">
  <i>Pick a module, run one command, and your Grafana Cloud stack is configured.</i>
</p>

<p align="center">
  <a href="#"><img alt="python" src="https://img.shields.io/badge/python-3.9%2B-3776AB?logo=python&logoColor=white"></a>
  <a href="LICENSE"><img alt="license" src="https://img.shields.io/badge/license-MIT-green"></a>
  <a href="CHANGELOG.md"><img alt="status" src="https://img.shields.io/badge/status-beta-blue"></a>
  <a href="https://grafana.com/products/cloud/"><img alt="platform" src="https://img.shields.io/badge/platform-Grafana%20Cloud-F46800?logo=grafana&logoColor=white"></a>
  <a href="CONTRIBUTING.md"><img alt="PRs welcome" src="https://img.shields.io/badge/PRs-welcome-brightgreen"></a>
</p>

<p align="center">
  <a href="#quick-start--5-minutes">Quick start</a> ·
  <a href="docs/QUICKSTART.md">Full tutorial</a> ·
  <a href="docs/MODULES.md">Module catalog</a> ·
  <a href="docs/CONFIGURATION.md">Config</a> ·
  <a href="docs/MANUAL_INSTALL.md">UI walkthrough</a> ·
  <a href="docs/SAMPLE_OUTPUT.md">Sample output</a> ·
  <a href="docs/ARCHITECTURE.md">Architecture</a> ·
  <a href="docs/RECIPES.md">Recipes</a> ·
  <a href="docs/DEBUG.md">Debug</a> ·
  <a href="CONTRIBUTING.md">Contribute</a>
</p>

---

## Why this project exists

Configuring Grafana Cloud properly is mostly the same five jobs over and over:
create a Synthetic Monitoring check per service, attach an alert rule that
won't flap, route the alert through a tidy Slack template, drop a dashboard
that everyone agrees is the "real" one, and remember to set the same labels
on every rule so notification policies actually work.

This repo encodes those five jobs as **modules** you can install instead of
re-writing. Each module is small, self-contained, and parametrized:

- A **module** is one resource type (one alert rule, one SM check, one Slack
  template, one dashboard).
- A **recipe** is a bundle of modules that produces a working setup end to
  end (e.g. "Synthetic Monitoring pack" = SM check + alert rule + Slack
  template, applied across a list of services).
- A small Python CLI (`gst`) reads the catalog and uses Grafana's
  provisioning APIs to install / preview / diff modules into your stack.
- A runtime [manifest](relay.manifest.json) acts as a kill-switch the operator can
  flip without touching code.

You can use the catalog two ways:

1. **`gst install`** — the automated path. Modules apply via Grafana's
   provisioning APIs in a few seconds.
2. **Grafana UI** — the manual path. Every module's `meta.yaml` and
   accompanying YAML/JSON file is also a paste-ready spec for clicking
   through the Grafana Cloud console. See
   [`docs/MANUAL_INSTALL.md`](docs/MANUAL_INSTALL.md).

---

## Table of contents

1. [Requirements](#requirements)
2. [Architecture at a glance](#architecture-at-a-glance)
3. [Repository layout](#repository-layout)
4. [Quick start — 5 minutes](#quick-start--5-minutes)
5. [Module catalog](#module-catalog)
6. [Recipes](#recipes)
7. [Two ways to install: CLI and UI](#two-ways-to-install-cli-and-ui)
8. [Runtime manifest (kill-switch)](#runtime-manifest-kill-switch)
9. [Local development](#local-development)
10. [Extending](#extending)
11. [Docs index](#docs-index)
12. [Contributing](#contributing)
13. [Security](#security)
14. [License](#license)

---

## Requirements

### On your workstation

| Tool   | Version          | Purpose                                       |
| ------ | ---------------- | --------------------------------------------- |
| Python | **3.9+**         | `gst` CLI runtime (3.9 / 3.10 / 3.11 / 3.12)  |
| `pip`  | any recent       | Install the CLI from PyPI or from a Git tag   |
| `git`  | any recent       | Clone, fork, publish                          |
| `make` | optional         | Common dev tasks (see [`Makefile`](Makefile)) |

### Grafana Cloud account & tokens

| Item | How to get it |
| --- | --- |
| `GRAFANA_URL` | Your stack URL, e.g. `https://yourstack.grafana.net` |
| `GRAFANA_TOKEN` | A **Cloud Access Policy** or **Service Account** token with the `alerts:write`, `metrics:read`, and `folders:write` scopes. Generate one in your stack: *Administration → Users and access → Service accounts → Add token*. Token format: `glsa_…` |
| `SM_ACCESS_TOKEN` | Required only for SM modules. Generate in *Synthetic Monitoring → Configuration → Access tokens*. |
| `SLACK_WEBHOOK` | Required only for Slack modules. Create one at [api.slack.com/messaging/webhooks](https://api.slack.com/messaging/webhooks). Format: `https://hooks.slack.com/services/T…/B…/…` |

`gst` reads all of these from environment variables, never from a file. See
[`.env.example`](.env.example) for a copy-paste starting point.

### Permissions / scopes

The `gst install` calls hit:

- `GET/POST/PUT /api/v1/provisioning/alert-rules`
- `GET/PUT     /api/v1/provisioning/templates/<name>`
- `GET/POST    /api/v1/provisioning/contact-points`
- `GET/POST/PUT https://synthetic-monitoring-api.grafana.net/api/v1/check`
- `GET         https://api.github.com/repos/<owner>/<repo>/contents/relay.manifest.json` (the runtime gate)

If your token can't do the first four, `gst install` will exit with a clear
HTTP-status error before doing any partial work.

---

## Architecture at a glance

```
                   ┌─────────────────────────────────────────────┐
                   │            grafana-stack-templates          │
                   │                                             │
   modules/  ────▶ │  catalog.py    catalog reader                │
                   │  installers/   one installer per resource    │
   recipes/  ────▶ │  cli.py        gst CLI (`ls/show/install`)   │
                   │  manifest.py   runtime gate (kill-switch)    │
                   └────────────────────┬────────────────────────┘
                                        │ provisioning API calls
                                        ▼
                   ┌─────────────────────────────────────────────┐
                   │                Grafana Cloud                │
                   │  alert-rules · contact-points · templates · │
                   │  Synthetic Monitoring · folders             │
                   └────────────────────┬────────────────────────┘
                                        │ webhook
                                        ▼
                              ┌──────────────────────┐
                              │  Slack (direct)      │
                              │   — or —             │
                              │  cloud-relay-hub →   │ (optional Cloudflare
                              │  Slack               │  Worker, with kill-
                              └──────────────────────┘  switch + KV-stored
                                                        webhooks)
```

The catalog and CLI are independent of which delivery path you choose. See
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full design rationale
(why modules look the way they do, how recipes compose, what the runtime
manifest gates, and the trade-offs of CLI vs UI installation).

---

## Repository layout

```
grafana-stack-templates/
├── README.md                        ← you are here
├── LICENSE                          ← MIT
├── CHANGELOG.md                     ← release notes
├── CONTRIBUTING.md                  ← dev setup + PR checklist
├── SECURITY.md                      ← reporting policy
├── CODE_OF_CONDUCT.md
├── Makefile                         ← `make install / test / lint`
├── pyproject.toml                   ← installable as `grafana-stack-templates`
├── relay.manifest.json              ← runtime kill-switch (read by `gst` and the relay)
├── .env.example                     ← starter env file
├── .github/                         ← issue + PR templates
│
├── modules/                         ← the catalog
│   ├── dashboards/                  ← JSON dashboards
│   │   └── synthetic-monitoring-overview/
│   ├── alert-rules/                 ← alert rule templates
│   │   └── sm-http-healthcheck/
│   ├── sm-checks/                   ← Synthetic Monitoring checks
│   │   └── http-healthz/
│   ├── slack-templates/             ← rich Slack notification templates
│   │   ├── app-status-rich/         ← block-kit style (default)
│   │   ├── app-status-compact/      ← single-line, mobile-friendly
│   │   └── app-status-detailed/     ← extra context for incident review
│   └── recipes/                     ← bundles
│       └── synthetic-monitoring-pack/
│
├── examples/
│   └── services.yaml                ← input file consumed by recipes
│
├── docs/
│   ├── QUICKSTART.md                ← 5-minute walkthrough
│   ├── ARCHITECTURE.md              ← design rationale
│   ├── MODULES.md                   ← every module, its inputs, what it produces
│   ├── RECIPES.md                   ← operational playbook (rotate webhook, …)
│   ├── MANUAL_INSTALL.md            ← UI walkthrough (no CLI required)
│   ├── CONFIGURATION.md             ← runtime manifest schema
│   ├── SAMPLE_OUTPUT.md             ← rendered Slack messages, gallery
│   └── DEBUG.md                     ← troubleshooting + dry-run + verify
│
├── src/grafana_stack_templates/     ← the `gst` CLI source
│   ├── cli.py
│   ├── catalog.py
│   ├── clients.py
│   ├── manifest.py
│   └── installers/
│
└── tests/                           ← pytest, fully offline
```

---

## Quick start — 5 minutes

> Goal: ship a Slack alert when one of your services starts failing its
> healthcheck — without writing any Grafana JSON yourself.

### 1. Install the CLI

```bash
pip install grafana-stack-templates    # latest tagged release
# or
pip install "grafana-stack-templates @ git+https://github.com/Tarunrj99/grafana-stack-templates.git@v0.1.0"
```

### 2. Set the four env vars

```bash
cp .env.example .env
$EDITOR .env                # fill in your stack URL + tokens
set -a && source .env && set +a
```

### 3. Browse the catalog

```bash
gst ls                                              # all modules
gst ls slack-templates                              # one category
gst show slack-templates/app-status-rich            # inputs, outputs, rendered preview
```

### 4. Pick a recipe and dry-run it

```bash
gst install recipes/synthetic-monitoring-pack \
  --deployment-id=my-prod \
  --inputs=examples/services.yaml \
  --dry-run
```

The dry-run prints the exact API calls `gst` would make. No side effects.

### 5. Apply it

```bash
gst install recipes/synthetic-monitoring-pack \
  --deployment-id=my-prod \
  --inputs=examples/services.yaml
```

You're done. New SM checks, an alert rule, and a Slack notification template
are now live in your stack and routed via the contact point you configured.

> Prefer the Grafana UI? Every module is also documented as a click-by-click
> recipe — see [`docs/MANUAL_INSTALL.md`](docs/MANUAL_INSTALL.md).

---

## Module catalog

A snapshot. The full table with inputs, outputs, and a rendered preview for
each module lives in [`docs/MODULES.md`](docs/MODULES.md).

| Category | Module | What it does |
|---|---|---|
| **dashboards** | [`synthetic-monitoring-overview`](modules/dashboards/synthetic-monitoring-overview/) | One-pager dashboard: per-service probe success, p95 latency, last-failure timestamps |
| **alert-rules** | [`sm-http-healthcheck`](modules/alert-rules/sm-http-healthcheck/) | Fires after 5 min of `probe_success == 0`. Carries the labels notification policies route on (`team`, `service`, `severity`, `alertgroup`). |
| **sm-checks** | [`http-healthz`](modules/sm-checks/http-healthz/) | Generic HTTP `/healthz` check, 10-min default frequency, 5-second timeout, single Ohio probe. |
| **slack-templates** | [`app-status-rich`](modules/slack-templates/app-status-rich/) | Default — colored bar + per-alert fields + inline link "buttons". Mobile-friendly. |
| **slack-templates** | [`app-status-compact`](modules/slack-templates/app-status-compact/) | Single-line per service. Best for high-volume noise channels. |
| **slack-templates** | [`app-status-detailed`](modules/slack-templates/app-status-detailed/) | Extra context (description, labels, timestamps in UTC + viewer-localized). For incident-review channels. |
| **recipes** | [`synthetic-monitoring-pack`](modules/recipes/synthetic-monitoring-pack/) | SM check + alert rule + Slack template, applied per service in your `services.yaml`. |

Each module has a `meta.yaml` with an explicit `requires:` block — `gst show
<module>` prints them, and `gst install` refuses to apply a module whose
inputs aren't satisfied.

---

## Recipes

A "recipe" is a bundle of modules — exactly one `gst install` provisions
many resources at once. The shipped recipe:

```yaml
# modules/recipes/synthetic-monitoring-pack/recipe.yaml
modules:
  - id: sm-checks/http-healthz                # apply for each service
    apply_for_each: services
  - id: alert-rules/sm-http-healthcheck       # apply for each service
    apply_for_each: services
  - id: slack-templates/app-status-rich       # apply once
    apply_once: true
```

Inputs come from [`examples/services.yaml`](examples/services.yaml) (or
your own equivalent — see [`docs/CONFIGURATION.md`](docs/CONFIGURATION.md)).

Operational playbooks for everyday tasks (rotate the Slack webhook, pause
one project, add a new service to the recipe, switch between Slack template
variants) live in [`docs/RECIPES.md`](docs/RECIPES.md).

---

## Two ways to install: CLI and UI

| | CLI (`gst install`) | Manual (Grafana UI) |
|---|---|---|
| Repeatable across stacks | ✅ same command everywhere | ❌ click-by-click |
| Idempotent | ✅ updates in place | ⚠️ depends on operator |
| Auditable change log | ✅ in your shell history / CI logs | ⚠️ Grafana audit log only |
| Dry-run preview | ✅ `--dry-run` | ❌ |
| Preferred for | bulk rollouts, fleets of services | one-off changes, evaluation |
| Walkthrough | [`docs/QUICKSTART.md`](docs/QUICKSTART.md) | [`docs/MANUAL_INSTALL.md`](docs/MANUAL_INSTALL.md) |

Both paths produce the **same result** in Grafana — `gst install` simply
calls the same provisioning APIs the UI does. You can mix and match (e.g.
install via UI, then later refactor with `gst`).

---

## Runtime manifest (kill-switch)

A small JSON file at the repo root, [`relay.manifest.json`](relay.manifest.json),
acts as a runtime gate consumed by both:

- The `gst` CLI before every `install` call (refuses to apply if
  `service_status != "active"`)
- The optional `cloud-relay-hub` Cloudflare Worker on every alert (drops
  forwards if `service_status != "active"`)

```jsonc
{
  "schema_version": 1,
  "service_status": "active",
  "min_supported_version": "0.1.0",
  "deprecated_versions": [],
  "projects": {
    "grafana-stack-templates": { "status": "active" }
  },
  "deployment_overrides": []
}
```

Flip `service_status: "active" → "paused"`, commit to `main`, and within
~60 seconds every alert flowing through the relay drops to a no-op
(`200 OK`, no Slack post) and every new `gst install` invocation refuses
to run. Full schema: [`docs/CONFIGURATION.md`](docs/CONFIGURATION.md).

---

## Local development

```bash
git clone https://github.com/Tarunrj99/grafana-stack-templates.git
cd grafana-stack-templates
make venv install        # creates .venv and installs in editable mode with [dev]
make test                # pytest
make lint                # ruff check
```

Or without `make`:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

Useful environment variables for development:

| Var | Purpose |
|---|---|
| `GST_DISABLE_MANIFEST_CHECK=1` | Skip the runtime gate (offline / air-gapped dev) |
| `GST_TOLERATE_MISSING_MANIFEST=1` | Continue if the manifest fetch fails (don't combine with the above) |
| `GST_DRY_RUN=1` | Equivalent to passing `--dry-run` on every command |

---

## Extending

### Add a new module

1. Pick the right category (`alert-rules/`, `dashboards/`, `slack-templates/`,
   `sm-checks/`).
2. Create `modules/<category>/<your-module>/` with at minimum:
   - `meta.yaml` — id, version, description, `requires:` block
   - `<your-resource>.yaml` (or `.json` / `.tpl`) — the templated resource
   - `README.md` — purpose, inputs, output, sample render
3. The catalog reader picks it up automatically — no registration required.
4. Add an entry to [`docs/MODULES.md`](docs/MODULES.md) and a one-line bullet
   to `CHANGELOG.md` under `## [Unreleased]`.

### Add a new recipe

1. Drop `modules/recipes/<your-recipe>/recipe.yaml` referencing existing
   modules.
2. List the inputs each `apply_for_each` step expects.
3. Add a worked example under `examples/`.

Full recipe + walkthrough in [`CONTRIBUTING.md`](CONTRIBUTING.md).

---

## Docs index

| Doc | Topic |
|---|---|
| [`QUICKSTART.md`](docs/QUICKSTART.md) | 5-minute end-to-end walkthrough |
| [`ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Design rationale and trade-offs |
| [`MODULES.md`](docs/MODULES.md) | Every module, its inputs, what it produces |
| [`MANUAL_INSTALL.md`](docs/MANUAL_INSTALL.md) | UI walkthrough (no CLI required) |
| [`RECIPES.md`](docs/RECIPES.md) | Operational playbook — rotate webhook, pause one project, switch templates, … |
| [`CONFIGURATION.md`](docs/CONFIGURATION.md) | Runtime manifest schema, env vars, defaults |
| [`SAMPLE_OUTPUT.md`](docs/SAMPLE_OUTPUT.md) | What rendered Slack messages look like, every template variant |
| [`DEBUG.md`](docs/DEBUG.md) | Troubleshooting checklist, common errors, dry-run modes |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Dev setup, PR checklist, commit style |
| [`SECURITY.md`](SECURITY.md) | Reporting policy, supported versions |
| [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) | Community norms |
| [`CHANGELOG.md`](CHANGELOG.md) | Release notes |

---

## Contributing

PRs and issues are very welcome. The short version:

1. Fork the repo and create a feature branch.
2. `make venv install && make test && make lint` — everything must be green.
3. If you add a new module, mirror it in [`docs/MODULES.md`](docs/MODULES.md)
   and add a bullet to [`CHANGELOG.md`](CHANGELOG.md) under `## [Unreleased]`.
4. Open a PR against `main` with a clear title and a link to any related issue.

Full checklist, coding conventions, and release process live in
[`CONTRIBUTING.md`](CONTRIBUTING.md). A community-friendly code of conduct
is in [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

---

## Security

`gst` keeps secrets out of files: `GRAFANA_TOKEN`, `SM_ACCESS_TOKEN`, and
`SLACK_WEBHOOK` are always read from environment variables. The runtime
manifest is intentionally public (no PAT to manage); only commit access to
the catalog repo gates writes. If you find a security issue, please do
**not** open a public issue — follow the disclosure process in
[`SECURITY.md`](SECURITY.md).

---

## License

MIT — see [`LICENSE`](LICENSE). Use it freely inside your organisation or
as the base for your own Grafana Cloud automation. Attribution is appreciated
but not required.
