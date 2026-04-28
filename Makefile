.PHONY: help venv install test lint format clean show ls

VENV ?= .venv
PY   ?= python3
PIP  := $(VENV)/bin/pip
GST  := $(VENV)/bin/gst

help:
	@echo "Common targets:"
	@echo "  venv         Create a local virtualenv in $(VENV)"
	@echo "  install      Install grafana-stack-templates with dev extras (editable)"
	@echo "  test         Run the test suite"
	@echo "  lint         Run ruff across src/ and tests/"
	@echo "  format       Run ruff format"
	@echo "  ls           List all modules in the catalog (dry, no Grafana calls)"
	@echo "  show MOD=...  Show one module's metadata"
	@echo "  clean        Remove virtualenv and caches"

venv:
	$(PY) -m venv $(VENV)

install: venv
	$(PIP) install -U pip
	$(PIP) install -e ".[dev]"

test:
	$(VENV)/bin/pytest -q

lint:
	$(VENV)/bin/ruff check src tests

format:
	$(VENV)/bin/ruff format src tests

ls:
	GST_DISABLE_MANIFEST_CHECK=1 $(GST) ls

show:
	@if [ -z "$(MOD)" ]; then echo "usage: make show MOD=<category>/<id>"; exit 2; fi
	GST_DISABLE_MANIFEST_CHECK=1 $(GST) show $(MOD)

clean:
	rm -rf $(VENV) .pytest_cache .ruff_cache **/__pycache__ *.egg-info src/*.egg-info build dist
