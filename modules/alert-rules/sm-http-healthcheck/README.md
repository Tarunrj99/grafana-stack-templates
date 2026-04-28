# alert-rules / sm-http-healthcheck

Alert rule template that fires when a Grafana Synthetic Monitoring HTTP
check has been failing for 5 minutes. Carries the standard label set the
rest of the catalog expects, so notification policies can route it
uniformly with every other alert rule produced by this catalog.

## Behavior

- **Query A** (Prometheus, datasource `grafanacloud-prom`):
  `avg_over_time(probe_success{job="<job>", instance="<target>"}[5m])`
- **Condition C** (threshold): result is below `0.5`
- **For:** `5m` (must be below threshold continuously)
- **No-data state / Error state:** Alerting
- **Severity (default):** `critical`
- **Folder:** `SM Alerts` (UID `sm-alerts-folder`)
- **Group:** `synthetic-monitoring-appstatus`

## Required inputs

| Variable | Example | Notes |
|---|---|---|
| `service` | `auth-service` | display name; used in the alert title and `service` label |
| `service_slug` | `auth-service` | safe-for-rule-name slug; goes into the rule UID and title (`SM_HealthCheck_<slug>_DOWN`) |
| `job` | `Api [auth-service] /healthz` | Grafana SM job string — must match what the SM check is named |
| `target` | `https://api.example.com/v2/auth-service/healthz` | full URL the SM check probes |
| `dashboard_url` | `https://yourstack.grafana.net/a/grafana-synthetic-monitoring-app/checks/123` | surfaced in the Slack annotations as `dashboard_url` |
| `team` | `devops` | propagated to label `team` |
| `createdby` | `your-username` | propagated to label `createdby` for audit |
| `alertgroup` | `appstatus` | label notification policies route on |
| `severity` | `critical` | optional; defaults to `critical` |

## What it produces

- One alert rule named `SM_HealthCheck_<service_slug>_DOWN`.
- Labels: `team`, `service`, `severity`, `alertgroup`, `createdby`.
- Annotations: `summary`, `description`, `runbook_url=<target>`,
  `dashboard_url=<dashboard_url>`.

## Install via the CLI

```bash
gst install alert-rules/sm-http-healthcheck \
  --deployment-id=my-prod \
  --inputs=- <<EOF
service: auth-service
service_slug: auth-service
job: "Api [auth-service] /healthz"
target: https://api.example.com/v2/auth-service/healthz
dashboard_url: https://yourstack.grafana.net/a/grafana-synthetic-monitoring-app/checks
team: devops
createdby: your-username
alertgroup: appstatus
EOF
```

Use `--dry-run` to preview the API call without applying.

## Install via the Grafana UI

Walkthrough: [`docs/MANUAL_INSTALL.md` § 4](../../../docs/MANUAL_INSTALL.md#4-install-an-alert-rule).

## Pairs nicely with

- [`sm-checks/http-healthz`](../../sm-checks/http-healthz/) — produces the `probe_success` metric this rule queries.
- [`slack-templates/app-status-rich`](../../slack-templates/app-status-rich/) — renders this rule's labels/annotations into a clean Slack message.
- [`recipes/synthetic-monitoring-pack`](../../recipes/synthetic-monitoring-pack/) — installs all three together for a list of services.

## License

MIT
