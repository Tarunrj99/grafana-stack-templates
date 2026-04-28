# Security Policy

## Supported versions

`grafana-stack-templates` is currently in **beta**. Only the latest tagged
release on `main` receives security fixes.

| Version | Supported |
| ------- | --------- |
| `0.1.x` | ✅        |
| `< 0.1` | ❌        |

## Reporting a vulnerability

**Please do not open a public GitHub issue** for security problems. Use one
of the following channels:

1. **GitHub Security Advisories** (preferred) — open a private advisory at
   <https://github.com/Tarunrj99/grafana-stack-templates/security/advisories/new>.
2. **Direct email** — send the details to the maintainer listed in
   [`pyproject.toml`](pyproject.toml) (`[project].authors`).

Please include:

- A description of the vulnerability and its impact.
- A minimal reproducer (module ID, inputs, the exact command, observed
  vs. expected behavior).
- The version / commit you tested against.
- Your preferred contact and attribution style if you'd like to be credited.

## What to expect

- **Acknowledgement** within 72 hours.
- **Triage** within 7 days, including whether it's in scope and a severity
  rating.
- **Fix or mitigation**:
  - High severity: targeted patch release within ~2 weeks.
  - Medium: bundled into the next minor release.
  - Low: addressed opportunistically in `main`.
- **Disclosure**: coordinated — we'll agree on a public disclosure date
  together, typically ≤ 30 days after a fix ships.

## Scope

In scope:

- Vulnerabilities in the `grafana_stack_templates` Python package
  (catalog reader, manifest fetcher, installers, CLI).
- Vulnerabilities in the runtime manifest schema or its consumers
  (the CLI's install-time gate; the optional Cloudflare Worker relay
  uses the same schema and is in scope only for the schema itself,
  not the Worker code which lives in a separate repo).
- Example modules in `modules/` and `examples/` that could leak secrets
  or grant unintended Grafana permissions when used as documented.

Out of scope:

- Vulnerabilities in third-party services this catalog targets
  (Grafana Cloud, Grafana Synthetic Monitoring, Slack incoming webhooks)
  — report those to their respective vendors.
- Issues that require an attacker to already have administrator access to
  the Grafana stack the operator is provisioning.
- Operator-induced misconfiguration (e.g. committing a real `glsa_…`
  token to a public fork) — report by opening a normal issue.

## Secrets handling — design summary

By design, `grafana-stack-templates` keeps secrets **out of files**:

- `GRAFANA_TOKEN`, `SM_ACCESS_TOKEN`, and `SLACK_WEBHOOK` are read only
  from environment variables. The CLI does not write them to disk and does
  not log them at any verbosity level.
- Module YAML uses `{{ variable_name }}` placeholders that the operator
  fills with non-secret values (service name, URL, target host) only.
- The runtime manifest is intentionally public and contains no secrets —
  only project status flags and version metadata.

If you find a code path that logs secrets, persists them to disk, or
includes them in error messages, please report it through the channels
above.
