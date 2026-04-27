# grafana-stack-templates

A curated catalog of ready-to-apply **Grafana Cloud** building blocks: dashboards, alert rules, Synthetic Monitoring checks, Slack notification templates, and full recipes that bundle them together.

Pick a module, run one command, and your Grafana Cloud stack is configured.

## What's inside

```
modules/
├── dashboards/         # JSON dashboards for common stacks
├── alert-rules/        # alert rule templates with sane defaults
├── sm-checks/          # Synthetic Monitoring check templates
├── slack-templates/    # rich Slack notification templates
└── recipes/            # bundles that combine modules into a cohesive setup
```

## Quick start

```bash
pip install grafana-stack-templates
gst ls                                                  # browse the catalog
gst show slack-templates/app-status-rich                # inspect a module
gst install recipes/synthetic-monitoring-pack \
  --grafana-url=$GRAFANA_URL \
  --grafana-token=$GRAFANA_TOKEN \
  --slack-webhook=$SLACK_WEBHOOK
```

## How alert delivery works

Alerts produced by these modules flow through [`cloud-relay-hub`](https://github.com/Tarunrj99/cloud-relay-hub) — a small public relay that transforms Grafana payloads into rich Slack Block Kit messages, with built-in runtime configuration.

You can opt out and send directly to Slack from Grafana — see [`docs/CONFIGURATION.md`](docs/CONFIGURATION.md).

## License

MIT
