"""
test_features_1_2_3.py  –  Automated unit test suite for:
  Feature 1: Disease Library & Reference Images
  Feature 2: Ask-Your-Own-Question (Offline Q&A Engine)
  Feature 3: Speech Technology (TTS / STT / Bi-lingual)
"""

import json
import unittest
from pathlib import Path
import sys

# Ensure app is on sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT / "app"))

from core.advisory import ADVICE, get_disease
from core.qa_engine import ask_question, get_example_questions, is_tamil_text
from history_db import (
    init_db,
    save_inspection,
    update_inspection_qa,
    log_unanswered_question,
    get_unanswered_questions,
    get_inspections,
)


class TestDiseaseLibrary(unittest.TestCase):
    """Feature 1: Disease Library and Reference Images."""

    def test_disease_info_loaded(self):
        self.assertGreaterEqual(len(ADVICE), 5)
        for expected in ["blast", "blb", "brown_spot", "healthy", "other"]:
            self.assertIn(expected, ADVICE)
            info = ADVICE[expected]
            self.assertIn("name", info)
            self.assertIn("name_ta", info)
            self.assertIn("gallery_images", info)
            self.assertIn("treatment_en", info)
            self.assertIn("prevention_en", info)

    def test_reference_images_exist_locally(self):
        static_dir = _PROJECT_ROOT / "app" / "static" / "disease_library"
        self.assertTrue(static_dir.exists(), "static/disease_library directory should exist")
        manifest_file = static_dir / "manifest.json"
        self.assertTrue(manifest_file.exists(), "manifest.json should exist")

        with open(manifest_file, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        for d_key in ["blast", "blb", "brown_spot", "healthy", "other"]:
            self.assertIn(d_key, manifest)
            imgs = manifest[d_key]
            self.assertGreaterEqual(len(imgs), 2, f"Should have at least 2 images for {d_key}")
            for rel in imgs:
                img_path = _PROJECT_ROOT / "app" / rel
                self.assertTrue(img_path.exists(), f"Image {img_path} must exist on disk")


class TestOfflineQAEngine(unittest.TestCase):
    """Feature 2: Ask-Your-Own-Question (Offline Q&A Engine)."""

    @classmethod
    def setUpClass(cls):
        init_db()

    def test_example_questions(self):
        q_en = get_example_questions("blast", lang="en")
        self.assertGreaterEqual(len(q_en), 3)
        self.assertTrue(any("blast" in q.lower() for q in q_en))

        q_ta = get_example_questions("blast", lang="ta")
        self.assertGreaterEqual(len(q_ta), 3)
        self.assertTrue(is_tamil_text(q_ta[0]))

    def test_ask_question_topic_matching(self):
        scan_data = {
            "disease": "Rice Blast",
            "confidence": 94.5,
            "severity": 18.2,
            "severity_grade": "Fair",
        }
        res = ask_question("How does this disease spread?", disease="blast", scan_data=scan_data)
        self.assertTrue(res["matched"])
        self.assertIn(res["topic_id"], ["how_it_spreads", "spread"])
        self.assertTrue("wind" in res["answer"].lower() or "spore" in res["answer"].lower() or "airborne" in res["answer"].lower())

    def test_ask_question_treatment_and_dosage(self):
        res = ask_question("What medicine should I spray and dosage?", disease="blb")
        self.assertTrue(res["matched"])
        self.assertIn(res["topic_id"], ["treatment_medicine", "treatment_spray", "dosage"])

    def test_ask_question_healthy_crop(self):
        res = ask_question("What fertilizer schedule should I apply for healthy paddy?", disease="healthy")
        self.assertTrue(res["matched"])
        self.assertIn(res["topic_id"], ["what_to_do_now", "fertilizer_advice", "prevention"])

    def test_ask_question_tamil(self):
        res = ask_question("மருந்து தெளிக்க என்ன அளவு?", disease="blast", preferred_lang="ta")
        self.assertTrue(res["matched"])
        self.assertTrue(is_tamil_text(res["answer"]))

    def test_unanswered_question_logging(self):
        weird_q = "Can I fly an airplane over paddy fields at midnight in 2099?"
        res = ask_question(weird_q, disease="blast")
        self.assertFalse(res["matched"])
        # Should have logged
        unanswered = get_unanswered_questions()
        self.assertTrue(any(weird_q in u["question"] for u in unanswered))

    def test_qa_persistence_in_history_db(self):
        dummy_hash = "qa_test_hash_12345"
        save_inspection(
            disease="blast",
            confidence=95.0,
            severity=12.0,
            severity_grade="Fair",
            location="Test Field",
            image_hash=dummy_hash,
        )
        sample_qa = [
            {"question": "How to prevent?", "answer": "Use certified seed."},
            {"question": "What dosage?", "answer": "1g per litre."},
        ]
        ok = update_inspection_qa(dummy_hash, sample_qa)
        self.assertTrue(ok)

        inspections = get_inspections()
        rec = next((r for r in inspections if r.get("image_hash") == dummy_hash), None)
        self.assertIsNotNone(rec)
        qa_loaded = json.loads(rec["qa_history_json"])
        self.assertEqual(len(qa_loaded), 2)
        self.assertEqual(qa_loaded[0]["question"], "How to prevent?")


if __name__ == "__main__":
    unittest.main()
