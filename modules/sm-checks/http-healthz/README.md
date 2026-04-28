# sm-checks / http-healthz

Generic HTTP `GET` healthcheck for Grafana Cloud Synthetic Monitoring.
Defaults are tuned for a service that exposes `/healthz` and returns
`200`/`201`.

## What it produces

One Synthetic Monitoring check with:

- **Type:** HTTP, GET, follow redirects.
- **Frequency:** 10 minutes (override via `frequency_ms`).
- **Timeout:** 5 seconds (override via `timeout_ms`).
- **Probe locations:** one (Ohio, probe id `853`) by default.
- **TLS:** validate; `failIfNotSSL: true`, `failIfSSL: false`.
- **Valid status codes:** `200, 201`.
- **`alertSensitivity: none`** — alerts come from the `alert-rules/sm-http-healthcheck` rule on top, not from SM's built-in alerting.
- **`basicMetricsOnly: true`** — smaller cardinality, identical signal for a healthcheck.

## Required inputs

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
| `probes` | `[853, 854]` | `[853]` (Ohio only) |

## Install via the CLI

```bash
gst install sm-checks/http-healthz \
  --deployment-id=my-prod \
  --inputs=- <<EOF
service: auth-service
target: https://api.example.com/v2/auth-service/healthz
team: devops
createdby: your-username
alertgroup: appstatus
EOF
```

Idempotent — re-running with the same `target` updates the existing check
in place; no duplicate is created.

## Install via the Grafana UI

Walkthrough: [`docs/MANUAL_INSTALL.md` § 1](../../../docs/MANUAL_INSTALL.md#1-install-a-synthetic-monitoring-http-check).

## Pairs nicely with

- [`alert-rules/sm-http-healthcheck`](../../alert-rules/sm-http-healthcheck/) — fires on 5 min of failure of this check.
- [`dashboards/synthetic-monitoring-overview`](../../dashboards/synthetic-monitoring-overview/) — visualises every check including this one.
- [`recipes/synthetic-monitoring-pack`](../../recipes/synthetic-monitoring-pack/) — installs the SM check + alert rule + Slack template for a list of services.

## License

MIT
