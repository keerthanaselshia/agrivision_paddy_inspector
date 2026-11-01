# -*- coding: utf-8 -*-
"""
test_phase2_content.py  -  Validation test suite for Phase 2:
  1. Verifies that all 10 priority diseases have all required Phase 2 fields in
     English, Tamil, and Tanglish:
       - symptoms_leaf (list of strings)
       - symptoms_other_parts (str)
       - how_to_check (list of strings)
       - how_it_spreads (str)
       - favourable_conditions (str)
       - prevention_before_planting (str)
       - prevention_during_crop (str)
       - prevention_after_harvest (str)
       - prevention_to_limit_spread (str)
       - when_to_call_officer (str)
       - similar_looking_problems (str)
       - symptoms_summary (str)
  2. Safety checks:
       - Zero chemical dose patterns (mg, ml, g/l, g/kg, kg/ha, ppm)
       - Zero commercial pesticide brand names
       - All Tamil and Tanglish entries marked with expert review disclaimer
"""

import json
import re
import sys
import unittest
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PROJECT_ROOT = Path(r"C:\Users\keert\paddy_dataset")
DATA_FILE = PROJECT_ROOT / "app" / "data" / "disease_info.json"

TARGET_DISEASES = [
    "brown_spot",
    "blast",
    "blb",
    "healthy",
    "tungro",
    "sheath_blight",
    "false_smut",
    "leaf_scald",
    "narrow_brown_spot",
    "other",
]

REQUIRED_FIELDS = [
    "symptoms_leaf",
    "symptoms_other_parts",
    "how_to_check",
    "how_it_spreads",
    "favourable_conditions",
    "prevention_before_planting",
    "prevention_during_crop",
    "prevention_after_harvest",
    "prevention_to_limit_spread",
    "when_to_call_officer",
    "similar_looking_problems",
    "symptoms_summary",
]

LANGUAGES = ["en", "ta", "tanglish"]

# Strict regex matching dose units like 2 ml, 1.5 g/l, 500 mg, 1 kg/ha, etc.
DOSE_REGEX = re.compile(
    r"\b\d+(\.\d+)?\s*(mg|ml|g/l|g/kg|kg/ha|ppm)\b",
    re.IGNORECASE,
)

# Known pesticide brand names to forbid
FORBIDDEN_BRANDS = [
    "beam", "bavistin", "contaf", "tilt", "amistar", "nativo", "score",
    "dithane", "ridomil", "saaf", "coragen", "confidor", "fame", "monocrotophos"
]


class TestPhase2Content(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.assertTrue(DATA_FILE.exists(), f"Missing {DATA_FILE}")
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            cls.data = json.load(f)

    def test_all_target_diseases_present(self):
        """Ensure all 10 target diseases exist in disease_info.json."""
        for dis in TARGET_DISEASES:
            self.assertIn(dis, self.data, f"Missing disease entry: '{dis}'")

    def test_all_fields_present_in_three_languages(self):
        """Verify each disease has all 12 fields across English, Tamil, and Tanglish."""
        for dis in TARGET_DISEASES:
            entry = self.data[dis]
            for field in REQUIRED_FIELDS:
                for lang in LANGUAGES:
                    key = f"{field}_{lang}"
                    self.assertIn(
                        key,
                        entry,
                        f"Disease '{dis}' is missing field '{key}'",
                    )
                    val = entry[key]
                    if field in ("symptoms_leaf", "how_to_check"):
                        self.assertIsInstance(
                            val,
                            list,
                            f"'{key}' in '{dis}' should be a list, got {type(val)}",
                        )
                        self.assertGreater(
                            len(val),
                            0,
                            f"'{key}' in '{dis}' list must not be empty",
                        )
                        for item in val:
                            self.assertIsInstance(item, str)
                            self.assertTrue(len(item.strip()) > 0)
                    else:
                        self.assertIsInstance(
                            val,
                            str,
                            f"'{key}' in '{dis}' should be a string",
                        )
                        self.assertTrue(
                            len(val.strip()) > 0,
                            f"'{key}' in '{dis}' must not be empty",
                        )

    def test_no_chemical_doses(self):
        """Verify zero chemical dose patterns (mg, ml, g/l, kg/ha) exist."""
        violating_matches = []
        for dis in TARGET_DISEASES:
            entry = self.data[dis]
            for field in REQUIRED_FIELDS:
                for lang in LANGUAGES:
                    key = f"{field}_{lang}"
                    val = entry.get(key, "")
                    text = " ".join(val) if isinstance(val, list) else str(val)
                    matches = DOSE_REGEX.findall(text)
                    if matches:
                        violating_matches.append((dis, key, matches))
        self.assertEqual(
            len(violating_matches),
            0,
            f"Found forbidden chemical dose patterns: {violating_matches}",
        )

    def test_no_forbidden_brand_names(self):
        """Verify zero pesticide brand names exist."""
        brand_violations = []
        for dis in TARGET_DISEASES:
            entry = self.data[dis]
            for field in REQUIRED_FIELDS:
                for lang in LANGUAGES:
                    key = f"{field}_{lang}"
                    val = entry.get(key, "")
                    text = (" ".join(val) if isinstance(val, list) else str(val)).lower()
                    for brand in FORBIDDEN_BRANDS:
                        if re.search(r"\b" + re.escape(brand) + r"\b", text):
                            brand_violations.append((dis, key, brand))
        self.assertEqual(
            len(brand_violations),
            0,
            f"Found forbidden brand names: {brand_violations}",
        )

    def test_expert_review_disclaimers(self):
        """Verify all Tamil and Tanglish entries carry or reference the expert review marker."""
        for dis in TARGET_DISEASES:
            entry = self.data[dis]
            # Verify symptoms_summary has the disclaimer tag
            sum_ta = entry.get("symptoms_summary_ta", "")
            sum_tang = entry.get("symptoms_summary_tanglish", "")
            self.assertTrue(
                "வல்லுநர் சரிபார்ப்பு தேவை" in sum_ta or "Needs expert review" in sum_ta,
                f"Disease '{dis}' symptoms_summary_ta lacks expert review tag",
            )
            self.assertTrue(
                "Needs expert review" in sum_tang,
                f"Disease '{dis}' symptoms_summary_tanglish lacks expert review tag",
            )


if __name__ == "__main__":
    unittest.main()
