# dashboards / synthetic-monitoring-overview

A single-pane dashboard for Grafana Cloud Synthetic Monitoring. Lists every
SM check on the stack with its current `probe_success` state, p95 latency,
and 24-hour uptime — auto-populating as new checks are created.

## What it produces

Three rows, top to bottom:

1. **Overview** — three stat tiles
   - *Total checks* — `count(probe_success)`
   - *Currently failing* — `count(probe_success == 0)` (background turns
     red when ≥ 1)
   - *% uptime (last 24 h)* — `100 * avg(avg_over_time(probe_success[24h]))`
     with thresholds at 95% / 99%
2. **Per-check probe success** — one stepped time-series, all checks
   overlaid, binary 0/1 (red bands when 0).
3. **Latency** — `histogram_quantile(0.95, …probe_duration_seconds_bucket…)`,
   same overlay.

A multi-select `instance` template variable lets you focus on one service
or compare a subset.

## Required datasource

- A Prometheus datasource. The dashboard JSON pins the UID
  `grafanacloud-prom` (Grafana Cloud's default). On import, the UI lets
  you remap it to whatever your stack uses.

## Install via the CLI

```bash
gst install dashboards/synthetic-monitoring-overview \
  --deployment-id=my-prod
```

The dashboard is created (or updated in place) under the `SM Alerts`
folder and assigned the UID `sm-overview` so subsequent installs won't
duplicate it.

## Install via the Grafana UI

Walkthrough: [`docs/MANUAL_INSTALL.md` § 5](../../../docs/MANUAL_INSTALL.md#5-install-a-dashboard).

Quick version: *Dashboards → New → Import* and paste the contents of
[`dashboard.json`](dashboard.json) into the *Import via panel json* field.

## Sample render

See [`docs/SAMPLE_OUTPUT.md`](../../../docs/SAMPLE_OUTPUT.md#dashboard-snapshot).

## See also

- [`alert-rules/sm-http-healthcheck`](../../alert-rules/sm-http-healthcheck/) — the alert rule that complements this dashboard.
- [`sm-checks/http-healthz`](../../sm-checks/http-healthz/) — the SM check this dashboard visualises.

## License

MIT
