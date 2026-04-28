# Quick start — 5 minutes

Goal: ship a Slack alert when one of your services starts failing its
healthcheck — without writing any Grafana JSON yourself.

## 1. Install the CLI

```bash
pip install grafana-stack-templates                  # latest tagged release
# — or pin to a tag —
pip install "grafana-stack-templates @ git+https://github.com/Tarunrj99/grafana-stack-templates.git@v0.1.0"
```

Verify:

```bash
gst --version
```

## 2. Fill in your env vars

```bash
cp .env.example .env
$EDITOR .env
set -a && source .env && set +a
```

You need at minimum:

| Var | Where to get it |
|---|---|
| `GRAFANA_URL` | your stack URL, e.g. `https://yourstack.grafana.net` |
| `GRAFANA_TOKEN` | *Administration → Users and access → Service accounts → Add token* |
| `SM_ACCESS_TOKEN` | *Synthetic Monitoring → Configuration → Access tokens* |
| `SLACK_WEBHOOK` | [api.slack.com/messaging/webhooks](https://api.slack.com/messaging/webhooks) (optional — only if you also want the CLI to wire up the contact point) |

## 3. Browse the catalog

```bash
gst ls                                              # all modules
gst ls slack-templates                              # one category
gst show slack-templates/app-status-rich            # inputs, outputs, files
```

## 4. Check the runtime gate

```bash
gst manifest
```

Expect to see `service_status: active` (green). If it says `paused`, see
[`DEBUG.md` § 8](DEBUG.md#8-gst-manifest-says-paused).

## 5. Pick a recipe and dry-run it

The shipped recipe creates an SM check + an alert rule + a Slack template
for every service in your `services.yaml`:

```bash
gst install recipes/synthetic-monitoring-pack \
  --deployment-id=my-prod \
  --inputs=examples/services.yaml \
  --dry-run
```

The dry-run prints exactly what `gst` would do without making any API
calls. Same end state as `gst plan`.

## 6. Apply

```bash
gst install recipes/synthetic-monitoring-pack \
  --deployment-id=my-prod \
  --inputs=examples/services.yaml
```

You should see `INSTALL: recipes/synthetic-monitoring-pack v0.1.0 → deployment=my-prod`
followed by a JSON record of every resource that was created or updated.

## 7. Verify in Grafana

- *Synthetic Monitoring → Checks* — your new check appears, going green
  within ~one cycle.
- *Alerts → Alert rules → SM Alerts folder* — `SM_HealthCheck_<slug>_DOWN`
  rules listed (one per service).
- *Alerts → Contact points → Notification templates* — `app_status_slack`
  template installed.
- *Alerts → Contact points → application-status* — points at your Slack
  webhook (or the relay URL).

## 8. Trigger a smoke test (optional)

Point one SM check at a URL that returns `500` (e.g.
`https://httpstat.us/500`) for a couple of minutes. The corresponding
alert rule should fire after ~5 minutes and a Slack message should appear.
Restore the URL to clear the alert.

## What's next?

- **Operational playbook** — [`RECIPES.md`](RECIPES.md) covers rotating
  the webhook, switching template variants, kill-switch, and pausing one
  deployment.
- **Manual UI walkthrough** — [`MANUAL_INSTALL.md`](MANUAL_INSTALL.md) for
  operators who prefer the Grafana UI to the CLI.
- **Module catalog** — [`MODULES.md`](MODULES.md) lists every module, its
  inputs, and what it produces.
- **Sample output** — [`SAMPLE_OUTPUT.md`](SAMPLE_OUTPUT.md) shows what
  rendered Slack messages look like for each template variant.
- **Debugging** — [`DEBUG.md`](DEBUG.md).
