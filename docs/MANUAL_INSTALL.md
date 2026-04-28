# Manual install — Grafana UI walkthrough

This is the click-by-click version of `gst install`. Same end result; useful
when you want to evaluate one module before committing to the CLI, or when
the CLI isn't available on your workstation.

> Every screenshot path below assumes Grafana Cloud's standard navigation
> as of 2026-04. Grafana ships UI changes regularly — if a button moved,
> the *function* is what matters, not the exact label.

## Contents

1. [Prerequisites](#prerequisites)
2. [Install a Synthetic Monitoring HTTP check](#1-install-a-synthetic-monitoring-http-check)
3. [Install a notification template](#2-install-a-notification-template)
4. [Wire up a Slack contact point](#3-wire-up-a-slack-contact-point)
5. [Install an alert rule](#4-install-an-alert-rule)
6. [Install a dashboard](#5-install-a-dashboard)
7. [Verify the whole flow](#6-verify-the-whole-flow)

---

## Prerequisites

Before you start, in your Grafana Cloud stack:

- A **folder** to hold alert rules. Default folder used by this catalog is
  `SM Alerts`. Create it now: *Alerts → Alert rules → New folder →
  `SM Alerts`*.
- A **Slack incoming webhook** URL. If you don't have one, create it at
  [api.slack.com/messaging/webhooks](https://api.slack.com/messaging/webhooks).
- A **notification policy** that routes on `alertgroup=appstatus`. Default
  one is fine if you only have one Slack channel for app-status alerts.

You'll need **read access** to this repo so you can copy module YAML into
the UI's text editors.

---

## 1. Install a Synthetic Monitoring HTTP check

**Module:** [`sm-checks/http-healthz`](../modules/sm-checks/http-healthz/)

**Steps:**

1. **Synthetic Monitoring → Checks → Add new check.**
2. **Check type:** *HTTP*.
3. Open
   [`modules/sm-checks/http-healthz/check.yaml`](../modules/sm-checks/http-healthz/check.yaml)
   from this repo and copy the values in:

   | UI field | YAML key | Example value |
   |---|---|---|
   | Job name | `job` | `Api [auth-service] /healthz` |
   | Target | `target` | `https://api.example.com/v2/auth-service/healthz` |
   | Probe locations | `probes` | one location, e.g. *Ohio* |
   | Frequency | `frequency` | `10 minutes` |
   | Timeout | `timeout` | `5 seconds` |
   | Labels | `labels` | `team=devops`, `createdby=<your-username>`, `alertgroup=appstatus` |

4. **Advanced options:**
   - *Alert sensitivity:* **None**. (We do not want SM's built-in alerting;
     we'll attach a normal alert rule on top.)
   - *Basic metrics only:* **On**. Smaller cardinality, identical signal
     for a healthcheck.
   - *Validate TLS:* leave default. *Fail if SSL not present:* **On**.
5. **Save**.

You should now see the check listed and turning green within ~one cycle.

---

## 2. Install a notification template

**Module:** [`slack-templates/app-status-rich`](../modules/slack-templates/app-status-rich/)
(or `app-status-compact` / `app-status-detailed` — same procedure)

**Steps:**

1. **Alerts → Contact points → Notification templates → New template.**
2. **Name:** `app_status_slack` (must match the name `gst install` uses;
   downstream contact-point references this name).
3. Open
   [`modules/slack-templates/app-status-rich/template.tpl`](../modules/slack-templates/app-status-rich/template.tpl)
   in this repo and **paste its entire contents** into the *Content*
   editor.
4. Click **Save template**.

If the editor rejects the template with a message like
`function "dateInZone" not defined`, you have an older Grafana stack —
this catalog ships only template functions that are available in
Grafana's `text/template` runtime (no Sprig functions). Re-check that you
copied the file from this repo and not from somewhere else.

---

## 3. Wire up a Slack contact point

**Steps:**

1. **Alerts → Contact points → Add contact point.**
2. **Name:** `application-status` (used downstream in alert rules and
   notification policies).
3. **Integration:** *Slack*.
4. **URL:** paste your Slack incoming webhook URL
   ([api.slack.com/messaging/webhooks](https://api.slack.com/messaging/webhooks)).
5. **Title:** `{{ template "app_status.title" . }}`
6. **Text body:** `{{ template "app_status.text" . }}`
7. Toggle **Show advanced** and set:
   - *Username:* `Application Healthcheck Status`
   - *Icon emoji:* `:rotating_light:`
8. **Test** — you should see a synthetic alert in the configured channel.
9. **Save**.

---

## 4. Install an alert rule

**Module:** [`alert-rules/sm-http-healthcheck`](../modules/alert-rules/sm-http-healthcheck/)

**Steps:**

1. **Alerts → Alert rules → New alert rule → Grafana managed alert rule.**
2. **Name:** `SM_HealthCheck_<service-slug>_DOWN` (e.g.
   `SM_HealthCheck_auth-service_DOWN`).
3. **Folder:** `SM Alerts`.
4. **Evaluation group:** `synthetic-monitoring-appstatus`, evaluate every
   `1m`.

5. **Query A** — Prometheus, datasource `grafanacloud-prom`, code mode:

   ```promql
   avg_over_time(probe_success{job="Api [auth-service] /healthz", instance="https://api.example.com/v2/auth-service/healthz"}[5m])
   ```

   *Range:* last 10 minutes (`from = 600s`, `to = 0s`).

6. **Condition C** — *Threshold*: `IS BELOW 0.5` of `A`.
7. **Pending period (`for`):** `5m`.
8. **No data state:** *Alerting*. **Error state:** *Alerting*.

9. **Annotations:**
   - `description` — short one-liner: `auth-service /healthz failing`
   - `dashboard_url` — link from your SM check
   - `runbook_url` — the target URL itself, used as the "endpoint" line
     in the Slack template

10. **Labels** (this is the part that makes notification routing work):

    | Label | Value |
    |---|---|
    | `team` | `devops` |
    | `service` | `auth-service` |
    | `severity` | `critical` |
    | `alertgroup` | `appstatus` |

11. **Notifications:** *Use notification policies* (the policy you set up
    in [Prerequisites](#prerequisites) routes on `alertgroup=appstatus`).
12. **Save**.

> **Tip:** the YAML in
> [`modules/alert-rules/sm-http-healthcheck/rule.yaml`](../modules/alert-rules/sm-http-healthcheck/rule.yaml)
> mirrors all of the above fields one-to-one, so you can refer to it
> while clicking through the UI.

---

## 5. Install a dashboard

**Module:** [`dashboards/synthetic-monitoring-overview`](../modules/dashboards/synthetic-monitoring-overview/)

**Steps:**

1. **Dashboards → New → Import.**
2. Open
   [`modules/dashboards/synthetic-monitoring-overview/dashboard.json`](../modules/dashboards/synthetic-monitoring-overview/dashboard.json)
   from this repo and **paste its entire contents** into the *Import via
   panel json* field.
3. **Folder:** `SM Alerts` (or any folder you prefer; it's purely for
   organisation).
4. **Datasource for `grafanacloud-prom`:** select your Prometheus
   datasource (the default `grafanacloud-prom` will appear if you only have
   one Grafana Cloud stack).
5. **Import**.

The dashboard auto-discovers every SM check on the stack — no per-service
edits required.

---

## 6. Verify the whole flow

1. **Force a failure** — point the SM check at a URL that returns `500`
   (e.g. `https://httpstat.us/500`) for a couple of minutes.
2. After ~5 minutes, the alert rule should transition to **Pending →
   Firing**, and a Slack message should appear in your test channel using
   the `app_status_slack` template.
3. Restore the URL. Within ~5 minutes the alert should clear and a
   resolved Slack message should follow.
4. Re-point the SM check at the real URL and you're done.

---

## Where to go next

- The same end state is reachable in one command via
  [`gst install`](QUICKSTART.md).
- Day-two operations (rotate webhook, switch templates, kill-switch) are
  in [`RECIPES.md`](RECIPES.md).
- If something goes wrong, [`DEBUG.md`](DEBUG.md) has the most common
  symptoms and their fixes.
