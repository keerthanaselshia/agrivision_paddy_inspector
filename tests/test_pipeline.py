"""
test_pipeline.py  –  Automated unit and integration test suite for AgriVision.

Runs with:
  venv2\\Scripts\\python.exe -m unittest discover -s tests -p "test_*.py"
"""

import sys
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

# Add app directory to sys.path
_TEST_DIR = Path(__file__).resolve().parent
_APP_DIR = _TEST_DIR.parent / "app"
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

from core.quality import check_quality
from core.reports import build_text_report
from core.scan_effect import image_to_data_uri, scanning_html
from core.severity import grade, severity
from core.strings import t
from history_db import get_schema_version, init_db
from telegram_queue import init_telegram_queue, queue_count
from validation_db import get_validations, init_validation_table


class TestQualityCheck(unittest.TestCase):
    def test_blank_image_fails_quality(self):
        blank = np.zeros((300, 300, 3), dtype=np.uint8)
        res = check_quality(blank)
        self.assertIn(res["grade"], ["Fair", "Poor"])
        self.assertTrue(len(res["reasons"]) > 0)

    def test_green_sharp_image_passes(self):
        # Create a synthetic sharp green rectangle
        img = np.zeros((300, 300, 3), dtype=np.uint8)
        img[:, :] = [34, 139, 34]  # Forest green
        # Add high-frequency noise for sharpness
        noise = np.random.randint(0, 50, (300, 300, 3), dtype=np.uint8)
        img = np.clip(img + noise, 0, 255)
        res = check_quality(img)
        self.assertIn("score", res)
        self.assertIn("grade", res)
        self.assertGreaterEqual(res["score"], 0)


class TestSeverityLogic(unittest.TestCase):
    def test_grade_boundaries(self):
        self.assertEqual(grade(0.0), "Very low (monitor)")
        self.assertEqual(grade(0.9), "Very low (monitor)")
        self.assertEqual(grade(1.0), "Moderate")
        self.assertEqual(grade(9.9), "Moderate")
        self.assertEqual(grade(10.0), "High")
        self.assertEqual(grade(24.9), "High")
        self.assertEqual(grade(25.0), "Severe (urgent)")
        self.assertEqual(grade(85.0), "Severe (urgent)")

    def test_severity_output_dimensions(self):
        dummy = np.zeros((200, 200, 3), dtype=np.uint8)
        dummy[:, :] = [40, 150, 40]
        sev_pct, overlay = severity(dummy, sat_min=40, lesion_hue_max=28)
        self.assertIsInstance(sev_pct, float)
        self.assertEqual(overlay.shape, (200, 200, 3))


class TestLocalizationStrings(unittest.TestCase):
    def test_english_translation(self):
        self.assertEqual(t("app_title", "en"), "AgriVision Paddy Inspector")
        self.assertEqual(t("nav_scan", "en"), "🔬  Scan")

    def test_tamil_translation(self):
        self.assertEqual(t("app_title", "ta"), "அக்ரிவிஷன் நெல் பயிர் பரிசோதகர்")
        self.assertEqual(t("nav_scan", "ta"), "🔬  பரிசோதனை")

    def test_missing_key_fallback(self):
        self.assertEqual(t("non_existent_key_xyz", "en"), "non_existent_key_xyz")


class TestScanEffect(unittest.TestCase):
    def test_data_uri_and_html(self):
        pil_img = Image.new("RGB", (100, 100), color=(50, 100, 50))
        uri = image_to_data_uri(pil_img)
        self.assertTrue(uri.startswith("data:image/jpeg;base64,"))
        html = scanning_html(uri, label="Scanning leaf...")
        self.assertIn("Scanning leaf...", html)
        self.assertIn(uri, html)


class TestDatabaseIntegrity(unittest.TestCase):
    def test_history_db_schema_version(self):
        init_db()
        ver = get_schema_version()
        self.assertGreaterEqual(ver, 3)

    def test_telegram_queue_init(self):
        init_telegram_queue()
        cnt = queue_count()
        self.assertIsInstance(cnt, int)

    def test_validation_db_init(self):
        init_validation_table()
        vals = get_validations()
        self.assertIsInstance(vals, list)


class TestReportGeneration(unittest.TestCase):
    def test_build_text_report(self):
        rep = build_text_report(
            name="Rice Blast",
            conf=88.5,
            sev=14.2,
            sev_grade="Moderate",
            location="Erode, TN",
            advice_en="Apply biocontrol agents.",
            advice_ta="உயிரியல் கட்டுப்பாட்டைப் பயன்படுத்தவும்.",
        )
        self.assertIn("Rice Blast", rep)
        self.assertIn("88%", rep)
        self.assertIn("Moderate", rep)
        self.assertIn("Erode, TN", rep)


if __name__ == "__main__":
    unittest.main()
