import sys
from pathlib import Path

# Force UTF-8 stdout
sys.stdout.reconfigure(encoding="utf-8")

APP_DIR = Path(r"C:\Users\keert\paddy_dataset\app")
sys.path.insert(0, str(APP_DIR))

from core.qa_engine import ask_question, detect_language

test_cases = [
    # (Query, Expected Topic, Expected Lang)
    ("what should i spray for blast?", "treatment_spray", "en"),
    ("what is the dosage?", "dosage", "en"),
    ("how does this disease spread?", "spread", "en"),
    ("what is blast?", "what_is_it", "en"),
    ("what fertilizer should i apply?", "fertilizer_advice", "en"),
    ("how to prevent it coming next season?", "prevention", "en"),

    # Tamil script
    ("இதற்கு என்ன மருந்து தெளிக்க வேண்டும்?", "treatment_spray", "ta"),
    ("மருந்தளவு எவ்வளவு?", "dosage", "ta"),
    ("இந்த நோய் எவ்வாறு பரவுகிறது?", "spread", "ta"),
    ("குலை நோய் என்றால் என்ன?", "what_is_it", "ta"),

    # Tanglish
    ("enna marunthu adikkanum?", "treatment_spray", "tanglish"),
    ("dosage evvalavu?", "dosage", "tanglish"),
    ("intha disease eppadi spread aagum?", "spread", "tanglish"),
    ("eppadi thadukkurathu?", "prevention", "tanglish"),
    ("urea podalama?", "fertilizer_advice", "tanglish"),
    ("epdi irukkum symptoms?", "symptoms", "tanglish"),
]

print("=====================================================================")
print("TRILINGUAL Q&A ENGINE VERIFICATION")
print("=====================================================================")

all_passed = True
for q, exp_topic, exp_lang in test_cases:
    res = ask_question(q, disease="blast")
    topic = res.get("topic_id")
    lang = res.get("lang")
    matched = res.get("matched")
    ans = res.get("answer", "")
    
    status = "OK"
    if topic != exp_topic:
        status = f"FAIL (Expected topic {exp_topic}, got {topic})"
        all_passed = False
    elif lang != exp_lang:
        status = f"FAIL (Expected lang {exp_lang}, got {lang})"
        all_passed = False
    elif not matched:
        status = "FAIL (Not matched)"
        all_passed = False
        
    print(f"[{status}] Q: {q}")
    print(f"   -> Lang: {lang} | Topic: {topic} | Title: {res.get('title')}")
    print(f"   -> Ans: {ans[:90]}...")
    print()

if all_passed:
    print(">>> ALL TRILINGUAL TEST CASES PASSED PERFECTLY! <<<")
else:
    print(">>> SOME TEST CASES FAILED! <<<")
    sys.exit(1)
