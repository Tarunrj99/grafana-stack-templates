# Contributing to `grafana-stack-templates`

Thanks for contributing! This catalog is intentionally small and opinionated,
so every change has a noticeable impact. Please read this guide before
opening a PR so your contribution lands cleanly.

---

## Ways to contribute

- **Report bugs** — open an issue with a minimal reproduction
  (module ID + the inputs you passed + the observed vs. expected output).
- **Suggest a module** — propose a new alert rule, SM check, dashboard,
  Slack template, or recipe.
- **Improve docs** — typos, clearer examples, better diagrams. Docs-only PRs
  are always welcome.
- **Code** — fix a bug, refactor an installer, add a CLI flag. See
  [development workflow](#development-workflow) below.

Before starting non-trivial work, open a short issue describing what you're
planning. That saves everyone from duplicated effort.

---

## Code of conduct

Participation is governed by the
[Contributor Covenant-style Code of Conduct](CODE_OF_CONDUCT.md). Be kind,
assume good intent, and keep the discussion focused on code and design.

---

## Development workflow

### 1. Fork and clone

```bash
git clone https://github.com/<your-fork>/grafana-stack-templates.git
cd grafana-stack-templates
```

### 2. Create a virtualenv and install in editable mode

```bash
make venv install     # python -m venv .venv && pip install -e ".[dev]"
source .venv/bin/activate
```

Or without `make`:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

### 3. Run the checks locally

```bash
make test     # pytest
make lint     # ruff check
```

Both must be green before you push.

### 4. Try your change end-to-end (offline)

You can dry-run any install path against a fake stack — no real Grafana
needed:

```bash
export GST_DISABLE_MANIFEST_CHECK=1
gst show alert-rules/sm-http-healthcheck
gst install recipes/synthetic-monitoring-pack \
  --deployment-id=local-dev \
  --inputs=examples/services.yaml \
  --dry-run
```

---

## Branching and PRs

- Work on a **feature branch**, never on `main`.
- Branch name convention: `feat/<short-desc>`, `fix/<short-desc>`,
  `docs/<short-desc>`, `refactor/<short-desc>`.
- Keep PRs **focused and small**. One logical change per PR.
- Rebase onto the latest `main` before marking the PR ready.
- Link the PR to an issue if one exists (`Fixes #12`).

### PR checklist

- [ ] Tests added or updated under `tests/`
- [ ] `make test` passes
- [ ] `make lint` passes
- [ ] Public behavior change? Updated `docs/` and `README.md`
- [ ] New module? Mirrored in [`docs/MODULES.md`](docs/MODULES.md)
- [ ] New runtime config key? Updated [`docs/CONFIGURATION.md`](docs/CONFIGURATION.md) + `relay.manifest.json`
- [ ] Added a bullet to [`CHANGELOG.md`](CHANGELOG.md) under `## [Unreleased]`
- [ ] No real org / customer / project / Slack-channel identifiers anywhere in the diff

A PR template prefilled from
[`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md) opens
automatically when you create a PR on GitHub.

---

## Commit style

Write commit messages in the imperative mood, with an optional scope prefix:

```
feat(modules): add slack-templates/app-status-compact
fix(installers/sm-check): retry once on transient 502
docs(quickstart): clarify SM_ACCESS_TOKEN provisioning
refactor(catalog): collapse module loader into one pass
test(installers): cover slack template render path
chore(release): v0.2.0
```

Prefixes in use: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ci`.

Keep the subject ≤ 72 characters. Add a body for anything non-obvious:
*why* the change matters, edge cases, deliberate trade-offs.

---

## Adding a new module

A module is a folder under `modules/<category>/<your-module>/`. The minimum
contents are:

1. **`meta.yaml`** — declares id, version, description, and `requires:`.

   ```yaml
   id: alert-rules/your-module
   name: Your alert rule
   version: 0.1.0
   type: alert-rule           # | synthetic-monitoring-check | notification-template | dashboard | recipe
   target: grafana-cloud
   description: |
     One-paragraph human description.
   requires:
     variables: [service, target]   # required inputs
     optional_variables: [team]
   ```

2. **The resource file** — `rule.yaml` / `check.yaml` / `template.tpl` /
   `dashboard.json` depending on the module type. Use Jinja-style `{{ … }}`
   placeholders for any value the operator should provide.

3. **`README.md`** — purpose, inputs, what gets created, and a sample
   rendered output.

The catalog reader picks up the new folder automatically. Verify with:

```bash
gst show <category>/<your-module>
```

After adding, also:

- Add a row to the table in [`docs/MODULES.md`](docs/MODULES.md).
- Add a worked example fragment to [`docs/SAMPLE_OUTPUT.md`](docs/SAMPLE_OUTPUT.md) if it produces visible output.
- Bullet under `## [Unreleased]` in [`CHANGELOG.md`](CHANGELOG.md).
- A test under `tests/` covering the loader and a render snapshot.

---

## Adding a new recipe

1. Create `modules/recipes/<your-recipe>/recipe.yaml` referencing existing
   modules.

   ```yaml
   id: recipes/your-recipe
   name: Your bundle
   version: 0.1.0
   description: |
     What it produces, and for whom.
   modules:
     - id: sm-checks/http-healthz
       apply_for_each: services
     - id: alert-rules/sm-http-healthcheck
       apply_for_each: services
     - id: slack-templates/app-status-rich
       apply_once: true
   inputs:
     services: { type: list }
   ```

2. Add a `README.md` describing the inputs and the end-state.
3. Drop a worked example into `examples/`.
4. Mirror in [`docs/MODULES.md`](docs/MODULES.md).

---

## Documentation conventions

- Markdown only. Keep lines reasonably short for diff review.
- Use **relative** links so they render correctly on GitHub. From the repo
  root, link to `docs/MODULES.md`; from inside `docs/`, link back as
  `../README.md`.
- Update the doc index in `README.md` when adding a new doc file.
- Inline code: backticks. File paths: backticks. Commands: fenced code
  blocks with the shell hint (` ```bash `).

---

## Release process (maintainers)

1. Update `version` in `pyproject.toml`.
2. Move entries from `## [Unreleased]` to a new version section in
   [`CHANGELOG.md`](CHANGELOG.md).
3. Commit: `chore(release): v0.y.z`.
4. Tag: `git tag v0.y.z && git push --tags`.
5. Optionally create a GitHub Release pointing at the tag with the
   CHANGELOG section pasted in.
6. Downstream users pin via `pip install "grafana-stack-templates @
   git+https://…@v0.y.z"` or `pip install grafana-stack-templates==0.y.z`.

---

## Questions?

Open a [discussion](https://github.com/Tarunrj99/grafana-stack-templates/discussions)
or an issue.
