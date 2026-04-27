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

Alerts produced by these modules can flow either:

- **Direct to Slack** — Grafana's built-in Slack contact-point pointed at a Slack incoming webhook. Simplest path, no extra hops.
- **Through a relay layer** — an optional Cloudflare Worker (or similar edge function) sits in front of Slack. The worker reads `relay.manifest.json` from this repo and uses it as a runtime kill-switch (project status, deployment overrides, etc.) before forwarding to Slack. This gives you a single file to flip if alert volume gets out of hand or something misfires in production.

The catalog and `gst` CLI in this repo are independent of which delivery path you choose. See [`docs/CONFIGURATION.md`](docs/CONFIGURATION.md) for the runtime manifest schema.

## License

MIT
