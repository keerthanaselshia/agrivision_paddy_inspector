"""
strings.py  –  Bilingual localization module (English and Tamil) for AgriVision.

Provides clean string translation dictionary and lookup helper t(key, lang).
"""

STRINGS = {
    # App Header & Branding
    "app_title": {
        "en": "AgriVision Paddy Inspector",
        "ta": "அக்ரிவிஷன் நெல் பயிர் பரிசோதகர்",
    },
    "app_tagline": {
        "en": "Scan. Detect. Protect your paddy.",
        "ta": "ஸ்கேன் செய்க. கண்டறிக. நெற்பயிரைக் காப்போம்.",
    },
    "badge_edge_ai": {
        "en": "Edge AI",
        "ta": "எட்ஜ் AI",
    },
    "badge_offline": {
        "en": "Works offline",
        "ta": "இணையமின்றி இயங்கும்",
    },
    "badge_bilingual": {
        "en": "Tamil + English",
        "ta": "தமிழ் + ஆங்கிலம்",
    },

    # Navigation Menu
    "nav_scan": {
        "en": "🔬  Scan",
        "ta": "🔬  பரிசோதனை",
    },
    "nav_library": {
        "en": "📚  Disease Library",
        "ta": "📚  நோய் வழிகாட்டி",
    },
    "nav_history": {
        "en": "📊  History",
        "ta": "📊  வரலாறு",
    },
    "nav_map": {
        "en": "🗺️  Map",
        "ta": "🗺️  வரைபடம்",
    },
    "nav_collection": {
        "en": "🌾  Field Collection",
        "ta": "🌾  களத் தரவு சேகரிப்பு",
    },
    "nav_validation": {
        "en": "📐  Severity Validation",
        "ta": "📐  தீவிரத்தன்மை சரிபார்ப்பு",
    },
    "nav_about": {
        "en": "ℹ️  About",
        "ta": "ℹ️  பற்றி",
    },

    # Sidebar settings
    "settings_header": {
        "en": "Settings",
        "ta": "அமைப்புகள்",
    },
    "model_file": {
        "en": "Model file",
        "ta": "மாதிரி கோப்பு",
    },
    "labels_file": {
        "en": "Labels file",
        "ta": "பெயர் லேபிள் கோப்பு",
    },
    "min_confidence": {
        "en": "Minimum confidence (%)",
        "ta": "குறைந்தபட்ச நம்பகத்தன்மை (%)",
    },
    "severity_settings": {
        "en": "Severity (OpenCV)",
        "ta": "பாதிப்பு அளவு (OpenCV)",
    },
    "sat_min": {
        "en": "Leaf saturation minimum",
        "ta": "இலை செறிவு குறைந்தபட்சம்",
    },
    "hue_max": {
        "en": "Lesion hue below (brown/yellow)",
        "ta": "புண் நிற அளவு (பழுப்பு/மஞ்சள்)",
    },
    "quality_thresholds": {
        "en": "Quality check thresholds",
        "ta": "படத் தர வரம்புகள்",
    },
    "report_location": {
        "en": "Location (GPS module comes later)",
        "ta": "இருப்பிடம் (GPS விவரம்)",
    },
    "auto_save_label": {
        "en": "Auto-save results",
        "ta": "முடிவுகளை தானாகச் சேமி",
    },

    # Scan Page
    "tab_upload": {
        "en": "Upload leaf photo",
        "ta": "இலை படத்தை பதிவேற்றுக",
    },
    "tab_camera": {
        "en": "Use camera",
        "ta": "கேமராவைப் பயன்படுத்துக",
    },
    "take_photo": {
        "en": "Take a photo of the leaf",
        "ta": "இலையை புகைப்படம் எடுக்கவும்",
    },
    "upload_instruction": {
        "en": "Upload or capture a paddy leaf photo to start. Use a plain white or grey background for best severity results.",
        "ta": "தொடங்க நெல் இலை புகைப்படத்தைப் பதிவேற்றவும் அல்லது எடுக்கவும். சிறந்த முடிவுகளுக்கு வெற்று வெள்ளை அல்லது சாம்பல் பின்னணியைப் பயன்படுத்தவும்.",
    },
    "scanning_label": {
        "en": "Scanning leaf...",
        "ta": "இலை ஸ்கேன் செய்யப்படுகிறது...",
    },
    "analysing_label": {
        "en": "⏳ Analysing…",
        "ta": "⏳ ஆய்வு செய்யப்படுகிறது…",
    },
    "quality_header": {
        "en": "Image Quality",
        "ta": "படத்தின் தரம்",
    },
    "input_leaf": {
        "en": "Input leaf",
        "ta": "உள்ளீடு இலை",
    },
    "detected_lesion": {
        "en": "Detected diseased area (red)",
        "ta": "கண்டறியப்பட்ட பாதிக்கப்பட்ட பகுதி (சிவப்பு)",
    },
    "predictions_header": {
        "en": "Predictions",
        "ta": "கணிப்புகள்",
    },
    "uncertain_title": {
        "en": "⚠️ Uncertain prediction",
        "ta": "⚠️ நிச்சயமற்ற கணிப்பு",
    },
    "advisory_header": {
        "en": "Advisory",
        "ta": "விவசாய ஆலோசனை",
    },
    "advisory_disclaimer": {
        "en": "Decision support only. Doses must come from the current TNAU guide or product label and be checked by an agriculture officer.",
        "ta": "இது முடிவெடுப்பதற்கான வழிகாட்டல் மட்டுமே. மருந்து அளவுகள் தமிழ்நாடு வேளாண்மைப் பல்கலைக்கழக (TNAU) வழிகாட்டி அல்லது வேளாண்மை அலுவலரின் பரிந்துரைப்படி இருக்க வேண்டும்.",
    },
    "report_header": {
        "en": "Report",
        "ta": "அறிக்கை",
    },
    "send_telegram": {
        "en": "📤 Send report to Telegram",
        "ta": "📤 டெலிகிராமிற்கு அறிக்கை அனுப்புக",
    },

    # Severity Grades
    "grade_very_low": {
        "en": "Very low (monitor)",
        "ta": "மிகக் குறைவு (கண்காணிக்கவும்)",
    },
    "grade_moderate": {
        "en": "Moderate",
        "ta": "மிதமானது",
    },
    "grade_high": {
        "en": "High",
        "ta": "அதிகம்",
    },
    "grade_severe": {
        "en": "Severe (urgent)",
        "ta": "தீவிரமானது (அவசரம்)",
    },
}


def t(key: str, lang: str = "en") -> str:
    """Retrieve localized string with fallback to English or the key itself."""
    entry = STRINGS.get(key)
    if not entry:
        return key
    return entry.get(lang) or entry.get("en") or key
