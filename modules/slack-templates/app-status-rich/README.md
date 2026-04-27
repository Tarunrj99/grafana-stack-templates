# slack-templates / app-status-rich

A polished Slack notification template for application status alerts in Grafana Cloud.

## What it produces

**On firing:**

- Red colored attachment bar
- Title: `🚨 CRITICAL — N service(s) DOWN`
- Per-alert: service, severity, team, endpoint, started time, full description
- Three clickable links: 🔧 Runbook · 📊 Dashboard · 🔕 Silence
- Footer: `Grafana Cloud SM · alertgroup=appstatus`

**On resolved:**

- Green colored bar
- Title: `🟢 RESOLVED — N service(s) UP`
- Resolved timestamp + same links

## Requirements

Your alert rules must include these labels:

- `team` (e.g. `devops`)
- `service` (the affected service identifier)
- `severity` (e.g. `critical`)
- `alertgroup` (used for routing; e.g. `appstatus`)

And these annotations:

- `runbook_url`
- `dashboard_url`
- `description`

## Install (manual)

1. **Add the template to Grafana**

   ```bash
   curl -X PUT \
     -H "Authorization: Bearer $GRAFANA_TOKEN" \
     -H "Content-Type: application/json" \
     -H "X-Disable-Provenance: true" \
     -d "$(jq -Rs --arg n app_status_slack '{name:$n, template:.}' < template.tpl)" \
     "$GRAFANA_URL/api/v1/provisioning/templates/app_status_slack"
   ```

2. **Update your Slack contact point** to reference the templates:

   ```json
   {
     "name": "application-status",
     "type": "slack",
     "settings": {
       "url": "$SLACK_WEBHOOK",
       "title": "{{ template \"app_status.title\" . }}",
       "text":  "{{ template \"app_status.text\" . }}",
       "username": "Grafana SM",
       "iconEmoji": ":satellite_antenna:"
     }
   }
   ```

## Install (via CLI)

```bash
gst install slack-templates/app-status-rich \
  --grafana-url=$GRAFANA_URL \
  --grafana-token=$GRAFANA_TOKEN \
  --slack-webhook=$SLACK_WEBHOOK
```

## License

MIT
