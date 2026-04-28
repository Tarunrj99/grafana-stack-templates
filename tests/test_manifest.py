"""Manifest gate logic. No real network call — we feed Manifest objects
directly into gate()."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from grafana_stack_templates.manifest import Manifest, ManifestError, _version_lt, gate


def test_version_lt_basic():
    assert _version_lt("0.0.9", "0.1.0")
    assert _version_lt("0.1.0", "0.2.0")
    assert _version_lt("0.1.0", "1.0.0")
    assert not _version_lt("0.1.0", "0.1.0")
    assert not _version_lt("1.0.0", "0.9.9")


def test_version_lt_pre_release_suffix_ignored():
    assert _version_lt("0.1.0-rc1", "0.2.0")
    assert not _version_lt("0.2.0+build", "0.2.0")


def test_version_lt_malformed_is_fail_open():
    # parse error → return False (don't block on malformed manifests)
    assert not _version_lt("not-a-version", "0.0.0")


def test_gate_active_passes():
    with patch("grafana_stack_templates.manifest.fetch_manifest", return_value=Manifest()):
        gate(version="0.1.0", deployment_id="my-prod")  # no exception


def test_gate_paused_service_status_blocks():
    m = Manifest(service_status="paused")
    with patch("grafana_stack_templates.manifest.fetch_manifest", return_value=m):
        with pytest.raises(ManifestError) as ei:
            gate(version="0.1.0", deployment_id="my-prod")
        assert "paused" in str(ei.value)


def test_gate_paused_project_blocks():
    m = Manifest(projects={"grafana-stack-templates": {"status": "paused"}})
    with patch("grafana_stack_templates.manifest.fetch_manifest", return_value=m):
        with pytest.raises(ManifestError) as ei:
            gate(version="0.1.0", deployment_id="my-prod")
        assert "Project" in str(ei.value)


def test_gate_paused_deployment_blocks():
    m = Manifest(
        deployment_overrides=[
            {"deployment_id": "my-prod", "status": "paused"},
        ]
    )
    with patch("grafana_stack_templates.manifest.fetch_manifest", return_value=m):
        with pytest.raises(ManifestError):
            gate(version="0.1.0", deployment_id="my-prod")


def test_gate_other_deployment_unaffected():
    m = Manifest(
        deployment_overrides=[
            {"deployment_id": "other-prod", "status": "paused"},
        ]
    )
    with patch("grafana_stack_templates.manifest.fetch_manifest", return_value=m):
        gate(version="0.1.0", deployment_id="my-prod")  # no exception


def test_gate_deprecated_version_blocks():
    m = Manifest(deprecated_versions=["0.1.0"])
    with patch("grafana_stack_templates.manifest.fetch_manifest", return_value=m):
        with pytest.raises(ManifestError):
            gate(version="0.1.0", deployment_id="my-prod")


def test_gate_min_supported_version_blocks():
    m = Manifest(min_supported_version="0.5.0")
    with patch("grafana_stack_templates.manifest.fetch_manifest", return_value=m):
        with pytest.raises(ManifestError) as ei:
            gate(version="0.1.0", deployment_id="my-prod")
        assert "min_supported_version" in str(ei.value)


def test_gate_returns_none_when_disabled(monkeypatch):
    monkeypatch.setenv("GST_DISABLE_MANIFEST_CHECK", "1")
    # No patching needed — fetch_manifest short-circuits.
    gate(version="0.1.0", deployment_id="my-prod")
