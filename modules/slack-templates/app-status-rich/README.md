# slack-templates / app-status-rich

The default Slack notification template for application status alerts.
Block-kit style with a colored bar (red firing / green resolved), per-alert
fields, inline link buttons, and viewer-localized timestamps via Slack's
native `<!date^>` token.

This is **Variant A**, the variant the reference deployment uses.

## What it produces

**On firing:**

```
🚨 1 service DOWN
🔴 auth-service · critical
   https://api.example.com/v2/auth-service/healthz
   Started: 28 Apr 2026 12:15 UTC · Today 5:45 PM your local
   🔗 Open · 📊 Dashboard
```

**On resolved:**

```
✅ 1 service recovered
🟢 auth-service · critical
   https://api.example.com/v2/auth-service/healthz
   Started:  28 Apr 2026 12:15 UTC · Today 5:45 PM your local
   Resolved: 28 Apr 2026 12:22 UTC · Today 5:52 PM your local
   🔗 Open · 📊 Dashboard
```

See the full sample gallery (multi-service, all timezones) in
[`docs/SAMPLE_OUTPUT.md`](../../../docs/SAMPLE_OUTPUT.md#app-status-rich).

## Required alert metadata

This template renders the following labels/annotations from the alert
payload. Alerts produced by the
[`alert-rules/sm-http-healthcheck`](../../alert-rules/sm-http-healthcheck/)
module already include all of these.

| | Source | Used as |
|---|---|---|
| `labels.service` | label | bold service name |
| `labels.severity` | label | severity tag |
| `annotations.runbook_url` | annotation | endpoint line + "Open" link |
| `annotations.dashboard_url` | annotation | "Dashboard" link |

## Install via the CLI

```bash
gst install slack-templates/app-status-rich \
  --deployment-id=my-prod
```

This uploads the template to Grafana under the name `app_status_slack` and
points the existing `application-status` contact point at it. Re-running
the command updates the template in place.

## Install via the Grafana UI

Walkthrough: [`docs/MANUAL_INSTALL.md` § 2](../../../docs/MANUAL_INSTALL.md#2-install-a-notification-template)
and [§ 3](../../../docs/MANUAL_INSTALL.md#3-wire-up-a-slack-contact-point).

Quick version: paste [`template.tpl`](template.tpl) into *Alerts → Contact
points → Notification templates → New template → Content* under the name
`app_status_slack`. Reference it from your contact point as:

```
Title: {{ template "app_status.title" . }}
Text:  {{ template "app_status.text" . }}
```

## See also

- [`slack-templates/app-status-compact`](../app-status-compact/) — single-line variant.
- [`slack-templates/app-status-detailed`](../app-status-detailed/) — incident-review variant.
- [`docs/SAMPLE_OUTPUT.md`](../../../docs/SAMPLE_OUTPUT.md) — rendered samples for all three variants.

## License

MIT
