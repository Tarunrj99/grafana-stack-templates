# recipes / synthetic-monitoring-pack

End-to-end Grafana Cloud Synthetic Monitoring setup in a single command.

For every service you list, this recipe creates:

1. An **HTTP `/healthz` Synthetic Monitoring check** ([`sm-checks/http-healthz`](../../sm-checks/http-healthz/)) — Ohio probe, 10-min frequency, `alertSensitivity: none`, `basicMetricsOnly: true`.
2. An **alert rule** ([`alert-rules/sm-http-healthcheck`](../../alert-rules/sm-http-healthcheck/)) that fires after 5 min of `probe_success < 1`, with the standard label set (`team`, `service`, `severity=critical`, `alertgroup=appstatus`).

Once per recipe invocation:

3. The **`app-status-rich` Slack notification template** ([`slack-templates/app-status-rich`](../../slack-templates/app-status-rich/)).

## Inputs

The recipe consumes a YAML file with a `services:` list (and optional
shared `defaults:`).

```yaml
# examples/services.yaml
defaults:
  team: devops
  createdby: your-username
  alertgroup: appstatus
  severity: critical
  path: /healthz
  frequency_ms: 600000
  timeout_ms: 5000
  probes: [853]

services:
  - service: auth-service
    service_slug: auth-service
    target: https://api.example.com/v2/auth-service/healthz
    job: "Api [auth-service] /healthz"
    dashboard_url: https://yourstack.grafana.net/a/grafana-synthetic-monitoring-app/checks
  - service: payments-service
    service_slug: payments-service
    target: https://api.example.com/v2/payments-service/healthz
    job: "Api [payments-service] /healthz"
    dashboard_url: https://yourstack.grafana.net/a/grafana-synthetic-monitoring-app/checks
```

A worked example ships at [`examples/services.yaml`](../../../examples/services.yaml).

## Install via the CLI

```bash
gst install recipes/synthetic-monitoring-pack \
  --deployment-id=my-prod \
  --inputs=examples/services.yaml \
  --dry-run                       # preview first
gst install recipes/synthetic-monitoring-pack \
  --deployment-id=my-prod \
  --inputs=examples/services.yaml
```

Both calls are idempotent: existing services are updated in place, new
ones are created, none are duplicated.

## Switching the Slack template variant

This recipe pins `slack-templates/app-status-rich`. If you want one of the
other variants for this deployment:

```bash
gst install slack-templates/app-status-compact   --deployment-id=my-prod
# or
gst install slack-templates/app-status-detailed  --deployment-id=my-prod
```

The contact-point name (`application-status`) and template name
(`app_status_slack`) are stable across variants, so the second command
**replaces** the template in place — alert rules don't need to change.

## Decommissioning a service

The recipe doesn't ship a destructive `gst uninstall`. To retire a
service, see [`docs/RECIPES.md` § 8](../../../docs/RECIPES.md#8-decommission-a-service-cleanly).

## See also

- [`docs/QUICKSTART.md`](../../../docs/QUICKSTART.md) — 5-minute walkthrough using this recipe.
- [`docs/RECIPES.md`](../../../docs/RECIPES.md) — operational playbook (rotate webhook, kill-switch, switch templates, decommission, …).
- [`docs/MANUAL_INSTALL.md`](../../../docs/MANUAL_INSTALL.md) — equivalent UI walkthrough, no CLI required.

## License

MIT
