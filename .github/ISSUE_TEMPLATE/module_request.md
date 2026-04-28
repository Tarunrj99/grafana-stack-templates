---
name: New module / recipe request
about: Propose a new alert rule, SM check, dashboard, Slack template, or recipe.
title: "[module] "
labels: enhancement, module
assignees: ''
---

## Module type

- [ ] alert-rule
- [ ] sm-check
- [ ] dashboard
- [ ] slack-template
- [ ] recipe (bundle of the above)

## Proposed module ID

`<category>/<short-id>` — e.g. `alert-rules/redis-memory-high`,
`slack-templates/incident-review-detailed`.

## What does it produce?

<!--
A one-paragraph plain-language description of the resource — labels it
adds, what it routes on, what dashboard panels look like, etc.
-->

## Inputs the operator must provide

| Variable | Required? | Example |
|---|---|---|
| `service` | yes | `auth-service` |
| `target`  | yes | `https://api.example.com/healthz` |
| ...       |     |     |

## Acceptance criteria

- [ ] Render preview matches the description above (paste a `gst show` output if you have one)
- [ ] Sample output added to [`docs/SAMPLE_OUTPUT.md`](../docs/SAMPLE_OUTPUT.md)
- [ ] Catalog entry in [`docs/MODULES.md`](../docs/MODULES.md)
