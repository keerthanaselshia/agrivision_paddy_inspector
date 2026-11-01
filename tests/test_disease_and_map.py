"""
test_disease_and_map.py  –  Tests for expanded disease categories, farmer advisory,
and location/map coordinate parsing & timezone safety.
"""

import sys
import unittest
from pathlib import Path
import pandas as pd

_TEST_DIR = Path(__file__).resolve().parent
_APP_DIR = _TEST_DIR.parent / "app"
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

from core.advisory import ADVICE
from map_page import _parse_latlon, TN_DISTRICT_COORDS


class TestDiseaseLibrary(unittest.TestCase):
    def test_all_22_diseases_present(self):
        expected_classes = [
            "blast", "blb", "brown_spot", "sheath_blight", "sheath_rot",
            "false_smut", "narrow_brown_spot", "leaf_scald", "stem_rot",
            "bakanae", "grain_discoloration", "bacterial_leaf_streak",
            "bacterial_panicle_blight", "tungro", "grassy_stunt", "ragged_stunt",
            "zinc_deficiency", "nitrogen_deficiency", "potassium_deficiency",
            "iron_toxicity", "healthy", "other",
        ]
        self.assertGreaterEqual(len(ADVICE), 22)
        for cls in expected_classes:
            self.assertIn(cls, ADVICE, f"Missing expected class: {cls}")

    def test_disease_categories_represented(self):
        causes = {info.get("cause_type") for info in ADVICE.values()}
        self.assertIn("Fungal", causes)
        self.assertIn("Bacterial", causes)
        self.assertIn("Viral", causes)
        self.assertIn("Physiological", causes)

    def test_symptoms_and_leaf_impact_present(self):
        for label, info in ADVICE.items():
            if label in ["healthy"]:
                continue
            # Check symptoms and foliar/leaf impact
            symptoms = info.get("symptoms_en", "")
            self.assertTrue(len(symptoms) > 10, f"Symptoms missing for {label}")
            if label != "other":
                self.assertIn("leaf", symptoms.lower(), f"Leaf impact missing for {label}")

    def test_management_advice_present(self):
        for label, info in ADVICE.items():
            if label in ["healthy"]:
                continue
            mgmt_en = info.get("en_full", "")
            mgmt_ta = info.get("ta_full", "")
            self.assertTrue(len(mgmt_en) > 15, f"Management advice missing for {label}")
            self.assertTrue(len(mgmt_ta) > 10, f"Tamil advice missing for {label}")


class TestMapAndLocation(unittest.TestCase):
    def test_parse_explicit_latlon(self):
        res = _parse_latlon("11.34, 77.72")
        self.assertIsNotNone(res)
        self.assertAlmostEqual(res[0], 11.34, places=2)
        self.assertAlmostEqual(res[1], 77.72, places=2)

    def test_parse_tamil_nadu_district_name(self):
        res = _parse_latlon("Erode, Tamil Nadu")
        self.assertIsNotNone(res)
        self.assertEqual(res, TN_DISTRICT_COORDS["erode"])

        res_thanjavur = _parse_latlon("Paddy fields in Thanjavur district")
        self.assertIsNotNone(res_thanjavur)
        self.assertEqual(res_thanjavur, TN_DISTRICT_COORDS["thanjavur"])

    def test_timestamp_comparison_safety(self):
        """Ensure mixed timezone timestamps from SQLite do not crash pandas comparison."""
        timestamps = [
            "2026-10-14T11:10:45+05:30",
            "2026-10-13 15:58:08",
            "2026-09-01T08:00:00Z",
        ]
        s = pd.Series(timestamps)
        # Clean to 19 characters naive timestamp
        cleaned = pd.to_datetime(s.astype(str).str.replace("T", " ", regex=False).str.slice(0, 19), errors="coerce")
        cutoff = pd.Timestamp.now() - pd.Timedelta(weeks=12)
        comparison = cleaned >= cutoff
        self.assertEqual(len(comparison), 3)
        self.assertTrue(comparison.iloc[0])


if __name__ == "__main__":
    unittest.main()
