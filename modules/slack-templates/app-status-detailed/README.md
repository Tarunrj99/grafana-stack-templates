# slack-templates / app-status-detailed

Block-kit Slack template, like
[`app-status-rich`](../app-status-rich/) but with the alert description,
all routing labels, and timestamps in two zones surfaced inline. Designed
for incident-review channels and post-incident threads where the goal is
grep-able context, not a tight headline.

## What it produces

**On firing:**

```
🚨 1 service DOWN — incident-review
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 auth-service · critical · team:devops · alertgroup:appstatus
   Endpoint: https://api.example.com/v2/auth-service/healthz
   Started:  28 Apr 2026 12:15 UTC · (Today 5:45 PM your local)
   Description: Healthcheck failing — pod count 0/2 in both clusters

   Labels:
     • team=devops
     • service=auth-service
     • severity=critical
     • alertgroup=appstatus

   🔗 Open · 📊 Dashboard · 📓 Runbook
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**On resolved:** identical layout plus a `Resolved:` line.

Full sample gallery in
[`docs/SAMPLE_OUTPUT.md`](../../../docs/SAMPLE_OUTPUT.md#app-status-detailed).

## Required alert metadata

| | Source | Used as |
|---|---|---|
| `labels.team` | label | "team:" tag |
| `labels.service` | label | bold service name |
| `labels.severity` | label | severity tag |
| `labels.alertgroup` | label | "alertgroup:" tag |
| `annotations.runbook_url` | annotation | endpoint line, "Open" + "Runbook" links |
| `annotations.dashboard_url` | annotation | "Dashboard" link |
| `annotations.description` | annotation | description block |

## When to use this variant

- Incident-review channels (`#incidents-review`, `#post-mortems`).
- Channels where alerts are referenced months later by ctrl-F.
- Multi-team channels where the `team:` and `alertgroup:` tags help
  readers skip unrelated alerts.

For everyday ops, prefer
[`app-status-rich`](../app-status-rich/). For mobile noise channels,
prefer [`app-status-compact`](../app-status-compact/).

## Install via the CLI

```bash
gst install slack-templates/app-status-detailed \
  --deployment-id=my-prod
```

## Install via the Grafana UI

Walkthrough: [`docs/MANUAL_INSTALL.md` § 2](../../../docs/MANUAL_INSTALL.md#2-install-a-notification-template).

## See also

- [`slack-templates/app-status-rich`](../app-status-rich/) — default block-kit variant.
- [`slack-templates/app-status-compact`](../app-status-compact/) — mobile single-line variant.

## License

MIT
