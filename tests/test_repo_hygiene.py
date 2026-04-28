"""Public-repo hygiene scan: walk every tracked file and ensure no real
identifier from the reference deployment leaked in. This is the same
shape `cloud-alert-hub` uses — keeps the public catalog free of personal
project / billing / Slack identifiers even if a future PR slips up.

The list is intentionally broad and the test is fast; if a true positive
fires, it's a real fix.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# Strings we never want to see in public commits. Replace with explicit
# placeholders before pushing.
FORBIDDEN_LITERALS = [
    "satschel",            # reference deployment company name
    "encryptly",           # reference deployment app name
    "tarun_shubham",       # reference operator handle (createdby tag)
    "elliptical-feat-364815",  # GCP project id
    "apps-gke",            # GKE cluster name
    "fast.satschel.com",
    "keystore.satschel.com",
    "mainnet.liquidity.io",
    "api.satschel.com",
]

# Regexes for shapes we never want to see, regardless of host.
FORBIDDEN_PATTERNS = [
    re.compile(r"hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[A-Za-z0-9]+"),  # Slack webhook
    re.compile(r"glsa_[A-Za-z0-9_-]{20,}"),  # Grafana SA token
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),     # GitHub PAT
]

# Files we never read for hygiene checks (binaries, lockfiles, this test).
SKIP = (
    ".git/",
    ".venv/",
    ".pytest_cache/",
    ".ruff_cache/",
    "__pycache__/",
    "node_modules/",
    "tests/test_repo_hygiene.py",   # contains the literals on purpose
    "CHANGELOG.md",                 # may legitimately reference deployment
    "package-lock.json",
)


def _iter_text_files():
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = str(path.relative_to(REPO_ROOT))
        if any(s in rel for s in SKIP):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        yield rel, text


@pytest.mark.parametrize("literal", FORBIDDEN_LITERALS)
def test_forbidden_literal_not_present(literal):
    hits = []
    for rel, text in _iter_text_files():
        if literal in text:
            hits.append(rel)
    assert not hits, (
        f"Forbidden literal {literal!r} appears in: {hits}. "
        "Replace with a generic placeholder before committing."
    )


def test_no_inline_secrets():
    hits = []
    for rel, text in _iter_text_files():
        for pat in FORBIDDEN_PATTERNS:
            if pat.search(text):
                hits.append((rel, pat.pattern))
    assert not hits, (
        f"Likely secret leaked in: {hits}. "
        "Rotate the secret immediately and replace with a placeholder."
    )
