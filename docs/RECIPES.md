# Operational recipes

Day-two playbook. Every section answers one common operator question.

## Contents

1. [Add a new service to the SM pack](#1-add-a-new-service-to-the-sm-pack)
2. [Switch Slack template variants](#2-switch-slack-template-variants)
3. [Rotate the Slack webhook](#3-rotate-the-slack-webhook)
4. [Pause one project (kill-switch)](#4-pause-one-project-kill-switch)
5. [Pause one deployment without affecting the others](#5-pause-one-deployment-without-affecting-the-others)
6. [Migrate from direct-Slack to the relay](#6-migrate-from-direct-slack-to-the-relay)
7. [Speed up an SM check during an incident, then restore](#7-speed-up-an-sm-check-during-an-incident-then-restore)
8. [Decommission a service cleanly](#8-decommission-a-service-cleanly)
9. [Audit: list every alert rule + its routing labels](#9-audit-list-every-alert-rule--its-routing-labels)
10. [Cut a release](#10-cut-a-release)

---

## 1. Add a new service to the SM pack

Goal: have Grafana probe a new service and post Slack alerts when it goes
down — with the same labels and template as every other service.

```bash
$EDITOR examples/services.yaml      # append a new service entry
```

```yaml
services:
  # … existing entries …
  - service: payments-service
    service_slug: payments-service
    target: https://api.example.com/v2/payments-service/healthz
    job: "Api [payments-service] /healthz"
    dashboard_url: https://yourstack.grafana.net/a/grafana-synthetic-monitoring-app/checks
```

Apply:

```bash
gst install recipes/synthetic-monitoring-pack \
  --deployment-id=my-prod \
  --inputs=examples/services.yaml \
  --dry-run                        # preview first
gst install recipes/synthetic-monitoring-pack \
  --deployment-id=my-prod \
  --inputs=examples/services.yaml
```

Both calls are idempotent — existing services are left alone, only the new
one is created.

---

## 2. Switch Slack template variants

Goal: change how alerts render in Slack without re-creating any alert rule.

The catalog ships three variants:

- `slack-templates/app-status-rich` (default — block-kit, colored bar)
- `slack-templates/app-status-compact` (mobile single-line)
- `slack-templates/app-status-detailed` (block-kit + labels block)

Replace the active template in place:

```bash
gst install slack-templates/app-status-compact \
  --deployment-id=my-prod
```

The Grafana templates API uses the template *name* as the identifier, so
the second `gst install` updates the existing template instead of creating
a duplicate. Your contact-point already references it by name; nothing else
needs to change.

> See rendered samples for each variant in
> [`SAMPLE_OUTPUT.md`](SAMPLE_OUTPUT.md).

---

## 3. Rotate the Slack webhook

Goal: replace the Slack incoming webhook URL without dropping any alert.

### A) When you post directly to Slack from Grafana

Update the Grafana contact point:

1. Generate a new webhook in Slack
   ([api.slack.com/messaging/webhooks](https://api.slack.com/messaging/webhooks)).
2. UI: *Alerts → Contact points → application-status → Edit → URL*.
3. Click *Test* — you should see the test message land in the new channel.
4. Save.
5. Revoke the old webhook in Slack so nothing accidentally posts there
   again.

### B) When you post via the cloud-relay-hub Worker

The webhook is stored only in the Worker's KV (Grafana doesn't see it):

1. Generate the new webhook.
2. Update the KV entry — see the relay repo's runbook
   (`docs/RUNBOOK.md` in the private `cloud-control` repo).
3. Revoke the old webhook in Slack.

Grafana's contact point stays pointed at the relay URL the whole time.

---

## 4. Pause one project (kill-switch)

Goal: stop everything related to this catalog without redeploying anything.

Edit `relay.manifest.json` on `main`:

```jsonc
{
  "schema_version": 1,
  "service_status": "active",            // ← leave alone for project-level pause
  "projects": {
    "grafana-stack-templates": { "status": "paused" }   // ← flip
  },
  "deployment_overrides": []
}
```

Commit and push to `main`. Within ~60 seconds:

- The optional relay drops every alert it gets for this project (logs
  `event: "suppressed"`, returns `200 OK` to Grafana, never posts to
  Slack).
- Every new `gst install` invocation refuses to run with
  `refused: project 'grafana-stack-templates' is currently 'paused'`.

Resume by setting `status: "active"` and pushing.

A whole-fleet pause: set top-level `service_status: "paused"`. Affects
every consumer of the manifest, not just this project.

---

## 5. Pause one deployment without affecting the others

Useful when one stack is in incident-response mode and you want to silence
its alerts without affecting other stacks that share this catalog.

```jsonc
{
  // ...
  "deployment_overrides": [
    { "deployment_id": "my-prod", "status": "paused", "reason": "incident-response" }
  ]
}
```

Commit, push. The CLI refuses to install for `my-prod` only; the relay
drops alerts for that deployment only. Everything else keeps working.

---

## 6. Migrate from direct-Slack to the relay

Goal: insert the optional `cloud-relay-hub` Cloudflare Worker between
Grafana and Slack so you get the kill-switch + audit log + per-deployment
suppression.

1. Stand up the Worker (separate private repo). It exposes a URL like
   `https://your-worker.example.workers.dev`.
2. Enroll the Slack webhook into the Worker's KV (one-shot, behind the
   `X-Admin-Token` header — see the relay's runbook).
3. In Grafana: *Alerts → Contact points → application-status → Edit →
   URL*. Replace the Slack webhook with the Worker URL plus your
   deployment ID, e.g.:

   ```
   https://your-worker.example.workers.dev/v1/forward?deployment_id=my-prod
   ```

4. Click *Test*; expect a Slack message to arrive *via* the Worker (you'll
   see the entry in `wrangler tail` if you have it running).
5. Watch alerts for one alert cycle. Then revoke the old direct-Slack
   webhook so it can't be re-used.

The catalog modules don't know or care whether you went through the relay.
Same alert rules, same templates, same labels.

---

## 7. Speed up an SM check during an incident, then restore

Goal: when triaging, you want probes every minute, not every ten minutes.

```bash
# faster while triaging
gst install sm-checks/http-healthz \
  --deployment-id=my-prod \
  --inputs=- <<EOF
service: auth-service
target: https://api.example.com/v2/auth-service/healthz
team: devops
createdby: your-username
alertgroup: appstatus
frequency_ms: 60000   # 1 min while triaging
EOF

# restore after the incident
gst install sm-checks/http-healthz \
  --deployment-id=my-prod \
  --inputs=- <<EOF
service: auth-service
target: https://api.example.com/v2/auth-service/healthz
team: devops
createdby: your-username
alertgroup: appstatus
frequency_ms: 600000  # back to 10 min
EOF
```

The installer is idempotent: same `target`, so the existing check is
updated in place — no duplicate created.

---

## 8. Decommission a service cleanly

Goal: remove the SM check, the alert rule, and the dashboard panel for a
retired service.

The catalog doesn't ship a destructive `gst uninstall` (deliberately —
making teardown explicit avoids "oops I deleted prod"). Use the Grafana UI:

1. *Synthetic Monitoring → Checks* → find by `target` URL → *Delete*.
2. *Alerts → Alert rules* → find `SM_HealthCheck_<slug>_DOWN` → *Delete*.
3. Optional: edit the dashboard JSON and remove the panel for that service.
4. Remove the entry from your `services.yaml` so it doesn't get
   re-created on the next `gst install`.

---

## 9. Audit: list every alert rule + its routing labels

```bash
curl -sH "Authorization: Bearer $GRAFANA_TOKEN" \
  "$GRAFANA_URL/api/v1/provisioning/alert-rules" \
| jq -r '.[] | [.uid, .title, .labels.team // "-",
                .labels.severity // "-",
                .labels.alertgroup // "-"] | @tsv' \
| column -t
```

Spot-check that every rule routes the same way (`alertgroup=appstatus`,
`severity=critical`). Inconsistencies usually mean a manual UI edit
diverged from the catalog.

---

## 10. Cut a release

Maintainers only.

1. Update `version` in [`pyproject.toml`](../pyproject.toml).
2. Move entries from `## [Unreleased]` to a new version section in
   [`CHANGELOG.md`](../CHANGELOG.md), with the date.
3. Commit: `chore(release): v0.y.z`.
4. Tag: `git tag -a v0.y.z -m "v0.y.z"` then `git push --tags`.
5. (Optional) Create a GitHub Release pointing at the tag with the
   CHANGELOG section pasted in.
6. Bump `min_supported_version` in [`relay.manifest.json`](../relay.manifest.json)
   if (and only if) this release breaks compatibility. Old CLIs will then
   refuse to run, surfacing the upgrade requirement at the operator's
   terminal.
