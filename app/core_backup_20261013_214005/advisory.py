"""
core/advisory.py  –  Loads advisory.json and exposes an ADVICE dict
that keeps the same shape as the original inline dict in app.py so the
rest of the UI code does not change.

Shape returned per label:
  {
    "name"       : str   # short English display name
    "scientific" : str   # scientific name (empty for healthy/other)
    "cause_type" : str   # Fungal / Bacterial / Viral / Various / None
    "en"         : str   # short advisory in English  (for report + sidebar)
    "ta"         : str   # short advisory in Tamil
    "en_full"    : str   # full management text in English (Disease Library page)
    "ta_full"    : str   # full management text in Tamil
    "symptoms_en": str
    "symptoms_ta": str
    "conditions_en": str
    "conditions_ta": str
    "tamil_needs_validation": bool
  }
"""

from __future__ import annotations

import json
from pathlib import Path

# advisory.json lives next to this file in app/data/
_JSON_PATH = Path(__file__).resolve().parent.parent / "data" / "advisory.json"

# ---------------------------------------------------------------------------
# Internal loader
# ---------------------------------------------------------------------------

def _load() -> dict:
    """Read advisory.json and reshape into the ADVICE dict format."""
    with open(_JSON_PATH, encoding="utf-8") as f:
        raw = json.load(f)

    result: dict[str, dict] = {}
    for label, d in raw.items():
        if label.startswith("_"):
            continue  # skip _meta key
        result[label] = {
            "name":                    d.get("name_en", label),
            "scientific":              d.get("scientific", ""),
            "cause_type":              d.get("cause_type", ""),
            "en":                      d.get("advisory_short_en", ""),
            "ta":                      d.get("advisory_short_ta", ""),
            "en_full":                 d.get("management_en", ""),
            "ta_full":                 d.get("management_ta", ""),
            "symptoms_en":             d.get("symptoms_en", ""),
            "symptoms_ta":             d.get("symptoms_ta", ""),
            "conditions_en":           d.get("conditions_en", ""),
            "conditions_ta":           d.get("conditions_ta", ""),
            "name_ta":                 d.get("name_ta", ""),
            "tamil_needs_validation":  d.get("tamil_needs_validation", True),
        }
    return result


# ---------------------------------------------------------------------------
# Public: ADVICE dict (same shape as the old inline dict in app.py)
# ---------------------------------------------------------------------------

ADVICE: dict[str, dict] = _load()
