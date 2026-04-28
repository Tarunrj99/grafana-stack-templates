# slack-templates / app-status-compact

A single-line-per-service Slack template. No block-kit, no colored bar, no
inline links — just plain mrkdwn lines that survive cold mobile clients
well. Designed for high-volume noise channels where you want a 30-second
skim rather than a click-through.

## What it produces

**On firing:**

```
🔴 auth-service DOWN since 12:15 UTC · https://api.example.com/v2/auth-service/healthz
🔴 payments-service  DOWN since 12:16 UTC · https://payments.example.com/
```

**On resolved:**

```
🟢 auth-service UP after 12:22 UTC (started 12:15) · https://api.example.com/v2/auth-service/healthz
🟢 payments-service  UP after 12:23 UTC (started 12:16) · https://payments.example.com/
```

See the full sample gallery in
[`docs/SAMPLE_OUTPUT.md`](../../../docs/SAMPLE_OUTPUT.md#app-status-compact).

## Required alert metadata

| | Source | Used as |
|---|---|---|
| `labels.service` | label | bold service name |
| `annotations.runbook_url` | annotation | endpoint suffix |

## When to use this variant

- Channels where five concurrent alerts is normal, not exceptional.
- Mobile-only ops (each line is one Slack notification chime, not an
  expandable attachment).
- Channels where you mute everything except `@here` and the line is just
  a "is X down right now" pulse.

For a richer rendering with explicit "Started/Resolved" lines and
clickable buttons, use
[`app-status-rich`](../app-status-rich/) instead.

## Install via the CLI

```bash
gst install slack-templates/app-status-compact \
  --deployment-id=my-prod
```

The contact point's *Title* / *Text* references the same template names
(`app_status.title` and `app_status.text`), so this command **replaces**
whichever variant is currently installed — there's no migration step.

## Install via the Grafana UI

Walkthrough: [`docs/MANUAL_INSTALL.md` § 2](../../../docs/MANUAL_INSTALL.md#2-install-a-notification-template).
Paste [`template.tpl`](template.tpl) under the name `app_status_slack`.

## See also

- [`slack-templates/app-status-rich`](../app-status-rich/) — default block-kit variant.
- [`slack-templates/app-status-detailed`](../app-status-detailed/) — verbose incident-review variant.

## License

MIT
