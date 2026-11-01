# -*- coding: utf-8 -*-
"""
build_phase2_disease_info.py
Injects structured symptoms, checklist, and 3-stage prevention fields
in English, Tamil, and Tanglish for the first 10 paddy diseases.
Strictly complies with safety rules:
  - Zero brand names
  - Zero dosage numbers (mg, ml, g/l, kg/ha)
  - Zero prices
  - All Tamil and Tanglish marked '[Needs expert review]'
"""

import json
from pathlib import Path

DATA_FILE = Path(r"C:\Users\keert\paddy_dataset\app\data\disease_info.json")

with open(DATA_FILE, "r", encoding="utf-8") as f:
    db = json.load(f)

PHASE2_DATA = {
    "brown_spot": {
        "name_tanglish": "Brown Spot (Pazhuppu Pulli Noi)",
        "symptoms_summary_en": "Small circular to oval sesame seed-shaped dark brown spots with grey centres and yellow halos.\nSevere spots merge, causing leaves to dry up and grains to become spotted.",
        "symptoms_summary_ta": "இலைகளில் எள் போன்ற உருண்டை அல்லது நீள்வட்டப் பழுப்புப் புள்ளிகள் சாம்பல் மையத்துடன் தோன்றும்.\nதீவிர பாதிப்பில் இலைகள் காய்ந்து சருகாவதுடன் நெல் மணிகளும் கரும்புள்ளிகளுடன் பதராகும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "symptoms_summary_tanglish": "Ilaila sesame seed (ellu) maathiri oval shape-la dark brown pulligal saambal center-oda varum.\nAthiga pulligal onna sernthu ilai karugi kaanjidum, nel maniyum karuppagi padhar aagum.\n[Needs expert review]",

        "symptoms_leaf_en": [
            "1. Initial appearance: Tiny, dark brown to purple-brown circular specks appear on leaf blades.",
            "2. Mature lesion: Spots enlarge into oval or circular sesame seed shapes with light brown to greyish centres.",
            "3. Characteristic halo: A distinct bright yellow chlorotic ring (halo) surrounds each mature lesion.",
            "4. Blighting stage: In severe cases, multiple lesions coalesce, causing extensive yellowing and drying of the leaf blade."
        ],
        "symptoms_leaf_ta": [
            "1. ஆரம்ப நிலை: இலைப்பரப்பில் சிறிய, அடர் பழுப்பு அல்லது ஊதா-பழுப்பு நிறப் புள்ளிகள் தோன்றும்.",
            "2. முதிர்ந்த புள்ளி: புள்ளிகள் எள் வடிவில் நீள்வட்டமாக மாறி நடுப்பகுதி சாம்பல் நிறமாகும்.",
            "3. மஞ்சள் வளையம்: ஒவ்வொரு முதிர்ந்த புள்ளியைச் சுற்றிலும் தெளிவான மஞ்சள் நிற வளையம் காணப்படும்.",
            "4. கருகல் நிலை: தீவிர நிலையில் புள்ளிகள் ஒன்றிணைந்து இலை முழுவதும் காய்ந்து சருகாகும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]"
        ],
        "symptoms_leaf_tanglish": [
            "1. Aaramba nilai: Ilaila chinna dark brown/purple-brown speckles thondrum.",
            "2. Valarntha pulli: Pulligal ellu maathiri oval shape-la saambal nira nadupaguthi yodu maarum.",
            "3. Yellow halo: Ovvoru pulliyai suthilum nalla bright yellow halo ring thondrum.",
            "4. Karugal nilai: Athiga pulligal onna sernthu ilai muzhuvathum kaanju pogum.\n[Needs expert review]"
        ],

        "symptoms_other_parts_en": "• Leaf sheaths: develop brown oblong lesions causing premature death of sheath.\n• Grain glumes: dark brown to black spots cover hulls, causing kernel shriveling and poor germination.",
        "symptoms_other_parts_ta": "• இலை உறை: பழுப்பு நிறப் புள்ளிகள் தோன்றி உறை அழுகும்.\n• நெல் மணிகள்: உமியின் மேல் கரும்பழுப்பு நிறப் புள்ளிகள் தோன்றி தானியங்கள் சுருங்கி முளைப்புத் திறன் குறையும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "symptoms_other_parts_tanglish": "• Ilai urai: Brown oblong pulligal thondri urai kaanjidum.\n• Nel mani: Nel umimeethu karuppu pulligal vanthu mani shrivel aagi germination korayum.\n[Needs expert review]",

        "how_to_check_en": [
            "Are the spots oval or circular shaped like sesame seeds?",
            "Is the centre of the spot grey or light brown with a dark margin?",
            "Do you see a distinct yellow halo around the spots?",
            "Are older bottom leaves affected first in nutrient-deficient patches?"
        ],
        "how_to_check_ta": [
            "புள்ளிகள் எள் வடிவில் உருண்டையாக அல்லது நீள்வட்டமாக உள்ளதா?",
            "புள்ளியின் மையப்பகுதி சாம்பல் நிறமாகவும் விளிம்பு அடர் பழுப்பாகவும் உள்ளதா?",
            "புள்ளியைச் சுற்றி மஞ்சள் நிற வளையம் தெரிகிறதா?",
            "சத்து குறைந்த இடங்களில் கீழ் இலைகளில் முதலில் பாதிப்பு தெரிகிறதா?\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]"
        ],
        "how_to_check_tanglish": [
            "Pulligal ellu maathiri oval shape-la irukka?",
            "Pulliyoda nadu paguthi saambal niramavum border dark brown-avum irukka?",
            "Pulliya suthi nalla yellow ring theriyutha?",
            "Satthu kuraivaana edathula adi ilaigal muthalil paathikkapattullatha?\n[Needs expert review]"
        ],

        "how_it_spreads_en": "• Primary infection carries over through infected seeds and volunteer rice stubble from previous harvests.\n• Airborne fungal conidia spread secondary infection across canopies through wind currents and rain splashes.\n• Nutrient-poor sandy soils and water drought stress accelerate infection rate.",
        "how_it_spreads_ta": "• முந்தைய பருவத்தின் பாதிக்கப்பட்ட விதைகள் மற்றும் பயிர்க் கழிவுகள் மூலம் முதன்மையாகத் தொடங்குகிறது.\n• காற்றில் அடித்துச் செல்லப்படும் பூஞ்சை வித்துக்கள் மற்றும் மழைத்துளிகள் மூலம் பக்கத்துப் பயிர்களுக்குப் பரவுகிறது.\n• சத்து குறைந்த நிலங்கள் மற்றும் வறட்சி இந்நோய் பரவுவதை விரைவுபடுத்துகிறது.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "how_it_spreads_tanglish": "• Paathikkapatta vidhaigal mattrum palaiya thaalgal moolama aarambikkirathu.\n• Kaathula vara spores mattrum mazhai thuligal moolama adutha payirukku vegama paravum.\n• Chathu kuraivaana mannilum varatchi soozhnilaiyilum noi vegama paravum.\n[Needs expert review]",

        "favourable_conditions_en": "• Temperatures of 25°C to 30°C with high relative humidity exceeding 85%.\n• Continuous heavy morning dew and overcast skies keeping leaves wet for prolonged hours.\n• Potassium and silicon deficient soils, acidic soils, or plants under drought stress.",
        "favourable_conditions_ta": "• 25°C முதல் 30°C வெப்பநிலை மற்றும் 85%க்கும் அதிகமான காற்றில் ஈரப்பதம்.\n• காலையில் நீடிக்கும் பனிப்பொழிவு மற்றும் தொடர் மேகமூட்டத்தால் இலைகள் நனைந்து இருத்தல்.\n• பொட்டாஷ் சத்து பற்றாக்குறை, களர் நிலங்கள் அல்லது பயிரில் வறட்சி நிலை.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "favourable_conditions_tanglish": "• 25°C - 30°C veppanilai mattrum 85%-kku mela athiga eerappatham.\n• Kaalaila neelikkum pani thuligalum thodar megamootamum ilaiyai nanaithu vaithirunthaal.\n• Potash satthu kuraipaadu, kalar nilam illa thanni kidaikkaatha varatchi.\n[Needs expert review]",

        "prevention_before_planting_en": "• Always perform certified seed treatment according to the current TNAU crop production guide.\n• Correct soil nutrient deficiencies by applying recommended organic manure, potash, and zinc sulfate based on soil test results.\n• Plough the field deeply during summer to expose fungal inoculum to sunlight.",
        "prevention_before_planting_ta": "• TNAU பயிர் உற்பத்தி வழிகாட்டியின்படி சான்றளிக்கப்பட்ட விதை நேர்த்தி முறையை தவறாமல் பின்பற்றவும்.\n• மண் பரிசோதனை பரிந்துரைப்படி தொழு உரம், சாம்பல் சத்து மற்றும் துத்தநாக உரங்களை இடவும்.\n• பூஞ்சை வித்துக்கள் அழிய கோடை உழவு செய்து மண்ணை சூரிய ஒளியில் காய விடவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_before_planting_tanglish": "• TNAU guideline padi certified vidhai nerthi (seed treatment) kandippa seiyavum.\n• Mann test padi thozhu uram, potash mattrum zinc urangalai sariyaana alavil idavum.\n• Poonjai azhiya kodai uzhavu panni nilathai nalla veyilil kaaya vaikkavum.\n[Needs expert review]",

        "prevention_during_crop_en": "• Avoid excessive single doses of chemical nitrogen; apply split doses with balanced potassium.\n• Ensure regular, uninterrupted irrigation during tillering and flowering; avoid drought cracks in the field.\n• Keep bunds and irrigation channels clean from collateral grassy weeds.",
        "prevention_during_crop_ta": "• யூரியாவை ஒரே முறையில் அதிகமாக இடாமல், சாம்பல் சத்துடன் சேர்த்து பிரித்து இடவும்.\n• தூர் கட்டும் மற்றும் பூக்கும் தருணத்தில் நிலத்தில் விரிசல் விழாமல் சீரான நீர்ப்பாசனம் செய்யவும்.\n• வரப்புகளிலும் வாய்க்கால்களிலும் உள்ள களைப் புற்களை அகற்றி சுத்தமாக வைக்கவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_during_crop_tanglish": "• Urea-va ore aadiyaaga athigamaaga podama potash-oda sernthu split panni podavum.\n• Thoor kattum mattrum pookkum nerathil vayal kaayama seerana thanni maintain seiyavum.\n• Varappula ulla pull kalaigalai azhithu clean-ah vechikonga.\n[Needs expert review]",

        "prevention_after_harvest_en": "• Remove and compost or burn infected crop stubble and straw to destroy surviving fungal sclerotia.\n• Practice crop rotation with non-host crops like pulses or green manure crops.\n• Do not use seeds harvested from heavily infected plots for the next season's sowing.",
        "prevention_after_harvest_ta": "• பாதிக்கப்பட்ட பயிர்க் கழிவுகளையும் வைக்கோலையும் வயலிலிருந்து அகற்றி பூஞ்சை வித்துக்களை அழிக்கவும்.\n• பயறு வகை அல்லது பசுந்தாள் உரப் பயிர்களுடன் பயிர் சுழற்சி செய்யவும்.\n• தீவிரமாக பாதிக்கப்பட்ட நிலத்தில் இருந்து அறுவடை செய்யப்பட்ட விதைகளை அடுத்த பருவத்திற்கு பயன்படுத்த வேண்டாம்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_after_harvest_tanglish": "• Paathikkapatta thaalgalaiyum payir saavalaigalaiyum agatri poonjaiyai azhithuvidavum.\n• Payaru illa pasunthaal uram payirgaludan crop rotation seiyavum.\n• Romba paathikkapatta vayal vidhaigalai adutha paruvathukku use panna koodadhu.\n[Needs expert review]",

        "prevention_to_limit_spread_en": "• Stop further nitrogen top-dressing immediately.\n• Apply soil-recommended potassium and ensure thin standing water across the field.\n• Consult your local agriculture officer for certified bio-control or TNAU-recommended management measures.",
        "prevention_to_limit_spread_ta": "• கூடுதல் யூரியா இடுவதை உடனடியாக நிறுத்தவும்.\n• பரிந்துரைக்கப்பட்ட சாம்பல் சத்தை இட்டு வயலில் சீரான மெல்லிய நீர் மட்டத்தை பராமரிக்கவும்.\n• தற்போதைய TNAU வழிகாட்டுதலின்படி சான்றளிக்கப்பட்ட கட்டுப்பாட்டு நடவடிக்கைகளுக்கு வேளாண் அலுவலரை அணுகவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_to_limit_spread_tanglish": "• Thodarnthu urea nitrogen poduvathai udane stop pannunga.\n• Thevaiyana potash uram pottu vayalla seerana thanni maintain pannunga.\n• TNAU recommend panna sariyaana aalosanai peruvatharku agriculture officer-ah sandhikavum.\n[Needs expert review]",

        "when_to_call_officer_en": "• Call your Assistant Agriculture Officer (AAO) if lesions spread over more than 20% of your crop canopy.\n• If grain spotting or panicle discolouration appears during head emergence.\n• Bring fresh symptomatic leaf samples in a clean plastic bag for on-site visual confirmation.",
        "when_to_call_officer_ta": "• வயலில் 20%க்கும் அதிகமான பரப்பளவில் புள்ளிகள் பரவினால் உடனடியாக வேளாண் அலுவலரைத் தொடர்பு கொள்ளவும்.\n• கதிர் வரும் தருணத்தில் தானியங்களில் கரும்புள்ளிகள் தோன்றினால் தகவல் தெரிவிக்கவும்.\n• பாதிக்கப்பட்ட புதிய இலைகளை ஒரு பையில் எடுத்துச் சென்று அலுவலரிடம் ஆய்வு பெறவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "when_to_call_officer_tanglish": "• Vayalil 20%-kku mela pulligal paravina udane Agriculture Officer (AAO)-ah contact pannunga.\n• Kathir varum pothu nel manigalil karuppu pulligal vanthaal therivikkavum.\n• Paathikkapatta fresh leaf sample-ah cover-la eduthutu poi officer-kitta kaattunga.\n[Needs expert review]",

        "similar_looking_problems_en": "• Rice Blast: lesions are diamond or spindle shaped with pointed ends and grey centres, not oval sesame shapes.\n• Narrow Brown Leaf Spot: forms linear, narrow reddish-brown streaks parallel to veins without round margins.\n• Potassium Deficiency: presents as yellowing and crispy brown scorching starting along mature outer leaf margins.",
        "similar_looking_problems_ta": "• குலை நோய்: கூர்மையான முனைகளுடன் ஈட்டி வடிவப் புள்ளிகளாகவும் சாம்பல் மையத்துடனும் தோன்றும்.\n• குறுகிய பழுப்பு புள்ளி நோய்: நரம்புகளுக்கு இணையாக நீண்ட மெல்லிய சிவந்த பழுப்பு கோடுகளாகக் காணப்படும்.\n• பொட்டாஷ் சத்து பற்றாக்குறை: இலையின் விளிம்புகளில் தீய்ந்தது போன்ற பழுப்பு கருகல் தோன்றும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "similar_looking_problems_tanglish": "• Rice Blast: Spindle diamond shape-la pointed ends-oda varum; oval ellu shape irukkadhu.\n• Narrow Brown Leaf Spot: Narambukalukku inaiyaga neelamaana narrow streaks mattum thondrum.\n• Potash deficiency: Ilai orathula theeyintha maathiri scorched brown karugal thondrum.\n[Needs expert review]"
    },

    "blast": {
        "name_tanglish": "Rice Blast (Kulai Noi)",
        "symptoms_summary_en": "Diamond or spindle-shaped lesions with pointed ends, ash-grey centres, and dark brown margins.\nAttacks leaf collars, stem nodes, and panicle necks, causing severe neck breakage and empty chaffy grains.",
        "symptoms_summary_ta": "இலைகளில் கூர்மையான முனைகளுடன் சாம்பல் நிற மையமும் பழுப்பு விளிம்பும் கொண்ட ஈட்டி வடிவப் புள்ளிகள் தோன்றும்.\nஇலைக் கழுத்து, தண்டு கணுக்கள் மற்றும் கதிர் கழுத்துப் பகுதியைத் தாக்கி கதிர் முறிந்து பதராகும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "symptoms_summary_tanglish": "Ilaila spindle diamond shape-la saambal nira nadupaguthiyum dark brown border-um ulla pulligal varum.\nIlai collar, thandu kanu mattrum kathir kazhutha thaakki kathir odinju 100% padhar aagum.\n[Needs expert review]",

        "symptoms_leaf_en": [
            "1. Initial stage: Small, water-soaked bluish-green specks appear on leaf blades.",
            "2. Spindle lesion development: Specks rapidly expand into diamond or spindle-shaped spots with pointed ends.",
            "3. Characteristic centre: Centre turns ash-grey or whitish surrounded by a dark brown or reddish-brown border.",
            "4. Severe coalescing: Spots fuse together, drying large sections of the leaf and giving the field a burnt appearance."
        ],
        "symptoms_leaf_ta": [
            "1. ஆரம்ப நிலை: இலைகளில் சிறிய, நீர் ஊறிய நீலப்பச்சை நிறப் புள்ளிகள் தோன்றும்.",
            "2. ஈட்டி வடிவ வளர்ச்சி: புள்ளிகள் கூர்மையான முனைகளைக் கொண்ட ஈட்டி அல்லது வைர வடிவமாக விரியும்.",
            "3. சாம்பல் நிற மையம்: மையப்பகுதி சாம்பல் அல்லது வெண்மையாகவும், விளிம்பு அடர் பழுப்பாகவும் மாறும்.",
            "4. தீவிர நிலை: புள்ளிகள் ஒன்றிணைந்து இலை காய்ந்து வயல் தீப்பற்றி எரிந்தது போல் காட்சியளிக்கும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]"
        ],
        "symptoms_leaf_tanglish": [
            "1. Aaramba nilai: Ilaila chinna blue-green neer ooriya flecks thondrum.",
            "2. Spindle valarchi: Pulligal spindle diamond shape-la koormaiyana munaigalaaga viriyum.",
            "3. Saambal center: Nadu paguthi saambal vellaiyagavum suthi dark brown border-um varum.",
            "4. Theevira nilai: Pulligal onna sernthu ilai karugi vayal theepatri erinthathu pol maarum.\n[Needs expert review]"
        ],

        "symptoms_other_parts_en": "• Collar blast: brown rot at the junction of leaf blade and sheath, causing the entire blade to die.\n• Node blast: stem nodes turn black, rot, and snap under light pressure.\n• Neck blast: panicle neck turns blackish-brown and rots, resulting in 100% sterile chaffy ears.",
        "symptoms_other_parts_ta": "• இலைக் கழுத்து குலை: இலை மற்றும் உறையின் இணைப்பு அழுகி இலை முழுதும் காயும்.\n• கணு குலை: தண்டு கணுக்கள் கறுத்து அழுகி எளிதில் முறியும்.\n• கதிர் குலை: கதிர் கழுத்துக் காம்பு கறுத்து அழுகி கதிர் முறிந்து மணிகள் பதராகும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "symptoms_other_parts_tanglish": "• Collar blast: Ilai inaiyum idathil brown rot vanthu ilai kaanjidum.\n• Node blast: Thandu kanukkal karuppagi azhugi seekiram odinjidum.\n• Neck blast: Kathir kazhuthu karuppagi odinju 100% padhar aagum.\n[Needs expert review]",

        "how_to_check_en": [
            "Do the leaf lesions look like pointed diamonds or spindles with tapering ends?",
            "Is the centre of the lesion ash-grey or whitish in colour?",
            "Are there dark rotten patches at leaf collars or stem nodes?",
            "Has the neck of the panicle turned dark brown and snapped over?"
        ],
        "how_to_check_ta": [
            "இலைப் புள்ளிகள் கூர்மையான முனைகளுடன் ஈட்டி அல்லது வைர வடிவில் உள்ளதா?",
            "புள்ளியின் மையப்பகுதி சாம்பல் அல்லது வெண்மை நிறத்தில் உள்ளதா?",
            "இலைக் கழுத்துப் பகுதியிலோ தண்டு கணுக்களிலோ கறுத்த அழுகல் உள்ளதா?",
            "கதிர் காம்பு கறுத்து அழுகி முறிந்து தொங்குகிறதா?\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]"
        ],
        "how_to_check_tanglish": [
            "Leaf spots spindle diamond shape-la pointed ends-oda irukka?",
            "Spot-oda nadu paguthi saambal illa whitish colour-la irukka?",
            "Ilai collar-layo illa thandu kanu-layo karuppu azhugal irukka?",
            "Kathir kazhuthu karuppagi odinju thongutha?\n[Needs expert review]"
        ],

        "how_it_spreads_en": "• Airborne fungal conidia are produced abundantly during cool humid nights and carried by wind.\n• Rain splashes and standing flood water rapidly disperse spores across nearby leaves and hills.\n• Lush, soft plant tissue from high nitrogen fertilization allows rapid spore germination and penetration.",
        "how_it_spreads_ta": "• குளிர்ந்த இரவுகளில் உற்பத்தியாகும் பூஞ்சை வித்துக்கள் காற்றில் வெகுதூரம் அடித்துச் செல்லப்பட்டு பரவுகிறது.\n• மழைத்துளிகள் மற்றும் பாசன நீர் மூலம் பக்கத்துப் பயிர்களுக்கு வேகமாகப் பரவும்.\n• அதிக யூரியா இடுவதால் மென்மையாகும் இலைத்திசுக்களில் பூஞ்சை மிக எளிதில் ஊடுருவுகிறது.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "how_it_spreads_tanglish": "• Kulirntha iravil urpathiyagum spores kaathula romba thooram paravum.\n• Mazhai thuligal mattrum thanni paasanam moolama adutha chedikku vegama paravum.\n• Athiga urea-val soft aagum ilaila poonjai vegama nuzhaiyum.\n[Needs expert review]",

        "favourable_conditions_en": "• Cool night temperatures (18°C to 22°C) combined with relative humidity above 90%.\n• Continuous leaf wetness for 10 hours or more from heavy morning dew or intermittent cloudy weather.\n• Excess chemical nitrogen application and closely spaced planting preventing airflow.",
        "favourable_conditions_ta": "• குளிர்ந்த இரவு நேரம் (18°C - 22°C) மற்றும் 90%க்கும் அதிகமான காற்றில் ஈரப்பதம்.\n• பனிப்பொழிவு மற்றும் மேகமூட்டத்தால் இலைகளில் 10 மணி நேரத்திற்கு மேல் பனித்துளி தேங்கி நிற்றல்.\n• அளவுக்கு அதிகமான யூரியா பயன்பாடு மற்றும் நெருக்கமான நடவு.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "favourable_conditions_tanglish": "• Kulirntha iravu (18°C - 22°C) mattrum 90% mela athiga eerappatham.\n• 10 manineram mela ilaila pani thanni thangi irunthaalum thodar megamootam irunthaalum.\n• Athiga urea nitrogen mattrum romba nerukkamaana nadavu.\n[Needs expert review]",

        "prevention_before_planting_en": "• Select certified blast-resistant or tolerant varieties recommended by TNAU for your region.\n• Treat seeds with biocontrol agents or certified seed dressing methods before raising nursery.\n• Maintain optimal spacing during transplanting to ensure adequate canopy aeration.",
        "prevention_before_planting_ta": "• உங்கள் பகுதிக்கு ஏற்ற TNAU பரிந்துரைத்த குலை நோய் எதிர்ப்பு நெல் ரகங்களைத் தேர்ந்தெடுக்கவும்.\n• நாற்று நடுவதற்கு முன் பரிந்துரைக்கப்பட்ட விதை நேர்த்தி முறையை தவறாமல் செய்யவும்.\n• பயிர்களுக்கு இடையே நல்ல காற்றோட்டம் கிடைக்க சரியான இடைவெளியில் நடவு செய்யவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_before_planting_tanglish": "• Unga paguthikku etha TNAU blast ethirppu ragangalai choose pannunga.\n• Naatru naduvatharku munnadi certified vidhai nerthi kandippa seiyavum.\n• Kaathottam kidaikka sariyaana idai veliyil nadavu seiyavum.\n[Needs expert review]",

        "prevention_during_crop_en": "• Apply nitrogen fertilizer in 3 to 4 split applications guided by the Leaf Colour Chart (LCC).\n• Immediately halt nitrogen top-dressing upon noticing initial spindle leaf lesions.\n• Maintain a shallow water layer in the field; do not let the soil dry out into cracking drought.",
        "prevention_during_crop_ta": "• இலை வண்ண அட்டை (LCC) வழிகாட்டல்படி தழைச்சத்தை 3 முதல் 4 தவணைகளாகப் பிரித்து இடவும்.\n• ஆரம்ப இலைப் புள்ளிகள் தென்பட்டவுடன் யூரியா இடுவதை உடனடியாக நிறுத்தவும்.\n• நிலத்தில் மெல்லிய நீர் மட்டத்தை பராமரிக்கவும்; வயல் முற்றிலும் காய்ந்து போக விடக்கூடாது.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_during_crop_tanglish": "• LCC card paarthu urea-va 3-4 thavanaiyaaga split panni podavum.\n• Aaramba spindle spots therintha udane urea poduvathai stop pannunga.\n• Vayal kaaya vidama thin water layer maintain pannunga.\n[Needs expert review]",

        "prevention_after_harvest_en": "• Burn or thoroughly compost infected straw and stubble to eliminate resting fungal mycelium.\n• Clear field bunds of wild grassy weeds that act as collateral hosts for the fungus.\n• Avoid using paddy seeds from severely infected fields for upcoming nursery establishment.",
        "prevention_after_harvest_ta": "• பூஞ்சை வித்துக்களை அழிக்க பாதிக்கப்பட்ட பயிர்க் கழிவுகளையும் வைக்கோலையும் அகற்றவும்.\n• வரப்புகளில் உள்ள காட்டுப் புற்களை அகற்றி வயல் பரப்பைச் சுத்தமாக வைக்கவும்.\n• இந்நோய் தாக்கிய நிலத்திலிருந்து பெறப்பட்ட விதைகளை அடுத்த சாகுபடிக்கு பயன்படுத்தக் கூடாது.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_after_harvest_tanglish": "• Poonjai spores azhiya paathikkapatta thaalgalai azhithuvidavum.\n• Varappula ulla kaatu pull kalaigalai azhithu clean-ah vechikonga.\n• Noi thonriya vayalilirunthu edutha vidhaigalai adutha nadavukku use panna koodadhu.\n[Needs expert review]",

        "prevention_to_limit_spread_en": "• Stop nitrogen top-dressing immediately.\n• Avoid evening overhead irrigation that prolongs leaf canopy wetness through the night.\n• Consult your Assistant Agriculture Officer immediately for certified TNAU-recommended treatments before neck emergence.",
        "prevention_to_limit_spread_ta": "• யூரியா மேலுரமிடுவதை உடனடியாக நிறுத்தவும்.\n• இரவு நேரத்தில் இலை ஈரமாக இருப்பதைத் தவிர்க்க மாலை நேரத் தெளிப்பைத் தவிர்க்கவும்.\n• கதிர் வெளிவரும் முன் TNAU பரிந்துரைத்த பாதுகாப்பு நடவடிக்கைக்கு உடனே வேளாண் அலுவலரை அணுகவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_to_limit_spread_tanglish": "• Urea poduratha udane stop pannunga.\n• Iravil ilai eeramaga irukkum pothu maalai neram thanni thelippathai thavirkkavum.\n• Kathir varuvatharku munnadi TNAU advice pera udane agriculture officer-ah sandhikavum.\n[Needs expert review]",

        "when_to_call_officer_en": "• Contact your Agriculture Officer immediately if spindle spots appear on upper flag leaves.\n• If neck blast symptoms are observed on emerging heads across your field.\n• Follow official extension guidelines rather than unverified commercial recommendations.",
        "when_to_call_officer_ta": "• கொடி இலையில் ஈட்டி வடிவப் புள்ளிகள் தோன்றினால் உடனே வேளாண் அலுவலரை அணுகவும்.\n• கதிர் வெளிவரும் போது கழுத்து அழுகல் தென்பட்டால் உடனடியாகத் தகவல் தெரிவிக்கவும்.\n• அதிகாரப்பூர்வமான வேளாண் விரிவாக்க பரிந்துரைகளை மட்டுமே பின்பற்றவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "when_to_call_officer_tanglish": "• Kodi ilaila spindle spots vantha udane agriculture officer-ah contact pannunga.\n• Kathir varum pothu neck blast symptoms therinthaal officer kitta sollavum.\n• Unverified marundhugal vangama official TNAU advice kelunga.\n[Needs expert review]",

        "similar_looking_problems_en": "• Brown Spot: spots are circular or oval like sesame seeds, lacking pointed diamond ends.\n• Sheath Rot: attacks the flag leaf sheath surrounding the panicle with oblong greyish rot.\n• Bacterial Leaf Blight: presents as yellow wavy blighting along leaf edges, not isolated spindle lesions.",
        "similar_looking_problems_ta": "• பழுப்பு புள்ளி நோய்: எள் போன்ற உருண்டை அல்லது நீள்வட்டப் புள்ளிகளாக இருக்கும்; கூர்மையான முனைகள் இருக்காது.\n• உறை அழுகல்: கொடி இலை உறையில் நீண்ட சாம்பல் நிற அழுகலை ஏற்படுத்தும்.\n• பாக்டீரியா இலைக்கருகல்: இலை விளிம்புகளில் அலை போன்ற மஞ்சள் கருகலை ஏற்படுத்தும்; தனித்தனிப் புள்ளிகளாக இருக்காது.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "similar_looking_problems_tanglish": "• Brown Spot: Oval ellu shape-la irukkum; blast maathiri pointed diamond ends irukkadhu.\n• Sheath Rot: Kodi ilai uraiyai thakkum oblong saambal azhugal.\n• BLB: Ilai orathula alaialaiya yellow karugal varum; isolated spots irukkadhu.\n[Needs expert review]"
    },

    "blb": {
        "name_tanglish": "Bacterial Leaf Blight (BLB / Karugal Noi)",
        "symptoms_summary_en": "Water-soaked stripes starting near leaf tips and margins, developing into wavy straw-yellow borders and bleached white blight.\nSystemic early infection causes rapid seedling wilting and death known as kresek.",
        "symptoms_summary_ta": "இலை நுனி மற்றும் ஓரங்களில் நீர் ஊறிய கோடுகள் தொடங்கி அலை அலையான மஞ்சள் விளிம்புடன் வெளிறிய கருகலாக மாறும்.\nஆரம்ப நாற்றுப் பருவத்தில் தாக்கும் போது பயிர் திடீரென வாடி கருகும் கிரேசக் நிலை ஏற்படும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "symptoms_summary_tanglish": "Ilai nuni mattrum orathula neer ooriya streaks thodangi alai alaiyana yellow border-oda karugi bleached white aagum.\nAaramba naatru paruvathil kresek vaadal thondri payir thideerena saagum.\n[Needs expert review]",

        "symptoms_leaf_en": [
            "1. Initial symptom: Water-soaked translucent lesions appear near the leaf tips or edges.",
            "2. Wavy border expansion: Lesions expand downward along margins with a distinctive undulating, wavy border.",
            "3. Colour progression: Infected areas turn greenish-yellow, straw-yellow, and eventually bleached grayish-white.",
            "4. Bacterial exudate: Small milky or amber-colored bacterial droplets ooze on leaf surfaces in early morning dew."
        ],
        "symptoms_leaf_ta": [
            "1. ஆரம்ப நிலை: இலை நுனி அல்லது ஓரங்களில் நீர் ஊறிய மெல்லிய கோடுகள் தோன்றும்.",
            "2. அலை போன்ற விளிம்பு: கருகல் அலை அலையான ஓரங்களுடன் கீழ்நோக்கி வேகமாகப் பரவும்.",
            "3. நிற மாற்றம்: பாதிக்கப்பட்ட பகுதி பச்சை-மஞ்சளாக மாறி பின்னர் வெளிறிய வைக்கோல் நிறமாக மாறும்.",
            "4. பாக்டீரியா கசிவு: அதிகாலையில் பனி இருக்கும் போது இலையின் மேல் பால் போன்ற சிறு கசிவுத் துளிகள் தென்படும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]"
        ],
        "symptoms_leaf_tanglish": [
            "1. Aaramba nilai: Ilai nuni illa orathula neer ooriya streaks thondrum.",
            "2. Wavy border: Karugal alai alaiyana border-oda keezh நோக்கி vegama paravum.",
            "3. Nira maatram: Yellow niramagi piragu straw-yellow bleached white aagum.",
            "4. Bacterial ooze: Kaalaila pani irukkum pothu ilai mela paal maathiri droplets kasivum.\n[Needs expert review]"
        ],

        "symptoms_other_parts_en": "• Seedlings: systemic kresek wilt causes tillers to rapidly wither, roll up, and collapse within 1 to 3 weeks.\n• Panicles: glumes on emerging heads can become blighted, resulting in sterile chaffy grains.",
        "symptoms_other_parts_ta": "• நாற்றுகள்: கிரேசக் வாடல் ஏற்பட்டு முழு தூர்களும் வாடி சுருண்டு சில நாட்களில் மடியும்.\n• கதிர் மணிகள்: கதிர் உமியில் கருகல் தோன்றி மணிகள் பதராகும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "symptoms_other_parts_tanglish": "• Naatru: Kresek vaadal thondri thoorgal thideerena vaadi churiya vidum.\n• Kathir: Kathir umimeethu karugal vanthu mani padhar aagum.\n[Needs expert review]",

        "how_to_check_en": [
            "Do leaf lesions begin at the margins near the tip and progress downward?",
            "Is the advancing margin of the yellow lesion wavy and undulating?",
            "Do infected leaves turn dry, bleached straw-white like paper?",
            "Are there amber or milky bacterial droplets visible on wet leaves in the early morning?"
        ],
        "how_to_check_ta": [
            "கருகல் இலை நுனி அல்லது ஓரங்களில் ஆரம்பித்து கீழ்நோக்கி பரவுகிறதா?",
            "மஞ்சள் கருகலின் விளிம்பு அலை அலையாக உள்ளதா?",
            "பாதிக்கப்பட்ட இலைகள் காகிதம் போல் வெளிறிய வைக்கோல் நிறமாக காய்ந்துள்ளதா?",
            "அதிகாலை வேளையில் இலை மீது பால் போன்ற பாக்டீரியா கசிவு தென்படுகிறதா?\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]"
        ],
        "how_to_check_tanglish": [
            "Karugal ilai nuni orathula thodangi keezhe pogutha?",
            "Yellow karugalin border alai alaiya (wavy) irukka?",
            "Paathikkapatta ilai paper maathiri bleached straw-white colour-la kaanjirukka?",
            "Kaalaila pani irukkum pothu bacterial ooze droplets theriyutha?\n[Needs expert review]"
        ],

        "how_it_spreads_en": "• Enters through leaf hydathodes and microscopic wounds caused by strong winds, storms, or transplanting.\n• Flooding irrigation water and rain splash transport bacteria rapidly across adjacent fields.\n• The practice of clipping seedling tips before planting directly inoculates bacteria into healthy tissue.",
        "how_it_spreads_ta": "• பலத்த காற்று, புயல் அல்லது நாற்று நடும் போது ஏற்படும் காயங்கள் வழியாக பாக்டீரியா ஊடுருவுகிறது.\n• வயலில் தேங்கும் பாசன நீர் மற்றும் மழைத்துளிகள் மூலம் அடுத்தடுத்த பயிர்களுக்குப் பரவும்.\n• நடும் முன் நாற்றின் நுனியை நறுக்குவது இந்நோய் நேரடியாகப் பரவ வழிவகுக்கும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "how_it_spreads_tanglish": "• Kaatru, mazhai illa kalai edukkum pothu ilaila padum kaayangalin vazhiya bacteria ulla pogum.\n• Vayal paasana thanni mattrum mazhai thuligal moolama adutha vayalukku romba vegama paravum.\n• Nadavukku munnadi naatru nuniyai killuvathu (clipping) intha noiya neradiya paravum.\n[Needs expert review]",

        "favourable_conditions_en": "• Warm temperatures (25°C to 34°C) with high relative humidity above 70%.\n• Heavy rainstorms, typhoons, and gusty winds that bruise and wound leaf canopies.\n• Deep standing irrigation water, waterlogged plots, and excess nitrogen top-dressing.",
        "favourable_conditions_ta": "• 25°C முதல் 34°C மிதமான வெப்பம் மற்றும் 70%க்கும் அதிகமான காற்றில் ஈரப்பதம்.\n• பலத்த காற்றுடன் கூடிய கனமழை மற்றும் புயல் இலைகளில் காயங்களை ஏற்படுத்துதல்.\n• வயலில் அதிக நீர் தேங்கி நிற்றல் மற்றும் அளவுக்கு அதிகமான தழைச்சத்து.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "favourable_conditions_tanglish": "• 25°C - 34°C veyil/veppam mattrum 70% mela athiga eerappatham.\n• Kaatrodu koodiya perumazhai mattrum cyclone ilaila kaayangalai undakki bacteria nuzhaiya vaikkum.\n• Vayalla athigamaana thanni thengi submergence aanaalum noi seekiram thondrum.\n[Needs expert review]",

        "prevention_before_planting_en": "• Cultivate BLB-resistant or tolerant varieties recommended by TNAU for your region.\n• Avoid clipping the tips of seedlings at the time of transplanting.\n• Ensure proper drainage channels are prepared around the field perimeter before sowing.",
        "prevention_before_planting_ta": "• உங்கள் பகுதிக்கு ஏற்ற TNAU பரிந்துரைத்த பாக்டீரியா இலைக்கருகல் எதிர்ப்பு நெல் ரகங்களைப் பயிரிடவும்.\n• நாற்று நடும் போது நாற்றின் நுனிகளை நறுக்குவதைத் தவிர்க்கவும்.\n• வயலைச் சுற்றி முறையான வடிகால் வாய்க்கால்களை அமைத்து நீர்த் தேங்குவதைத் தவிர்க்கவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_before_planting_tanglish": "• TNAU BLB ethirppu ragangalai choose panni payiridavum.\n• Nadavu seiyum pothu naatru nuniyai narakkave koodadhu.\n• Vayalai suthi nalla vadigaal kalvaai amaithu thanni thengaama paathukonga.\n[Needs expert review]",

        "prevention_during_crop_en": "• Avoid excessive chemical nitrogen top-dressing; apply split doses with adequate potassium.\n• Drain standing floodwater immediately from infected plots to stop water-borne transmission.\n• Avoid entering or working in wet fields to prevent brushing bacteria onto healthy leaves.",
        "prevention_during_crop_ta": "• அதிகப்படியான யூரியாவைத் தவிர்த்து, சாம்பல் சத்துடன் சேர்த்து தவணைகளாக இடவும்.\n• பாக்டீரியா பரவாமல் இருக்க வயலில் தேங்கியுள்ள பாசன நீரை உடனடியாக வடித்துவிடவும்.\n• இலைகளில் ஈரம் இருக்கும் போது வயலில் வேலை செய்வதைத் தவிர்க்கவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_during_crop_tanglish": "• Athiga urea poduratha stop panni potash urathai sariyaaga ittu payirin ethirppai kootunga.\n• Bacteria paravama irukka vayalla thengi nirkum thanniya udane vadithuvidavum.\n• Ilaila eerappatham irukkum pothu vayalla irangi velai seivathai thavirkkavum.\n[Needs expert review]",

        "prevention_after_harvest_en": "• Plough the field deeply after harvest to bury and decompose stubble carrying bacteria.\n• Clear field bunds of volunteer rice and wild host weeds (like Leersia oryzoides).\n• Allow the soil to dry out thoroughly under bright summer sun between cropping cycles.",
        "prevention_after_harvest_ta": "• பாக்டீரியா அழிய அறுவடைக்குப்பின் வயலை ஆழமாக உழுது பயிர்க் கழிவுகளை மக்க வைக்கவும்.\n• வயல் வரப்புகளில் உள்ள காட்டுப் புற்களையும் தேவையற்ற நெற்பயிர்களையும் அகற்றவும்.\n• அடுத்த சாகுபடிக்கு முன் நிலத்தை வெயிலில் நன்கு காய விடவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_after_harvest_tanglish": "• Bacteria azhiya aruvadaikku pin nilathai aazhamaaga uzhuthu thalgalai makka vaikkavum.\n• Varappula ulla kaatu pull kalaigalai clean panni azhithuvidavum.\n• Adutha season-kku munnadi mannai nalla veyilil kaaya vidavum.\n[Needs expert review]",

        "prevention_to_limit_spread_en": "• Drain standing irrigation water immediately.\n• Halt nitrogen top-dressing completely until fresh healthy leaves emerge.\n• Consult your local agriculture officer for certified bio-control or TNAU-recommended management.",
        "prevention_to_limit_spread_ta": "• வயலில் தேங்கியுள்ள பாசன நீரை உடனடியாக வடித்துவிடவும்.\n• புதிய ஆரோக்கியமான இலைகள் வரும் வரை யூரியா இடுவதை முழுமையாக நிறுத்தவும்.\n• TNAU வழிகாட்டுதலின்படி சரியான பாதுகாப்பு நடவடிக்கைக்கு வட்டார வேளாண் அலுவலரை அணுகவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_to_limit_spread_tanglish": "• Paathikkapatta vayalilirunthu thengi nirkum thanniya udane vadithuvidavum.\n• Pudhu pacha ilai varum varai urea nitrogen poduvathai stop pannunga.\n• TNAU recommendation padi sariyaana aalosanai pera agriculture officer-ah sandhikavum.\n[Needs expert review]",

        "when_to_call_officer_en": "• Contact your Agriculture Officer if marginal yellowing spreads rapidly across fields after a rainstorm.\n• Request a confirmed bacterial ooze test to distinguish BLB from fungal leaf scald.\n• Rely on authorized agricultural department advisories rather than unverified commercial sprays.",
        "when_to_call_officer_ta": "• மழை அல்லது புயலுக்குப் பிறகு இலை ஓரங்கள் வேகமாக கருகினால் உடனே வேளாண் அலுவலரை அணுகவும்.\n• இது பாக்டீரியா கருகலா என்பதை உறுதி செய்ய அலுவலரிடம் 'கசிவு ஆய்வு' பெறவும்.\n• அங்கீகரிக்கப்பட்ட வேளாண் துறை பரிந்துரைகளை மட்டுமே பின்பற்றவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "when_to_call_officer_tanglish": "• Mazhaikku piragu ilai nuni vegama karuginaal udane agriculture officer-ah contact pannunga.\n• Ithu bacteria karugala nu confirm panna officer kitta ooze test seiyavum.\n• Government agriculture department solra official advice mattum kelunga.\n[Needs expert review]",

        "similar_looking_problems_en": "• Leaf Scald: produces concentric zonate bands from leaf tips without wavy margins.\n• Bacterial Leaf Streak: confined to narrow interveinal streaks without broad undulating marginal blighting.\n• Salinity/Drought stress: causes dry straw-colored leaf tips without bacterial ooze or yellow wavy advancing margins.",
        "similar_looking_problems_ta": "• இலை வெளிரல் (Leaf Scald): இலை நுனியிலிருந்து வளைய வளையமான பட்டைகளாகக் கருகும்.\n• பாக்டீரியா இலைக்கீற்று: நரம்புகளுக்கு இடையே மெல்லிய நேர்க்கோடுகளாக இருக்கும்.\n• உவர்/வறட்சி பாதிப்பு: நுனி காய்ந்திருக்கும் ஆனால் அலை அலையான மஞ்சள் விளிம்போ பாக்டீரியா கசிவோ இருக்காது.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "similar_looking_problems_tanglish": "• Leaf Scald: Ilai nuniyilirunthu chevron valaiyagalaga karugum; wavy margin irukkadhu.\n• Bacterial Leaf Streak: Narambukalukku idaiyila straight line streaks mattum varum.\n• Uppu/Varatchi paathippu: Nuni kaanjirukkum aana bacterial ooze illa wavy yellow margin irukkadhu.\n[Needs expert review]"
    },

    "healthy": {
        "name_tanglish": "Aarokkiyamaana Payir (Healthy Paddy)",
        "symptoms_summary_en": "Vigorous, uniform dark green erect leaves with clean sheaths and zero spots or lesions.\nHealthy white feeder root system with active tillering and sturdy stems.",
        "symptoms_summary_ta": "ஒரே சீரான அடர் பச்சை நிறத்தில் நிமிர்ந்த இலைகளும், புள்ளிகளோ கருகலோ அற்ற தூய்மையான உறைகளும் காணப்படும்.\nவீரியமான வெண்மை வேர் மண்டலத்துடன் தீவிர தூர் கட்டும் வளர்ச்சி இருக்கும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "symptoms_summary_tanglish": "Nalla dark green nimirntha ilaigalum, pulligal illaatha clean sheaths-um thondrum.\nVellai ver valarchiyoda thoor katti sturdyaana thandu irukkum.\n[Needs expert review]",

        "symptoms_leaf_en": [
            "1. Uniform canopy colour: Leaves exhibit a healthy, uniform dark green coloration from tip to base.",
            "2. Smooth leaf surface: Blade surfaces are clean, erect, and firm with no necrotic specks, stripes, or watersoaked areas.",
            "3. Intact leaf margins: Edges are clean, unbroken, and free of yellowing, firing, or wavy borders.",
            "4. Firm collar junction: The collar connecting blade to sheath is pale green, firm, and rot-free."
        ],
        "symptoms_leaf_ta": [
            "1. சீரான இலை வண்ணம்: இலை நுனி முதல் அடிப்பகுதி வரை ஒரே சீரான அடர் பச்சை நிறம் காணப்படும்.",
            "2. சுத்தமான இலைப்பரப்பு: புள்ளிகளோ, கருகலோ அல்லது நீர் ஊறிய அடையாளங்களோ இன்றி இலை நிமிர்ந்து இருக்கும்.",
            "3. ஆரோக்கியமான விளிம்புகள்: இலை ஓரங்கள் மஞ்சள் நிறமோ தீய்ந்த அமைப்போ இன்றி உறுதியாக இருக்கும்.",
            "4. உறுதியான இலைக் கழுத்து: இலை மற்றும் உறையின் இணைப்பு இளம்பச்சை நிறத்தில் அழுகலின்றி இருக்கும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]"
        ],
        "symptoms_leaf_tanglish": [
            "1. Seerana pacha niram: Ilai nuni mudhal adi varai ore seerana dark green colour irukkum.",
            "2. Clean leaf surface: Pulligal karugal illaamal ilai nalla nimirnthu firm-ah irukkum.",
            "3. Nalla leaf margins: Ilai orathula yellowing illa crispy burning illaamal clean-ah irukkum.",
            "4. Strong collar: Ilai collar azhugal illaamal pale green colour-la irukkum.\n[Needs expert review]"
        ],

        "symptoms_other_parts_en": "• Stem and sheath: clean, firm, pale green with no lesions, mycelium, or sclerotial bodies.\n• Roots: vigorous, extensive root system with white active feeder roots.",
        "symptoms_other_parts_ta": "• தண்டு மற்றும் உறை: அழுகல், பூஞ்சை படலம் அல்லது புள்ளிகள் இன்றி உறுதியாக இருக்கும்.\n• வேர் மண்டலம்: வெண்மை மற்றும் இளமஞ்சள் நிறத்துடன் வீரியமாக வேர்விட்டு இருக்கும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "symptoms_other_parts_tanglish": "• Thandu mattrum urai: Azhugal, poonjai illaamal pale green colour-la firm-ah irukkum.\n• Vergal: Vella veler-nu nalla virintha ver valarchi irukkum.\n[Needs expert review]",

        "how_to_check_en": [
            "Is the entire leaf blade uniformly green without yellow or brown spots?",
            "Are the leaf edges smooth and free of wavy dried margins?",
            "Is the collar and sheath base clean without any dark brown rot?",
            "Are the tiller stems firm and actively growing?"
        ],
        "how_to_check_ta": [
            "இலைப்பரப்பு முழுவதும் புள்ளிகளோ கருகலோ இன்றி சீரான பச்சையாக உள்ளதா?",
            "இலை விளிம்புகள் அலை அலையான கருகலின்றி சுத்தமாக உள்ளதா?",
            "இலைக் கழுத்துப் பகுதியும் தண்டின் அடிப்பகுதியும் அழுகலின்றி உள்ளதா?",
            "தூர்கள் உறுதியாகவும் சுறுசுறுப்பாகவும் வளர்கிறதா?\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]"
        ],
        "how_to_check_tanglish": [
            "Leaf muzhuvathum pulligal karugal illama uniform green-ah irukka?",
            "Ilai orangal wavy dried margin illama clean-ah irukka?",
            "Collar mattrum thandu adi paguthi azhugal illama irukka?",
            "Thoorgal nalla firm-avum nalla valarchiyodavum irukka?\n[Needs expert review]"
        ],

        "how_it_spreads_en": "• Healthy conditions are sustained by practicing clean field sanitation, adequate spacing, and balanced water cycles.\n• Good soil aeration keeps pathogen populations below harmful threshold levels.",
        "how_it_spreads_ta": "• சுத்தமான வயல் சுகாதாரம், சரியான பயிர் இடைவெளி மற்றும் சீரான பாசனம் பயிர் ஆரோக்கியத்தை நிலைநிறுத்துகிறது.\n• நல்ல மண் காற்றோட்டம் நோய் கிருமிகளின் வளர்ச்சியைத் தடுத்து பயிரைக் காக்கிறது.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "how_it_spreads_tanglish": "• Clean field sanitation, sariyaana spacing mattrum thanni paasanam payir aarokkiyathai kaakkum.\n• Nalla man kaathottam poonjaigal peruguvathai thadukkum.\n[Needs expert review]",

        "favourable_conditions_en": "• 25°C to 32°C temperatures with bright daytime sunlight during tillering and reproductive phases.\n• Well-drained fertile loam soils with balanced organic matter and active soil biology.",
        "favourable_conditions_ta": "• 25°C முதல் 32°C வெப்பநிலை மற்றும் தூர் கட்டும் பருவத்தில் நல்ல பிரகாசமான சூரிய ஒளி.\n• இயற்கை உரம் மற்றும் முறையான வடிகால் வசதி கொண்ட வளமான மண் சூழல்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "favourable_conditions_tanglish": "• 25°C - 32°C veppam mattrum thoor kattum nerathil nalla bright sooriya velicham.\n• Nalla man valai mattrum vadigaal vasathi ulla nilam.\n[Needs expert review]",

        "prevention_before_planting_en": "• Source high-quality certified seeds from authorized government depots.\n• Complete seed treatment before nursery sowing as advised in the TNAU guide.\n• Test your soil and apply recommended basal nutrients including compost.",
        "prevention_before_planting_ta": "• அரசு அங்கீகாரம் பெற்ற மையங்களில் இருந்து தரமான சான்றளிக்கப்பட்ட விதைகளைப் பெறவும்.\n• TNAU வழிகாட்டியின்படி நடும் முன் விதை நேர்த்தி முறையை தவறாமல் செய்யவும்.\n• மண் ஆய்வு செய்து பரிந்துரைக்கப்பட்ட இயற்கை மற்றும் அடி உரங்களை இடவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_before_planting_tanglish": "• Government authorized depots-la certified seeds vangavum.\n• TNAU guide padi vidhai nerthi kandippa seiyavum.\n• Mann test eduthu thevaiyana adi uram mattrum iyarkai urangalai podavum.\n[Needs expert review]",

        "prevention_during_crop_en": "• Use the Leaf Colour Chart (LCC) to apply nitrogen only when necessary; avoid excessive greenness.\n• Practice Alternate Wetting and Drying (AWD) to aerate root zones.\n• Scout fields weekly to detect any localized pest or disease initiation early.",
        "prevention_during_crop_ta": "• இலை வண்ண அட்டை (LCC) மூலம் ஆய்வு செய்து தேவைப்படும் போது மட்டும் தழைச்சத்தை இடவும்.\n• வேர்களுக்குக் காற்றோட்டம் கிடைக்க காய்ச்சலும் பாய்ச்சலுமாக நீர்ப்பாசனம் செய்யவும்.\n• ஏதேனும் பூச்சி நோய் தாக்குதல் ஆரம்பிக்கிறதா என்பதை வாரம் ஒருமுறை கண்காணிக்கவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_during_crop_tanglish": "• LCC card paarthu thevaiyana nerathil mattum nitrogen urea podavum.\n• Vergalukku kaathottam kidaikka kaichalum paichalumaaga thanni paasanam seiyavum.\n• Varam oru murai vayalil noi arikurigal irukka nu scout panni check pannunga.\n[Needs expert review]",

        "prevention_after_harvest_en": "• Deep summer ploughing to expose soil pests and resting spores to natural solarization.\n• Clean threshing equipment to avoid contaminating healthy harvest lots.\n• Practice crop rotation with green manure or pulses to replenish soil nitrogen naturally.",
        "prevention_after_harvest_ta": "• கோடை உழவு செய்து மண்ணை சூரிய ஒளியில் காய விட்டு மண் நலத்தைப் பராமரிக்கவும்.\n• அறுவடை செய்யும் கருவிகளை சுத்தமாக வைத்து விதைகளின் தூய்மையைப் பாதுகாக்கவும்.\n• தக்கைப்பூண்டு அல்லது பயறு வகைப் பயிர்களுடன் பயிர் சுழற்சி செய்து மண் வளத்தை உயர்த்தவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_after_harvest_tanglish": "• Kodai uzhavu panni mannil ulla spores azhiya nalla veyilil kaaya vaikkavum.\n• Aruvadai tools clean-ah vachu vidhaigalai paadhukaakkavum.\n• Pasunthaal uram illa payaru vachu crop rotation seiyavum.\n[Needs expert review]",

        "prevention_to_limit_spread_en": "• No chemical treatment is needed for healthy paddy crops.\n• Avoid routine preventative spraying of chemical pesticides to protect beneficial spiders and predators.\n• Maintain balanced soil nutrition and water drainage across all field plots.",
        "prevention_to_limit_spread_ta": "• ஆரோக்கியமான பயிருக்கு எவ்வித ரசாயன மருந்துகளையும் தெளிக்கத் தேவையில்லை.\n• நன்மை செய்யும் சிலந்திகள் மற்றும் பூச்சிகளைப் பாதுகாக்க தேவையற்ற தெளிப்பைத் தவிர்க்கவும்.\n• அனைத்துப் பாத்திகளிலும் சீரான சத்து சமநிலையையும் வடிகால் வசதியையும் பராமரிக்கவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_to_limit_spread_tanglish": "• Aarokkiyamaana payirukku endha chemical marunthum thevaiye illa.\n• Nanmai seiyum poochigala kaakka thevaillatha spray thavirkkavum.\n• Ella edathilum seerana uram mattrum thanni vadigaal maintain seiyavum.\n[Needs expert review]",

        "when_to_call_officer_en": "• Consult your Agriculture Officer to collect government soil health cards and input subsidies.\n• Seek guidance on seasonal weather advisories and certified variety performance in your taluk.",
        "when_to_call_officer_ta": "• மண் சுகாதார அட்டை மற்றும் அரசு மானிய இடுபொருட்களைப் பெற வேளாண் அலுவலரை அணுகலாம்.\n• பருவ கால வானிலை ஆலோசனைகள் மற்றும் சிறந்த ரகங்கள் பற்றிய விவரங்களைப் பெறவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "when_to_call_officer_tanglish": "• Man vala card mattrum government subsidy porutkal pera agriculture officer-ah sandhikavum.\n• Paruva kaala aalosanai kettukollavum.\n[Needs expert review]",

        "similar_looking_problems_en": "• Healthy leaves are uniform green with smooth surfaces and unbroken edges.\n• Early blast or brown spot begins as tiny pinhead-sized specks.\n• Early BLB shows water-soaked marginal streaks in early morning dew.",
        "similar_looking_problems_ta": "• ஆரோக்கியமான இலைகள் புள்ளிகள் இன்றி சீரான பச்சையாகவும் மென்மையாகவும் இருக்கும்.\n• ஆரம்ப குலை அல்லது பழுப்பு புள்ளி நோய் மிகச் சிறிய ஊசி முனை புள்ளிகளாகத் தொடங்கும்.\n• ஆரம்ப பாக்டீரியா கருகல் அதிகாலையில் விளிம்புகளில் நீர் ஊறிய கோடுகளாகத் தென்படும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "similar_looking_problems_tanglish": "• Healthy ilaila spots illaamal uniform green smooth surface irukkum.\n• Blast illa brown spot oosi munai maathiri chinna speckles-aaga aarambikkum.\n• BLB aarambathula kaalaila ilai orathula neer ooriya streaks thondrum.\n[Needs expert review]"
    },

    "tungro": {
        "name_tanglish": "Rice Tungro Virus (Manjal noi)",
        "symptoms_summary_en": "Stunted plant growth with yellow or orange-yellow discolouration starting from leaf tips on older leaves.\nSevere reduction in tiller number, delayed flowering, and sterile panicles transmitted by green leafhoppers.",
        "symptoms_summary_ta": "செடிகள் குட்டையாகி முதிர்ந்த இலைகளின் நுனியிலிருந்து மஞ்சள்-ஆரஞ்சு நிறமாக மாறும்.\nதூர் கட்டுவது வெகுவாகக் குறைந்து பூப்பது தாமதமாகி கதிர்கள் பதராகும்; பச்சை தத்துப்பூச்சிகளால் பரவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "symptoms_summary_tanglish": "Chedi kuttaiyaagi (stunted) pazhaiya ilai nuniyilirunthu yellow-orange colour aagum.\nThoor kattuvathu ninnu poi pookkavathu delay aagi kathir padhar aagum; pacha thathupoochiyal paravum.\n[Needs expert review]",

        "symptoms_leaf_en": [
            "1. Leaf yellowing: Discolouration begins at the tips of outer older leaves, turning bright yellow or orange-yellow.",
            "2. Mottling pattern: Interveinal chlorosis and irregular rusty mottling appear on the leaf blade.",
            "3. Young leaf symptoms: Younger leaves appear slightly mottled or pale green with twisted margins.",
            "4. Stunted erect habit: Leaves become stiff, erect, and narrow on noticeably stunted plant hills."
        ],
        "symptoms_leaf_ta": [
            "1. இலை மஞ்சள் நிறமாதல்: வெளி முதிர்ந்த இலைகளின் நுனியிலிருந்து பிரகாசமான மஞ்சள் அல்லது ஆரஞ்சு நிறம் தொடங்கும்.",
            "2. புள்ளிகள் அமைவு: இலை நரம்புகளுக்கு இடையே சீரற்ற துரு நிற புள்ளிகள் தோன்றும்.",
            "3. இளம் இலைகள்: இளங்குருத்து இலைகள் வெளிறிய பச்சையாகவும் விளிம்புகள் சற்றே சுருண்டும் காணப்படும்.",
            "4. குட்டைத் தோற்றம்: செடிகள் உயரமின்றி குட்டையாகி இலைகள் நிமிர்ந்து விறைப்பாக இருக்கும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]"
        ],
        "symptoms_leaf_tanglish": [
            "1. Ilai manjal niram: Pazhaiya ilai nuniyilirunthu bright yellow illa orange-yellow colour thodangum.",
            "2. Mottling pattern: Narambukalukku idaiyila rusty speckles thondrum.",
            "3. Ilam ilai: Ilam ilaigal pale green colour-avum viruthalaga irukkum.",
            "4. Kuttai thotram: Chedi kuttaiyaagi ilaigal viraippaaga nimirnthu nikkum.\n[Needs expert review]"
        ],

        "symptoms_other_parts_en": "• Whole hill: marked stunting with significantly reduced tiller count per hill.\n• Panicles: delayed, partially exerted, and produce small sterile discoloured grains.",
        "symptoms_other_parts_ta": "• முழு செடி: செடிகள் உயரமின்றி மிகக் குட்டையாகி தூர்கள் கட்டாமல் முடங்கும்.\n• கதிர்: கதிர் வெளிவருவது தாமதமாகி மணிகள் சிறுத்துப் பதராகும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "symptoms_other_parts_tanglish": "• Muzhu chedi: Chedi kuttaiyaagi thoor kattuvathu romba koranjidum.\n• Kathir: Kathir veliye varuvathu late aagi nel mani chinnathaagi padhar aagum.\n[Needs expert review]",

        "how_to_check_en": [
            "Is the plant noticeably stunted compared to surrounding normal hills?",
            "Are the older leaves turning distinct yellow or orange-yellow from the tips?",
            "Are green leafhopper insects present when shaking the plant canopy?",
            "Is tillering severely suppressed with stiff, erect foliage?"
        ],
        "how_to_check_ta": [
            "பக்கத்து செடிகளை விட இச்செடி மிகவும் குட்டையாக உள்ளதா?",
            "முதிர்ந்த இலைகளின் நுனி மஞ்சள் அல்லது ஆரஞ்சு நிறமாக மாறியுள்ளதா?",
            "செடியை அசைக்கும் போது பச்சை தத்துப்பூச்சிகள் பறக்கின்றனவா?",
            "தூர் கட்டுவது முற்றிலும் குறைந்து இலைகள் விறைப்பாக உள்ளதா?\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]"
        ],
        "how_to_check_tanglish": [
            "Pakkathu chediyai vida intha chedi nalla kuttaiyaaga irukka?",
            "Pazhaiya ilai nuni bright yellow illa orange-yellow colour-la irukka?",
            "Chediyai aattum pothu pacha thathupoochi (green leafhopper) parakkutha?",
            "Thoor kattuvathu koranju ilaigal viraippaaga nikkutha?\n[Needs expert review]"
        ],

        "how_it_spreads_en": "• Transmitted by the Green Leafhopper (Nephotettix virescens) in a semi-persistent manner.\n• Leafhoppers acquire the virus from infected volunteer paddy or weeds and transmit it within minutes while feeding.\n• Not seed-borne and not transmitted mechanically or through irrigation water.",
        "how_it_spreads_ta": "• பச்சை தத்துப்பூச்சிகள் (Nephotettix virescens) மூலம் இந்நோய் ஒரு பயிரிலிருந்து மற்றொரு பயிருக்கு பரவுகிறது.\n• பூச்சிகள் பாதிக்கப்பட்ட பயிரில் சாறு உறிஞ்சும் போது வைரஸை எடுத்துக்கொண்டு அடுத்த பயிரில் பரப்புகின்றன.\n• இது விதை மூலமாகவோ அல்லது பாசன நீர் மூலமாகவோ பரவுவதில்லை.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "how_it_spreads_tanglish": "• Pacha thathupoochi (Green Leafhopper) intha virus-ai oru payirilirunthu innoru payirukku paravum.\n• Poochigal saaru urinjum pothu virus-ai eduthu adutha payirukku transmit pannum.\n• Ithu vidhai moolamavo thanni moolamavo paravathu.\n[Needs expert review]",

        "favourable_conditions_en": "• High populations of green leafhoppers during early vegetative crop stages.\n• Continuous staggered planting in nearby plots providing continuous food for vectors.\n• Warm humid weather favoring leafhopper multiplication.",
        "favourable_conditions_ta": "• ஆரம்ப பருவத்தில் பச்சை தத்துப்பூச்சிகளின் எண்ணிக்கை அதிகமாக இருத்தல்.\n• அருகில் உள்ள வயல்களில் வெவ்வேறு பருவங்களில் நடவு செய்யப்பட்டு தொடர் உணவு கிடைத்தல்.\n• தத்துப்பூச்சிகள் பெருக சாதகமான மிதமான வெப்பம் மற்றும் காற்றில் ஈரப்பதம்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "favourable_conditions_tanglish": "• Aaramba paruvathil pacha thathupoochi athigamaaga irunthaal.\n• Pakkathu vayalgalil thodarnthu maathi maathi nadavu seithirunthaal.\n• Poochigal peruga etha veppam mattrum eerappatham.\n[Needs expert review]",

        "prevention_before_planting_en": "• Grow Tungro-resistant varieties recommended by TNAU for vector-prone zones.\n• Synchronize planting across the village block to break the vector cycle.\n• Destroy volunteer rice and stubble harboring the virus during land preparation.",
        "prevention_before_planting_ta": "• உங்கள் பகுதிக்கு ஏற்ற TNAU துங்ரோ எதிர்ப்பு நெல் ரகங்களைப் பயிரிடவும்.\n• பூச்சிகளின் பெருக்கத்தைத் தடுக்க கிராமம் முழுவதும் ஒரே நேரத்தில் நடவு செய்யவும்.\n• நில தயாரிப்பின் போது வைரஸ் தாங்கிய முந்தைய பயிர்க் கழிவுகளை அகற்றவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_before_planting_tanglish": "• TNAU tungro ethirppu ragangalai choose panni payiridavum.\n• Oorellaam ore nerathil synchronised nadavu seiyavum.\n• Nilam thayarippin pothu palaiya thaalgalai azhithuvidavum.\n[Needs expert review]",

        "prevention_during_crop_en": "• Monitor green leafhopper vector populations using light traps.\n• Remove and bury rogue infected stunted hills in early stages to eliminate the virus reservoir.\n• Apply balanced fertilizer and avoid excessive urea.",
        "prevention_during_crop_ta": "• விளக்குப் பொறிகள் அமைத்து பச்சை தத்துப்பூச்சிகளின் நடமாட்டத்தைக் கண்காணிக்கவும்.\n• ஆரம்பத்தில் தென்படும் துங்ரோ தாக்கிய குட்டை செடிகளை வேரோடு பிடுங்கி அழிக்கவும்.\n• சமச்சீரான உரமிடுதலைப் பின்பற்றி அளவுக்கு அதிகமான யூரியாவைத் தவிர்க்கவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_during_crop_tanglish": "• Vilakku pori vachu pacha thathupoochi irukka nu monitor pannunga.\n• Aarambathil theriyum kuttai infected chedigalai pidungi azhithuvidavum.\n• Samacheer uram pottu athiga urea-va thavirkkavum.\n[Needs expert review]",

        "prevention_after_harvest_en": "• Plough the field immediately after harvest to incorporate and destroy stubbles.\n• Clear all grassy weed hosts along bunds and channels between seasons.\n• Maintain a rice-free period (crop holiday) of at least 3 weeks before the next planting.",
        "prevention_after_harvest_ta": "• அறுவடைக்குப்பின் உடனே நிலத்தை உழுது பயிர்க் கழிவுகளை மக்க வைக்கவும்.\n• வரப்பு மற்றும் வாய்க்காலில் உள்ள தத்துப்பூச்சி தங்கும் களைகளை அகற்றவும்.\n• அடுத்த சாகுபடிக்கு முன் குறைந்தது 3 வாரங்கள் வயலை நெல் பயிரின்றி விடவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_after_harvest_tanglish": "• Aruvadai mudintha udane uzhavu panni thaalgalai azhikkavum.\n• Varappula ulla pull kalaigalai clean-ah vechikonga.\n• Adutha season-kku munnadi kurainthathu 3 vaaram nilathil nel illaamal gap vidavum.\n[Needs expert review]",

        "prevention_to_limit_spread_en": "• Rouge out and destroy infected stunted hills immediately.\n• Manage green leafhopper vector populations based on TNAU economic threshold guidelines.\n• Consult your local agriculture officer for certified eco-friendly vector management advice.",
        "prevention_to_limit_spread_ta": "• பாதிக்கப்பட்ட குட்டை செடிகளை உடனே பிடுங்கி குழியில் புதைத்து அழிக்கவும்.\n• TNAU பொருளாதார சேத வரம்பிற்கு ஏற்ப தத்துப்பூச்சிகளை கட்டுப்படுத்த நடவடிக்கை எடுக்கவும்.\n• பூச்சிக் கட்டுப்பாட்டிற்கு உடனடியாக வேளாண்மை அலுவலரிடம் ஆலோசனை பெறவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_to_limit_spread_tanglish": "• Paathikkapatta kuttai chedigalai udane pidungi pudhaithuvidavum.\n• TNAU guidelines padi thathupoochigala control panna step edunga.\n• Sariyaana poochikkattuppaadu aalosanai pera agriculture officer-ah sandhikavum.\n[Needs expert review]",

        "when_to_call_officer_en": "• Contact your Agriculture Officer if stunted yellow patches appear within 45 days after transplanting.\n• If green leafhoppers are observed in large numbers during scouting.\n• Follow official extension guidelines for community-wide vector control.",
        "when_to_call_officer_ta": "• நட்ட 45 நாட்களுக்குள் வயலில் ஆங்காங்கே குட்டை மஞ்சள் செடிகள் தென்பட்டால் உடனே வேளாண் அலுவலரை அணுகவும்.\n• தத்துப்பூச்சிகள் அதிகளவில் காணப்பட்டால் தகவல் தெரிவிக்கவும்.\n• கிராம அளவிலான ஒருங்கிணைந்த பூச்சிக் கட்டுப்பாட்டு வழிகாட்டல்களைப் பின்பற்றவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "when_to_call_officer_tanglish": "• Nadavu panni 45 naalukkul kuttai manjal patches vantha udane agriculture officer-ah sandhikavum.\n• Thathupoochi kootam athigama irunthaal officer kitta sollavum.\n• Official extension aalosanai padi nadavadikkai edunga.\n[Needs expert review]",

        "similar_looking_problems_en": "• Zinc Deficiency: causes rusty bronze spots along midribs of younger/middle leaves without stunting tillering.\n• Grassy Stunt Virus: causes severe plant stunting but with profuse narrow tillers, looking like a dense grassy clump.\n• Nitrogen Deficiency: causes uniform pale yellowing starting from bottom leaves without leafhopper vectors.",
        "similar_looking_problems_ta": "• துத்தநாகக் குறைபாடு: இலை நரம்புகளில் துரு நிறப் புள்ளிகள் தோன்றும்; தூர் கட்டுவது பாதிக்கப்படாது.\n• புல் குட்டை நோய்: செடி குட்டையாகும் ஆனால் மிக அதிகமான மெல்லிய தூர்கள் தோன்றி புல் போல் இருக்கும்.\n• தழைச்சத்து குறைபாடு: முதிர்ந்த கீழ் இலைகள் ஒரே சீராக வெளிறிய மஞ்சளாகும்; தத்துப்பூச்சிகள் இருக்காது.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "similar_looking_problems_tanglish": "• Zinc deficiency: Ilaila rust maathiri bronze speckles varum aana thoor kattuvathu nirkadhu.\n• Grassy Stunt: Chedi kuttaiyagi romba athiga narrow thoorgal vanthu pullu maathiri kaattum.\n• Nitrogen deficiency: Adi ilaigal seerana pale yellow colour aagum; poochigal irukkadhu.\n[Needs expert review]"
    },

    "sheath_blight": {
        "name_tanglish": "Sheath Blight (Urai Karugal)",
        "symptoms_summary_en": "Large oval greenish-grey water-soaked lesions with dark brown borders on lower leaf sheaths.\nLesions coalesce with snake-skin banded appearance, climbing up to flag leaves and suffocating panicles.",
        "symptoms_summary_ta": "தண்டின் கீழ் இலை உறைகளில் சாம்பல்-பச்சை நிறத்தில் பெரிய நீள்வட்ட அழுகல் புள்ளிகள் தோன்றும்.\nபாம்புத் தோல் போன்ற பட்டைகளாக ஒன்றிணைந்து கொடி இலை வரை பரவி கதிர் வெளிவருவதைத் தடுக்கும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "symptoms_summary_tanglish": "Adi ilai uraila periya oval greenish-grey neer ooriya azhugal pulligal thondrum.\nPaambu thol maathiri bands aagi maele kodi ilai varai paravi kathir veliye varatha thadukkum.\n[Needs expert review]",

        "symptoms_leaf_en": [
            "1. Waterline lesions: Oval or oblong greenish-grey water-soaked spots appear on leaf sheaths near water level.",
            "2. Banded progression: Spots enlarge with irregular dark brown margins and bleached greyish centres resembling snake skin.",
            "3. Upward spread: The fungal mycelium creeps upward, forming banded lesions across leaf blades in dense canopies.",
            "4. Canopy lodging: Severely blighted tillers rot, soften, and lodge easily under wind."
        ],
        "symptoms_leaf_ta": [
            "1. நீர்மட்டப் புள்ளிகள்: நீர் மட்டத்திற்கு அருகில் உள்ள இலை உறைகளில் நீள்வட்ட சாம்பல்-பச்சை புள்ளிகள் தோன்றும்.",
            "2. பட்டை வடிவ வளர்ச்சி: புள்ளிகள் விரிவடைந்து அடர் பழுப்பு விளிம்புடன் பாம்புத் தோல் போன்ற பட்டைகளாக மாறும்.",
            "3. மேல்நோக்கிப் பரவுதல்: பூஞ்சை வலைகள் மேல்நோக்கிப் பரவி இலைகளிலும் பட்டைக் கருகலை உண்டாக்கும்.",
            "4. பயிர் சாய்ந்து விழுதல்: தண்டு அழுகி பலமிழந்து காற்றுக்கு எளிதில் சாய்ந்துவிடும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]"
        ],
        "symptoms_leaf_tanglish": [
            "1. Thanni matta pulligal: Thanni mattathukku kitta ilai uraila oval greenish-grey spots varum.",
            "2. Banded valarchi: Pulligal virinthu paambu thol maathiri bands aagi maarum.",
            "3. Maele paravuthal: Poonjai valaigal maele eri ilai blades-aiyum thakkum.",
            "4. Payir saainthu vizhuthal: Thandu azhugi soft aagi kaathukku seekiram saanjidum.\n[Needs expert review]"
        ],

        "symptoms_other_parts_en": "• Leaf sheaths: primary target, completely rotting from water level upward.\n• Panicles: emerging heads become choked in infected sheaths, causing sterile, discoloured grains.",
        "symptoms_other_parts_ta": "• இலை உறைகள்: முதன்மையாகத் தாக்கப்பட்டு நீர் மட்டத்திலிருந்து மேல்நோக்கி அழுகும்.\n• கதிர்கள்: அழுகிய உறைக்குள் கதிர் வெளிவர முடியாமல் மாட்டிக்கொண்டு பதராகும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "symptoms_other_parts_tanglish": "• Ilai urai: Mukkiyamaana target, adi muthal maele varai azhugi kaanjidum.\n• Kathir: Azhugiya urai ulla kathir maattikittu veliye varama padhar aagum.\n[Needs expert review]",

        "how_to_check_en": [
            "Are there large oval greenish-grey spots on leaf sheaths near the water line?",
            "Do the spots look banded with irregular dark brown margins like snake skin?",
            "Can you see white or brown mustard seed-like mustard sclerotia on infected sheaths?",
            "Is the infection moving upward toward the upper leaves in densely planted patches?"
        ],
        "how_to_check_ta": [
            "நீர்மட்டத்திற்கு அருகில் உள்ள இலை உறைகளில் பெரிய சாம்பல்-பச்சை அழுகல் புள்ளிகள் உள்ளதா?",
            "புள்ளிகள் பாம்புத் தோல் போல் ஒழுங்கற்ற பழுப்பு பட்டைகளாக உள்ளதா?",
            "இலை உறைகளில் கடுகு போன்ற வெண்மை அல்லது பழுப்பு நிற மணி உருண்டைகள் (ஸ்கிளரோஷியா) தென்படுகின்றனவா?",
            "அடர்த்தியான பயிர்களில் பாதிப்பு மேல்நோக்கி இலைகளுக்குப் பரவுகிறதா?\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]"
        ],
        "how_to_check_tanglish": [
            "Thanni mattathukku kitta ilai uraila periya oval greenish-grey spots irukka?",
            "Pulligal paambu thol maathiri dark brown banded margin-oda irukka?",
            "Infected uraila kadugu maathiri sclerotia manigal otti irukka?",
            "Adarthiyaana edathula noi maele kodi ilai நோக்கி pogutha?\n[Needs expert review]"
        ],

        "how_it_spreads_en": "• Soil-borne sclerotial bodies float on irrigation water and attach to rice tillers at water level.\n• Fungal hyphae spread rapidly through direct leaf-to-leaf contact in dense, heavily fertilized canopies.\n• Sclerotia survive in the soil and on crop debris for over a year.",
        "how_it_spreads_ta": "• மண்ணில் உள்ள பூஞ்சை மணிகள் பாசன நீரில் மிதந்து பயிரின் அடிப்பகுதியில் ஒட்டிக்கொள்கின்றன.\n• அடர்த்தியாக உள்ள பயிர்களில் இலைகள் ஒன்றோடு ஒன்று உரசும் போது பூஞ்சை இழைகள் வேகமாகப் பரவும்.\n• பூஞ்சை மணிகள் மண்ணிலும் பயிர்க் கழிவுகளிலும் ஒரு வருடத்திற்கும் மேலாக உயிர்வாழும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "how_it_spreads_tanglish": "• Mannil ulla poonjai sclerotia manigal thannila mithanthu payir adiyila ottikkum.\n• Nerukkamaana payiril ilaigal urasum pothu poonjai vegama paravum.\n• Intha sclerotia mannil oru varushathukku mela uyiroda irukkum.\n[Needs expert review]"
        ,
        "favourable_conditions_en": "• Warm temperatures (28°C to 32°C) combined with high relative humidity of 85% to 100%.\n• Dense plant spacing with lush canopy closure preventing airflow and light penetration.\n• Excess chemical nitrogen and continuous deep standing water in the field.",
        "favourable_conditions_ta": "• 28°C முதல் 32°C வெப்பநிலை மற்றும் 85% முதல் 100% வரையிலான அதிக ஈரப்பதம்.\n• பயிர்கள் மிகவும் நெருக்கமாக இருத்தல் மற்றும் சூரிய ஒளி தரைப்பகுதியில் படாமல் இருத்தல்.\n• அதிகப்படியான யூரியா பயன்பாடு மற்றும் வயலில் தொடர் ஆழமான நீர் தேக்கம்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "favourable_conditions_tanglish": "• 28°C - 32°C veppanilai mattrum 85%-100% athiga eerappatham.\n• Payir romba nerukkama irunthu kaathottam sooriyan velicham illama irunthaal.\n• Athiga urea nitrogen mattrum thodarnthu thengi nirkum thanni.\n[Needs expert review]",

        "prevention_before_planting_en": "• Avoid excessive plant density; adopt recommended spacing (e.g., 20 x 15 cm) for proper canopy aeration.\n• Skim and remove floating plant debris and sclerotia during final puddling.\n• Apply recommended balanced basal nutrients and well-decomposed organic manure.",
        "prevention_before_planting_ta": "• பயிர்கள் நெருக்கமாக இருப்பதைத் தவிர்த்து சரியான இடைவெளியில் நடவு செய்யவும்.\n• நடவு வயல் தயாரிக்கும் போது மிதக்கும் பயிர்க் கழிவுகளையும் பூஞ்சை உருண்டைகளையும் அரித்து அகற்றவும்.\n• பரிந்துரைக்கப்பட்ட சரிவிகித அடி உரங்கள் மற்றும் தொழு உரத்தை இடவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_before_planting_tanglish": "• Nerukkattai thavirthu sariyaana idai veliyil nadavu seiyavum.\n• Mudivu uzhavil thannila mithakkum thaalgal mattrum sclerotia-va arithu edukavum.\n• Sariyana adi uram mattrum thozhu uram idavum.\n[Needs expert review]",

        "prevention_during_crop_en": "• Practice alternate wetting and drying (AWD) to drain the field periodically and lower humidity at the base.\n• Avoid excess urea; apply nitrogen strictly in split applications with balanced potash.\n• Keep bunds free of grassy weeds.",
        "prevention_during_crop_ta": "• தூரின் அடிப்பகுதியில் ஈரப்பதத்தைக் குறைக்க காய்ச்சலும் பாய்ச்சலுமாக நீர்ப்பாசனம் செய்யவும்.\n• அதிகப்படியான யூரியாவைத் தவிர்த்து, சாம்பல் சத்துடன் தவணைகளாக இடவும்.\n• வரப்புகளில் உள்ள களைப் புற்களை சுத்தமாக வைத்திருக்கவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_during_crop_tanglish": "• Kaichalum paichalumaaga thanni paasanam panni adi paguthiyil eerappathathai kuraikkavum.\n• Athiga urea-va thavirthu potash-oda sernthu split panni podavum.\n• Varappula ulla pull kalaigalai azhithuvidavum.\n[Needs expert review]",

        "prevention_after_harvest_en": "• Deep summer ploughing to bury fungal sclerotia deep into the soil profile.\n• Burn or compost infected straw completely; do not spread raw straw onto fields.\n• Rotate crops with non-graminaceous crops like pulses.",
        "prevention_after_harvest_ta": "• பூஞ்சை மணிகளை மண்ணில் புதைத்து அழிக்க கோடை உழவு செய்யவும்.\n• பாதிக்கப்பட்ட வைக்கோலை மக்க வைக்கவும்; பச்சையாக வயலில் பரப்ப வேண்டாம்.\n• பயறு வகை பயிர்களுடன் பயிர் சுழற்சி மேற்கொள்ளவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_after_harvest_tanglish": "• Kodai uzhavu panni sclerotia-va mannil pudhaithu azhikkavum.\n• Paathikkapatta vaikkolai makka vaikkavum.\n• Payaru vachu crop rotation seiyavum.\n[Needs expert review]",

        "prevention_to_limit_spread_en": "• Drain standing irrigation water immediately to prevent sclerotial spread.\n• Stop nitrogen top-dressing completely.\n• Consult your Assistant Agriculture Officer for authorized TNAU-approved bio-control or management options.",
        "prevention_to_limit_spread_ta": "• பூஞ்சை பரவுவதைத் தடுக்க தேங்கிய பாசன நீரை உடனடியாக வடித்துவிடவும்.\n• யூரியா மேலுரமிடுவதை முழுமையாக நிறுத்தவும்.\n• TNAU பரிந்துரைத்த பாதுகாப்பு வழிகாட்டலுக்கு வட்டார வேளாண் அலுவலரை அணுகவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_to_limit_spread_tanglish": "• Thanni moolama noi paravama irukka thengiya thanniya udane vadikkavum.\n• Urea poduratha udane stop pannunga.\n• TNAU approved advice pera agriculture officer-ah sandhikavum.\n[Needs expert review]",

        "when_to_call_officer_en": "• Contact your Agriculture Officer if snake-skin banded lesions reach the top third of tillers.\n• If panicles are unable to emerge from rotten sheaths.\n• Seek advice on authorized eco-friendly bio-fungicide alternatives.",
        "when_to_call_officer_ta": "• பாம்புத் தோல் கருகல் தண்டின் மேல் பகுதி வரை பரவினால் உடனே வேளாண் அலுவலரை அணுகவும்.\n• அழுகிய உறைக்குள் கதிர் வெளிவர முடியாமல் சிக்கினால் தகவல் தெரிவிக்கவும்.\n• பரிந்துரைக்கப்பட்ட இயற்கை நுண்ணுயிர் பூஞ்சைக்கொல்லிகள் பற்றி ஆலோசனை பெறவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "when_to_call_officer_tanglish": "• Banded karugal thandin mael paguthi varai erinaal agriculture officer-ah sandhikavum.\n• Kathir veliye varama azhugal ulla maattikittaal officer kitta sollavum.\n• Bio-control aalosanai kettukollavum.\n[Needs expert review]",

        "similar_looking_problems_en": "• Sheath Rot: produces continuous greyish-brown rot on the flag leaf sheath without snake-skin bands.\n• Stem Rot: produces black shiny lesions on stem culms at water level, causing stem hollow rot.\n• Bacterial Leaf Blight: blighting is on leaf blades with wavy edges, not on leaf sheaths.",
        "similar_looking_problems_ta": "• உறை அழுகல்: கொடி இலை உறையில் ஒரே சீரான பழுப்பு அழுகல் தோன்றும்; பாம்புத் தோல் பட்டைகள் இருக்காது.\n• தண்டு அழுகல்: நீர்மட்டத்தில் தண்டுப் பகுதியில் பளபளப்பான கறுப்புப் புள்ளிகள் தோன்றி தண்டு அழுகும்.\n• பாக்டீரியா இலைக்கருகல்: இலை உறைகளில் தோன்றாது; இலைப்பரப்பில் அலை போன்ற விளிம்புடன் தோன்றும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "similar_looking_problems_tanglish": "• Sheath Rot: Kodi ilai uraila seerana brown azhugal varum; bands irukkadhu.\n• Stem Rot: Thanni mattathula thandula shiny black azhugal vanthu thandu ulla azhugum.\n• BLB: Ilai uraila varathu, ilai parappula wavy borders-oda varum.\n[Needs expert review]"
    },

    "false_smut": {
        "name_tanglish": "False Smut (Kari poottai noi)",
        "symptoms_summary_en": "Individual grains transform into large velvety yellow-orange or greenish-black smut balls.\nGrain balls burst open, releasing powdery spores that contaminate adjacent healthy grain panicles.",
        "symptoms_summary_ta": "தனித்தனி நெல் மணிகள் உருமாறி பஞ்சு போன்ற பெரிய மஞ்சள்-ஆரஞ்சு அல்லது கரும்பச்சை நிறப் பந்துகளாக மாறும்.\nஇப்பந்துகள் வெடித்து தூள் போன்ற வித்துக்கள் வெளியாகி பக்கத்து நெல் மணிகளைப் பாழ்படுத்தும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "symptoms_summary_tanglish": "Thani thani nel manigal maarithu velvety yellow-orange illa karuppu panthu maathiri smut balls aagum.\nPanthugal vedithu powder maathiri spores veliye vanthu pakkathu manigalaiyum paazhaakkum.\n[Needs expert review]",

        "symptoms_leaf_en": [
            "1. Leaf appearance: Leaves generally remain green and symptomless; disease targets the developing flowers and grains.",
            "2. Floral infection: Fungal mycelium invades ovary tissue during the flowering/booting stage.",
            "3. Smut ball swelling: Grains swell into yellowish-orange globose velvety balls, twice the size of normal grains.",
            "4. Maturation to black: Smut balls turn dark olive-green to greenish-black, bursting and releasing powdery chlamydospores."
        ],
        "symptoms_leaf_ta": [
            "1. இலைகள்: இலைகளில் பாதிப்பு தெரியாது; நோய் நேரடியாக பூ மற்றும் தானியங்களைத் தாக்கும்.",
            "2. பூப் பருவம்: பூக்கும் தருணத்தில் பூஞ்சை கருப்பையைத் தாக்கும்.",
            "3. மஞ்சள் பந்து உருவாதல்: நெல் மணிகள் சாதாரண அளவை விட இரு மடங்கு பெரிதாகி பஞ்சு போன்ற மஞ்சள் பந்தாக மாறும்.",
            "4. கறுப்பாக மாறுதல்: முதிர்ந்த பந்துகள் கரும்பச்சை அல்லது கறுப்பாக மாறி வெடித்து தூள்களைக் கக்கும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]"
        ],
        "symptoms_leaf_tanglish": [
            "1. Ilai: Ilaila ethuvum arikuri irukkadhu; noi neradiyaaga kathir manigalai thakkum.",
            "2. Pookkum neram: Pookkum pothu poonjai ulla nuzhaiyum.",
            "3. Manjal panthu: Nel mani nalla perisaagi velvety yellow panthu maathiri aagum.",
            "4. Karuppaga maaruthal: Mudinthathum dark green/karuppaagi vedithu powder spores-ah veliyidum.\n[Needs expert review]"
        ],

        "symptoms_other_parts_en": "• Panicles: conspicuous yellow-orange and greenish-black smut balls scatter across the panicle.\n• Grains: infected grains are completely replaced by fungal spore masses; adjacent grains become sterile.",
        "symptoms_other_parts_ta": "• கதிர்கள்: கதிர்களில் தனித்தனியாகப் பஞ்சு போன்ற மஞ்சள் மற்றும் கறுப்புப் பந்துகள் தென்படும்.\n• தானியங்கள்: பாதிக்கப்பட்ட மணிகள் முழுமையாக பூஞ்சை உருண்டையாக மாறி சுற்றியுள்ள மணிகளையும் பதராக்கும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "symptoms_other_parts_tanglish": "• Kathir: Kathir muzhuka velvety yellow mattrum karuppu smut balls thondrum.\n• Nel mani: Nel manikku pathila poonjai balls aagi pakkathu manigalaiyum padhar aakkum.\n[Needs expert review]",

        "how_to_check_en": [
            "Are individual rice grains on the panicle replaced by large velvety yellow or orange balls?",
            "Have some older balls turned greenish-black and powdery?",
            "Do the smut balls rupture when touched, leaving black or orange powder on your fingers?",
            "Did the infection appear during a cloudy, rainy flowering period?"
        ],
        "how_to_check_ta": [
            "கதிரில் உள்ள தனித்தனி நெல் மணிகள் பெரிய மஞ்சள் அல்லது ஆரஞ்சு நிற பஞ்சு பந்துகளாக மாறியுள்ளதா?",
            "முதிர்ந்த பந்துகள் கரும்பச்சை அல்லது கறுப்பாக மாறி தூள் போல் உள்ளதா?",
            "தொடும் போது விரல்களில் மஞ்சள் அல்லது கறுப்பு தூள் ஒட்டுகிறதா?",
            "பூக்கும் தருணத்தில் மேகமூட்டம் மற்றும் மழை இருந்ததா?\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]"
        ],
        "how_to_check_tanglish": [
            "Kathirula nel manikku pathila periya velvety yellow-orange balls irukka?",
            "Chila pazhaiya balls dark greenish-black-ah maarirukka?",
            "Thottu paatha kaiyila karuppu illa orange powder ottutha?",
            "Pookkum nerathil megamootamum mazhaiyum irunthutha?\n[Needs expert review]"
        ],

        "how_it_spreads_en": "• Fungal spores (chlamydospores and ascospores) survive in soil and on infected seeds.\n• Spores become airborne during cloudy rainy weather and infect floral spikelets during heading.\n• High nitrogen levels combined with intermittent rains during flowering accelerate disease.",
        "how_it_spreads_ta": "• பூஞ்சை வித்துக்கள் மண்ணிலும் விதைகளிலும் உயிர்வாழ்கின்றன.\n• மழை மற்றும் மேகமூட்டமான நாட்களில் காற்றில் மிதந்து பூக்கும் தருணத்தில் பூக்களைத் தாக்குகின்றன.\n• அதிகப்படியான யூரியா மற்றும் பூக்கும் போது பெய்யும் மழை இந்நோயைத் தூண்டுகிறது.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "how_it_spreads_tanglish": "• Poonjai spores mannilum vidhaiyilum thangi irukkum.\n• Mazhai megamootathula kaathula paravi pookkum pothu kathira thakkum.\n• Athiga urea nitrogen mattrum pookkum nerathu mazhai noiya vegamaakkum.\n[Needs expert review]"
        ,
        "favourable_conditions_en": "• Moderate temperatures (25°C to 30°C) with relative humidity exceeding 90%.\n• Continuous overcast, rainy days and high morning relative humidity during flowering.\n• Excessive nitrogen top-dressing at late vegetative and panicle initiation stages.",
        "favourable_conditions_ta": "• 25°C முதல் 30°C வெப்பநிலை மற்றும் 90%க்கும் அதிகமான காற்றில் ஈரப்பதம்.\n• பூக்கும் தருணத்தில் நீடிக்கும் மேகமூட்டம், தூறல் மழை மற்றும் காலைப் பனி.\n• கதிர் வரும் தருணத்தில் அளவுக்கு அதிகமாக யூரியா இடுதல்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "favourable_conditions_tanglish": "• 25°C - 30°C veppam mattrum 90% mela athiga eerappatham.\n• Pookkum nerathil thodarnthu megamootam, thooral mazhai mattrum pani irunthaal.\n• Kathir varum nerathil athiga urea poduvathu.\n[Needs expert review]",

        "prevention_before_planting_en": "• Use certified, pathogen-free paddy seeds from reliable seed centers.\n• Perform certified hot water seed treatment or biocontrol seed dressing as per TNAU guide.\n• Deep summer ploughing to invert and bury soil-borne resting spores.",
        "prevention_before_planting_ta": "• சான்றளிக்கப்பட்ட நோய் தாக்காத தரமான நெல் விதைகளைப் பயன்படுத்தவும்.\n• TNAU வழிகாட்டியின்படி சான்றளிக்கப்பட்ட விதை நேர்த்தி முறையை பின்பற்றவும்.\n• கோடை உழவு செய்து மண்ணில் உள்ள வித்துக்களை சூரிய ஒளியில் அழிக்கவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_before_planting_tanglish": "• Certified disease-free vidhaigalai use pannunga.\n• TNAU guide padi vidhai nerthi kandippa seiyavum.\n• Kodai uzhavu panni mannil ulla spores azhiya nalla veyilil kaaya vaikkavum.\n[Needs expert review]",

        "prevention_during_crop_en": "• Avoid excess nitrogen fertilizer during boot leaf and flowering stages.\n• Maintain balanced split applications of potassium fertilizer.\n• Avoid excessive stagnation of water around heading phase.",
        "prevention_during_crop_ta": "• கொடி இலை மற்றும் பூக்கும் பருவத்தில் அதிகப்படியான யூரியா இடுவதைத் தவிர்க்கவும்.\n• பரிந்துரைக்கப்பட்ட பொட்டாஷ் உரத்தைச் சரியான தவணைகளில் இடவும்.\n• கதிர் வெளிவரும் போது வயலில் அதிக நீர் தேங்காமல் பார்த்துக் கொள்ளவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_during_crop_tanglish": "• Kodi ilai mattrum pookkum nerathil athiga urea poduvathai thavirkkavum.\n• Potash urathai sariyaana thavanaiyil idavum.\n• Kathir varum nerathil vayalla athiga thanni thengaama paathukonga.\n[Needs expert review]",

        "prevention_after_harvest_en": "• Rogue out and bag individual smutted heads carefully before combining to prevent scattering spores.\n• Clean seeds thoroughly to eliminate smut balls before storing for future seed purpose.\n• Plough field deeply post-harvest to incorporate remaining stubble.",
        "prevention_after_harvest_ta": "• அறுவடையின் போது வித்துக்கள் பரவாமல் இருக்க கரிப்பூட்டை கதிர்களை கவனமாகப் பையில் சேகரித்து அழிக்கவும்.\n• விதைகளைச் சேமிக்கும் முன் கரிப்பூட்டை மணிகளை முழுமையாக நீக்கி சுத்தம் செய்யவும்.\n• அறுவடை முடிந்தவுடன் நிலத்தை ஆழமாக உழவு செய்யவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_after_harvest_tanglish": "• Spores paravama irukka smutted panicles-ai cover-la eduthu azhikkavum.\n• Vidhaiya store pannum munnadi smut balls-ai nalla clean panni edukavum.\n• Aruvadai mudintha udane aazhamaaga uzhavu seiyavum.\n[Needs expert review]",

        "prevention_to_limit_spread_en": "• Carefully hand-pick smut balls into a plastic bag before harvest to avoid contaminating the threshing floor.\n• Do not apply late nitrogen fertilizer.\n• Consult your Agriculture Officer for safe pre-booting advisory during cloudy rainy seasons.",
        "prevention_to_limit_spread_ta": "• அறுவடைக்கு முன் கரிப்பூட்டை உருண்டைகளை ஒரு பையில் சேகரித்து அப்புறப்படுத்தவும்.\n• பிந்திய பருவத்தில் யூரியா இடுவதை தவிர்க்கவும்.\n• மேகமூட்டமான காலங்களில் கதிர் வரும் முன் உரிய பாதுகாப்பு ஆலோசனைக்கு வேளாண் அலுவலரை அணுகவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_to_limit_spread_tanglish": "• Kalathula paravama irukka smut balls-ai cover-la eduthu clean pannunga.\n• Late-ah urea nitrogen podatheenga.\n• Pookkum munnadi TNAU advice pera agriculture officer-ah sandhikavum.\n[Needs expert review]",

        "when_to_call_officer_en": "• Contact your Agriculture Officer if smut balls appear across many panicles in your field.\n• Seek advice on safe seed certification and post-harvest cleaning methods.",
        "when_to_call_officer_ta": "• வயலில் பல கதிர்களில் கரிப்பூட்டை உருண்டைகள் தென்பட்டால் உடனே வேளாண் அலுவலரை அணுகவும்.\n• விதை சுத்திகரிப்பு மற்றும் பாதுகாப்பு முறைகள் பற்றி ஆலோசனை பெறவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "when_to_call_officer_tanglish": "• Vayalil athiga kathirgalil smut balls vantha udane agriculture officer-ah sandhikavum.\n• Vidhai clean pannum murai patri aalosanai kettukollavum.\n[Needs expert review]",

        "similar_looking_problems_en": "• False Smut produces distinctive velvety yellow-orange balls, whereas healthy grains are smooth and cream.\n• Grain Discolouration causes dark brown spotted hulls, not swollen velvety balls.\n• Udbatta Disease causes panicles to emerge as a continuous whitish-grey cylindrical rod.",
        "similar_looking_problems_ta": "• கரிப்பூட்டை நோய் தனித்துவமான மஞ்சள்-ஆரஞ்சு பஞ்சு பந்துகளை உருவாக்கும்.\n• தானிய நிறமாற்றம் மணிகளில் கரும்புள்ளிகளை உண்டாக்குமே தவிர பஞ்சு போன்ற உருண்டைகளை உருவாக்காது.\n• உத்பட்டா நோய் கதிர்களை மெல்லிய உருளைக் கோல் போல் வெண்மையாக மாற்றும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "similar_looking_problems_tanglish": "• False Smut distinctive velvety yellow-orange balls tharum; healthy mani smooth cream-ah irukkum.\n• Grain discoloration nel umimeethu karuppu pulligal tharum; swollen balls aagathu.\n• Udbatta noi kathirai silambal cylindrical rod maathiri aakkum.\n[Needs expert review]"
    },

    "leaf_scald": {
        "name_tanglish": "Leaf Scald (Ilai Veliral noi)",
        "symptoms_summary_en": "Large zonate or chevron lesions starting from leaf tips and margins with alternating light and dark brown bands.\nInfected leaf tips look scalded by hot water, drying and splitting into a ragged bleached appearance.",
        "symptoms_summary_ta": "இலை நுனி மற்றும் ஓரங்களிலிருந்து தொடங்கும் சுடுதண்ணீர் பட்டது போன்ற வளைந்த பட்டைக் கருகல்.\nஒன்று மாற்றி ஒன்றாக வெளிர் மற்றும் அடர் பழுப்பு வளையங்கள் தோன்றி இலை நுனி காய்ந்து வெளிறும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "symptoms_summary_tanglish": "Ilai nuni mattrum orathula chevron valaiyagalaga alternating light/dark brown bands aagi karugum.\nHot water oothina maathiri scald aagi ilai nuni split aagi bleached aagum.\n[Needs expert review]",

        "symptoms_leaf_en": [
            "1. Tip scald: Begins near leaf tips or margins as water-soaked olive-green oblong blotches.",
            "2. Chevron banding: Lesions expand rapidly, developing characteristic alternating concentric bands of light and dark brown.",
            "3. Bleached drying: As lesions dry, centers turn dull straw-colored with dark brown undulating margins.",
            "4. Scalded canopy: Leaves look scalded, brittle, and frayed at the tips, curling inward."
        ],
        "symptoms_leaf_ta": [
            "1. நுனி வெளிரல்: இலை நுனி அல்லது விளிம்புகளில் நீர் ஊறிய ஆலிவ்-பச்சை நிறப் புள்ளிகள் தோன்றும்.",
            "2. வளையப் பட்டைகள்: வெளிர் மற்றும் அடர் பழுப்பு நிறத்தில் மாறி மாறி அமைந்த வளையப் பட்டைகளாக விரிவடையும்.",
            "3. காய்ந்து வெளிறல்: கருகலின் மையப்பகுதி வைக்கோல் போல் வெளிறி விளிம்பு அடர் பழுப்பாக மாறும்.",
            "4. சுட்ட தோற்றம்: இலை நுனிகள் கொதிக்கும் நீர் பட்டது போல் கருகி சுருண்டு உடையும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]"
        ],
        "symptoms_leaf_tanglish": [
            "1. Nuni scald: Ilai nuni orathula olive-green water-soaked blotches thondrum.",
            "2. Chevron banding: Light mattrum dark brown alternating concentric valaiyagalaga viriyum.",
            "3. Bleached drying: Nadu paguthi straw colour aagi border dark brown aagum.",
            "4. Scalded thotram: Hot water patta maathiri ilai nuni brittle aagi curl aagum.\n[Needs expert review]"
        ],

        "symptoms_other_parts_en": "• Leaf collar: infection can spread to leaf collars, girdling and withering upper blades.\n• Panicles: emerging grains may become spotted and chaffy if flag leaf scald is severe.",
        "symptoms_other_parts_ta": "• இலைக் கழுத்து: கழுத்துப் பகுதி வரை பரவி மேல் இலைகளைக் காய வைக்கும்.\n• கதிர்: கொடி இலை கடுமையாகப் பாதிக்கப்பட்டால் கதிர் மணிகள் சிறுத்துப் பதராகும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "symptoms_other_parts_tanglish": "• Ilai collar: Collar varai paravi mael ilaigalai kaaya vaikkum.\n• Kathir: Kodi ilai romba paathikkapattaal nel mani padhar aagum.\n[Needs expert review]",

        "how_to_check_en": [
            "Do leaf lesions show concentric chevron or banded patterns of alternating light and dark brown?",
            "Did the lesion start from the leaf tip or margin and move downward like hot-water scalding?",
            "Is the infected leaf tip brittle, dry, and frayed?",
            "Are there no wavy bacterial margins, distinguishing it from Bacterial Leaf Blight?"
        ],
        "how_to_check_ta": [
            "கருகல் வெளிர் மற்றும் அடர் பழுப்பு நிறத்தில் வளைய வளையமான பட்டைகளாக உள்ளதா?",
            "இலை நுனியிலிருந்து சுடுநீர் பட்டது போல் கீழ்நோக்கி பரவியுள்ளதா?",
            "பாதிக்கப்பட்ட இலை நுனி காய்ந்து எளிதில் உடையும் நிலையில் உள்ளதா?",
            "பாக்டீரியா இலைக்கருகல் போன்ற அலை அலையான விளிம்பு இல்லாமல் பட்டைகளாக உள்ளதா?\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]"
        ],
        "how_to_check_tanglish": [
            "Lesions concentric chevron light/dark brown alternating bands maathiri irukka?",
            "Hot water patta maathiri ilai nuniyilirunthu keezhe paravutha?",
            "Infected ilai nuni brittle-aagi kaanjirukka?",
            "BLB maathiri wavy border illama chevron bands-oda irukka?\n[Needs expert review]"
        ],

        "how_it_spreads_en": "• Seed-borne fungal pathogen (Microdochium oryzae) that survives on seeds and crop stubbles.\n• Conidia are splash-dispersed by raindrops and carried by wind during humid cloudy weather.\n• Frequent storms, high nitrogen, and dense canopies accelerate field spread.",
        "how_it_spreads_ta": "• விதைகள் மற்றும் முந்தைய பயிர்க் கழிவுகளில் பூஞ்சை உயிர்வாழ்கிறது.\n• மழைத்துளிகள் மற்றும் காற்றில் வித்துக்கள் பக்கத்துப் பயிர்களுக்குப் பரவுகின்றன.\n• பலத்த காற்று, அதிக தழைச்சத்து மற்றும் நெருக்கமான நடவு பரவுவதை விரைவுபடுத்துகிறது.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "how_it_spreads_tanglish": "• Vidhaigal mattrum palaiya thaalgalil poonjai thangi irukkum.\n• Mazhai thuligal mattrum kaathula spores adutha payirukku paravum.\n• Kaatru, athiga urea nitrogen mattrum nerukkamaana nadavu noiya paravum.\n[Needs expert review]",

        "favourable_conditions_en": "• Temperatures of 22°C to 28°C accompanied by high relative humidity (above 85%).\n• Frequent wet weather, rains, and heavy dew keeping foliage wet for long periods.\n• Excess nitrogen fertilizer and closely planted crop stands.",
        "favourable_conditions_ta": "• 22°C முதல் 28°C வெப்பநிலை மற்றும் 85%க்கும் அதிகமான காற்றில் ஈரப்பதம்.\n• தொடர் மழை, தூறல் மற்றும் நீண்ட நேரம் இலைகளில் நீடிக்கும் பனிப்பொழிவு.\n• அளவுக்கு அதிகமான யூரியா பயன்பாடு மற்றும் நெருக்கமான நடவு.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "favourable_conditions_tanglish": "• 22°C - 28°C veppam mattrum 85% mela athiga eerappatham.\n• Thodarnthu mazhai, thooral mattrum neelikkum pani thuligal.\n• Athiga urea nitrogen mattrum romba nerukkamaana nadavu.\n[Needs expert review]",

        "prevention_before_planting_en": "• Use certified clean seeds and perform seed treatment as recommended in the TNAU guide.\n• Adopt optimal planting spacing to allow sunlight penetration and canopy aeration.\n• Incorporate crop stubble with deep summer ploughing.",
        "prevention_before_planting_ta": "• TNAU பரிந்துரைப்படி சான்றளிக்கப்பட்ட விதை நேர்த்தி முறையை பின்பற்றவும்.\n• சூரிய ஒளி படவும் காற்றோட்டம் கிடைக்கவும் சரியான இடைவெளியில் நடவு செய்யவும்.\n• பயிர்க் கழிவுகள் மக்க கோடை உழவு செய்யவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_before_planting_tanglish": "• TNAU guide padi certified vidhai nerthi kandippa seiyavum.\n• Sooriyan velicham kaathottam kidaikka sariyaana spacing vachu nadavum.\n• Kodai uzhavu panni thaalgalai makka vaikkavum.\n[Needs expert review]",

        "prevention_during_crop_en": "• Apply nitrogen fertilizer in split doses; avoid heavy late applications.\n• Apply recommended balanced potash to strengthen leaf tissues.\n• Avoid field submergence and maintain proper drainage.",
        "prevention_during_crop_ta": "• தழைச்சத்தை தவணைகளாகப் பிரித்து இடவும்; பிந்திய பருவத்தில் அதிக யூரியாவைத் தவிர்க்கவும்.\n• இலைத் திசுக்களை வலுப்படுத்த பரிந்துரைக்கப்பட்ட பொட்டாஷ் உரத்தை இடவும்.\n• வயலில் அதிக நீர் தேங்குவதைத் தவிர்த்து நல்ல வடிகால் வசதி செய்யவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_during_crop_tanglish": "• Urea-va split panni podavum; late stage-la athiga urea thavirkkavum.\n• Ilai tissues strong aaga potash uram idavum.\n• Vayalla athiga thanni thengaama nalla vadigaal maintain seiyavum.\n[Needs expert review]",

        "prevention_after_harvest_en": "• Remove and destroy infected straw and harvest debris.\n• Practice crop rotation with non-host pulses.\n• Do not retain seeds from severely infected fields for future sowing.",
        "prevention_after_harvest_ta": "• பாதிக்கப்பட்ட பயிர்க் கழிவுகளையும் வைக்கோலையும் வயலிலிருந்து அகற்றவும்.\n• பயறு வகைப் பயிர்களுடன் பயிர் சுழற்சி செய்யவும்.\n• இந்நோய் தாக்கிய நிலத்திலிருந்து பெறப்பட்ட விதைகளை அடுத்த சாகுபடிக்கு பயன்படுத்த வேண்டாம்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_after_harvest_tanglish": "• Paathikkapatta thaalgalai azhithu clean pannavum.\n• Payaru payirgaludan crop rotation seiyavum.\n• Noi thonriya vayalilirunthu edutha vidhaigalai adutha season-kku use panna koodadhu.\n[Needs expert review]",

        "prevention_to_limit_spread_en": "• Stop further nitrogen top-dressing immediately.\n• Ensure field drainage is functioning to prevent humidity buildup.\n• Consult your local Agriculture Officer for certified management guidance.",
        "prevention_to_limit_spread_ta": "• கூடுதல் யூரியா இடுவதை உடனடியாக நிறுத்தவும்.\n• காற்றில் ஈரப்பதம் குறைய வயலில் உள்ள அதிகப்படியான நீரை வடிக்கவும்.\n• சரியான மேலாண்மை வழிகாட்டலுக்கு வட்டார வேளாண் அலுவலரை அணுகவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_to_limit_spread_tanglish": "• Urea nitrogen poduvathai udane stop pannunga.\n• Eerappatham kuraikka vayal thanniya vadithuvidavum.\n• TNAU approved advice pera agriculture officer-ah sandhikavum.\n[Needs expert review]",

        "when_to_call_officer_en": "• Contact your Agriculture Officer if chevron banded scald spreads to upper canopy leaves.\n• If distinguishing between bacterial blight and fungal leaf scald is uncertain.\n• Follow official extension guidelines rather than unverified commercial formulations.",
        "when_to_call_officer_ta": "• வளையப் பட்டைக் கருகல் மேல் இலைகள் வரை பரவினால் உடனே வேளாண் அலுவலரை அணுகவும்.\n• இது பாக்டீரியா கருகலா அல்லது பூஞ்சை வெளிரலா என்ற சந்தேகம் இருந்தால் ஆய்வு பெறவும்.\n• வேளாண் துறை ஆலோசனைகளை மட்டுமே பின்பற்றவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "when_to_call_officer_tanglish": "• Chevron banded scald mael ilaigal varai paravinaal agriculture officer-ah sandhikavum.\n• BLB-a illa Leaf Scald-a nu sandhegam irunthaal officer kitta kaattavum.\n• Official extension aalosanai padi nadavadikkai edunga.\n[Needs expert review]",

        "similar_looking_problems_en": "• Bacterial Leaf Blight: has wavy undulating margins without concentric zonate bands.\n• Brown Spot: spots are small and oval/circular with yellow halos, not large tip scalds.\n• Drought Scorch: uniform tip drying without alternating dark and light brown chevron bands.",
        "similar_looking_problems_ta": "• பாக்டீரியா இலைக்கருகல்: அலை அலையான விளிம்புகளுடன் இருக்கும்; வளையப் பட்டைகள் இருக்காது.\n• பழுப்பு புள்ளி நோய்: எள் போன்ற சிறு உருண்டை புள்ளிகளாக இருக்கும்; பெரிய நுனி வெளிரலாக இருக்காது.\n• வறட்சி கருகல்: நுனி காய்ந்திருக்கும் ஆனால் மாறி மாறி வரும் வளையப் பட்டைகள் இருக்காது.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "similar_looking_problems_tanglish": "• BLB: Wavy undulating margins irukkum; chevron bands irukkadhu.\n• Brown Spot: Chinna oval ellu spots-aaga irukkum; periya tip scald irukkadhu.\n• Varatchi karugal: Nuni kaanjirukkum aana alternating chevron bands irukkadhu.\n[Needs expert review]"
    },

    "narrow_brown_spot": {
        "name_tanglish": "Narrow Brown Leaf Spot (Kurugiya Pazhuppu Pulli)",
        "symptoms_summary_en": "Short, narrow, linear reddish-brown streaks running parallel to leaf veins.\nUnlike common brown spot, lesions are elongated lines with no yellow halo, appearing during late growth stages.",
        "symptoms_summary_ta": "இலை நரம்புகளுக்கு இணையாகத் தோன்றும் குறுகிய, நீண்ட நேர்க்கோட்டுச் சிவந்த பழுப்புப் புள்ளிகள்.\nவழக்கமான பழுப்புப் புள்ளியைப் போல் வட்டமாகவோ மஞ்சள் வளையத்துடனோ இருக்காது; பிந்திய பருவத்தில் தோன்றும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "symptoms_summary_tanglish": "Ilai narambukalukku inaiyaga short, narrow, linear reddish-brown streaks varum.\nCommon brown spot maathiri circular/oval-avum yellow halo-vum illama, late stage-la thondrum.\n[Needs expert review]",

        "symptoms_leaf_en": [
            "1. Linear streaks: Lesions appear as short, narrow linear stripes strictly parallel to leaf veins.",
            "2. Coloration: Spots are uniform reddish-brown to dark brown with sharp defined parallel borders.",
            "3. Lack of halo: Unlike common brown spot, lesions have no distinct yellow halo.",
            "4. Late season blighting: In severe cases near maturity, numerous streaks coalesce causing premature leaf drying."
        ],
        "symptoms_leaf_ta": [
            "1. நேர்க்கோட்டுப் புள்ளிகள்: இலை நரம்புகளுக்கு இணையாக குறுகிய மெல்லிய சிவந்த பழுப்பு வரிகளாகத் தோன்றும்.",
            "2. நிறம்: அடர் பழுப்பு அல்லது சிவந்த பழுப்பு நிறத்தில் தெளிவான விளிம்புகளுடன் காணப்படும்.",
            "3. வளையம் இல்லாமை: வழக்கமான பழுப்புப் புள்ளியைப் போல் மஞ்சள் நிற வளையம் இருக்காது.",
            "4. பிந்திய கருகல்: முதிர்ச்சிப் பருவத்தில் பல வரிகள் ஒன்றிணைந்து இலை முன்கூட்டியே காய்ந்துவிடும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]"
        ],
        "symptoms_leaf_tanglish": [
            "1. Linear streaks: Ilai narambukalukku inaiyaga short, narrow stripes varum.",
            "2. Niram: Reddish-brown mudhal dark brown varai sariyaana parallel borders-oda irukkum.",
            "3. Halo illai: Common brown spot maathiri yellow ring irukkadhu.",
            "4. Late stage karugal: Aruvadai nerathil athiga streaks onna sernthu ilai kaanjidum.\n[Needs expert review]"
        ],

        "symptoms_other_parts_en": "• Leaf sheaths: develop narrow brown streaks.\n• Panicles: glumes on grain heads can develop small linear brown spots, leading to grain discolouration.",
        "symptoms_other_parts_ta": "• இலை உறை: குறுகிய பழுப்பு வரிகள் தோன்றும்.\n• கதிர் மணிகள்: உமியின் மேல் சிறிய பழுப்பு கோடுகள் தோன்றி தானிய நிறமாற்றம் ஏற்படும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "symptoms_other_parts_tanglish": "• Ilai urai: Narrow brown streaks thondrum.\n• Kathir: Nel umimeethu chinna brown lines vanthu grain discoloration undaagum.\n[Needs expert review]",

        "how_to_check_en": [
            "Are the spots narrow, short linear streaks running parallel to leaf veins?",
            "Do the spots lack the circular sesame shape and yellow halo of common brown spot?",
            "Are the lesions uniform reddish-brown in colour?",
            "Did the streaks appear primarily during the heading to grain-filling stage?"
        ],
        "how_to_check_ta": [
            "புள்ளிகள் இலை நரம்புகளுக்கு இணையாக குறுகிய நேர்க்கோடுகளாக உள்ளதா?",
            "வழக்கமான பழுப்புப் புள்ளி போல் எள் வடிவமும் மஞ்சள் வளையமும் இல்லாமல் உள்ளதா?",
            "புள்ளிகள் ஒரே சீரான சிவந்த பழுப்பு நிறத்தில் உள்ளதா?",
            "கதிர் வரும் அல்லது பால் பிடிக்கும் பருவத்தில் இந்நோய் தென்படுகிறதா?\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]"
        ],
        "how_to_check_tanglish": [
            "Spots narambukalukku inaiyaga narrow short linear streaks-ah irukka?",
            "Common brown spot maathiri oval ellu shape-um yellow halo-vum illama irukka?",
            "Spots ore seerana reddish-brown colour-la irukka?",
            "Kathir varum nerathil intha arikurigala paarthangala?\n[Needs expert review]"
        ],

        "how_it_spreads_en": "• Seed-borne fungus (Cercospora janseana) that also overwinters on rice stubble.\n• Airborne spores are dispersed by wind during warm humid conditions late in the season.\n• Deficiencies in soil potassium and phosphorus exacerbate disease expression.",
        "how_it_spreads_ta": "• பூஞ்சை விதைகள் மற்றும் பயிர்க் கழிவுகள் மூலம் முதன்மையாகத் தொடங்குகிறது.\n• காற்றில் அடித்துச் செல்லப்படும் வித்துக்கள் மூலம் பிந்திய பருவத்தில் பரவுகிறது.\n• பொட்டாஷ் மற்றும் மணிச்சத்து பற்றாக்குறை இந்நோயின் தீவிரத்தை அதிகரிக்கிறது.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "how_it_spreads_tanglish": "• Vidhaigal mattrum palaiya thaalgalil poonjai thangi irukkum.\n• Kaathula spores paravi late season-la adutha payirukku paravum.\n• Potash mattrum phosphorus satthu kuraipaadu noiyai athigarikkum.\n[Needs expert review]",

        "favourable_conditions_en": "• Warm temperatures (25°C to 32°C) with alternating sunny and humid days.\n• Crops approaching maturity under low soil potassium conditions.\n• Extended leaf moisture from late-season rains and dew.",
        "favourable_conditions_ta": "• 25°C முதல் 32°C வெப்பநிலை மற்றும் காற்றில் ஈரப்பதம்.\n• பயிர் முதிர்ச்சி அடையும் பருவத்தில் பொட்டாஷ் சத்து குறைவாக இருத்தல்.\n• பிந்திய பருவத்து மழை மற்றும் காலைப் பனி.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "favourable_conditions_tanglish": "• 25°C - 32°C veppam mattrum athiga eerappatham.\n• Aruvadai nerungum pothu nilathil potash kammiya irunthaal.\n• Late season mazhai mattrum pani.\n[Needs expert review]",

        "prevention_before_planting_en": "• Use certified disease-free seeds and adopt seed treatment per TNAU guide.\n• Correct soil potassium and phosphorus deficiencies based on soil testing.\n• Incorporate crop stubble with deep tillage.",
        "prevention_before_planting_ta": "• சான்றளிக்கப்பட்ட விதைகளைப் பயன்படுத்தி TNAU பரிந்துரைப்படி விதை நேர்த்தி செய்யவும்.\n• மண் ஆய்வு பரிந்துரைப்படி பொட்டாஷ் மற்றும் மணிச்சத்தை இடவும்.\n• கோடை உழவு செய்து பயிர்க் கழிவுகளை மக்க வைக்கவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_before_planting_tanglish": "• Certified vidhaigal use panni TNAU guide padi vidhai nerthi seiyavum.\n• Mann test padi potash mattrum phosphorus urangalai idavum.\n• Kodai uzhavu panni thaalgalai makka vaikkavum.\n[Needs expert review]",

        "prevention_during_crop_en": "• Ensure balanced potassium application at active tillering and panicle initiation.\n• Avoid nutrient stress during late grain filling.\n• Maintain regular shallow irrigation.",
        "prevention_during_crop_ta": "• தூர் கட்டும் மற்றும் கதிர் உருவாகும் தருணத்தில் பரிந்துரைக்கப்பட்ட பொட்டாஷ் உரத்தை இடவும்.\n• பிந்திய பருவத்தில் பயிருக்கு ஊட்டச்சத்து பற்றாக்குறை ஏற்படாமல் பராமரிக்கவும்.\n• சீரான நீர்ப்பாசனத்தைப் பராமரிக்கவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_during_crop_tanglish": "• Thoor kattum mattrum kathir varum pothu potash urathai sariyaaga idavum.\n• Late stage-la chathu kuraipaadu varaama paathukonga.\n• Seerana thanni maintain seiyavum.\n[Needs expert review]",

        "prevention_after_harvest_en": "• Plough the field post-harvest to decompose remaining crop straw.\n• Eliminate volunteer rice and grassy weeds on bunds.\n• Do not save seeds from infected fields for next planting.",
        "prevention_after_harvest_ta": "• அறுவடை முடிந்தவுடன் நிலத்தை உழுது பயிர்க் கழிவுகளை மக்க வைக்கவும்.\n• வரப்புகளில் உள்ள களைப் புற்களை அழிக்கவும்.\n• பாதிக்கப்பட்ட நிலத்திலிருந்து பெறப்பட்ட விதைகளை அடுத்த சாகுபடிக்கு பயன்படுத்த வேண்டாம்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_after_harvest_tanglish": "• Aruvadai mudintha udane uzhavu panni thaalgalai makka vaikkavum.\n• Varappula ulla pull kalaigalai azhithuvidavum.\n• Noi vantha vayal vidhaigalai adutha season-kku use panna koodadhu.\n[Needs expert review]",

        "prevention_to_limit_spread_en": "• Ensure adequate soil potassium to prevent premature leaf senescence.\n• Avoid moisture stress during grain filling.\n• Consult your local Agriculture Officer if widespread heading-stage infection occurs.",
        "prevention_to_limit_spread_ta": "• இலைகள் முன்கூட்டியே காய்வதைத் தடுக்க தேவையான பொட்டாஷ் சத்தை இடவும்.\n• தானியம் முதிரும் போது வறட்சி ஏற்படாமல் சீரான பாசனம் செய்யவும்.\n• கதிர் பருவத்தில் பாதிப்பு அதிகமானால் வேளாண் அலுவலரை அணுகவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_to_limit_spread_tanglish": "• Ilai seekiram kaayama irukka thevaiyana potash podavum.\n• Nel mani vilayum pothu varatchi varaama paathukonga.\n• Paathippu athigamaanaal agriculture officer-ah sandhikavum.\n[Needs expert review]",

        "when_to_call_officer_en": "• Consult your Agriculture Officer if narrow brown streaks cover upper flag leaves heavily.\n• Seek advice on variety susceptibility and balanced potassium nutrition.",
        "when_to_call_officer_ta": "• கொடி இலையில் குறுகிய பழுப்பு கோடுகள் அதிகளவில் பரவினால் வேளாண் அலுவலரை அணுகவும்.\n• ரகங்களின் எதிர்ப்புத் திறன் மற்றும் பொட்டாஷ் மேலாண்மை பற்றி ஆலோசனை பெறவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "when_to_call_officer_tanglish": "• Kodi ilaila narrow brown streaks athigama vanthaal agriculture officer-ah sandhikavum.\n• Potash management patri aalosanai peravum.\n[Needs expert review]",

        "similar_looking_problems_en": "• Common Brown Spot: lesions are oval or circular like sesame seeds with yellow halos, not thin linear streaks.\n• Bacterial Leaf Streak: streaks are translucent water-soaked stripes between veins with bacterial beads.\n• Rice Blast: lesions are diamond or spindle shaped with pointed ends and ash-grey centres.",
        "similar_looking_problems_ta": "• பழுப்பு புள்ளி நோய்: எள் போன்ற உருண்டை அல்லது நீள்வட்டப் புள்ளிகளாக மஞ்சள் வளையத்துடன் இருக்கும்.\n• பாக்டீரியா இலைக்கீற்று: நரம்புகளுக்கு இடையே நீர் ஊறிய கோடுகளாகவும் பாக்டீரியா கசிவுடனும் இருக்கும்.\n• குலை நோய்: கூர்மையான முனைகளுடன் ஈட்டி வடிவப் புள்ளிகளாகவும் சாம்பல் மையத்துடனும் இருக்கும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "similar_looking_problems_tanglish": "• Common Brown Spot: Oval ellu shape-la yellow halo-voda irukkum; linear streaks illa.\n• Bacterial Leaf Streak: Narambukalukku idaiyila water-soaked streaks bacterial droplets-oda irukkum.\n• Rice Blast: Spindle diamond shape-la pointed ends mattrum saambal center-oda irukkum.\n[Needs expert review]"
    },

    "other": {
        "name_tanglish": "Leaf Smut / Matra Nel Noigal",
        "symptoms_summary_en": "Small, angular black raised spots (sori) scattered across mature leaf blades like specks of soot or charcoal.\nCaused by Entyloma oryzae during late growth stages; distinct from other spot diseases by its raised, powdery black texture.",
        "symptoms_summary_ta": "முதிர்ந்த இலைகளில் நிலக்கரித் தூள் போன்ற சிறிய, கோண வடிவ மேடான கறுப்புப் புள்ளிகள் தோன்றும்.\nபிந்திய பருவத்தில் என்டிலோமா ஒரைசே பூஞ்சையால் உண்டாகும்; மேடான கறுப்பு தூள் அமைப்பு இதன் அடையாளம்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "symptoms_summary_tanglish": "Muthirntha ilaila kariyathool maathiri chinna raised black spots sori thondrum.\nLate stage-la Entyloma poonjaiyinaal varum; raised powdery black texture ithoda mukkiya அடையாளம்.\n[Needs expert review]",

        "symptoms_leaf_en": [
            "1. Black angular sori: Tiny, slightly raised angular black spots appear scattered across leaf blades.",
            "2. Sooty appearance: Spots look like tiny specks of lead, charcoal, or soot on both leaf surfaces.",
            "3. Epidermal rupture: In moist weather, the epidermis over the black spots ruptures, exposing powdery black spores.",
            "4. Late maturity: Symptoms become noticeable primarily as the crop reaches late grain filling and maturity."
        ],
        "symptoms_leaf_ta": [
            "1. கோணக் கறுப்புப் புள்ளிகள்: இலைப்பரப்பில் சிறிய, சற்றே மேடான கோண வடிவக் கறுப்புப் புள்ளிகள் தோன்றும்.",
            "2. நிலக்கரித் தூள் தோற்றம்: இலைகளின் இருபுறமும் கரிக்கூடு அல்லது கரித்தூள் போன்ற புள்ளிகள் காணப்படும்.",
            "3. தோல் வெடிப்பு: காற்றில் ஈரப்பதம் உள்ள போது புள்ளிகளின் மேல் உள்ள தோல் வெடித்து கறுப்புத் தூள் வெளியாகும்.",
            "4. பிந்திய பருவம்: கதிர் முதிர்ச்சி அடையும் பிந்திய பருவத்தில் மட்டுமே இந்நோய் வெளிப்படும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]"
        ],
        "symptoms_leaf_tanglish": [
            "1. Angular black sori: Ilaila chinna slightly raised angular black spots thondrum.",
            "2. Kariyathool thotram: Ilaiyin iru puramum charcoal soot speckles maathiri irukkum.",
            "3. Thol vedippu: Eerappatham irukkum pothu spots mela ulla layer vedithu black powder veliyidum.",
            "4. Late paruvam: Payir muthirchi aagum late grain-filling stage-la thaan arikurigal theriyum.\n[Needs expert review]"
        ],

        "symptoms_other_parts_en": "• Leaf sheaths: occasional small black sori may develop on mature sheaths.\n• Panicles: does not directly attack grain ears, but severe leaf blighting causes premature senescence.",
        "symptoms_other_parts_ta": "• இலை உறை: முதிர்ந்த இலை உறைகளிலும் சில நேரங்களில் சிறிய கறுப்புப் புள்ளிகள் தோன்றும்.\n• கதிர்: தானியங்களை நேரடியாகத் தாக்காது; இலைகள் முன்கூட்டியே காய்வதால் தானியம் பாதிக்கப்படலாம்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "symptoms_other_parts_tanglish": "• Ilai urai: Chila nerangalil urailayum chinna black sori varalam.\n• Kathir: Manigalai neradiyaaga thakkathu; ilai seekiram kaayvathaal indirect loss varalam.\n[Needs expert review]",

        "how_to_check_en": [
            "Are the spots tiny, slightly raised, angular black specks like charcoal dust on the leaf?",
            "Do the spots lack yellow halos and stay small without enlarging into oval lesions?",
            "Does black powdery residue rub off slightly when scraping the mature raised spot?",
            "Did the condition appear late in the season as the crop approached harvest?"
        ],
        "how_to_check_ta": [
            "புள்ளிகள் நிலக்கரித் தூள் போல் சிறிய, சற்றே மேடான கோண வடிவக் கறுப்புப் புள்ளிகளாக உள்ளதா?",
            "மஞ்சள் வளையம் இன்றியும், பெரிய புள்ளிகளாக விரியாமலும் உள்ளதா?",
            "முதிர்ந்த புள்ளிகளைச் சுரண்டினால் லேசான கறுப்புத் தூள் ஒட்டுகிறதா?",
            "அறுவடைக்கு முந்தைய பிந்திய பருவத்தில் இது தென்பட்டதா?\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]"
        ],
        "how_to_check_tanglish": [
            "Spots charcoal dust maathiri chinna raised angular black specks-ah irukka?",
            "Yellow halo illamalum perisaaga viriyamalum chinna pulligalaagave irukka?",
            "Muthirntha spot-ah thottaal black powder residue ottutha?",
            "Aruvadai nerungum late season-la ithu therinthatha?\n[Needs expert review]"
        ],

        "how_it_spreads_en": "• Fungus (Entyloma oryzae) survives as teliospores on infected leaves and crop residue in the soil.\n• Spores are air-borne and splash-dispersed by late rains and heavy morning dew.\n• High plant density and nitrogen-rich soil late in the season promote sporulation.",
        "how_it_spreads_ta": "• மண்ணில் உள்ள பயிர்க் கழிவுகள் மற்றும் பழைய இலைகளில் பூஞ்சை வித்துக்கள் உயிர்வாழ்கின்றன.\n• பிந்திய பருவத்து மழை மற்றும் காலைப் பனி மூலம் காற்றில் அடித்துச் செல்லப்பட்டு பரவுகிறது.\n• அதிகப் பயிர் அடர்த்தி மற்றும் பிந்திய தழைச்சத்து இந்நோயைத் தூண்டுகிறது.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "how_it_spreads_tanglish": "• Mannil ulla palaiya ilai thaalgalil poonjai spores thangi irukkum.\n• Late season mazhai mattrum pani moolama kaathula paravum.\n• Athiga payir nerukkam mattrum late urea poduvathu noiya thoondum.\n[Needs expert review]",

        "favourable_conditions_en": "• Warm temperatures (25°C to 30°C) with high relative humidity late in the crop cycle.\n• Dense canopy closure and excessive late nitrogen applications.\n• Intermittent rains and heavy morning dew keeping senescing leaves wet.",
        "favourable_conditions_ta": "• 25°C முதல் 30°C வெப்பநிலை மற்றும் பிந்திய பருவத்தில் காற்றில் அதிக ஈரப்பதம்.\n• நெருக்கமான நடவு மற்றும் பிந்திய பருவத்தில் இடப்படும் அதிகப்படியான யூரியா.\n• முதிர்ந்த இலைகளில் நீடிக்கும் பனிப்பொழிவு மற்றும் தூறல் மழை.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "favourable_conditions_tanglish": "• 25°C - 30°C veppam mattrum late cycle-la athiga eerappatham.\n• Nerukkamaana payir mattrum late stage-la athiga urea poduvathu.\n• Muthirntha ilaila pani thanni thangi irunthaal.\n[Needs expert review]",

        "prevention_before_planting_en": "• Practice deep summer ploughing to invert and bury infected leaf debris.\n• Use certified clean seeds and adopt recommended spacing for canopy aeration.\n• Maintain balanced soil potassium and organic matter based on soil tests.",
        "prevention_before_planting_ta": "• பயிர்க் கழிவுகள் மக்க கோடை உழவு செய்து மண்ணைப் பண்படுத்தவும்.\n• சான்றளிக்கப்பட்ட விதைகளைப் பயன்படுத்தி சரியான இடைவெளியில் நடவு செய்யவும்.\n• மண் பரிசோதனை அடிப்படையில் பொட்டாஷ் மற்றும் இயற்கை உரங்களை இடவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_before_planting_tanglish": "• Kodai uzhavu panni palaiya thaalgalai makka vaikkavum.\n• Certified seeds use panni sariyaana spacing-la nadavum.\n• Mann test padi potash mattrum thozhu uram idavum.\n[Needs expert review]",

        "prevention_during_crop_en": "• Avoid late-stage nitrogen top-dressing after heading.\n• Ensure balanced potassium nutrition during panicle development.\n• Maintain field drainage and prevent continuous deep water stagnation.",
        "prevention_during_crop_ta": "• கதிர் வெளிவந்த பின் பிந்திய பருவத்தில் யூரியா இடுவதைத் தவிர்க்கவும்.\n• கதிர் உருவாகும் போது பரிந்துரைக்கப்பட்ட பொட்டாஷ் உரத்தைச் சரியான அளவில் இடவும்.\n• வயலில் அதிக நீர் தேங்காமல் முறையான வடிகால் வசதி செய்யவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_during_crop_tanglish": "• Kathir vantha piragu late stage urea poduvathai thavirkkavum.\n• Kathir varum nerathil potash urathai sariyaana alavil idavum.\n• Vayalla athiga thanni thengaama nalla vadigaal maintain seiyavum.\n[Needs expert review]",

        "prevention_after_harvest_en": "• Remove or thoroughly incorporate infected stubble after harvest.\n• Practice crop rotation with non-cereal crops like pulses.\n• Clean threshing and harvesting areas to eliminate residue.",
        "prevention_after_harvest_ta": "• அறுவடைக்குப்பின் பயிர்க் கழிவுகளையும் வைக்கோலையும் வயலில் இருந்து அகற்றவும்.\n• பயறு வகைப் பயிர்களுடன் பயிர் சுழற்சி மேற்கொள்ளவும்.\n• களத்து மேடுகளைச் சுத்தமாகப் பராமரிக்கவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_after_harvest_tanglish": "• Aruvadai mudintha udane thaalgalai azhithuvidavum.\n• Payaru payirgaludan crop rotation seiyavum.\n• Aruvadai idathai clean-ah vechikonga.\n[Needs expert review]",

        "prevention_to_limit_spread_en": "• Stop further chemical nitrogen applications.\n• Generally leaf smut causes minor late damage; chemical sprays are rarely justified.\n• Consult your local Agriculture Officer if unclassified black spots spread prematurely.",
        "prevention_to_limit_spread_ta": "• கூடுதல் யூரியா இடுவதை உடனடியாக நிறுத்தவும்.\n• பொதுவாக இலைக்கரிப்பூட்டை பிந்திய பருவத்தில் குறைந்த சேதத்தையே உண்டாக்கும்; ரசாயன தெளிப்பு தேவையில்லை.\n• கறுப்புப் புள்ளிகள் மிக முன்கூட்டியே அதிகமாகப் பரவினால் வேளாண் அலுவலரை அணுகவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "prevention_to_limit_spread_tanglish": "• Urea poduratha udane stop pannunga.\n• Ithu late stage-la kuraintha paathippu thaan tharum; chemical thevaiye illa.\n• Black spots aarambathiliye athigama vanthaal agriculture officer-ah sandhikavum.\n[Needs expert review]",

        "when_to_call_officer_en": "• Consult your Agriculture Officer if black raised spots appear prematurely during early tillering.\n• If distinguishing between leaf smut and other fungal spots or insect frass is uncertain.\n• Follow official TNAU extension guidelines.",
        "when_to_call_officer_ta": "• தூர் கட்டும் ஆரம்பப் பருவத்திலேயே கறுப்புப் புள்ளிகள் தோன்றினால் வேளாண் அலுவலரை அணுகவும்.\n• இது இலைக்கரிப்பூட்டையா அல்லது பிற நோயா என்ற சந்தேகம் இருந்தால் ஆய்வு பெறவும்.\n• அதிகாரப்பூர்வ வேளாண் வழிகாட்டல்களைப் பின்பற்றவும்.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "when_to_call_officer_tanglish": "• Aaramba thoor paruvathiliye black spots vanthaal agriculture officer-ah sandhikavum.\n• Ithu leaf smut-a illa vera noi-a nu sandhegam irunthaal officer kitta kaattavum.\n• Official TNAU advice kelunga.\n[Needs expert review]",

        "similar_looking_problems_en": "• Brown Spot: spots are oval or circular with grey centres and yellow halos, not black raised sori.\n• Rice Blast: produces diamond spindle-shaped lesions with ash-grey centres, not angular black dots.\n• False Smut: produces large velvety smut balls replacing grains on panicles, not tiny leaf specks.",
        "similar_looking_problems_ta": "• பழுப்பு புள்ளி நோய்: எள் போன்ற உருண்டை அல்லது நீள்வட்டப் புள்ளிகளாக மஞ்சள் வளையத்துடன் இருக்கும்.\n• குலை நோய்: கூர்மையான முனைகளுடன் ஈட்டி வடிவப் புள்ளிகளாகவும் சாம்பல் மையத்துடனும் இருக்கும்.\n• கரிப்பூட்டை நோய்: கதிரில் உள்ள நெல் மணிகளில் பெரிய பஞ்சு பந்துகளை உண்டாக்கும்; இலையில் தோன்றாது.\n[வல்லுநர் சரிபார்ப்பு தேவை / Needs expert review]",
        "similar_looking_problems_tanglish": "• Brown Spot: Oval ellu shape-la yellow halo-voda irukkum; raised black dots illa.\n• Rice Blast: Spindle diamond shape-la pointed ends mattrum saambal center-oda irukkum.\n• False Smut: Kathir manigalai periya velvety balls aakkum; ilaila varathu.\n[Needs expert review]"
    }
}

# Apply updates to database for the 10 diseases
count = 0
for d_key, fields in PHASE2_DATA.items():
    if d_key in db:
        db[d_key].update(fields)
        count += 1

with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print(f"SUCCESS: Enriched {count} disease entries in {DATA_FILE}")
