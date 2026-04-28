# Module catalog

Every module in this repo, what it produces, and what it expects from the
operator.

> Run `gst ls` to see this list at a terminal. Run `gst show <id>` to see
> the same info plus the resource files the module ships.

## Contents

- [Dashboards](#dashboards)
- [Alert rules](#alert-rules)
- [Synthetic Monitoring checks](#synthetic-monitoring-checks)
- [Slack notification templates](#slack-notification-templates)
- [Recipes](#recipes)

---

## Dashboards

### `dashboards/synthetic-monitoring-overview`

A single-pane dashboard listing every Synthetic Monitoring check in the
stack with its current `probe_success`, p95 latency, and last-failure
timestamp. The intended use is "the screen you put up in a Slack huddle
when an alert fires".

| | |
|---|---|
| **Type** | `dashboard` |
| **Target** | `grafana-cloud` |
| **Folder** | `SM Alerts` (created if missing) |
| **Source file** | [`modules/dashboards/synthetic-monitoring-overview/dashboard.json`](../modules/dashboards/synthetic-monitoring-overview/dashboard.json) |

**Required inputs:** none.

**What it creates:** one dashboard with three rows — overview tiles,
per-check probe success time-series, latency p95 panel.

**Sample render:** see the screenshots referenced in
[`SAMPLE_OUTPUT.md`](SAMPLE_OUTPUT.md#dashboard-snapshot).

---

## Alert rules

### `alert-rules/sm-http-healthcheck`

Fires when a Grafana Synthetic Monitoring HTTP check has been failing for
five minutes. Carries the standard label set the rest of the catalog
expects.

| | |
|---|---|
| **Type** | `alert-rule` |
| **Target** | `grafana-cloud` |
| **Source file** | [`modules/alert-rules/sm-http-healthcheck/rule.yaml`](../modules/alert-rules/sm-http-healthcheck/rule.yaml) |
| **Folder** | `SM Alerts` |
| **Group** | `synthetic-monitoring-appstatus` |

**Required inputs:**

| Variable | Example | Notes |
|---|---|---|
| `service` | `auth-service` | display name, used in the alert title |
| `service_slug` | `auth-service` | safe-for-rule-name slug |
| `job` | `Api [auth-service] /healthz` | Grafana SM job string |
| `target` | `https://api.example.com/v2/auth-service/healthz` | full URL the check probes |
| `dashboard_url` | `https://yourstack.grafana.net/a/grafana-synthetic-monitoring-app/checks/12345` | link the Slack template will surface |
| `team` | `devops` | propagated to label `team` |

**What it creates:** an alert rule named `SM_HealthCheck_<slug>_DOWN`
with `for: 5m`, `severity: critical`, `team: <team>`, and
`alertgroup: appstatus`.

**Routing labels:** `team`, `service`, `severity=critical`,
`alertgroup=appstatus`. These are what notification policies key on.

---

## Synthetic Monitoring checks

### `sm-checks/http-healthz`

Generic HTTP `GET` healthcheck for Grafana Cloud Synthetic Monitoring.
Defaults are tuned for a service that exposes `/healthz` and returns
`200`/`201`.

| | |
|---|---|
| **Type** | `synthetic-monitoring-check` |
| **Target** | `grafana-cloud-sm` |
| **Source file** | [`modules/sm-checks/http-healthz/check.yaml`](../modules/sm-checks/http-healthz/check.yaml) |
| **Probe locations** | one (Ohio, probe id `853`) by default |

**Required inputs:**

| Variable | Example | Default |
|---|---|---|
| `service` | `auth-service` | — |
| `target` | `https://api.example.com/v2/auth-service/healthz` | — |
| `team` | `devops` | — |
| `createdby` | `your-username` | — |
| `alertgroup` | `appstatus` | — |
| `path` | `/healthz` | `/healthz` |
| `frequency_ms` | `60000` | `600000` (10 min) |
| `timeout_ms` | `5000` | `5000` |
| `probes` | `[853, 854]` | `[853]` |

**What it creates:** one Synthetic Monitoring check with
`alertSensitivity: none` (alerts are produced by the *alert rule* on top,
not by SM's built-in alerting).

**Why `alertSensitivity: none`:** SM's built-in alerts can't carry the
standard label set, can't be silenced from Grafana's UI, and can't share a
notification template with non-SM alerts. Routing through a normal alert
rule keeps everything uniform.

---

## Slack notification templates

Three variants are shipped. Pick whichever matches the channel you're
posting to.

| Variant | Channel | One-line summary |
|---|---|---|
| [`app-status-rich`](#slack-templatesapp-status-rich) | default ops channel | One block per service, colored bar (red firing / green resolved), inline "Open" + "Dashboard" links, both UTC and viewer-local timestamps. |
| [`app-status-compact`](#slack-templatesapp-status-compact) | high-volume noise channel | One line per service. No links, no color. Designed to be skimmable on mobile. |
| [`app-status-detailed`](#slack-templatesapp-status-detailed) | incident-review channel | Same as `app-status-rich` plus the alert description, all routing labels, and timestamps in two zones. |

All three expect the same alert annotations (`description`, `dashboard_url`,
optionally `runbook_url`) and the same labels (`team`, `service`,
`severity`, `alertgroup`). The alert rule modules in this catalog produce
exactly that label set, so the three templates are drop-in interchangeable.

### `slack-templates/app-status-rich`

| | |
|---|---|
| **Source file** | [`modules/slack-templates/app-status-rich/template.tpl`](../modules/slack-templates/app-status-rich/template.tpl) |
| **Block-kit** | yes |
| **Mobile-friendly** | yes |
| **Rendered preview** | [`SAMPLE_OUTPUT.md` § app-status-rich](SAMPLE_OUTPUT.md#app-status-rich) |

The reference deployment uses this variant.

### `slack-templates/app-status-compact`

| | |
|---|---|
| **Source file** | [`modules/slack-templates/app-status-compact/template.tpl`](../modules/slack-templates/app-status-compact/template.tpl) |
| **Block-kit** | no (plain mrkdwn) |
| **Lines per service** | 1 |
| **Rendered preview** | [`SAMPLE_OUTPUT.md` § app-status-compact](SAMPLE_OUTPUT.md#app-status-compact) |

### `slack-templates/app-status-detailed`

| | |
|---|---|
| **Source file** | [`modules/slack-templates/app-status-detailed/template.tpl`](../modules/slack-templates/app-status-detailed/template.tpl) |
| **Block-kit** | yes |
| **Includes labels block** | yes |
| **Rendered preview** | [`SAMPLE_OUTPUT.md` § app-status-detailed](SAMPLE_OUTPUT.md#app-status-detailed) |

---

## Recipes

### `recipes/synthetic-monitoring-pack`

End-to-end Synthetic Monitoring setup for a list of services. For every
service you list, this recipe creates one HTTP `/healthz` check, one alert
rule that fires after 5 min of failure, and ensures one Slack notification
template is installed once.

| | |
|---|---|
| **Source file** | [`modules/recipes/synthetic-monitoring-pack/recipe.yaml`](../modules/recipes/synthetic-monitoring-pack/recipe.yaml) |
| **Inputs** | `services: list` (see [`examples/services.yaml`](../examples/services.yaml)) |

**Modules invoked:**

- `sm-checks/http-healthz` — once per service
- `alert-rules/sm-http-healthcheck` — once per service
- `slack-templates/app-status-rich` — once total

**Switching the Slack template variant:** override the recipe's `modules:`
list in your fork, or run `gst install slack-templates/app-status-compact`
*after* the recipe to replace the template in place. The contact-point
wiring stays the same.

**End state:** the alert rules carry `team`, `service`, `severity`,
`alertgroup` labels — the standard labels notification policies route on.
Adjust your existing notification policy to match `alertgroup=appstatus`
and you're done.

---

## Adding a new module

See [`CONTRIBUTING.md`](../CONTRIBUTING.md#adding-a-new-module) for the
full walkthrough. Short version: drop a folder under
`modules/<category>/<id>/` with `meta.yaml` + the resource file + a
`README.md`, then add a row to this table.
