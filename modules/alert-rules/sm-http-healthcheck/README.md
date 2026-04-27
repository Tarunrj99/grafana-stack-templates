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
| `service` | `encryptly` | yes |
| `service_slug` | `encryptly` | yes |
| `job` | `Api [encryptly] /healthz` | yes |
| `target` | `https://api.satschel.com/v2/encryptly/healthz` | yes |
| `dashboard_url` | `https://yourstack.grafana.net/a/grafana-synthetic-monitoring-app/checks/123` | yes |
| `team` | `devops` | yes |
| `createdby` | `tarun_shubham` | yes |
| `alertgroup` | `appstatus` | yes |
| `severity` | `critical` | no (default `critical`) |

## Pairs nicely with

- [`slack-templates/app-status-rich`](../../slack-templates/app-status-rich/) — for the Slack output
- [`recipes/synthetic-monitoring-pack`](../../recipes/synthetic-monitoring-pack/) — for a full end-to-end setup
