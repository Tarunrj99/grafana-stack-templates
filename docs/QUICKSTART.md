# Quick start

## 1. Install

```bash
pip install grafana-stack-templates
```

## 2. Browse the catalog

```bash
gst ls                                      # list all modules
gst ls slack-templates                      # list a category
gst show slack-templates/app-status-rich    # inspect a module
```

## 3. Get your Grafana credentials

You'll need:

- `GRAFANA_URL` — e.g. `https://yourstack.grafana.net`
- `GRAFANA_TOKEN` — Service Account token (`glsa_...`) with Editor role
- `SM_ACCESS_TOKEN` — Synthetic Monitoring access token (only for SM modules)
- `SLACK_WEBHOOK` — your Slack incoming webhook URL (only for Slack modules)

Export them:

```bash
export GRAFANA_URL="https://yourstack.grafana.net"
export GRAFANA_TOKEN="glsa_xxx"
export SM_ACCESS_TOKEN="xxx"
export SLACK_WEBHOOK="https://hooks.slack.com/services/..."
```

## 4. Install a recipe

A "recipe" bundles multiple modules into a cohesive setup:

```bash
gst install recipes/synthetic-monitoring-pack \
  --deployment-id=my-prod \
  --dry-run                                   # preview first
gst install recipes/synthetic-monitoring-pack \
  --deployment-id=my-prod
```

## 5. Verify

```bash
gst status --deployment-id=my-prod
```

This shows what's installed in your Grafana stack from this catalog.
