# -*- coding: utf-8 -*-
"""
core/qa_engine.py  -  Trilingual Offline Paddy Disease Q&A Engine for AgriVision.

Adheres strictly to Phase 1 Requirements:
  1. Trilingual detection: Tamil script (ta), Tanglish (tanglish), English (en).
     Preserves multi-turn language memory for short/ambiguous messages.
  2. Scored keyword matching for 11 distinct intents:
     - symptoms
     - how_it_spreads
     - prevention
     - treatment_medicine
     - cause
     - favourable_conditions
     - what_to_do_now
     - yield_effect
     - see_officer
     - similar_diseases
     - which_parts_affected
  3. Compound rule: Spread term + Stop/Reduce/Prevent term -> resolves strictly to prevention.
  4. Answers strictly in the query's language (EN -> EN, TA -> TA, Tanglish -> Tanglish)
     in short bullet points without chemical brand names or dosages.
  5. Fallback responses provide 5 example questions in the query language.
  6. Politely refuses questions unrelated to paddy or the current disease context.
  7. Offline-first with SQLite history logging.
"""

import json
import re
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    from history_db import log_unanswered_question
except ImportError:
    from app.history_db import log_unanswered_question

_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "qa_knowledge.json"

_QA_DATA: dict | None = None
_VECTORIZERS: dict[str, TfidfVectorizer] = {}
_TOPIC_MATRICES: dict[str, any] = {}
_TOPIC_KEYS: dict[str, list[str]] = {}

# Comprehensive vocabulary for Tanglish detection
_TANGLISH_MARKERS = [
    r"\b(epadi|eppadi|yeppadi|yepdi|enna|ethu|evlo|evvalavu|yevvalavu|yen|yenna|edhavadhu|edhanala)\b",
    r"\b(panna|pannunga|pannalam|pannuratha|panrathu|pannanum|pannave)\b",
    r"\b(aagum|agum|aachu|aaguthu|aaguma|aagathu)\b",
    r"\b(irukku|irukkum|irukkura|iruntha|illai|illa|illama)\b",
    r"\b(varum|varathu|varama|varuthu|vanthurukku|vantha|vara)\b",
    r"\b(thadukka|thadukkurathu|thaduppathu|thadukkalam|thadukka mudiyuma)\b",
    r"\b(kuraikka|kuraikkalam|kuraipathu|korakka|korai)\b",
    r"\b(marundhu|maruthu|marunthu|marundhai|marundhugal)\b",
    r"\b(adikanum|adikkanum|thelikka|thelikkanum|thelichu|adikka)\b",
    r"\b(ilai|ilaigal|ilaila|ilaiya|ilaiyil)\b",
    r"\b(vayal|vayalla|vayalil|kollai)\b",
    r"\b(noi|nooi|noiyin|noigal)\b",
    r"\b(payir|payirin|payirukku|payiril|nel|kadhir|kathir)\b",
    r"\b(magasool|vilaiychal|padhar|mani)\b",
    r"\b(venum|vendam|thevai|thevailla)\b",
    r"\b(sollu|sollunga|theriyanum|puriyala)\b",
    r"\b(urram|uram|urea|potash|saambral|thazhai)\b",
    r"\b(vidhai|nerthi|naatru|aruvadai)\b",
    r"\b(velanmai|aluvalar|paravum|paravuthu|paravuma|kaathula|ippo|udane|paguthi|paathikkapadum|maathiri)\b",
]

# Aliases mapping legacy topic keys to the 11 Phase 1 standard intents
INTENT_ALIASES = {
    "spread": "how_it_spreads",
    "how_it_spreads": "how_it_spreads",
    "prevention": "prevention",
    "symptoms": "symptoms",
    "treatment_spray": "treatment_medicine",
    "treatment_medicine": "treatment_medicine",
    "dosage": "treatment_medicine",
    "cause": "cause",
    "favourable_weather": "favourable_conditions",
    "favourable_conditions": "favourable_conditions",
    "severity_meaning": "what_to_do_now",
    "what_to_do_now": "what_to_do_now",
    "harvest_safety": "yield_effect",
    "yield_effect": "yield_effect",
    "see_officer": "see_officer",
    "similar_diseases": "similar_diseases",
    "which_parts_affected": "which_parts_affected",
}

# Scored intent vocabulary across English, Tamil, and Tanglish
_INTENT_KEYWORD_RULES = {
    "symptoms": {
        "en": ["symptom", "symptoms", "sign", "signs", "look like", "looks like", "appearance", "spots", "lesion", "lesions", "damage pattern", "shape of spot", "what do i see"],
        "ta": ["அறிகுறி", "அறிகுறிகள்", "தோற்றம்", "எப்படி இருக்கும்", "புள்ளி", "புள்ளிகள்", "சாம்பல்", "மஞ்சள் வளையம்", "ஈட்டி வடிவம்"],
        "tanglish": ["symptoms", "symptoms enna", "epdi irukkum", "eppadi irukkum", "thotram", "pulligal", "signs", "damage", "lesion"],
    },
    "how_it_spreads": {
        "en": ["spread", "how it spreads", "transmission", "airborne", "contagious", "transmit", "wind", "rain splash", "conidia", "spores", "neighboring field"],
        "ta": ["பரவ", "பரவும்", "பரவுதல்", "பரவுகிறது", "எப்படி பரவுகிறது", "எப்படி பரவும்", "எவ்வாறு பரவுகிறது", "காற்று", "மழைத்துளி", "அடுத்த வயல்", "தொற்று"],
        "tanglish": ["spread agum", "epadi spread agum", "eppadi paravum", "paravum", "paravuthu", "kaathula paravuma", "paravuma", "transmission"],
    },
    "prevention": {
        "en": ["prevent", "prevention", "stop", "reduce", "control", "avoid", "stop spread", "reduce spread", "avoid recurrence", "next season", "seed treatment", "resistant variety"],
        "ta": ["தடுக்க", "தடுக்கலாம்", "எப்படி தடுக்கலாம்", "குறைக்க", "பரவுவதை குறைக்க", "கட்டுப்படுத்த", "அடுத்த பருவம்", "விதை நேர்த்தி", "முன்னெச்சரிக்கை", "வராமல் தடுக்க"],
        "tanglish": ["thadukka", "kuraikka", "reduce panna", "spread reduce", "spread reduce panna", "epadi spread pannuratha reduce panna", "stop panna", "next season", "varama thadukka", "seed treatment"],
    },
    "treatment_medicine": {
        "en": ["medicine", "spray", "treatment", "cure", "fungicide", "bactericide", "chemical", "what to spray", "drug", "remedy", "dosage", "dose", "how much to spray"],
        "ta": ["மருந்து", "தெளிப்பு", "தெளிக்க", "மருந்தளவு", "சிகிச்சை", "பூஞ்சைக்கொல்லி", "பாக்டீரியாக்கொல்லி", "அளவு"],
        "tanglish": ["marunthu", "marundhu", "maruthu", "thelikka", "thelikkanum", "adikanum", "spray panna", "dosage", "evvalavu spray", "cure"],
    },
    "cause": {
        "en": ["cause", "caused by", "pathogen", "fungus name", "bacteria name", "why does it occur", "reason", "organism"],
        "ta": ["காரணம்", "ஏன் வருகிறது", "உண்டாக்குவது எது", "காரணி", "எதனால் ஏற்படுகிறது"],
        "tanglish": ["kaaranam", "kaaranam enna", "yen varuthu", "edhanala varuthu", "edhanala", "pathogen", "reason"],
    },
    "favourable_conditions": {
        "en": ["weather", "climate", "temperature", "humidity", "dew", "rain", "favourable", "fog", "cloudy", "overcast", "conditions"],
        "ta": ["வானிலை", "சூழல்", "பனி", "ஈரப்பதம்", "வெப்பநிலை", "மழை", "மேகமூட்டம்"],
        "tanglish": ["weather", "climate", "pani kaalam", "mazhai kaalam", "eerappatham", "season", "soozhnilai"],
    },
    "what_to_do_now": {
        "en": ["what to do now", "severity", "action", "immediate action", "urgent steps", "my scan", "damage level", "grade meaning", "fertilizer", "fertilizer schedule"],
        "ta": ["இப்போது என்ன செய்ய வேண்டும்", "உடனடி நடவடிக்கை", "சேத சதவீதம்", "தீவிரம்", "அடுத்த நடவடிக்கை", "உரம்", "உர அட்டவணை"],
        "tanglish": ["what to do now", "ippo enna pannanum", "ippo udane enna pannanum", "action", "udane enna seiyanum", "udane", "severity", "damage level", "uram"],
    },
    "yield_effect": {
        "en": ["yield", "loss", "chaffy", "grain filling", "effect on yield", "harvest", "crop loss", "panicle loss"],
        "ta": ["மகசூல்", "தானியம்", "பதர்", "விளைச்சல் இழப்பு", "மகசூல் பாதிப்பு", "அறுவடை"],
        "tanglish": ["yield", "magasool", "loss", "padhar", "evlo loss", "chaffy", "grain loss"],
    },
    "see_officer": {
        "en": ["officer", "agriculture officer", "extension officer", "aao", "kvk", "contact officer", "expert visit", "inspection"],
        "ta": ["வேளாண் அலுவலர்", "அலுவலர்", "வேளாண்மை அலுவலர்", "தொடர்பு கொள்ள", "அலுவலகம்"],
        "tanglish": ["agriculture officer", "velanmai aluvalar", "aao", "kvk", "contact officer", "officer-ah"],
    },
    "similar_diseases": {
        "en": ["similar", "similar disease", "confuse", "looks like", "difference", "narrow brown spot", "sheath rot", "other disease lookalike"],
        "ta": ["ஒத்த நோய்கள்", "வேறுபாடு", "குலை நோய் வேறுபாடு", "ஒப்பீடு"],
        "tanglish": ["similar", "similar diseases", "vithiyaasam", "vera noi maathiri", "vera endha noi", "maathiri", "difference enna"],
    },
    "which_parts_affected": {
        "en": ["which parts", "plant parts", "leaf", "sheath", "node", "collar", "neck", "panicle", "glume", "roots", "affected parts"],
        "ta": ["பாதிக்கப்படும் உறுப்புகள்", "இலை", "கணு", "கழுத்து", "கதிர்", "உறை", "தாவர உறுப்புகள்"],
        "tanglish": ["endha paguthi", "plant parts", "ilai", "kanu", "kathir kazhuthu", "collar", "paguthi", "paathikkapadum"],
    },
}

# Compound Rule Keywords: Transmission vs Mitigation
_SPREAD_WORDS = {"spread", "transmission", "airborne", "paravum", "paravuthu", "paravuratha", "பரவ", "பரவுதல்", "பரவுகிறது"}
_MITIGATION_WORDS = {"reduce", "stop", "prevent", "avoid", "control", "limit", "kuraikka", "thadukka", "thadukkurathu", "தடுக்க", "குறைக்க", "கட்டுப்படுத்த"}

# Irrelevant query rejection keywords (non-paddy / non-crop)
_IRRELEVANT_PATTERNS = [
    r"\b(cricket|football|movie|cinema|song|actor|actress|politics|election|stock market|bitcoin|gold rate|car|bike|laptop|flight)\b",
    r"\b(weather today in chennai|who is prime minister|tell me a joke|write a poem)\b",
    r"\b(விளையாட்டு|சினிமா|பாடல்|நடிகர்|தேர்தல்|தங்கம் விலை)\b",
]


def _load_qa_data() -> dict:
    global _QA_DATA
    if _QA_DATA is None:
        if _DATA_FILE.exists():
            with open(_DATA_FILE, "r", encoding="utf-8") as f:
                _QA_DATA = json.load(f)
        else:
            _QA_DATA = {}
    return _QA_DATA


def is_tamil_text(text: str) -> bool:
    """Check if the text contains Tamil Unicode script (U+0B80 - U+0BFF)."""
    return bool(re.search(r"[\u0b80-\u0bff]", text))


def is_tanglish_text(text: str) -> bool:
    """Check if Latin-script text contains characteristic Tamil phonetics/vocabulary."""
    if is_tamil_text(text):
        return False
    t_clean = text.lower()
    for pat in _TANGLISH_MARKERS:
        if re.search(pat, t_clean):
            return True
    return False


def detect_language(text: str, fallback_lang: str = "en") -> str:
    """Detect language as 'ta' (Tamil script), 'tanglish' (Romanized Tamil), or 'en' (English).

    Short or ambiguous text falls back to the previous turn or user's preference.
    """
    clean = text.strip()
    if is_tamil_text(clean):
        return "ta"
    if is_tanglish_text(clean):
        return "tanglish"

    # Very short single-token queries retain fallback
    words = clean.split()
    if len(words) <= 1 and fallback_lang in ["ta", "tanglish", "en"]:
        return fallback_lang

    return "en"


def _clean_text(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^\w\s\u0b80-\u0bff]", " ", s)
    return " ".join(s.split())


def _build_index_for_disease(disease: str, qa_data: dict):
    cache_key = disease.lower().strip()
    if cache_key in _VECTORIZERS:
        return _VECTORIZERS[cache_key], _TOPIC_MATRICES[cache_key], _TOPIC_KEYS[cache_key]

    d_info = qa_data.get(cache_key) or qa_data.get("other") or {}
    topics = d_info.get("topics", {})

    corpus = []
    keys = []
    for t_key, t_val in topics.items():
        keys.append(t_key)
        text_parts = [
            t_val.get("title_en", ""),
            t_val.get("title_ta", ""),
            t_val.get("title_tanglish", ""),
            " ".join(t_val.get("keywords_en", [])),
            " ".join(t_val.get("keywords_ta", [])),
            " ".join(t_val.get("keywords_tanglish", [])),
            t_val.get("answer_en", ""),
            t_val.get("answer_ta", ""),
            t_val.get("answer_tanglish", ""),
        ]
        doc = _clean_text(" ".join(text_parts))
        corpus.append(doc)

    if not corpus:
        corpus = ["rice paddy disease question answer"]
        keys = ["general"]

    vec = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b")
    matrix = vec.fit_transform(corpus)

    _VECTORIZERS[cache_key] = vec
    _TOPIC_MATRICES[cache_key] = matrix
    _TOPIC_KEYS[cache_key] = keys
    return vec, matrix, keys


def get_example_questions(disease: str = "blast", lang: str = "en") -> list[str]:
    """Return 5 farmer-friendly example questions in the requested language."""
    d_clean = disease.lower().strip()
    d_display = {
        "blast": ("Rice Blast", "குலை நோய்", "Rice Blast"),
        "brown_spot": ("Brown Spot", "பழுப்பு புள்ளி நோய்", "Brown Spot"),
        "blb": ("Bacterial Leaf Blight", "பாக்டீரியா இலைக்கருகல்", "BLB Karugal"),
        "healthy": ("Healthy Paddy", "ஆரோக்கியமான நெற்பயிர்", "Aarokkiya Nel"),
        "other": ("Paddy Disease", "நெற்பயிர் நோய்", "Nel Noi"),
    }.get(d_clean, ("Rice Disease", "நெற்பயிர் நோய்", "Nel Noi"))

    if lang == "ta":
        return [
            f"1. {d_display[1]} எவ்வாறு பரவுகிறது?",
            f"2. இதை அடுத்த பருவத்தில் வராமல் தடுப்பது எப்படி?",
            f"3. {d_display[1]} நோயின் முக்கிய அறிகுறிகள் என்ன?",
            f"4. இந்நோய்க்கு என்ன மருந்து தெளிக்க வேண்டும்?",
            f"5. வேளாண்மை அலுவலரை எப்போது தொடர்பு கொள்ள வேண்டும்?",
        ]
    elif lang == "tanglish":
        return [
            f"1. {d_display[2]} epadi spread agum?",
            f"2. {d_display[2]} spread pannuratha reduce panna enna seiyanum?",
            f"3. Intha noiyoda symptoms enna?",
            f"4. Enna marunthu adikanum?",
            f"5. Agriculture officer-ah eppo contact pannanum?",
        ]
    else:
        return [
            f"1. How does {d_display[0]} spread?",
            f"2. How can I stop it from coming back next season?",
            f"3. What are the clear symptoms of {d_display[0]}?",
            f"4. What medicine should I spray for this?",
            f"5. When should I contact the Agriculture Officer?",
        ]


def ask_question(
    question: str,
    disease: str,
    scan_data: dict | None = None,
    conversation_history: list[dict] | None = None,
    preferred_lang: str | None = None,
) -> dict:
    """Process a user question against the diagnosed disease knowledge base.

    Returns:
      {
        "topic_id": str,          # One of the 11 intents
        "matched": bool,
        "answer": str,
        "title": str,
        "suggestions": list[str], # 5 example questions
        "lang": str,               # 'en', 'ta', or 'tanglish'
        "confidence_score": float,
        "tamil_script_answer": str # Tamil text used by TTS for Tanglish
      }
    """
    qa_data = _load_qa_data()
    q_raw = question.strip()

    # Determine fallback language from prior turn or UI preference
    last_lang = conversation_history[-1].get("lang") if conversation_history else None
    fallback_lang = last_lang or preferred_lang or "en"
    lang = detect_language(q_raw, fallback_lang=fallback_lang)

    if not q_raw:
        examples = get_example_questions(disease, lang=lang)
        prompt_msg = {
            "en": "Please ask a question about your rice crop or this disease.",
            "ta": "உங்கள் நெற்பயிர் அல்லது இந்நோய் பற்றிய கேள்வியைக் கேட்கவும்.",
            "tanglish": "Unga nel payir illa intha noi patriya kelviya kekkavum.",
        }.get(lang, "Please ask a question about your rice crop.")
        return {
            "topic_id": None,
            "matched": False,
            "answer": prompt_msg,
            "title": "",
            "suggestions": examples,
            "lang": lang,
            "confidence_score": 0.0,
            "tamil_script_answer": "",
        }

    # Normalize disease context
    d_key = disease.lower().strip()
    if d_key not in qa_data:
        if "blast" in d_key:
            d_key = "blast"
        elif "blb" in d_key or "bacterial" in d_key:
            d_key = "blb"
        elif "brown" in d_key:
            d_key = "brown_spot"
        elif "healthy" in d_key:
            d_key = "healthy"
        else:
            d_key = "other"

    disease_info = qa_data.get(d_key, qa_data.get("other", {}))
    topics = disease_info.get("topics", {})
    q_clean = _clean_text(q_raw)
    q_tokens = set(q_clean.split())

    # Check for irrelevant / out-of-domain queries
    for pat in _IRRELEVANT_PATTERNS:
        if re.search(pat, q_clean):
            refusal_text = {
                "en": "I can only answer questions related to paddy crops, rice leaf diseases, and agricultural management.",
                "ta": "மன்னிக்கவும், நெற்பயிர், இலை நோய்கள் மற்றும் விவசாய வழிகாட்டுதல் தொடர்பான கேள்விகளுக்கு மட்டுமே என்னால் பதிலளிக்க முடியும்.",
                "tanglish": "Mannikkavum, nel payir, noi nirvaagam mattrum velanmai thodarbaana kelvigalukku mattume pathil alikka mudiyum.",
            }.get(lang, "I can only answer questions about paddy crops.")
            return {
                "topic_id": None,
                "matched": False,
                "answer": refusal_text,
                "title": "",
                "suggestions": get_example_questions(d_key, lang=lang),
                "lang": lang,
                "confidence_score": 0.0,
                "tamil_script_answer": "",
            }

    # =========================================================================
    # COMPOUND RULE CHECK:
    # If the question contains both a SPREAD term AND a MITIGATION/STOP term,
    # the agricultural intent is firmly resolved to PREVENTION, not how_it_spreads!
    # =========================================================================
    has_spread_term = bool(q_tokens.intersection(_SPREAD_WORDS)) or any(w in q_clean for w in ["spread agum", "epadi spread", "eppadi paravum", "paravuratha"])
    has_mitigation_term = bool(q_tokens.intersection(_MITIGATION_WORDS)) or any(w in q_clean for w in ["reduce panna", "stop panna", "varama thadukka", "spread reduce"])

    compound_prevention = has_spread_term and has_mitigation_term

    # Scored Intent Evaluation
    intent_scores: dict[str, float] = {}

    if compound_prevention:
        # Heavily boost prevention so that spread never takes precedence
        intent_scores["prevention"] = 5.0
    else:
        for target_intent, group in _INTENT_KEYWORD_RULES.items():
            kw_list = group.get("en", []) + group.get("ta", []) + group.get("tanglish", [])
            for kw in kw_list:
                kw_c = kw.lower()
                if " " in kw_c and kw_c in q_clean:
                    # Multi-word phrase matches get highest score
                    weight = 2.8 + (len(kw_c.split()) * 0.5)
                    intent_scores[target_intent] = max(intent_scores.get(target_intent, 0.0), weight)
                elif kw_c in q_tokens or (len(kw_c) >= 3 and kw_c in q_clean):
                    weight = 2.0 if len(kw_c) > 4 else 1.5
                    intent_scores[target_intent] = max(intent_scores.get(target_intent, 0.0), weight)

    # TF-IDF Cosine Similarity across topics
    vec, matrix, keys = _build_index_for_disease(d_key, qa_data)
    q_vec = vec.transform([q_clean])
    sims = cosine_similarity(q_vec, matrix)[0]

    final_scores = []
    for idx, t_key in enumerate(keys):
        t_canonical = INTENT_ALIASES.get(t_key, t_key)
        t_val = topics.get(t_key, {})
        base_sim = float(sims[idx])

        bonus = intent_scores.get(t_canonical, 0.0)
        total = base_sim + bonus
        final_scores.append((total, t_canonical, t_key, t_val))

    final_scores.sort(key=lambda x: x[0], reverse=True)
    top_score, top_canonical, top_raw_key, top_val = final_scores[0] if final_scores else (0.0, None, None, {})

    CONFIDENCE_THRESHOLD = 0.25

    if top_score < CONFIDENCE_THRESHOLD or not top_val:
        try:
            log_unanswered_question(q_raw, disease=d_key, lang=lang)
        except Exception:
            pass
        fallback_msg = {
            "en": "I did not understand your question clearly. Here are 5 questions you can ask me about this disease:",
            "ta": "உங்கள் கேள்வி எனக்கு தெளிவாகப் புரியவில்லை. இந்நோய் பற்றி நீங்கள் கேட்கக்கூடிய 5 மாதிரி கேள்விகள் கீழே கொடுக்கப்பட்டுள்ளன:",
            "tanglish": "Unga kelvi enaku sariya puriyala. Intha noi patri neenga keka koodiya 5 example kelvigal:",
        }.get(lang, "I did not understand your question clearly.")
        return {
            "topic_id": None,
            "matched": False,
            "answer": fallback_msg,
            "title": "",
            "suggestions": get_example_questions(d_key, lang=lang),
            "lang": lang,
            "confidence_score": top_score,
            "tamil_script_answer": "",
        }

    # Language-matched answer extraction
    if lang == "ta":
        answer_text = top_val.get("answer_ta", "")
        title_text = top_val.get("title_ta", "")
        tamil_script_answer = answer_text
    elif lang == "tanglish":
        answer_text = top_val.get("answer_tanglish") or top_val.get("answer_en", "")
        title_text = top_val.get("title_tanglish") or top_val.get("title_en", "")
        tamil_script_answer = top_val.get("answer_ta", "")
    else:
        answer_text = top_val.get("answer_en", "")
        title_text = top_val.get("title_en", "")
        tamil_script_answer = top_val.get("answer_ta", "")

    # Duplicate question check: if the exact same intent was just answered, append additional context
    if conversation_history:
        prev_topic = conversation_history[-1].get("topic_id")
        if prev_topic == top_canonical:
            supp_note = {
                "en": "\n\n• (Additional Note): Always confirm with your local Assistant Agriculture Officer (AAO) before taking field action.",
                "ta": "\n\n• (கூடுதல் குறிப்பு): கள நடவடிக்கை எடுக்கும் முன் உங்கள் வட்டார வேளாண்மை அலுவலரை அணுகி உறுதிப்படுத்தவும்.",
                "tanglish": "\n\n• (Additional Note): Field-la nadavadikkai edukkum munnadi local Agriculture Officer-kitta confirmation vangikonga.",
            }.get(lang, "")
            answer_text = f"{answer_text}{supp_note}"

    # Prefix live scan metrics if applicable
    if scan_data and top_canonical in ["what_to_do_now", "symptoms"]:
        sev = scan_data.get("severity")
        grade_val = scan_data.get("severity_grade") or ""
        if sev is not None:
            if lang == "ta":
                prefix = f"உங்கள் பரிசோதனை முடிவின்படி, இலையின் சேத அளவு {sev:.1f}% ({grade_val}).\n"
            elif lang == "tanglish":
                prefix = f"Unga scan mudivupadi, ilaila {sev:.1f}% damage ({grade_val}) irukku.\n"
            else:
                prefix = f"Based on your scan, your leaf has {sev:.1f}% damage ({grade_val} grade).\n"
            answer_text = f"{prefix}{answer_text}"

    return {
        "topic_id": top_canonical,
        "matched": True,
        "answer": answer_text,
        "title": title_text,
        "suggestions": get_example_questions(d_key, lang=lang),
        "lang": lang,
        "confidence_score": round(top_score, 3),
        "tamil_script_answer": tamil_script_answer,
    }
