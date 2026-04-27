"""Catalog browsing and module loading.

Walks the modules/ directory in this repo and returns metadata for each
module found, plus helpers to load module contents.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

CATEGORIES = ("slack-templates", "alert-rules", "sm-checks", "dashboards", "recipes")


@dataclass
class Module:
    id: str
    category: str
    path: Path
    meta: dict[str, Any]

    @property
    def name(self) -> str:
        return self.meta.get("name", self.id)

    @property
    def version(self) -> str:
        return self.meta.get("version", "0.0.0")

    @property
    def description(self) -> str:
        return (self.meta.get("description") or "").strip()


def repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        if (parent / "modules").is_dir() and (parent / "pyproject.toml").is_file():
            return parent
    raise RuntimeError("Could not locate repo root (looking for modules/ + pyproject.toml).")


def list_modules(category: str | None = None) -> list[Module]:
    root = repo_root()
    out: list[Module] = []
    cats = [category] if category else CATEGORIES
    for cat in cats:
        cat_dir = root / "modules" / cat
        if not cat_dir.is_dir():
            continue
        for entry in sorted(cat_dir.iterdir()):
            if not entry.is_dir():
                continue
            meta_file = entry / "meta.yaml"
            if not meta_file.is_file():
                meta_file = entry / "recipe.yaml"
            if not meta_file.is_file():
                continue
            try:
                meta = yaml.safe_load(meta_file.read_text()) or {}
            except yaml.YAMLError:
                meta = {"name": entry.name, "_parse_error": True}
            module_id = f"{cat}/{entry.name}"
            out.append(Module(id=module_id, category=cat, path=entry, meta=meta))
    return out


def get_module(module_id: str) -> Module | None:
    for m in list_modules():
        if m.id == module_id:
            return m
    return None
