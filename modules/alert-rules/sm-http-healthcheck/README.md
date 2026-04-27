# alert-rules / sm-http-healthcheck

Alert rule template that fires when a Grafana Synthetic Monitoring HTTP check has been failing for 5 minutes.

## Behavior

- **Query:** `avg_over_time(probe_success{job="<job>", instance="<target>"}[5m])`
- **Threshold:** result `< 1` → fire
- **For:** `5m`
- **NoData / Error state:** Alerting
- **Severity (default):** `critical`

## Variables

When applying this template you provide:

| Variable | Example | Required |
|---|---|---|
| `service` | `auth-service` | yes |
| `service_slug` | `auth-service` | yes |
| `job` | `Api [auth-service] /healthz` | yes |
| `target` | `https://api.acme.com/v2/auth-service/healthz` | yes |
| `dashboard_url` | `https://yourstack.grafana.net/a/grafana-synthetic-monitoring-app/checks/123` | yes |
| `team` | `devops` | yes |
| `createdby` | `your-username` | yes |
| `alertgroup` | `appstatus` | yes |
| `severity` | `critical` | no (default `critical`) |

## Pairs nicely with

- [`slack-templates/app-status-rich`](../../slack-templates/app-status-rich/) — for the Slack output
- [`recipes/synthetic-monitoring-pack`](../../recipes/synthetic-monitoring-pack/) — for a full end-to-end setup
