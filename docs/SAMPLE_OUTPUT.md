# Sample output

What rendered Slack messages look like for each template variant, both
firing and resolved states. Copy these into a Slack draft message preview
to verify your formatting locally before deploying.

> All examples assume the standard alert label set produced by this
> catalog: `team=devops`, `service=<name>`, `severity=critical`,
> `alertgroup=appstatus`. Annotations: `description`, `runbook_url`,
> `dashboard_url`.

## Contents

- [`app-status-rich`](#app-status-rich) — default
- [`app-status-compact`](#app-status-compact) — mobile single-line
- [`app-status-detailed`](#app-status-detailed) — incident-review
- [Dashboard snapshot](#dashboard-snapshot)

---

## app-status-rich

Block-kit style with colored bar, per-alert fields, and inline link
buttons. Mobile-friendly. Used by the reference deployment.

### Firing — single service

```
🚨 1 service DOWN
🔴 auth-service · critical
   https://api.example.com/v2/auth-service/healthz
   Started: 28 Apr 2026 12:15 UTC · Today 5:45 PM your local
   🔗 Open · 📊 Dashboard
```

### Resolved — single service

```
✅ 1 service recovered
🟢 auth-service · critical
   https://api.example.com/v2/auth-service/healthz
   Started:  28 Apr 2026 12:15 UTC · Today 5:45 PM your local
   Resolved: 28 Apr 2026 12:22 UTC · Today 5:52 PM your local
   🔗 Open · 📊 Dashboard
```

### Firing — multiple services

```
🚨 3 services DOWN
🔴 auth-service · critical
   https://api.example.com/v2/auth-service/healthz
   Started: 28 Apr 2026 12:15 UTC · Today 5:45 PM your local
   🔗 Open · 📊 Dashboard
🔴 payments-service · critical
   https://payments.example.com/
   Started: 28 Apr 2026 12:16 UTC · Today 5:46 PM your local
   🔗 Open · 📊 Dashboard
🔴 fast · critical
   https://fast.example.com/
   Started: 28 Apr 2026 12:16 UTC · Today 5:46 PM your local
   🔗 Open · 📊 Dashboard
```

### Notes on rendering

- The "Today 5:45 PM your local" portion is rendered by Slack's native
  `<!date^TIMESTAMP^...|fallback>` token — every viewer sees their own
  timezone. Grafana sees only the UTC string.
- The colored bar is set via Slack's `attachments[].color` field
  (`#dc3545` for firing, `#28a745` for resolved).
- The icon emoji is configured at the contact-point level
  (`:rotating_light:`).

---

## app-status-compact

Single line per service. No links, no color, designed for high-volume
noise channels where you want a 30-second skim.

### Firing

```
🔴 auth-service DOWN since 12:15 UTC · https://api.example.com/v2/auth-service/healthz
🔴 payments-service  DOWN since 12:16 UTC · https://payments.example.com/
```

### Resolved

```
🟢 auth-service UP after 7m · https://api.example.com/v2/auth-service/healthz
🟢 payments-service  UP after 6m · https://payments.example.com/
```

### Notes

- Plain mrkdwn — no block-kit. Costs Slack less to render and shows up
  faster on cold mobile clients.
- Best in channels where you mute everything except @here mentions and
  use the line as a "is X down right now" pulse.

---

## app-status-detailed

Block-kit, includes the alert description and the full label set. Designed
for incident-review channels and post-incident threads.

### Firing — single service

```
🚨 1 service DOWN — incident-review
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 auth-service · critical · team:devops · alertgroup:appstatus
   Endpoint: https://api.example.com/v2/auth-service/healthz
   Started:  28 Apr 2026 12:15 UTC (Today 5:45 PM your local)
   Description: Healthcheck failing — pod count 0/2 in both clusters

   Labels:
     team=devops · service=auth-service · severity=critical
     alertgroup=appstatus · __alert_rule_uid__=…

   🔗 Open · 📊 Dashboard · 📓 Runbook
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Resolved — single service

```
✅ 1 service recovered — incident-review
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🟢 auth-service · critical · team:devops · alertgroup:appstatus
   Endpoint: https://api.example.com/v2/auth-service/healthz
   Started:  28 Apr 2026 12:15 UTC (Today 5:45 PM your local)
   Resolved: 28 Apr 2026 12:22 UTC (Today 5:52 PM your local)
   Duration: 7m

   Labels:
     team=devops · service=auth-service · severity=critical
     alertgroup=appstatus · __alert_rule_uid__=…

   🔗 Open · 📊 Dashboard · 📓 Runbook
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Notes

- "Duration" is computed in the template (`EndsAt - StartsAt` rounded to
  whole minutes).
- The labels block is intentionally verbose — the goal is to support
  later post-incident review by grep'ing channel history.

---

## Dashboard snapshot

Shipped under
[`modules/dashboards/synthetic-monitoring-overview/dashboard.json`](../modules/dashboards/synthetic-monitoring-overview/dashboard.json).

Three rows top to bottom:

1. **Overview tiles**
   - Total checks · Currently failing · % uptime in last 24 h
2. **Per-check probe success** — one time-series, all checks overlaid,
   binary 0/1 (red bands when 0).
3. **Latency p95** — same overlay, `probe_duration_seconds{quantile="0.95"}`.

The dashboard does not pin a service list — it uses
`label_values(probe_success, instance)` so adding a new SM check
auto-populates everywhere.

---

## How to render locally without Slack

The Grafana template editor includes a *Preview* button that takes a
synthetic alert payload and renders the template. To test against a real
payload:

1. **Alerts → Alert rules → \<your rule\> → … → Show JSON**, copy.
2. **Alerts → Contact points → Notification templates → \<your template\>
   → Preview**, paste the JSON into the *Sample data* field.
3. The right-hand pane shows the rendered output exactly as Slack would
   receive it.

This works without sending anything to Slack and is the safest way to
verify a template change before pushing it to production.
