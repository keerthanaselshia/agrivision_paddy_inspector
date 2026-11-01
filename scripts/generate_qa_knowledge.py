"""
generate_qa_knowledge.py
Builds app/data/qa_knowledge.json with short, farmer-friendly Q&A topics
in English and Tamil with comprehensive keyword lists and TNAU verification tags.
"""

import json
from pathlib import Path

qa_data = {
    "_meta": {
        "version": 1,
        "title": "AgriVision Offline Q&A Knowledge Base for Paddy Diseases",
        "status": "Starter content - to be verified against TNAU recommendations"
    },
    "blast": {
        "name_en": "Rice Blast",
        "name_ta": "குலை நோய்",
        "topics": {
            "what_is_it": {
                "title_en": "What is Rice Blast?",
                "title_ta": "குலை நோய் என்றால் என்ன?",
                "keywords_en": ["what is", "tell me about", "explain", "disease info", "meaning", "blast", "leaf blast", "identify", "about blast"],
                "keywords_ta": ["என்ன நோய்", "குலை நோய்", "விளக்கம்", "பற்றி சொல்லுங்கள்", "குலைநோய்"],
                "answer_en": "Rice Blast is a destructive fungal disease affecting rice leaves, collars, nodes, and panicle necks. It produces characteristic spindle-shaped diamond lesions with ash-grey centres and brown borders.",
                "answer_ta": "குலை நோய் என்பது நெற்பயிரின் இலை, கணு மற்றும் கதிர் கழுத்துப் பகுதியைத் தாக்கும் ஒரு கடுமையான பூஞ்சை நோய். இது சாம்பல் நிற மையமும் பழுப்பு நிற விளிம்பும் கொண்ட ஈட்டி வடிவ புள்ளிகளை உருவாக்குகிறது."
            },
            "cause": {
                "title_en": "What causes Rice Blast?",
                "title_ta": "இந்நோய்க்கான காரணம் என்ன?",
                "keywords_en": ["cause", "caused by", "fungus", "bacteria", "pathogen", "why", "reason", "organism", "fungal"],
                "keywords_ta": ["காரணம்", "பூஞ்சை", "ஏன் வருகிறது", "எதனால்", "உண்டாக்குவது எது"],
                "answer_en": "It is caused by the airborne fungus Magnaporthe oryzae (Pyricularia oryzae). Fungal spores land on wet leaves and penetrate tissue under cool night temperatures and high humidity.",
                "answer_ta": "இது மேக்னபோர்த்தே ஒரைசே (பைரிகுலேரியா ஒரைசே) என்ற காற்று வழிப் பரவும் பூஞ்சையினால் ஏற்படுகிறது. குளிர்ந்த மற்றும் ஈரப்பதமான இரவுகளில் இதன் வித்துக்கள் இலைகளில் புகுந்து தாக்குகின்றன."
            },
            "symptoms": {
                "title_en": "Symptoms and leaf damage",
                "title_ta": "அறிகுறிகள் மற்றும் இலை பாதிப்பு",
                "keywords_en": ["symptoms", "signs", "look like", "damage", "leaf effect", "spots", "spindle", "lesion", "affects the leaf", "leaf blade"],
                "keywords_ta": ["அறிகுறிகள்", "இலை பாதிப்பு", "புள்ளிகள்", "தோற்றம்", "எப்படி தெரியும்", "இலை சேதம்"],
                "answer_en": "Initial symptoms are small bluish-green flecks that rapidly enlarge into spindle-shaped diamond lesions with greyish centres and dark brown margins. Lesions coalesce, killing the leaf blade. In neck blast, the panicle base rots and snaps.",
                "answer_ta": "ஆரம்பத்தில் இலைகளில் நீல-பச்சை நிற சிறிய புள்ளிகள் தோன்றி, பின்னர் சாம்பல் நிற நடுப்பகுதியும் பழுப்பு விளிம்பும் கொண்ட ஈட்டி வடிவப் புள்ளிகளாக மாறும். புள்ளிகள் இணைந்து முழு இலையையும் கருகச் செய்யும். கழுத்து பகுதியில் தாக்கினால் கதிர் ஒடிந்து பதராகிவிடும்."
            },
            "spread": {
                "title_en": "How does Rice Blast spread?",
                "title_ta": "இந்நோய் எவ்வாறு பரவுகிறது?",
                "keywords_en": ["spread", "how does it spread", "transmission", "wind", "rain", "airborne", "contagious", "carrier", "travel"],
                "keywords_ta": ["எப்படி பரவும்", "பரவுதல்", "காற்று", "மழை", "பரவும் விதம்", "பக்கத்து வயல்"],
                "answer_en": "Rice blast spreads primarily via microscopic wind-borne fungal conidia (spores) that travel long distances. Rain splash, infected seed stocks, and weed hosts along irrigation bunds also spread the fungus across neighboring fields.",
                "answer_ta": "குலை நோய் முக்கியமாக காற்றின் மூலம் வெகுதூரம் அடித்துச் செல்லப்படும் பூஞ்சை வித்துக்கள் வழியாக பரவுகிறது. மழைத்துளிகள், பாதிக்கப்பட்ட விதைகள் மற்றும் வரப்புகளில் உள்ள களைகள் மூலமும் அடுத்த வயல்களுக்குப் பரவுகிறது."
            },
            "favourable_weather": {
                "title_en": "Favourable weather and conditions",
                "title_ta": "சாதகமான வானிலை மற்றும் சூழல்",
                "keywords_en": ["weather", "climate", "temperature", "humidity", "rain", "dew", "cloudy", "favourable", "season", "fog"],
                "keywords_ta": ["வானிலை", "பனி", "மழை", "வெப்பநிலை", "ஈரப்பதம்", "சீசன்", "சூழல்"],
                "answer_en": "Cool night temperatures (18–22 °C), prolonged relative humidity above 90%, continuous overcast/cloudy skies, heavy morning dew on leaves for over 10 hours, and excessive nitrogen fertiliser strongly trigger blast epidemics.",
                "answer_ta": "குளிர்ந்த இரவு வெப்பம் (18-22 °C), 90% க்கும் அதிகமான காற்றின் ஈரப்பதம், மேகமூட்டமான வானிலை, இலைகளில் 10 மணி நேரத்திற்கும் மேலாக தங்கும் காலைப் பனித்துளி மற்றும் அதிகப்படியான யூரியா உரம் இந்நோயை தீவிரமாகத் தூண்டுகின்றன."
            },
            "treatment_spray": {
                "title_en": "Medicine and spray treatment",
                "title_ta": "மருந்து மற்றும் தெளிப்பு சிகிச்சை",
                "keywords_en": ["medicine", "spray", "fungicide", "chemical", "treatment", "cure", "control", "what to spray", "pesticide", "remedy"],
                "keywords_ta": ["மருந்து", "தெளிப்பு", "பூஞ்சைக்கொல்லி", "கட்டுப்பாடு", "என்ன தெளிக்க வேண்டும்", "மருந்துகள்", "நிவாரணம்"],
                "answer_en": "Spray TNAU-recommended systemic fungicides such as Tricyclazole 75% WP or Azoxystrobin 18.2% + Difenoconazole 11.4% SC or Carbendazim 50% WP at the first sign of leaf spots. Spray in the early morning or late evening for best absorption.",
                "answer_ta": "இலைகளில் புள்ளிகள் தோன்றிய உடனே வேளாண் அலுவலர் பரிந்துரைத்த ட்ரைசைக்ளசோல் 75% WP அல்லது அசோக்சிஸ்ட்ரோபின் + டைபனகோனசோல் மருந்தை தெளிக்கவும். அதிகாலை அல்லது மாலை வேளையில் தெளிப்பது சிறந்தது."
            },
            "dosage": {
                "title_en": "Recommended dosage",
                "title_ta": "பரிந்துரைக்கப்படும் மருந்தளவு",
                "keywords_en": ["dosage", "dose", "how much", "quantity", "grams", "ml", "per litre", "per acre", "tank", "measurement"],
                "keywords_ta": ["அளவு", "மருந்தளவு", "எவ்வளவு", "ஒரு ஏக்கருக்கு", "டேங்க் அளவு", "கிராம்", "மில்லி"],
                "answer_en": "Standard agricultural guidance suggests Tricyclazole 75% WP at 0.6 g per litre of water (approx 120 g per acre in 200 L water) or Azoxystrobin @ 1 ml per litre. Always confirm exact product concentration with your local TNAU Agriculture Extension Officer.",
                "answer_ta": "பொதுவான வழிகாட்டுதலின்படி ட்ரைசைக்ளசோல் 75% WP லிட்டருக்கு 0.6 கிராம் (ஏக்கருக்கு 120 கிராம் / 200 லிட்டர் தண்ணீர்) அல்லது அசோக்சிஸ்ட்ரோபின் லிட்டருக்கு 1 மி.லி. தெளிக்க வேண்டும். தெளிப்பதற்கு முன் உங்கள் வட்டார வேளாண் அலுவலரிடம் அளவை உறுதிப்படுத்தவும்."
            },
            "prevention": {
                "title_en": "How to prevent it next season?",
                "title_ta": "அடுத்த பருவத்தில் வராமல் தடுப்பது எப்படி?",
                "keywords_en": ["prevention", "prevent", "stop coming back", "next season", "cultural", "seed treatment", "avoid", "protect"],
                "keywords_ta": ["தடுப்பது எப்படி", "வருமுன் காப்போம்", "அடுத்த பருவம்", "விதை நேர்த்தி", "வராமல் தடுக்க", "பாதுகாக்க"],
                "answer_en": "Treat seeds with Pseudomonas fluorescens @ 10 g/kg seed or Trichoderma @ 4 g/kg seed before sowing. Clear weed hosts on bunds, avoid excessive urea, and apply nitrogen in 3–4 split doses based on a Leaf Colour Chart (LCC).",
                "answer_ta": "விதைப்பதற்கு முன் ஒரு கிலோ விதைக்கு 10 கிராம் சூடோமோனாஸ் கொண்டு விதை நேர்த்தி செய்யவும். பாதிக்கப்பட்ட பயிர்க்கழிவுகளை வயலில் விடாமல் அப்புறப்படுத்தவும். LCC அட்டைப்படி தழைச்சத்தை பிரித்து இடவும், பொட்டாஷ் உரத்தை போதிய அளவு இடவும்."
            },
            "harvest_safety": {
                "title_en": "Harvest safety and grain quality",
                "title_ta": "அறுவடை பாதுகாப்பு மற்றும் தானிய தரம்",
                "keywords_en": ["harvest", "waiting period", "grain quality", "eating safety", "safe to eat", "withholding period", "chaffy", "reap"],
                "keywords_ta": ["அறுவடை", "பாதுகாப்பு", "தானிய தரம்", "சாப்பிடலாமா", "பயிர் காப்பு காலம்", "அறுவடை காலம்"],
                "answer_en": "If blast infects panicle necks, grains turn chaffy and yield is lost. Observe a strict 14-day pre-harvest waiting interval (withholding period) after spraying chemical fungicides before reaping paddy for human consumption.",
                "answer_ta": "கதிர் உருவாகும் தருவாயில் கழுத்துக் குலை நோய் தாக்கினால் மணிகள் பதராகி கதிர் ஒடிந்துவிடும். பூஞ்சைக்கொல்லி தெளித்த பிறகு குறைந்தபட்சம் 14 நாட்கள் கழித்தே அறுவடை செய்ய வேண்டும்."
            },
            "severity_meaning": {
                "title_en": "What does my scan severity percentage mean?",
                "title_ta": "எனது பரிசோதனை சேத சதவீதம் என்ன காட்டுகிறது?",
                "keywords_en": ["severity", "percentage", "damage", "grade", "my scan", "lesion area", "what does percentage mean", "moderate", "high", "score"],
                "keywords_ta": ["சேத சதவீதம்", "தீவிரம்", "சேதம்", "கிரேடு", "சதவீதம் என்ன சொல்கிறது", "பாதிப்பு அளவு"],
                "answer_en": "Severity measures lesion surface area relative to total green leaf blade: <1% is Very Low (monitor only), 1–10% is Moderate (start biocontrol or light spray), 10–25% is High (immediate fungicide spray required), and >25% is Severe (urgent canopy intervention needed to stop neck blast).",
                "answer_ta": "சேத சதவீதம் என்பது இலையின் மொத்த பரப்பளவில் நோய்ப் புள்ளிகள் எவ்வளவு பரவியுள்ளது என்பதைக் குறிக்கிறது: 1% கீழ் இருந்தால் மிகக் குறைவு (கண்காணிக்கவும்), 1-10% நடுத்தர பாதிப்பு (உடனடி கவனம் தேவை), 10-25% அதிக பாதிப்பு (உடனே மருந்து தெளிக்கவும்), 25% மேல் இருந்தால் மிகத் தீவிரம்."
            },
            "fertilizer_advice": {
                "title_en": "Fertilizer guidance during blast",
                "title_ta": "குலை நோயின் போது உர மேலாண்மை",
                "keywords_en": ["fertilizer", "urea", "nitrogen", "potash", "manure", "npk", "soil", "feeding", "mop"],
                "keywords_ta": ["உரம்", "யூரியா", "தழைச்சத்து", "பொட்டாஷ்", "சாம்பல் சத்து", "உரங்கள்", "உர மேலாண்மை"],
                "answer_en": "Stop top-dressing urea immediately! Excess plant nitrogen softens cell walls, enabling rapid fungal hyphal penetration. Top-dress 20–25 kg/acre of Muriate of Potash (MOP) to harden epidermis cell walls and improve blast resistance.",
                "answer_ta": "குலை நோய் இருக்கும்போது யூரியா (தழைச்சத்து) இடுவதை உடனடியாக நிறுத்த வேண்டும். அதிகப்படியான யூரியா இலைகளை மென்மையாக்கி பூஞ்சை எளிதில் நுழையச் செய்யும். இலைகளை கடினப்படுத்த ஏக்கருக்கு 15-20 கிலோ பொட்டாஷ் உரம் இடவும்."
            },
            "seed_variety_advice": {
                "title_en": "Blast-resistant rice varieties",
                "title_ta": "குலை நோய் எதிர்ப்பு நெல் ரகங்கள்",
                "keywords_en": ["variety", "resistant", "seeds", "cultivar", "co 51", "adt", "tps", "hybrid", "which seed"],
                "keywords_ta": ["ரகங்கள்", "எதிர்ப்பு ரகம்", "விதை ரகம்", "நெல் ரகம்", "கோ 51", "ஏடிடீ ரகம்"],
                "answer_en": "In blast-prone tracts, sow blast-resistant cultivars recommended by TNAU such as CO 51, TPS 5, ADT 45, or TRY 3. Avoid highly susceptible traditional varieties during cool, foggy samba/thaladi season.",
                "answer_ta": "குலை நோய் அதிகம் தாக்கும் பகுதிகளில் தமிழ்நாடு வேளாண் பல்கலைக்கழகத்தால் பரிந்துரைக்கப்பட்ட CO 51, TPS 5, ADT 45 போன்ற எதிர்ப்புத் திறன் கொண்ட ரகங்களைப் பயிரிடுங்கள்."
            }
        }
    },
    "blb": {
        "name_en": "Bacterial Leaf Blight (BLB)",
        "name_ta": "பாக்டீரியல் இலைக்கருகல் நோய்",
        "topics": {
            "what_is_it": {
                "title_en": "What is Bacterial Leaf Blight?",
                "title_ta": "பாக்டீரியல் இலைக்கருகல் என்றால் என்ன?",
                "keywords_en": ["what is", "explain", "tell me", "blb", "bacterial blight", "kresek", "bacterial leaf blight", "identify"],
                "keywords_ta": ["என்ன நோய்", "இலைக்கருகல்", "பாக்டீரியா நோய்", "விளக்கம்", "கிரெசக்"],
                "answer_en": "Bacterial Leaf Blight (BLB) is a destructive bacterial vascular disease caused by Xanthomonas oryzae. It produces wavy, water-soaked marginal lesions that bleach into straw-white stripes down the leaf blade.",
                "answer_ta": "பாக்டீரியல் இலைக்கருகல் (BLB) என்பது சாந்தோமோனாஸ் ஒரைசே என்ற பாக்டீரியாவால் ஏற்படும் கடுமையான இலை நரம்புப் பாதை நோயாகும். இது இலை ஓரங்களில் அலை அலையான கருகல் கோடுகளை ஏற்படுத்தி இலைகளை உலரச் செய்கிறது."
            },
            "cause": {
                "title_en": "What causes Bacterial Leaf Blight?",
                "title_ta": "இந்நோய்க்கான காரணம் என்ன?",
                "keywords_en": ["cause", "caused by", "bacteria", "fungus or bacteria", "pathogen", "why", "reason", "xanthomonas"],
                "keywords_ta": ["காரணம்", "பாக்டீரியா", "எதனால் வருகிறது", "பூஞ்சையா பாக்டீரியாவா"],
                "answer_en": "Caused by the bacterium Xanthomonas oryzae pv. oryzae. IMPORTANT: This is a bacterial disease, so conventional fungal fungicides are completely ineffective!",
                "answer_ta": "இது சாந்தோமோனாஸ் ஒரைசே பிவி. ஒரைசே என்ற பாக்டீரியாவால் உண்டாகிறது. முக்கிய குறிப்பு: இது பாக்டீரியா நோய் என்பதால் சாதாரண பூஞ்சைக் கொல்லி மருந்துகள் வேலை செய்யாது!"
            },
            "symptoms": {
                "title_en": "Symptoms and leaf damage",
                "title_ta": "அறிகுறிகள் மற்றும் இலை பாதிப்பு",
                "keywords_en": ["symptoms", "signs", "look like", "damage", "wavy margin", "ooze", "yellow stripe", "kresek", "affects the leaf"],
                "keywords_ta": ["அறிகுறிகள்", "இலை பாதிப்பு", "மஞ்சள் கோடு", "கருகல்", "சுருளுதல்", "திரவத் துளி"],
                "answer_en": "Water-soaked green-yellow stripes start from leaf tips and margins, progressing downward with irregular wavy edges. Leaves turn bleached straw-white and curl inward. In early mornings, amber/milky bacterial ooze drops appear on lesions.",
                "answer_ta": "இலை நுனி மற்றும் ஓரங்களில் ஈரப்பதம் கொண்ட கோடுகள் தோன்றி கீழ்நோக்கி அலை அலையாகப் பரவும். பின்னர் சாம்பல்-வெள்ளை நிறமாக காய்ந்துவிடும். அதிகாலையில் இலைகளில் மஞ்சள் நிற பாக்டீரியா திரவத் துளிகள் காணப்படும்."
            },
            "spread": {
                "title_en": "How does BLB spread?",
                "title_ta": "இந்நோய் எவ்வாறு பரவுகிறது?",
                "keywords_en": ["spread", "how does it spread", "water", "flood", "wind", "rain splash", "wounds", "walking in field"],
                "keywords_ta": ["எப்படி பரவும்", "பரவுதல்", "நீர்", "மழை", "காற்று", "வெள்ளம்"],
                "answer_en": "BLB spreads via canal irrigation, storm floodwaters, and wind-driven rain that tears leaf surfaces. Walking or operating sprayers through wet infected crops also spreads the bacterial ooze mechanically from leaf to leaf.",
                "answer_ta": "பாசன நீர், பெருமழை மற்றும் இலைகளில் உராய்வினால் ஏற்படும் சிறு காயங்கள் வழியாக பாக்டீரியா விரைவாகப் பரவுகிறது. ஈரமான பயிர்களில் நடமாடும் போது ஆடைகள் மற்றும் கருவிகள் மூலமும் அடுத்த பயிருக்கு பரவும்."
            },
            "favourable_weather": {
                "title_en": "Favourable weather conditions",
                "title_ta": "சாதகமான வானிலை சூழல்",
                "keywords_en": ["weather", "climate", "temperature", "rain", "humidity", "stagnant water", "typhoon"],
                "keywords_ta": ["வானிலை", "வெப்பம்", "ஈரப்பதம்", "மழைக்காலம்", "தேங்கிய நீர்"],
                "answer_en": "Warm temperatures (25–34 °C), high relative humidity (>80%), heavy monsoon gales that bruise foliage, and stagnant standing water in fields accelerate BLB epidemics.",
                "answer_ta": "25-34 °C வெப்பம், 80% க்கும் அதிகமான ஈரப்பதம், பலத்த காற்றுடன் கூடிய மழை மற்றும் வயலில் நீண்ட நேரம் தேங்கி நிற்கும் நீர் இந்நோய் வேகமாகப் பரவ சாதகமானவை."
            },
            "treatment_spray": {
                "title_en": "Treatment and spray advice",
                "title_ta": "சிகிச்சை மற்றும் தெளிப்பு மருந்துகள்",
                "keywords_en": ["treatment", "spray", "medicine", "bactericide", "cure", "streptomycin", "copper", "cow dung", "control"],
                "keywords_ta": ["மருந்து", "தெளிப்பு", "பாக்டீரியா மருந்து", "சாணக் கரைசல்", "ஸ்ட்ரெப்டோமைசின்", "காப்பர்"],
                "answer_en": "Drain field water immediately! Spray fresh cow dung slurry extract (20%) or TNAU-recommended Streptocycline (Streptomycin sulphate + Tetracycline) combined with Copper Oxychloride per extension officer advisories.",
                "answer_ta": "முதலில் வயலில் தேங்கிய நீரை உடனடியாக வடிக்கவும்! 20% புதிய சாணக் கரைசல் அல்லது வேளாண் அலுவலர் ஆலோசனைப்படி ஸ்ட்ரெப்டோமைசின் சல்பேட் உடன் காப்பர் ஆக்ஸிகுளோரைடு கலந்து தெளிக்கவும்."
            },
            "dosage": {
                "title_en": "Dosage guidelines",
                "title_ta": "மருந்தளவு வழிகாட்டுதல்",
                "keywords_en": ["dosage", "dose", "how much", "quantity", "grams", "ml", "per acre", "ratio"],
                "keywords_ta": ["அளவு", "மருந்தளவு", "எவ்வளவு", "ஏக்கருக்கு", "டேங்க் அளவு"],
                "answer_en": "Standard guidelines specify Streptocycline @ 1.5 g combined with Copper Oxychloride @ 15 g in 10 litres of water (approx 30 g + 300 g per acre in 200 L water). Verify exact formulation with your extension office.",
                "answer_ta": "பொதுவாக 10 லிட்டர் தண்ணீருக்கு ஸ்ட்ரெப்டோசைக்ளின் 1.5 கிராம் மற்றும் காப்பர் ஆக்ஸிகுளோரைடு 15 கிராம் கலந்து தெளிக்க வேண்டும் (ஏக்கருக்கு 30 கிராம் + 300 கிராம் / 200 லிட்டர் நீர்). உள்ளூர் வேளாண் அலுவலரிடம் அளவை உறுதிப்படுத்தவும்."
            },
            "prevention": {
                "title_en": "Prevention and field sanitation",
                "title_ta": "வருமுன் தடுக்கும் முறைகள்",
                "keywords_en": ["prevention", "prevent", "drain", "sanitation", "clean", "next season", "avoid"],
                "keywords_ta": ["தடுப்பது எப்படி", "வருமுன் காப்போம்", "நீர் வடிகால்", "சுத்தம்", "அடுத்த பருவம்"],
                "answer_en": "Ensure proper field drainage to prevent prolonged submergence. Avoid clipping seedling tips when transplanting. Treat seeds with Pseudomonas fluorescens @ 10 g/kg seed before nursery sowing.",
                "answer_ta": "வயலில் நீர் தேங்காமல் நல்ல வடிகால் வசதி செய்ய வேண்டும். நாற்று நடும்போது இலை நுனிகளை கிள்ளுவதைத் தவிர்க்கவும். விதைக்கும் முன் சூடோமோனாஸ் கொண்டு விதை நேர்த்தி செய்யவும்."
            },
            "harvest_safety": {
                "title_en": "Harvest safety and grain filling",
                "title_ta": "அறுவடை பாதுகாப்பு",
                "keywords_en": ["harvest", "waiting period", "eating safety", "grain", "chaffy grains"],
                "keywords_ta": ["அறுவடை", "பாதுகாப்பு", "தானியங்கள்", "பயிர் காப்பு காலம்"],
                "answer_en": "BLB bleaches flag leaves and starves grain filling. If copper sprays were applied, observe a mandatory 10–14 day pre-harvest waiting interval before harvesting crop.",
                "answer_ta": "இலைக்கருகல் நோய் கொடி இலையை உலர வைப்பதால் தானியங்கள் பதராகும் அபாயம் உண்டு. காப்பர் அல்லது பாக்டீரியா மருந்து தெளித்த பின் 10-14 நாட்கள் கழித்தே அறுவடை செய்ய வேண்டும்."
            },
            "severity_meaning": {
                "title_en": "Severity interpretation",
                "title_ta": "சேத சதவீத விளக்கம்",
                "keywords_en": ["severity", "percentage", "damage", "lesion", "grade", "my scan", "meaning"],
                "keywords_ta": ["சேத சதவீதம்", "தீவிரம்", "கிரேடு", "பாதிப்பு அளவு"],
                "answer_en": "Severity represents the percentage of leaf area blighted: <1% is Very Low, 1–10% is Moderate (drain standing water immediately), 10–25% is High (bactericide/cow dung spray required), and >25% is Severe (risk of widespread canopy loss).",
                "answer_ta": "சேத சதவீதம் இலைப்பரப்பில் கருகல் எவ்வளவு தூரம் பரவியுள்ளது என்பதைக் குறிக்கும்: 1% கீழ் மிகக் குறைவு, 1-10% நடுத்தரம் (உடனே நீரை வடிக்கவும்), 10-25% அதிகம் (பாக்டீரியா மருந்து தெளிக்கவும்), 25% மேல் மிகத் தீவிரம்."
            },
            "fertilizer_advice": {
                "title_en": "Fertilizer advice for BLB",
                "title_ta": "இலைக்கருகலின் போது உர மேலாண்மை",
                "keywords_en": ["fertilizer", "urea", "nitrogen", "potash", "manure", "potassium", "mop"],
                "keywords_ta": ["உரம்", "யூரியா", "தழைச்சத்து", "பொட்டாஷ்", "சாம்பல் சத்து"],
                "answer_en": "Halt all urea applications immediately! Top-dress additional Potassium (MOP @ 20–25 kg/acre) which strengthens cell wall lignification and inhibits bacterial colonization.",
                "answer_ta": "யூரியா உரத்தை முழுமையாக நிறுத்தவும்! ஏக்கருக்கு 20-25 கிலோ பொட்டாஷ் (சாம்பல் சத்து) இடவும். பொட்டாஷ் தண்டு மற்றும் இலை நரம்புகளை உறுதியாக்கி பாக்டீரியா பரவுவதை தடுக்கும்."
            },
            "seed_variety_advice": {
                "title_en": "BLB-tolerant varieties",
                "title_ta": "இலைக்கருகல் எதிர்ப்பு நெல் ரகங்கள்",
                "keywords_en": ["variety", "resistant", "tolerant", "cultivars", "improved samba mahsuri", "co 51"],
                "keywords_ta": ["ரகங்கள்", "எதிர்ப்பு ரகம்", "நெல் ரகம்", "சாம்பா மசூரி", "கோ 51"],
                "answer_en": "Plant resistant or gene-pyramided cultivars such as Improved Samba Mahsuri (RP Bio-226), TNAU Rice CO 51, or ADT 43 that carry specific Xa-resistance genes.",
                "answer_ta": "இம்பிரூவ்டு சாம்பா மசூரி, TNAU கோ 51 அல்லது ஏடிடீ 43 போன்ற பாக்டீரியல் இலைக்கருகலை எதிர்க்கும் எதிர்ப்புத் திறன் கொண்ட ரகங்களைப் பயிரிடவும்."
            }
        }
    },
    "brown_spot": {
        "name_en": "Brown Spot",
        "name_ta": "பழுப்பு புள்ளி நோய்",
        "topics": {
            "what_is_it": {
                "title_en": "What is Brown Spot?",
                "title_ta": "பழுப்பு புள்ளி நோய் என்றால் என்ன?",
                "keywords_en": ["what is", "explain", "brown spot", "sesame spot", "bipolaris", "meaning"],
                "keywords_ta": ["என்ன நோய்", "பழுப்பு புள்ளி", "எள் புள்ளி", "விளக்கம்", "புள்ளி நோய்"],
                "answer_en": "Brown Spot is a common foliar fungal disease that creates circular to oval sesame-seed-like dark brown spots on paddy leaves, sheaths, and glumes.",
                "answer_ta": "பழுப்பு புள்ளி நோய் என்பது நெற்பயிரின் இலை மற்றும் உமிப் பகுதியில் எள் போன்ற சிறிய வட்ட வடிவ பழுப்பு நிறப் புள்ளிகளை உண்டாக்கும் ஒரு பூஞ்சை நோயாகும்."
            },
            "cause": {
                "title_en": "What causes Brown Spot?",
                "title_ta": "இந்நோய்க்கான காரணம் என்ன?",
                "keywords_en": ["cause", "caused by", "fungus", "nutrient deficiency", "bipolaris oryzae", "why"],
                "keywords_ta": ["காரணம்", "பூஞ்சை", "சத்து குறைபாடு", "எதனால்", "ஏன் வருகிறது"],
                "answer_en": "Caused by the fungus Bipolaris oryzae. It is globally recognized as a disease of nutrient-starved, sandy, or drought-stressed soils lacking Potassium (K), Silicon (Si), or Zinc (Zn).",
                "answer_ta": "இது பைபோலாரிஸ் ஒரைசே என்ற பூஞ்சையால் உண்டாகிறது. மண்ணில் போதிய சத்துக்கள் இல்லாமலோ அல்லது வறட்சியினாலோ பயிர் பலவீனமடையும் போது இந்நோய் எளிதில் தாக்குகிறது."
            },
            "symptoms": {
                "title_en": "Symptoms on leaves and grains",
                "title_ta": "இலை மற்றும் தானிய அறிகுறிகள்",
                "keywords_en": ["symptoms", "signs", "look like", "spots", "sesame", "yellow halo", "pecky rice", "damage"],
                "keywords_ta": ["அறிகுறிகள்", "புள்ளிகள்", "எள் போன்ற", "மஞ்சள் வளையம்", "தானிய புள்ளிகள்", "கருமை"],
                "answer_en": "Leaves show numerous round to oval brown spots with grey centres and distinct yellow halos. When glumes are attacked, grains become dark-spotted and discolored (\"pecky rice\").",
                "answer_ta": "இலைகளில் வட்ட/நீள்வட்ட பழுப்பு புள்ளிகள் தோன்றும்; புள்ளியின் நடுவில் சாம்பல் நிறமும் சுற்றிலும் தெளிவான மஞ்சள் வளையமும் இருக்கும். தானியங்களில் கருமை புள்ளிகளை உண்டாக்கும்."
            },
            "spread": {
                "title_en": "How does Brown Spot spread?",
                "title_ta": "இந்நோய் எவ்வாறு பரவுகிறது?",
                "keywords_en": ["spread", "transmission", "spores", "wind", "seed borne", "airborne"],
                "keywords_ta": ["எப்படி பரவும்", "பரவுதல்", "விதைகள்", "காற்று", "வித்துக்கள்"],
                "answer_en": "The pathogen is seed-borne and wind-borne. Spores produced on unmanaged crop debris, weed hosts, and infected seed stocks germinate and reinfect young tillers.",
                "answer_ta": "இது விதை மற்றும் காற்றின் மூலம் பரவக்கூடியது. பயிர்க்கழிவுகளில் இருந்து காற்றில் மிதந்து வரும் வித்துக்கள் மூலமும், பாதிக்கப்பட்ட விதைகளை விதைப்பதன் மூலமும் பரவுகிறது."
            },
            "favourable_weather": {
                "title_en": "Favourable weather and soil",
                "title_ta": "சாதகமான வானிலை மற்றும் மண்",
                "keywords_en": ["weather", "climate", "sandy soil", "potassium deficiency", "drought", "humidity"],
                "keywords_ta": ["வானிலை", "வறட்சி", "மணல் மண்", "சத்து குறைபாடு", "ஈரப்பதம்"],
                "answer_en": "High humidity (85–100%), temperatures of 25–30 °C, sandy nutrient-depleted soil, moisture stress, and deficiencies of potassium and silicon accelerate outbreaks.",
                "answer_ta": "85-100% ஈரப்பதம், 25-30 °C வெப்பநிலை, ஊட்டச்சத்து குறைபாடுள்ள மணல் பாங்கான மண், வறட்சி மற்றும் பொட்டாசியம் சத்து குறைபாடு ஆகியவை இந்நோயை அதிகப்படுத்துகின்றன."
            },
            "treatment_spray": {
                "title_en": "Spray treatment and remedies",
                "title_ta": "தெளிப்பு மருந்துகள் மற்றும் தீர்வுகள்",
                "keywords_en": ["treatment", "spray", "medicine", "mancozeb", "propiconazole", "cure", "control"],
                "keywords_ta": ["மருந்து", "தெளிப்பு", "மேன்கோசெப்", "புரோபிகோனசோல்", "பூஞ்சைக்கொல்லி"],
                "answer_en": "Spray Mancozeb 75% WP or Propiconazole 25% EC or Carbendazim + Mancozeb at early boot leaf stage when spots begin to coalesce.",
                "answer_ta": "இலைகளில் புள்ளிகள் அதிகரிக்கும் போது மேன்கோசெப் 75% WP அல்லது புரோபிகோனசோல் 25% EC பூஞ்சைக் கொல்லி மருந்தை தெளிக்கவும்."
            },
            "dosage": {
                "title_en": "Dosage guidelines",
                "title_ta": "பரிந்துரைக்கப்படும் மருந்தளவு",
                "keywords_en": ["dosage", "dose", "how much", "quantity", "grams", "per acre", "tank"],
                "keywords_ta": ["அளவு", "மருந்தளவு", "எவ்வளவு", "ஏக்கருக்கு", "டேங்க் அளவு"],
                "answer_en": "Mancozeb @ 2 g/L (400 g/acre) or Propiconazole @ 1 ml/L (200 ml/acre) mixed in 200 L water. Verify product directions with your local agriculture officer.",
                "answer_ta": "மேன்கோசெப் லிட்டருக்கு 2 கிராம் (ஏக்கருக்கு 400 கிராம் / 200 லிட்டர் நீர்) அல்லது புரோபிகோனசோல் லிட்டருக்கு 1 மி.லி. தெளிக்கவும். உள்ளூர் வேளாண் அலுவலரிடம் அளவை உறுதிப்படுத்தவும்."
            },
            "prevention": {
                "title_en": "How to prevent Brown Spot?",
                "title_ta": "தடுக்கும் முறைகள்",
                "keywords_en": ["prevention", "prevent", "seed treatment", "soil test", "potash", "next season"],
                "keywords_ta": ["தடுப்பது எப்படி", "வருமுன் காப்போம்", "விதை நேர்த்தி", "மண் பரிசோதனை", "அடுத்த பருவம்"],
                "answer_en": "Treat seeds with Carbendazim @ 2 g/kg or Pseudomonas @ 10 g/kg seed before planting. Conduct a soil test and amend sandy soil with farmyard manure and adequate potassium.",
                "answer_ta": "ஒரு கிலோ விதைக்கு கார்பென்டாசிம் 2 கிராம் அல்லது சூடோமோனாஸ் 10 கிராம் கொண்டு விதை நேர்த்தி செய்யவும். மண் பரிசோதனை செய்து சரியான அளவில் மக்கிய உரம் மற்றும் பொட்டாஷ் இடவும்."
            },
            "harvest_safety": {
                "title_en": "Harvest safety and grain value",
                "title_ta": "அறுவடை பாதுகாப்பு",
                "keywords_en": ["harvest", "grain quality", "market price", "milling", "broken grains"],
                "keywords_ta": ["அறுவடை", "தானிய தரம்", "விலை", "அரிசி உடைதல்"],
                "answer_en": "Brown spot causes grain discolouration and rice breakage during milling. Ensure a 14-day pre-harvest waiting interval after any fungicide application before reaping.",
                "answer_ta": "பழுப்பு புள்ளி நோய் தானியங்களில் கரும்புள்ளிகளை உண்டாக்கி அரைக்கும் போது அரிசி உடைந்து சந்தை விலையைக் குறைக்கும். மருந்து தெளித்த பின் 14 நாட்கள் கழித்து அறுவடை செய்யவும்."
            },
            "severity_meaning": {
                "title_en": "Understanding your scan severity",
                "title_ta": "சேத சதவீத விளக்கம்",
                "keywords_en": ["severity", "percentage", "damage", "my scan", "grade", "score"],
                "keywords_ta": ["சேத சதவீதம்", "தீவிரம்", "கிரேடு", "பாதிப்பு"],
                "answer_en": "Severity tracks the proportion of leaf area covered in lesions: <1% is Very Low, 1–10% is Moderate (foliar potassium recommended), 10–25% is High (fungicide spray required), and >25% is Severe (risk of early canopy drying).",
                "answer_ta": "சேத சதவீதம் இலைப்பரப்பில் புள்ளிகளின் அடர்த்தியைக் குறிக்கிறது: 1% கீழ் மிகக் குறைவு, 1-10% நடுத்தரம் (பொட்டாசியம்/நுண்ணூட்டம் தெளிக்கவும்), 10-25% அதிகம் (பூஞ்சை மருந்து தெளிக்கவும்), 25% மேல் மிகத் தீவிரம்."
            },
            "fertilizer_advice": {
                "title_en": "Nutrient and fertilizer management",
                "title_ta": "உர மேலாண்மை",
                "keywords_en": ["fertilizer", "potash", "zinc", "urea", "silicon", "kcl"],
                "keywords_ta": ["உரம்", "பொட்டாஷ்", "துத்தநாகம்", "நுண்ணூட்டம்", "சாம்பல் சத்து"],
                "answer_en": "Apply balanced NPK with adequate Potash. A foliar spray of 1% Potassium Chloride (KCl) or micronutrient mixture during active tillering strengthens leaf resistance.",
                "answer_ta": "சமச்சீர் NPK உரமிட வேண்டும். குறிப்பாக போதிய பொட்டாஷ் உரமிடவும். 1% பொட்டாசியம் குளோரைடு கரைசல் இலைவழியாகத் தெளிப்பது இலைகளின் நோய் எதிர்ப்பை உடனடியாக அதிகரிக்கும்."
            },
            "seed_variety_advice": {
                "title_en": "Tolerant varieties",
                "title_ta": "தாங்கி வளரும் நெல் ரகங்கள்",
                "keywords_en": ["variety", "tolerant", "seeds", "resistant", "adt 36", "co 52"],
                "keywords_ta": ["ரகங்கள்", "எதிர்ப்பு ரகம்", "விதை ரகம்", "ஏடிடீ"],
                "answer_en": "Cultivate tolerant varieties recommended by TNAU such as ADT 36, ADT 44, or CO 52. Always use certified, disease-free seed.",
                "answer_ta": "ADT 36, ADT 44 அல்லது CO 52 போன்ற தாங்கி வளரக்கூடிய சான்றளிக்கப்பட்ட விதை ரகங்களைப் பயன்படுத்தவும்."
            }
        }
    },
    "healthy": {
        "name_en": "Healthy Paddy Leaf",
        "name_ta": "ஆரோக்கியமான நெற்பயிர் இலை",
        "topics": {
            "what_is_it": {
                "title_en": "What does a Healthy result mean?",
                "title_ta": "ஆரோக்கியமான முடிவு என்ன குறிக்கிறது?",
                "keywords_en": ["what is", "healthy", "result", "status", "good leaf", "clean", "meaning"],
                "keywords_ta": ["ஆரோக்கியம்", "முடிவு", "நல்ல பயிர்", "விளக்கம்", "ஆரோக்கியமான இலை"],
                "answer_en": "Great news! Your scanned paddy leaf is clean, vibrant green, and free from detectable signs of fungal, bacterial, or viral disease.",
                "answer_ta": "மகிழ்ச்சியான செய்தி! உங்கள் நெல் இலை சீரான பசுமையுடன், எவ்வித பூஞ்சை, பாக்டீரியா அல்லது வைரஸ் நோய் அறிகுறிகளும் இன்றி ஆரோக்கியமாக உள்ளது."
            },
            "cause": {
                "title_en": "Why is my crop healthy?",
                "title_ta": "பயிர் ஆரோக்கியமாக இருக்க காரணம் என்ன?",
                "keywords_en": ["why healthy", "cause", "reason", "good health", "how"],
                "keywords_ta": ["காரணம்", "நல்ல வளர்ச்சி", "ஏன் ஆரோக்கியம்"],
                "answer_en": "Proper nutrition, sound water management, clean seed quality, and favourable microclimate have protected your canopy from pathogen infestation.",
                "answer_ta": "சமச்சீரான உரமிடுதல், முறையான நீர்ப்பாசனம் மற்றும் நல்ல விதை நேர்த்தி ஆகியவை உங்கள் பயிரை நோய்களின்றி ஆரோக்கியமாக வைத்துள்ளன."
            },
            "symptoms": {
                "title_en": "Healthy leaf appearance",
                "title_ta": "ஆரோக்கியமான இலையின் தோற்றம்",
                "keywords_en": ["look like", "appearance", "green leaf", "characteristics", "symptoms"],
                "keywords_ta": ["தோற்றம்", "பச்சை இலை", "அறிகுறிகள்", "எப்படி இருக்கும்"],
                "answer_en": "Uniform vibrant green coloration, intact uncurled margins, clean leaf collars, and complete absence of brown, yellow, or bleached spots.",
                "answer_ta": "சீரான அடர் பச்சை நிறம், கருகல் இல்லாத சுத்தமான இலை ஓரங்கள் மற்றும் புள்ளிகள் இல்லாத மிருதுவான இலைப்பரப்பு."
            },
            "spread": {
                "title_en": "Can healthy crops catch disease?",
                "title_ta": "ஆரோக்கியமான பயிருக்கு நோய் பரவ வாய்ப்புண்டா?",
                "keywords_en": ["spread", "catch disease", "risk", "vulnerable", "neighbour", "danger"],
                "keywords_ta": ["நோய் வருமா", "அடுத்த வயல்", "பாதுகாப்பு", "ஆபத்து"],
                "answer_en": "Yes, airborne spores or irrigation runoff from adjacent diseased fields can spread pathogens during warm, humid, or overcast weather. Routine monitoring is recommended.",
                "answer_ta": "ஆம், பக்கத்து வயல்களில் நோய் இருந்தால் காற்று மற்றும் பாசன நீர் வழியே பரவ வாய்ப்புள்ளது. தொடர்ந்து வயலை கண்காணித்து வரவும்."
            },
            "favourable_weather": {
                "title_en": "Weather risks to watch out for",
                "title_ta": "கவனிக்க வேண்டிய வானிலை மாற்றங்கள்",
                "keywords_en": ["weather", "risk", "rain", "humidity", "cloudy", "threat"],
                "keywords_ta": ["வானிலை", "மழை", "பனி", "எச்சரிக்கை", "மேகமூட்டம்"],
                "answer_en": "Watch closely during extended cloudy periods, high humidity (>90%), and heavy morning dews, which create favourable conditions for blast or blight spores to germinate.",
                "answer_ta": "தொடர் மேகமூட்டம், அதிகப்படியான பனித்துளி மற்றும் மழைக்காலங்களில் நோய் பரவ வாய்ப்புள்ளதால் அப்போது கூடுதல் கவனம் தேவை."
            },
            "treatment_spray": {
                "title_en": "Should I spray any chemicals now?",
                "title_ta": "இப்போது ஏதேனும் மருந்து தெளிக்க வேண்டுமா?",
                "keywords_en": ["spray", "chemical", "medicine", "need to spray", "precautionary spray", "pesticide"],
                "keywords_ta": ["மருந்து தெளிக்கவா", "தெளிப்பு தேவையா", "இப்போது மருந்து", "மருந்து அடிக்கலாமா"],
                "answer_en": "No chemical fungicide or bactericide sprays are needed! Avoiding unnecessary chemical sprays preserves beneficial predator spiders and mirid bugs in your paddy field.",
                "answer_ta": "எந்தவொரு ரசாயன பூச்சிக்கொல்லியோ அல்லது பூஞ்சைக்கொல்லியோ இப்போது தெளிக்க வேண்டிய அவசியமில்லை! நன்மை செய்யும் பூச்சிகளைப் பாதுகாக்க தேவையற்ற தெளிப்பைத் தவிர்க்கவும்."
            },
            "dosage": {
                "title_en": "Dosage for preventive bio-inputs",
                "title_ta": "இயற்கை பாதுகாப்பு மருந்தளவு",
                "keywords_en": ["dosage", "bio inputs", "neem oil", "pseudomonas", "panchagavya", "quantity"],
                "keywords_ta": ["அளவு", "இயற்கை உரம்", "பஞ்சகவ்யா", "சூடோமோனாஸ்", "மருந்தளவு"],
                "answer_en": "If using preventive bio-inputs, apply Pseudomonas fluorescens foliar spray @ 2 g/L or 3% Panchagavya spray to reinforce foliar plant immunity.",
                "answer_ta": "முன்னெச்சரிக்கையாக பயிர் நோய் எதிர்ப்பாற்றலை அதிகரிக்க லிட்டருக்கு 2 கிராம் சூடோமோனாஸ் அல்லது 3% பஞ்சகவ்யா தெளிக்கலாம்."
            },
            "prevention": {
                "title_en": "How to keep it healthy?",
                "title_ta": "தொடர்ந்து ஆரோக்கியமாக பராமரிப்பது எப்படி?",
                "keywords_en": ["keep healthy", "maintain", "protection", "care", "tips", "how to protect"],
                "keywords_ta": ["பராமரிப்பு", "தொடர்ந்து ஆரோக்கியமாக", "குறிப்புகள்", "பாதுகாப்பது எப்படி"],
                "answer_en": "Practice Alternate Wetting and Drying (AWD) water management, keep bunds weed-free, and apply urea in 3–4 split doses matched to the Leaf Colour Chart (LCC).",
                "answer_ta": "காய்ச்சலும் பாய்ச்சலுமாக நீர்ப்பாசனம் செய்யவும், வரப்புகளில் உள்ள களைகளை சுத்தமாக வைக்கவும், மற்றும் LCC அட்டைப்படி தழைச்சத்தைப் பிரித்து இடவும்."
            },
            "harvest_safety": {
                "title_en": "Expected grain harvest",
                "title_ta": "எதிர்பார்க்கப்படும் மகசூல் தரம்",
                "keywords_en": ["harvest", "yield", "grain filling", "panicle", "crop output"],
                "keywords_ta": ["மகசூல்", "அறுவடை", "தானிய எடை", "விளைச்சல்"],
                "answer_en": "Healthy leaves ensure maximum photosynthetic energy is channeled to developing panicles, supporting high thousand-grain weight and superior milling quality.",
                "answer_ta": "ஆரோக்கியமான இலைகள் ஒளிச்சேர்க்கையை முழுமையாக மேற்கொண்டு மணிகள் நன்கு திரளவும், அதிக மகசூல் கிடைக்கவும் வழிவகுக்கும்."
            },
            "severity_meaning": {
                "title_en": "Severity score explanation",
                "title_ta": "சேத சதவீத விளக்கம்",
                "keywords_en": ["severity", "percentage", "zero", "score", "my scan", "damage"],
                "keywords_ta": ["சேத சதவீதம்", "பூஜ்ஜியம்", "மதிப்பெண்", "கிரேடு"],
                "answer_en": "Your scan shows approximately 0% lesion severity, confirming an intact, healthy leaf blade free of necrotic lesions.",
                "answer_ta": "உங்கள் பரிசோதனை 0% சேதத்தைக் காட்டுகிறது, இது இலை முழுமையாக நலமாக இருப்பதை உறுதிசெய்கிறது."
            },
            "fertilizer_advice": {
                "title_en": "Fertilizer schedule for healthy paddy",
                "title_ta": "ஆரோக்கியமான பயிருக்கான உர அட்டவணை",
                "keywords_en": ["fertilizer", "urea", "schedule", "potash", "zinc", "top dressing", "npk"],
                "keywords_ta": ["உர அட்டவணை", "உரம்", "யூரியா", "பொட்டாஷ்", "நுண்ணூட்டம்", "மேலுரம்"],
                "answer_en": "Follow the standard schedule: 25% basal N, 50% active tillering N, and 25% panicle initiation N, with balanced phosphorus and potash. Use LCC to prevent over-fertilizing with urea.",
                "answer_ta": "தழைச்சத்தை 3-4 தவணைகளாகப் பிரித்து இடவும் (அடி உரம், தூர் கட்டும் பருவம், கதிர் உருவாகும் பருவம்). யூரியா உரத்தை அளவுக்கு அதிகமாக இடாமல் LCC அட்டைப்படி இடவும்."
            },
            "seed_variety_advice": {
                "title_en": "When to scan next?",
                "title_ta": "அடுத்த பரிசோதனை எப்போது?",
                "keywords_en": ["when to scan", "next scan", "monitoring", "routine", "schedule", "interval"],
                "keywords_ta": ["அடுத்த பரிசோதனை", "எப்போது பரிசோதிக்க வேண்டும்", "கண்காணிப்பு", "அடுத்த ஸ்கேன்"],
                "answer_en": "Scan random leaves once every 7 to 10 days, particularly during active tillering and panicle emergence, or immediately after stormy monsoon rains.",
                "answer_ta": "7 முதல் 10 நாட்களுக்கு ஒருமுறை வயலில் உள்ள இலைகளை பரிசோதிக்கவும். குறிப்பாக தூர் கட்டும் போதும், கதிர் வரும் தருணத்திலும் அல்லது மழைக்கு பிறகும் கண்காணிப்பது நல்லது."
            }
        }
    },
    "other": {
        "name_en": "Other Foliar Stress / Disorders",
        "name_ta": "இதர இலை பாதிப்புகள் / கோளாறுகள்",
        "topics": {
            "what_is_it": {
                "title_en": "What is the \"Other\" classification?",
                "title_ta": "\"இதர\" வகைப்பாடு என்றால் என்ன?",
                "keywords_en": ["what is", "other", "unclassified", "meaning", "disorder", "unknown"],
                "keywords_ta": ["இதர", "விளக்கம்", "மற்ற நோய்கள்", "என்ன நோய்"],
                "answer_en": "The model detected foliar abnormalities different from standard Blast, BLB, or Brown Spot. This encompasses Tungro Virus, Leaf Scald, Narrow Brown Spot, Sheath Blight, or physiological nutrient deficiencies.",
                "answer_ta": "குலை நோய், இலைக்கருகல் அல்லது பழுப்பு புள்ளி அல்லாத பிற பாதிப்புகளை மாதிரி கண்டறிந்துள்ளது. இதில் துங்க்ரோ வைரஸ், இலை கருகல், உறை கருகல் அல்லது ஊட்டச்சத்து குறைபாடுகள் அடங்கும்."
            },
            "cause": {
                "title_en": "Possible causes of this symptom",
                "title_ta": "சாத்தியமான காரணங்கள்",
                "keywords_en": ["cause", "caused by", "tungro", "leaf scald", "virus", "nutrient deficiency", "reason"],
                "keywords_ta": ["காரணம்", "வைரஸ்", "சத்து குறைபாடு", "பூச்சி", "எதனால்"],
                "answer_en": "Potential causes include: (1) Tungro Virus transmitted by green leafhopper vectors, (2) Leaf Scald fungus, (3) Sheath Rot, or (4) Micronutrient deficiencies such as Zinc deficiency (Khaira) or Nitrogen chlorosis.",
                "answer_ta": "சாத்தியமான காரணங்கள்: (1) பச்சை தத்துப்பூச்சிகளால் பரவும் துங்க்ரோ வைரஸ், (2) இலை பிளத்தல் பூஞ்சை, அல்லது (3) துத்தநாகம், தழைச்சத்து போன்ற ஊட்டச்சத்து குறைபாடுகள்."
            },
            "symptoms": {
                "title_en": "How to identify specific symptoms",
                "title_ta": "குறிப்பிட்ட அறிகுறிகளை அடையாளம் காண்பது எப்படி?",
                "keywords_en": ["symptoms", "tungro symptoms", "leaf scald", "zinc", "yellowing", "bronzing"],
                "keywords_ta": ["அறிகுறிகள்", "துங்க்ரோ", "மஞ்சள் இலை", "துத்தநாக குறைபாடு", "துரு"],
                "answer_en": "Tungro causes bright orange-yellow discoloration from leaf tips with stunted tillers. Leaf Scald produces chevron-banded lesions. Zinc deficiency causes rusty bronzing patches across leaf blades.",
                "answer_ta": "துங்க்ரோவில் இலை நுனி முதல் மஞ்சள்-ஆரஞ்சு நிறமாக மாறி பயிர் குட்டையாகும். இலை பிளத்தலில் அலை அலையான திட்டுகள் தோன்றும். துத்தநாக குறைபாட்டில் துரு போன்ற பழுப்பு நிற புள்ளிகள் தோன்றும்."
            },
            "spread": {
                "title_en": "How do these disorders spread?",
                "title_ta": "எவ்வாறு பரவுகிறது?",
                "keywords_en": ["spread", "leafhopper", "vector", "insects", "soil", "transmission"],
                "keywords_ta": ["எப்படி பரவும்", "தத்துப்பூச்சி", "பூச்சிகள்", "மண்", "பரவுதல்"],
                "answer_en": "Viral diseases spread via insect vectors (Green Leafhopper). Fungal scald spreads through rain splashes. Physiological nutrient deficiencies do not spread and are tied to soil chemistry.",
                "answer_ta": "துங்க்ரோ வைரஸ் பச்சை தத்துப்பூச்சிகள் மூலம் பரவுகிறது. பிற பூஞ்சை நோய்கள் மழை நீர் மூலம் பரவும். ஊட்டச்சத்து குறைபாடுகள் பரவாது, அவை மண்ணின் தன்மையை சார்ந்தது."
            },
            "favourable_weather": {
                "title_en": "Favourable weather and soil triggers",
                "title_ta": "சாதகமான வானிலை மற்றும் மண் சூழல்",
                "keywords_en": ["weather", "vector population", "high ph", "soil condition", "climate"],
                "keywords_ta": ["வானிலை", "மண் தன்மை", "பூச்சி தாக்குதல்", "வெப்பம்"],
                "answer_en": "Humid overcast weather increases green leafhopper populations. Calcareous, alkaline, or poorly drained soils trigger severe zinc and iron micro-nutrient deficiencies.",
                "answer_ta": "மேகமூட்டமான வானிலை தத்துப்பூச்சிகளின் பெருக்கத்திற்கு சாதகமானது. காரத்தன்மை கொண்ட சுண்ணாம்பு மண் துத்தநாக சத்து குறைபாட்டை உண்டாக்கும்."
            },
            "treatment_spray": {
                "title_en": "Treatment and corrective actions",
                "title_ta": "சிகிச்சை மற்றும் தீர்வுகள்",
                "keywords_en": ["treatment", "spray", "medicine", "zinc sulphate", "insecticide", "cure", "control"],
                "keywords_ta": ["மருந்து", "தெளிப்பு", "துத்தநாக சல்பேட்", "பூச்சிக்கொல்லி", "கட்டுப்பாடு"],
                "answer_en": "For suspected Tungro: manage green leafhoppers with recommended insecticide. For Zinc deficiency: spray 0.5% Zinc Sulphate + 1% Urea. For fungal scald: spray Carbendazim + Mancozeb.",
                "answer_ta": "துங்க்ரோவாக இருந்தால்: பச்சை தத்துப்பூச்சியைக் கட்டுப்படுத்த பரிந்துரைக்கப்பட்ட பூச்சிக்கொல்லி தெளிக்கவும். துத்தநாக குறைபாட்டிற்கு: 0.5% ஜிங்க் சல்பேட் + 1% யூரியா இலைவழியாக தெளிக்கவும்."
            },
            "dosage": {
                "title_en": "Dosage guidelines",
                "title_ta": "பரிந்துரைக்கப்படும் மருந்தளவு",
                "keywords_en": ["dosage", "dose", "how much", "quantity", "grams", "zinc dose", "per acre"],
                "keywords_ta": ["அளவு", "மருந்தளவு", "எவ்வளவு", "கிராம்", "ஏக்கருக்கு"],
                "answer_en": "For Zinc foliar correction: dissolve 5 g Zinc Sulphate + 10 g Urea per litre of water (1 kg + 2 kg per acre in 200 L water). For insect vectors, consult your local agriculture officer for certified dosages.",
                "answer_ta": "துத்தநாக தெளிப்பிற்கு: ஒரு லிட்டர் தண்ணீருக்கு 5 கிராம் ஜிங்க் சல்பேட் + 10 கிராம் யூரியா கலந்து தெளிக்கவும். பூச்சிக் கட்டுப்பாட்டு மருந்துகளுக்கு உள்ளூர் வேளாண் அலுவலரை அணுகவும்."
            },
            "prevention": {
                "title_en": "Prevention measures",
                "title_ta": "தடுக்கும் வழிமுறைகள்",
                "keywords_en": ["prevention", "prevent", "vector management", "basal zinc", "next season"],
                "keywords_ta": ["தடுப்பது எப்படி", "வருமுன் காப்போம்", "ஜிங்க் இடல்", "அடுத்த பருவம்"],
                "answer_en": "Apply basal Zinc Sulphate @ 10 kg/acre at final puddling. Use light traps to monitor leafhopper buildup and keep field bunds clear of weed reservoirs.",
                "answer_ta": "கடைசி உழவின் போது ஏக்கருக்கு 10 கிலோ ஜிங்க் சல்பேட் இடவும். விளக்குப் பொறி வைத்து தத்துப்பூச்சிகளைக் கண்காணிக்கவும். வரப்புகளை சுத்தமாக பராமரிக்கவும்."
            },
            "harvest_safety": {
                "title_en": "Harvest and yield precautions",
                "title_ta": "அறுவடை பாதுகாப்பு",
                "keywords_en": ["harvest", "yield loss", "safety interval", "waiting period"],
                "keywords_ta": ["அறுவடை", "மகசூல் இழப்பு", "பயிர் காப்பு காலம்"],
                "answer_en": "Uncorrected virus or nutrient disorders cause severe stunting and empty spikelets. Adhere to a 14–21 day waiting interval after spraying any chemical before harvesting.",
                "answer_ta": "வைரஸ் அல்லது சத்து குறைபாடுகளை உடனே சரிசெய்யாவிட்டால் பயிர் வளர்ச்சி குன்றி மகசூல் குறையும். மருந்து தெளித்த பின் போதிய இடைவெளி விட்டு அறுவடை செய்யவும்."
            },
            "severity_meaning": {
                "title_en": "Severity interpretation for other disorders",
                "title_ta": "சேத சதவீத விளக்கம்",
                "keywords_en": ["severity", "percentage", "damage", "lesion", "grade", "my scan"],
                "keywords_ta": ["சேத சதவீதம்", "தீவிரம்", "கிரேடு", "பாதிப்பு"],
                "answer_en": "Severity indicates the percentage of foliar discoloration, bronzing, or blighting across the scanned blade. High values warrant on-site inspection by an agricultural extension specialist.",
                "answer_ta": "சேத சதவீதம் இலையில் பசுமை இழந்த பகுதியின் அளவைக் காட்டுகிறது. சதவீதம் அதிகமாக இருந்தால் வேளாண் அலுவலரிடம் நேரில் ஆலோசனை பெறுவது நல்லது."
            },
            "fertilizer_advice": {
                "title_en": "Nutrient correction advice",
                "title_ta": "ஊட்டச்சத்து திருத்த வழிகாட்டுதல்",
                "keywords_en": ["fertilizer", "zinc", "micronutrient", "manure", "urea", "correction"],
                "keywords_ta": ["உரம்", "நுண்ணூட்டம்", "ஜிங்க் சல்பேட்", "மக்கிய உரம்", "சத்து"],
                "answer_en": "Do not apply excessive urea if viral yellowing is suspected. Apply organic compost and foliar micronutrient mixtures to revive balanced nutrient uptake.",
                "answer_ta": "மஞ்சள் நிறம் தென்பட்டால் உடனே யூரியாவை கொட்ட வேண்டாம். மக்கிய தொழு உரம் மற்றும் நுண்ணூட்டச் சத்துக்களை வழங்கி வேர்களின் சத்து உறிஞ்சும் திறனை அதிகரிக்கவும்."
            },
            "seed_variety_advice": {
                "title_en": "Resistant varieties",
                "title_ta": "எதிர்ப்பு ரகங்கள்",
                "keywords_en": ["variety", "resistant", "tungro resistant", "adt 45", "co 47", "seeds"],
                "keywords_ta": ["ரகங்கள்", "எதிர்ப்பு ரகம்", "துங்க்ரோ எதிர்ப்பு", "நெல் ரகம்"],
                "answer_en": "Cultivate vector-resistant varieties like IR 20, ADT 45, or CO 47 in regions prone to seasonal green leafhopper and Tungro outbreaks.",
                "answer_ta": "துங்க்ரோ அதிகம் தாக்கும் பகுதிகளில் IR 20, ADT 45 அல்லது CO 47 போன்ற தத்துப்பூச்சி மற்றும் வைரஸ் எதிர்ப்பு ரகங்களைப் பயிரிடவும்."
            }
        }
    }
}

out_path = Path(__file__).resolve().parent.parent / "app" / "data" / "qa_knowledge.json"
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(qa_data, f, indent=2, ensure_ascii=False)

print(f"Generated {out_path} with {len(qa_data)-1} disease classes and all 12 topics.")
