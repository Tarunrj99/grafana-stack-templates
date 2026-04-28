<!-- Thanks for the PR! Please fill out the sections below. -->

## What does this PR do?

<!-- One or two sentences. -->

## Why?

<!--
Link the issue you're fixing or the scenario you're enabling. If there's
no issue, describe the operator pain that motivated the change.
-->

Fixes #

## Type of change

- [ ] Bug fix
- [ ] New module (`modules/<category>/<id>/`)
- [ ] New recipe (`modules/recipes/<id>/`)
- [ ] CLI change (`src/grafana_stack_templates/cli.py` or `installers/`)
- [ ] Manifest-schema change (`relay.manifest.json` / `manifest.py`)
- [ ] Docs only
- [ ] Refactor / chore / CI

## Checklist

- [ ] `make test` passes locally
- [ ] `make lint` passes locally
- [ ] Public behavior change → updated `docs/` and `README.md`
- [ ] New module → mirrored in [`docs/MODULES.md`](../docs/MODULES.md)
- [ ] New runtime config key → updated [`docs/CONFIGURATION.md`](../docs/CONFIGURATION.md) + `relay.manifest.json`
- [ ] Bullet added to [`CHANGELOG.md`](../CHANGELOG.md) under `## [Unreleased]`
- [ ] No real org / customer / project / Slack-channel identifiers in the diff
- [ ] No `glsa_…` tokens, Slack webhooks, or other secrets in the diff

## Anything reviewers should pay attention to?

<!-- Edge cases, deliberate trade-offs, follow-ups deferred to a later PR. -->
