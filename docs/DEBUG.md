# Debug runbook

When something doesn't work, walk this checklist before opening an issue.

## Contents

1. [`gst install` exits with `refused: …`](#1-gst-install-exits-with-refused-)
2. [`gst install` exits with HTTP 401 / 403](#2-gst-install-exits-with-http-401--403)
3. [`gst install` exits with HTTP 4xx other than 401/403](#3-gst-install-exits-with-http-4xx-other-than-401403)
4. [`gst install` succeeds but nothing visibly changed in Grafana](#4-gst-install-succeeds-but-nothing-visibly-changed-in-grafana)
5. [Alert never fires even though the SM check is red](#5-alert-never-fires-even-though-the-sm-check-is-red)
6. [Alert fires in Grafana but Slack stays silent](#6-alert-fires-in-grafana-but-slack-stays-silent)
7. [Slack message arrives looking wrong / unstyled](#7-slack-message-arrives-looking-wrong--unstyled)
8. [`gst manifest` says `paused`](#8-gst-manifest-says-paused)
9. [Offline / air-gapped development](#9-offline--air-gapped-development)
10. [Where to capture diagnostics](#10-where-to-capture-diagnostics)

---

## 1. `gst install` exits with `refused: …`

The runtime manifest gate refused the install. Possible reasons:

- `service is currently 'paused'` — a maintainer paused the whole catalog
  in `relay.manifest.json`. Wait for it to flip back, or override with
  `GST_DISABLE_MANIFEST_CHECK=1` if you have authority to do so.
- `project '…' is currently 'paused'` — only this project is paused;
  same fix.
- `deployment '…' is currently 'paused'` — your specific
  `--deployment-id` is overridden. Pick a different one or wait.
- `CLI version '…' < min_supported '…'` — upgrade `gst`:

  ```bash
  pip install -U grafana-stack-templates
  ```

`gst manifest` shows the current state — if you're unsure, run that first.

## 2. `gst install` exits with HTTP 401 / 403

Authentication failed.

- **401 Unauthorized** — `GRAFANA_TOKEN` is wrong, expired, or revoked.
  Generate a new one (*Administration → Service accounts → Add token*)
  and re-export.
- **403 Forbidden** — token is valid but lacks the required scopes.
  `gst install` for alert rules / contact points / templates needs
  `alerts:write`. SM modules also need a separate `SM_ACCESS_TOKEN`.

Token format reminder: `glsa_…` for Grafana, opaque base64 for SM.

## 3. `gst install` exits with HTTP 4xx other than 401/403

| Status | Likely cause | Fix |
|---|---|---|
| 400 | Required field missing or invalid in the rendered resource | Re-run `gst show <module>` to see required inputs; pass them via `--inputs`. |
| 404 | Folder UID doesn't exist | Create the `SM Alerts` folder in the UI, or change `folderUID` in the module's resource file. |
| 409 | Resource already exists with conflicting metadata | This usually means a previous install was partial. Inspect in the UI; if safe, delete the conflicting resource and re-run. |
| 422 | Validation error from Grafana | `gst install` prints the response body on error — the field name pinpoints it (e.g. `"data[0].relativeTimeRange.from must be > to"`). |

## 4. `gst install` succeeds but nothing visibly changed in Grafana

Provisioned resources are read-only in the UI. If you provisioned a rule
and went looking for it under *Alert rules*, you probably see the lock
icon — that's the rule. If you don't even see it:

1. Make sure you're in the right Grafana stack. The `GRAFANA_URL` you used
   determines this; double-check `gst manifest` output and your
   `.env`.
2. Folders are scoped — switch the folder filter in the UI to
   *All folders*.
3. Check the API directly:

   ```bash
   curl -sH "Authorization: Bearer $GRAFANA_TOKEN" \
     "$GRAFANA_URL/api/v1/provisioning/alert-rules" \
   | jq '.[] | select(.title | startswith("SM_HealthCheck_"))'
   ```

## 5. Alert never fires even though the SM check is red

- Confirm the SM check is *actually* failing in Grafana's UI: *Synthetic
  Monitoring → Checks → \<check\>*. Check the green/red bar over time.
- Open the alert rule in the UI: *Alerts → Alert rules → \<your rule\>*.
  Click *Test* — Grafana shows the most recent query result.
- Verify the rule's PromQL has the right `job=` and `instance=` labels.
  The most common bug is: catalog defaults the `job` to
  `Api [<service>] /healthz`, but the operator created the SM check with
  a different `job` value in the UI. Either align them or update the rule.
- Verify the Prometheus datasource UID — the catalog assumes
  `grafanacloud-prom`. If your datasource has a different UID, override
  it in your fork.

## 6. Alert fires in Grafana but Slack stays silent

Walk the path Grafana → notification policy → contact point → Slack:

1. **Notification policy** — *Alerts → Notification policies → … →
   Show details*. Confirm the policy matches `alertgroup=appstatus`.
2. **Contact point** — *Alerts → Contact points → application-status →
   Test*. If the test message lands in Slack, the contact point is fine;
   the problem is in the routing.
3. **Webhook URL** — open the contact point's edit page. The URL field
   shows `[redacted]` after first save — that's expected. Replace it with
   the real URL temporarily, *Test*, then *Save* again to re-redact.
4. **Slack-side rate limiting** — the webhook will silently drop messages
   if you cross ~1/s. If you have a recent incident with a wave of
   alerts, this can show up as "the first one arrived, the next 20 didn't".
## 7. Slack message arrives looking wrong / unstyled

- The contact-point's *Title* and *Text body* fields must reference the
  template by name. Default values:

  ```
  Title: {{ template "app_status.title" . }}
  Text:  {{ template "app_status.text" . }}
  ```

  If they're empty or missing, the message will fall back to Grafana's
  default rendering (no color bar, no service line).

- The notification template must be named `app_status_slack` (the value
  the catalog uses). If you renamed it, update the contact point too.

- For block-kit colors to render, the contact point's *Use mrkdwn:*
  toggle must be **off**. (`gst install` sets this for you; the manual
  walkthrough lists the right toggles.)

## 8. `gst manifest` says `paused`

That's by design. The manifest is a kill-switch — somebody (maybe past-you)
flipped it for a reason. Look at the commit history of
[`relay.manifest.json`](../relay.manifest.json) on `main` to find out why
and whether it's safe to re-enable.

If you legitimately need to bypass for development:

```bash
GST_DISABLE_MANIFEST_CHECK=1 gst install ...
```

Never use this for production deploys.

## 9. Offline / air-gapped development

```bash
export GST_DISABLE_MANIFEST_CHECK=1   # don't fetch the manifest at all
export GST_DRY_RUN=1                  # equivalent to --dry-run on every command
```

Together these make `gst install` a pure local rendering pipeline. Use it
to inspect what the API call *would* look like without leaving your
machine.

## 10. Where to capture diagnostics

When opening an issue, please include:

| What | How |
|---|---|
| `gst --version` | `gst --version` |
| Manifest state | `gst manifest` |
| The exact `gst install` command (redact tokens) | shell history |
| Full stderr+stdout of the failing call | `2>&1 \| tee /tmp/gst.log` |
| Grafana stack region | from `GRAFANA_URL` |
| Module ID + inputs YAML | redact `target` if it identifies a customer |

The maintainers can usually reproduce from the manifest state + the inputs
+ the failing API status alone.
