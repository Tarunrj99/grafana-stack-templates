"""Template rendering helpers (Jinja2)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, StrictUndefined

_env = Environment(
    keep_trailing_newline=True,
    undefined=StrictUndefined,
    autoescape=False,
)


def render_str(s: str, ctx: dict[str, Any]) -> str:
    return _env.from_string(s).render(**ctx)


def render_yaml_file(path: Path, ctx: dict[str, Any]) -> Any:
    rendered = render_str(path.read_text(), ctx)
    return yaml.safe_load(rendered)
