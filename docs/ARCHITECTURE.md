# Architecture

This document explains *why* the project looks the way it does. If you only
want to install something, start with the [README](../README.md) or the
[QUICKSTART](QUICKSTART.md).

## Goals

1. **Make Grafana Cloud configuration repeatable.** Same config across
   stacks, same labels across rules, same Slack template across services.
2. **Stay declarative.** Every module is a YAML/JSON file you can read,
   diff, and review in a PR. No imperative "click this then that" recipes.
3. **Stay dual-mode.** Operators who like the CLI get `gst install`;
   operators who prefer the UI get a step-by-step recipe in
   [`MANUAL_INSTALL.md`](MANUAL_INSTALL.md). Both produce the same result.
4. **Keep secrets out of the repo.** Tokens and webhooks live in env vars
   only, both for the CLI and for the optional relay layer.
5. **Have a runtime kill-switch.** A single file at the repo root
   (`relay.manifest.json`) can stop the world without redeploying anything.

## Three layers

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1 — the catalog                                       │
│   modules/{category}/{id}/  +  recipes/                     │
│   declarative YAML/JSON only                                │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ read by both:
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
┌──────────────────────────┐   ┌───────────────────────────────┐
│ Layer 2a — `gst` CLI     │   │ Layer 2b — Manual UI install  │
│   catalog.py reads YAML  │   │   docs/MANUAL_INSTALL.md      │
│   manifest.py gates      │   │   walks the same shape, just  │
│   installers/* call APIs │   │   click-by-click              │
└──────────────────┬───────┘   └────────────────┬──────────────┘
                   │                            │
                   └────────────┬───────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────┐
│ Layer 3 — Grafana Cloud (provisioning APIs)                 │
│   alert-rules · contact-points · templates                  │
│   Synthetic Monitoring · folders                            │
└────────────────────────────┬────────────────────────────────┘
                             │ Slack webhook
                             ▼
                ┌───────────────────────────────┐
                │ Slack — directly, OR via the  │
                │ optional cloud-relay-hub      │
                │ Cloudflare Worker (separate   │
                │ private repo).                │
                └───────────────────────────────┘
```

## Layer 1: the catalog

Each `modules/<category>/<id>/` folder is a self-describing unit:

- `meta.yaml` — id, version, type, target system, human description, and a
  `requires:` block listing the inputs the operator must supply.
- One or more **resource files** — `rule.yaml`, `check.yaml`, `template.tpl`,
  `dashboard.json`. These are Jinja-templated where they need operator
  values; everything else is plain text.
- `README.md` — one-paragraph purpose, inputs, outputs, sample rendered output.

A **recipe** is just another folder under `modules/recipes/<id>/` with a
`recipe.yaml` instead of `meta.yaml`. It references existing modules and
declares whether each is `apply_once` or `apply_for_each: <input-list>`.

### Why YAML, not Python

Modules are configuration, not behavior. YAML is:

- Easy to diff (no formatting noise, no symbol drift).
- Easy to validate without executing it.
- Friendly to operators who don't write Python.

The Python layer reads the YAML and calls APIs. None of the *content* of an
alert rule lives in Python.

### Why one folder per module (instead of one big file)

- The `README.md` lives next to the resource it documents → it stays in sync.
- Module-level boundaries make PRs scope-tight: one new alert rule = one new
  folder.
- The catalog reader walks the directory and discovers modules
  automatically; there's no central registry to forget to update.

## Layer 2a: the `gst` CLI

Source: [`src/grafana_stack_templates/`](../src/grafana_stack_templates/).

| Module | What it owns |
|---|---|
| `catalog.py` | Walks `modules/` and returns `Module` records. Used by `gst ls`, `gst show`, and every installer. |
| `manifest.py` | Fetches `relay.manifest.json` from the GitHub Contents API; raises `ManifestError` if the deployment is paused or the CLI version is unsupported. |
| `clients.py` | One `Env` dataclass for credentials; one `APIError` type all installers raise. |
| `cli.py` | Click commands: `ls`, `show`, `manifest`, `plan`, `install`. |
| `installers/` | One module per resource type: `alert_rule.py`, `slack_template.py`, `sm_check.py`, `recipe.py`. Each one is responsible for *idempotency* (creating or updating, never duplicating). |

### Idempotency

Every installer follows the same pattern:

1. Render the resource from the module's templated file + the operator's inputs.
2. Look up the existing resource by a stable identifier (`uid` for alert
   rules, `name` for templates, `target` URL for SM checks).
3. If found → `PUT` (update). If not found → `POST` (create). Never `POST`
   twice.

That means re-running `gst install` is always safe: no duplicate alert rules,
no duplicate SM checks. CI pipelines can run it on every merge without
fearing drift.

### Why a manifest gate at install time

Even though `relay.manifest.json` is mostly used by the runtime relay, the
CLI consults it too. Reasons:

- Lets a maintainer pause *all* operator workflows by editing one file
  (e.g. during a partial-outage cleanup, or while migrating manifests).
- Lets a maintainer reject installs from old CLI versions when a breaking
  change ships in the catalog (`min_supported_version`).
- Lets a maintainer pause one specific deployment without touching the
  others (`deployment_overrides`).

Operators who want to dev offline pass `GST_DISABLE_MANIFEST_CHECK=1`.

## Layer 2b: manual UI install

Every module's `meta.yaml` and resource file are also paste-ready specs for
the Grafana UI. [`MANUAL_INSTALL.md`](MANUAL_INSTALL.md) walks the four
common cases:

- Create a Synthetic Monitoring HTTP check.
- Create a notification template.
- Create / wire up a Slack contact point.
- Create an alert rule with the standard label set.

The point is that the catalog and the UI agree: nothing in the YAML
"requires the CLI". The CLI is a convenience.

## Layer 3: Grafana Cloud

`gst install` calls only the **provisioning** API surfaces, not the UI APIs:

- `POST/PUT /api/v1/provisioning/alert-rules`
- `PUT      /api/v1/provisioning/templates/<name>`
- `POST/PUT /api/v1/provisioning/contact-points`
- `POST/PUT https://synthetic-monitoring-api.grafana.net/api/v1/check/{add,update}`

Provisioned resources show up in the Grafana UI but are *read-only* there
unless you also flip the `editor` flag — which is intentional. Drift between
the UI and the catalog is annoying; making provisioned objects read-only
prevents most of it.

## The optional relay (cross-reference)

For richer routing (project-level kill-switch, per-deployment pause, audit
logs of every alert before it hits Slack), you can put a Cloudflare Worker
between Grafana and Slack. The Worker reads the **same**
`relay.manifest.json` this catalog publishes, and it's stored in a separate
private repo (`Tarunrj99/cloud-control`, folder `relays/cloud-relay-hub`).

If you don't deploy the relay, Grafana's built-in Slack contact point
points directly at your incoming webhook and everything still works. The
catalog modules are agnostic to that choice.

## Trade-offs

| We chose… | Over… | Because… |
|---|---|---|
| YAML modules | Terraform / Pulumi providers | smaller dependency surface; works against the same provisioning APIs without a state file; no schema drift between provider versions and Grafana itself. |
| One repo, no build step | Wheel + entry-points | the catalog *is* the artefact; you read it before you install it. |
| GitHub Contents API for manifest | A signed S3 / Workers KV manifest | zero new infrastructure to host; transparent diffs; world-readable. |
| Idempotent PUTs | Apply-then-verify | one round-trip per module; safe to re-run; no orphan state file. |
| `apply_for_each` recipe semantics | One YAML per service | adding a new service = one row in `services.yaml`, not a new module. |

## What's *not* in scope

- **Dashboard authoring.** The catalog ships ready-made dashboards but
  doesn't replace Grafana's dashboard designer. Use the UI to design,
  export the JSON, drop it in `modules/dashboards/<id>/dashboard.json`.
- **Metrics scraping configuration.** Out of scope; this catalog assumes
  your stack already scrapes the metrics it queries.
- **Cross-stack dependency management.** A module is one resource on one
  stack. If your stack imports another stack's data source, that wiring is
  yours to maintain.

## Future directions

Tracked in [issues](https://github.com/Tarunrj99/grafana-stack-templates/issues),
but the broad shape:

- More dashboard modules (per language runtime, per common third-party).
- More alert-rule modules (saturation, latency, error-budget burn).
- A `gst diff` command that compares the catalog state to the live stack.
- A `gst export` command that pulls existing UI-configured resources into
  module shape (one-shot migration helper).
