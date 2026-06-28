"""Dump the backend's OpenAPI spec to shared/openapi.json.

This is the input for cross-language type generation: the spec is produced from
the backend's Pydantic models, then turned into TypeScript types in shared/ (via
openapi-typescript), so the frontend's types cannot drift from the backend.

Run with: python scripts/export_openapi.py  (from the backend/ directory)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "backend" / "src"))

from main import app  # noqa: E402

# Schemas-only: the data models are what the frontend imports. The full spec
# (with paths/operations) is always available at runtime via GET /openapi.json.
spec = app.openapi()
spec.pop("paths", None)

_OUT = _ROOT / "shared" / "openapi.json"
_OUT.write_text(json.dumps(spec, indent=2) + "\n")
print(f"Wrote {_OUT.relative_to(_ROOT)} (schemas-only)")
