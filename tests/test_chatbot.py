# -*- coding: utf-8 -*-
"""
test_chatbot.py  -  Automated test suite for AgriVision Chatbot (Phase 1).
Validates:
  1. Trilingual detection (Tamil script -> 'ta', Tanglish -> 'tanglish', English -> 'en')
  2. Intent classification across all 11 required intents
  3. Compound rule: Spread term + Stop/Reduce/Mitigation term -> 'prevention'
  4. Mandatory test cases from specifications
"""

import sys
import unittest
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PROJECT_ROOT = Path(r"C:\Users\keert\paddy_dataset")
sys.path.insert(0, str(PROJECT_ROOT / "app"))

from core.qa_engine import ask_question, detect_language

# 45+ test cases: (Question, Expected Intent, Expected Lang, Disease Context)
TEST_CASES = [
    # ---- MANDATORY CASES FROM SPECIFICATION ----
    ("epadi spread agum", "how_it_spreads", "tanglish", "brown_spot"),
    ("epadi spread pannuratha reduce panna", "prevention", "tanglish", "brown_spot"),
    ("How can I stop it from coming back next season?", "prevention", "en", "blast"),
    ("இது எப்படி பரவும்?", "how_it_spreads", "ta", "blast"),
    ("இதை எப்படி தடுக்கலாம்?", "prevention", "ta", "blast"),
    ("symptoms enna?", "symptoms", "tanglish", "blast"),

    # ---- COMPOUND SPREAD + REDUCE / STOP CASES ----
    ("how to stop the spread of blast?", "prevention", "en", "blast"),
    ("how can i reduce the spread?", "prevention", "en", "blb"),
    ("spread aaguratha eppadi stop panna?", "prevention", "tanglish", "brown_spot"),
    ("noi paravuratha thadukka enna pannanum?", "prevention", "tanglish", "blast"),
    ("பரவுவதை குறைக்க என்ன செய்ய வேண்டும்?", "prevention", "ta", "brown_spot"),
    ("நோய் மேலும் பரவாமல் தடுக்க வழி என்ன?", "prevention", "ta", "blb"),

    # ---- SYMPTOMS INTENT ----
    ("What are the main symptoms of brown spot?", "symptoms", "en", "brown_spot"),
    ("What does the leaf lesion look like?", "symptoms", "en", "blast"),
    ("குலை நோயின் அறிகுறிகள் என்ன?", "symptoms", "ta", "blast"),
    ("இலை புள்ளிகள் எவ்வாறு தோன்றும்?", "symptoms", "ta", "brown_spot"),
    ("ilai epdi irukkum?", "symptoms", "tanglish", "blast"),
    ("intha noiyoda signs enna?", "symptoms", "tanglish", "blb"),

    # ---- HOW IT SPREADS INTENT ----
    ("How does bacterial leaf blight spread across fields?", "how_it_spreads", "en", "blb"),
    ("Is this disease airborne or seed-borne?", "how_it_spreads", "en", "brown_spot"),
    ("பழுப்பு புள்ளி நோய் எவ்வாறு பரவுகிறது?", "how_it_spreads", "ta", "brown_spot"),
    ("காற்றின் மூலம் நோய் பரவுமா?", "how_it_spreads", "ta", "blast"),
    ("eppadi paravum intha noi?", "how_it_spreads", "tanglish", "blast"),
    ("kaathula paravuma?", "how_it_spreads", "tanglish", "blast"),

    # ---- PREVENTION INTENT ----
    ("How to prevent brown spot in next season?", "prevention", "en", "brown_spot"),
    ("What seed treatment is recommended before sowing?", "prevention", "en", "blast"),
    ("அடுத்த பருவத்தில் இந்நோய் வராமல் தடுப்பது எப்படி?", "prevention", "ta", "blast"),
    ("விதை நேர்த்தி எவ்வாறு செய்ய வேண்டும்?", "prevention", "ta", "brown_spot"),
    ("adutha season varama thadukka enna pannanum?", "prevention", "tanglish", "blast"),
    ("seed treatment eppadi pannanum?", "prevention", "tanglish", "brown_spot"),

    # ---- TREATMENT / MEDICINE INTENT ----
    ("What medicine should I spray for this disease?", "treatment_medicine", "en", "blast"),
    ("What chemical or fungicide is recommended?", "treatment_medicine", "en", "blb"),
    ("இதற்கு என்ன மருந்து தெளிக்க வேண்டும்?", "treatment_medicine", "ta", "blast"),
    ("மருந்தளவு மற்றும் தெளிப்பு முறை என்ன?", "treatment_medicine", "ta", "brown_spot"),
    ("enna marunthu thelikkanum?", "treatment_medicine", "tanglish", "blast"),
    ("spray panna enna marundhu use pannalam?", "treatment_medicine", "tanglish", "blb"),

    # ---- CAUSE INTENT ----
    ("What causes blast disease in paddy?", "cause", "en", "blast"),
    ("Which pathogen or fungus causes brown spot?", "cause", "en", "brown_spot"),
    ("இந்நோய் உண்டாகக் காரணம் என்ன?", "cause", "ta", "blb"),
    ("இதை உண்டாக்கும் பூஞ்சை எது?", "cause", "ta", "blast"),
    ("noi vara kaaranam enna?", "cause", "tanglish", "blast"),
    ("edhanala intha karugal varuthu?", "cause", "tanglish", "blb"),

    # ---- FAVOURABLE CONDITIONS INTENT ----
    ("What weather conditions favour blast development?", "favourable_conditions", "en", "blast"),
    ("Does cloudy weather and dew trigger the disease?", "favourable_conditions", "en", "brown_spot"),
    ("நோய் தீவிரமடைய சாதகமான வானிலை என்ன?", "favourable_conditions", "ta", "blast"),
    ("weather eppadi iruntha noi athigarikkum?", "favourable_conditions", "tanglish", "blast"),

    # ---- WHAT TO DO NOW (SEVERITY) INTENT ----
    ("What should I do now for my affected field?", "what_to_do_now", "en", "blast"),
    ("தற்போது எடுக்க வேண்டிய உடனடி நடவடிக்கை என்ன?", "what_to_do_now", "ta", "brown_spot"),
    ("ippo udane enna pannanum?", "what_to_do_now", "tanglish", "blb"),

    # ---- YIELD EFFECT INTENT ----
    ("How does neck blast affect rice yield and grain filling?", "yield_effect", "en", "blast"),
    ("மகசூல் மற்றும் தானியத்தின் மீது என்ன பாதிப்பு ஏற்படும்?", "yield_effect", "ta", "brown_spot"),
    ("evlo magasool loss aagum?", "yield_effect", "tanglish", "blast"),

    # ---- SEE OFFICER INTENT ----
    ("When should I contact the Agriculture Officer?", "see_officer", "en", "blast"),
    ("வேளாண்மை அலுவலரை எப்போது தொடர்பு கொள்ள வேண்டும்?", "see_officer", "ta", "brown_spot"),
    ("agriculture officer-ah eppo contact pannanum?", "see_officer", "tanglish", "blb"),

    # ---- SIMILAR DISEASES INTENT ----
    ("What are the similar looking diseases to brown spot?", "similar_diseases", "en", "brown_spot"),
    ("குலை நோய் போன்ற பிற நோய்கள் எவை?", "similar_diseases", "ta", "blast"),
    ("vera endha noi maathiri ithu irukkum?", "similar_diseases", "tanglish", "brown_spot"),

    # ---- WHICH PARTS AFFECTED INTENT ----
    ("Which plant parts are affected by blast?", "which_parts_affected", "en", "blast"),
    ("இந்நோயால் தாக்கப்படும் தாவர உறுப்புகள் எவை?", "which_parts_affected", "ta", "blb"),
    ("payirin endha paguthi paathikkapadum?", "which_parts_affected", "tanglish", "blast"),
]


class TestChatbotEngine(unittest.TestCase):
    """Test suite for AgriVision Chatbot Phase 1."""

    def test_all_queries(self):
        passed = 0
        failed = 0
        failures = []

        print("\n" + "=" * 76)
        print("RUNNING 50+ TRILINGUAL Q&A INTENT & LANGUAGE BENCHMARK TESTS")
        print("=" * 76)

        for q, exp_intent, exp_lang, disease in TEST_CASES:
            res = ask_question(q, disease=disease)
            act_lang = res.get("lang")
            act_intent = res.get("topic_id")
            matched = res.get("matched", False)

            is_ok = (act_lang == exp_lang) and (act_intent == exp_intent) and matched

            if is_ok:
                passed += 1
                status_icon = "PASS"
            else:
                failed += 1
                status_icon = "FAIL"
                failures.append({
                    "q": q,
                    "exp_intent": exp_intent,
                    "act_intent": act_intent,
                    "exp_lang": exp_lang,
                    "act_lang": act_lang,
                    "matched": matched,
                })

            print(f"[{status_icon:4s}] Q: {q}")
            print(f"       Exp: ({exp_lang}, {exp_intent}) -> Act: ({act_lang}, {act_intent})")

        print("=" * 76)
        print(f"RESULTS: {passed} PASSED, {failed} FAILED OUT OF {len(TEST_CASES)} TOTAL TESTS")
        print("=" * 76)

        if failures:
            for f in failures:
                print(f"FAILED CASE: Q: {f['q']}")
                print(f"  Expected: intent={f['exp_intent']}, lang={f['exp_lang']}")
                print(f"  Actual:   intent={f['act_intent']}, lang={f['act_lang']}, matched={f['matched']}")

        self.assertEqual(failed, 0, f"{failed} test cases failed!")


if __name__ == "__main__":
    unittest.main()
