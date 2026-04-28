"""Shared pytest fixtures.

The catalog tests need to bypass the runtime manifest fetch (no network in
CI). Setting GST_DISABLE_MANIFEST_CHECK=1 at the process level is the
cleanest way; the gate function returns immediately when it sees that.
"""

from __future__ import annotations

import os

os.environ.setdefault("GST_DISABLE_MANIFEST_CHECK", "1")
