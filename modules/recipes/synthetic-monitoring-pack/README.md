# recipes / synthetic-monitoring-pack

End-to-end Grafana Cloud Synthetic Monitoring setup in a single command.

## What it installs

For every service you list:

1. An **HTTP /healthz Synthetic Monitoring check** (Atlanta probe, 10-min frequency, basicMetricsOnly)
2. An **alert rule** that fires after 5 minutes of `probe_success < 1`, with `severity=critical`
3. (Once, shared) The **`app-status-rich` Slack notification template**

## Quick try

Save this as `services.yaml`:

```yaml
defaults:
  team: devops
  createdby: tarun_shubham
  alertgroup: appstatus

services:
  - service: encryptly
    service_slug: encryptly
    target: https://api.satschel.com/v2/encryptly/healthz
    dashboard_url: https://yourstack.grafana.net/...
    job: "Api [encryptly] /healthz"
```

Then:

```bash
gst install recipes/synthetic-monitoring-pack \
  --inputs=services.yaml \
  --grafana-url=$GRAFANA_URL \
  --grafana-token=$GRAFANA_TOKEN \
  --sm-token=$SM_ACCESS_TOKEN \
  --slack-webhook=$SLACK_WEBHOOK \
  --dry-run
```

Drop `--dry-run` to apply.

## Composing modules

This recipe wires up three independent modules:

- [`sm-checks/http-healthz`](../../sm-checks/http-healthz/)
- [`alert-rules/sm-http-healthcheck`](../../alert-rules/sm-http-healthcheck/)
- [`slack-templates/app-status-rich`](../../slack-templates/app-status-rich/)

You can use any of them independently if you don't want the full pack.
