import json
from pathlib import Path

DATA_FILE = Path(r"C:\Users\keert\paddy_dataset\app\data\qa_knowledge.json")

with open(DATA_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

# Tanglish translations and keywords per disease and topic
TANGLISH_DATA = {
    "blast": {
        "what_is_it": {
            "title_tanglish": "Rice Blast na enna?",
            "answer_tanglish": "Rice Blast (Kulai Noi) oru kodiya fungus noi. Ithu nel payirin ilai, kanu mattrum kathir kazhutha thakkum. Ilaila spindle shape-la saambal nira nadupaguthiyum dark brown border-um ulla pulligal varum. Kathir kazhutha thaakkuna kathir odinju 100% padhar aagidum.",
            "keywords_tanglish": ["blast na enna", "kulai noi na enna", "intha noi patri sollunga", "disease explain", "blast pathi"]
        },
        "cause": {
            "title_tanglish": "Blast noi vara kaaranam enna?",
            "answer_tanglish": "Ithu Magnaporthe oryzae (Pyricularia oryzae) endra kaathula vara fungal spores moolama varuthu. Kulirntha iravu neramum, ilaila 10 manineram mela pani thanni thangi irunthaalum intha poonjai vegama ilaikkulla nuzhaiyum.",
            "keywords_tanglish": ["kaaranam enna", "yen varuthu", "edhanala varuthu", "fungus kaaranam", "pathogen", "reason"]
        },
        "symptoms": {
            "title_tanglish": "Blast noiyin arikurigalum ilai paathippum",
            "answer_tanglish": "Aarambathula ilaila blue-green flecks thondrum. Piragu saambal nira nadupaguthiyum brown border-um ulla eetti vadiva pulligalaaga maarum. Pulligal onna sernthu ilaiyai karuga vaikkum. Kathir kazhuthu karuppaagi odinju vizhum.",
            "keywords_tanglish": ["epdi irukkum", "eppadi irukkum", "symptoms enna", "pulligal", "ilai paathippu", "thotram", "signs", "damage"]
        },
        "spread": {
            "title_tanglish": "Blast noi eppadi paravum?",
            "answer_tanglish": "Intha Rice Blast kaathula vara fungal spores (conidia) moolama romba vegama paravum. Mazhai thuligal, kottu paasana thanni, mattrum varappula irukkira kalaigal moolamavum adutha vayalukku paravum.",
            "keywords_tanglish": ["spread aagum", "eppadi paravum", "paravuthu", "kaathula paravuma", "adutha vayalukku", "transmission", "spread"]
        },
        "favourable_weather": {
            "title_tanglish": "Noi thondra saadhagamaana vaanaillai",
            "answer_tanglish": "Kulirntha iravu (18-22 °C), athiga eerappatham (90% mela), thodar megamootam, ilaila 10 manineram mela thangum pani thuli, mattrum athiga urea intha blast noi vara mukkiya kaaranangal.",
            "keywords_tanglish": ["weather enna", "pani kaalam", "mazhai kaalam", "eerappatham", "climate", "favourable season", "season"]
        },
        "treatment_spray": {
            "title_tanglish": "Enna marunthu thelikkanum?",
            "answer_tanglish": "TNAU recommend panna Tricyclazole 75% WP (1g/litre thanni) illa Azoxystrobin 18.2% + Difenoconazole 11.4% SC (1ml/litre) spray pannunga. Bio-control-kku Pseudomonas fluorescens (2g/L) thelikkavum. Excessive urea poduratha udane stop pannunga.",
            "keywords_tanglish": ["enna marunthu adikkanum", "marunthu thelikkanum", "spray pannanum", "enna spray", "cure panna", "marunthu enna", "fungicide spray", "treatment", "marundu"]
        },
        "dosage": {
            "title_tanglish": "Marundhu alavu (Dosage) evvalavu?",
            "answer_tanglish": "Tricyclazole 75% WP na 1 gram oru litre thannikku kalakkanum (acre-ku 200g in 200L water). Azoxystrobin na 1 ml oru litre thannikku kalakkanum. Kaalai illa maalai nerathula ilai nalla nanaivara maathiri spray pannunga.",
            "keywords_tanglish": ["dosage evvalavu", "alavu ethanai", "ethana gram", "ml evvalavu", "evvalavu marunthu", "dosage", "quantity", "alavu"]
        },
        "prevention": {
            "title_tanglish": "Adutha paruvathil varamal thaduppathu eppadi?",
            "answer_tanglish": "Seed treatment panni Pseudomonas fluorescens (10g/kg vidhai) use pannunga. LCC card paathu urea-va 3-4 thavanaiyaaga split panni podunga. Vayalla thanni thengaama paathukonga. Blast ethirppu ragangalaana CO 51, TPS 5 payiridavum.",
            "keywords_tanglish": ["thadukkurathu eppadi", "thadukka enna pannanum", "varama thadukka", "next season", "prevention", "seed treatment", "stop panna"]
        },
        "harvest_safety": {
            "title_tanglish": "Aruvadai paadhukaappu mattrum waiting period",
            "answer_tanglish": "Kulai noi kathirodu kazhutha thaakkuna 100% padhar aagidum. Fungicide thelichu 12-15 naal kazhichu thaan aruvadai pannanum (mandatory safety waiting period).",
            "keywords_tanglish": ["aruvadai", "harvest", "padhar", "waiting period", "safety", "magasool"]
        },
        "severity_meaning": {
            "title_tanglish": "Sedha sathavigam (Severity %) vilakkam",
            "answer_tanglish": "Ungaloda ilaila sedha sathavigam (severity %) ilai parappula kulai noi pulligal evvalavu paravirukku nu kaattuthu: 1% kulla na Low, 1-10% na Moderate, 10% mela na High damage. Udane spray panna vendum.",
            "keywords_tanglish": ["severity na enna", "percentage enna", "damage level", "evvalavu paathippu", "grade meaning", "score"]
        },
        "fertilizer_advice": {
            "title_tanglish": "Ura melaanmai mattrum urea alavu",
            "answer_tanglish": "Urea poduratha udane stop pannunga! Excessive nitrogen blast noiya vegama paravum. Potash (MOP) acre-ku 20-25 kg podunga, ithu thandu mattrum ilaiya balapaduthi noi ethirppa tharum.",
            "keywords_tanglish": ["urea podalama", "uram enna podanum", "potash evvalavu", "fertilizer", "nitrogen", "npk", "uram"]
        },
        "seed_variety_advice": {
            "title_tanglish": "Thaangi valarum ethirppu nel ragangal",
            "answer_tanglish": "Blast noi thaanga koodiya CO 51, ADT 45, TPS 5 pondra TNAU ethirppu ragangalai therdheduthu payiridavum. Certified disease-free seeds mattume use pannanum.",
            "keywords_tanglish": ["ragam", "ethirpu ragam", "seeds", "variety", "cultivar", "nalla vidhai"]
        }
    },
    "blb": {
        "what_is_it": {
            "title_tanglish": "Bacterial Leaf Blight na enna?",
            "answer_tanglish": "Bacterial Leaf Blight (BLB / Ilaikkarugal) oru kodiya bacteria noi. Ithu ilai nuniyil aarambithu ilaiyodu oram vazhiyaaga alai-alaiyana manjal-vellai karugal kottugalai undakkum. Ilai vaikkol pola kaainju surundidum.",
            "keywords_tanglish": ["blb na enna", "ilaikkarugal na enna", "bacterial blight pathi", "explain blb"]
        },
        "cause": {
            "title_tanglish": "BLB noi vara kaaranam enna?",
            "answer_tanglish": "Ithu Xanthomonas oryzae pv. oryzae endra bacteria-vaala varuthu. Kaathadikkira podhu ilai kaayam vazhiyaaga bacteria ilaikkulla nuzhaiyum.",
            "keywords_tanglish": ["kaaranam enna", "yen varuthu", "bacteria kaaranam", "pathogen", "reason"]
        },
        "symptoms": {
            "title_tanglish": "BLB noiyin arikurigalum ilai paathippum",
            "answer_tanglish": "Ilai nuniyil thanni patta maathiri stripes aarambithu, wavy manjal-vellai kottugalaaga ilai muzhuvathum paravum. Kaalai nerathula ilaila manjal bacteria thuli (ooze) kaanapadum. Ilai vaikkol pola kaainjupoidum.",
            "keywords_tanglish": ["epdi irukkum", "eppadi irukkum", "symptoms enna", "ooze", "ilai karugal", "signs", "damage"]
        },
        "spread": {
            "title_tanglish": "BLB eppadi paravum?",
            "answer_tanglish": "BLB paasanam panra thanni, mazhai thuligal mattrum kaathula ilai urasum podhu varra kaayangal vazhiyaaga vegama paravum. Vayalla thanni thenginaal noi udane muzhu field-kum paravum.",
            "keywords_tanglish": ["eppadi paravum", "spread aagum", "paravuthu", "thanni vazhiya", "transmission", "spread"]
        },
        "favourable_weather": {
            "title_tanglish": "BLB thondra saadhagamaana vaanaillai",
            "answer_tanglish": "Mazhai kaalam, 25-34 °C veppam, athiga eerappatham mattrum vayalla thengum thanni BLB noiyai vegama thundukirathu.",
            "keywords_tanglish": ["weather enna", "mazhai kaalam", "eerappatham", "climate", "season"]
        },
        "treatment_spray": {
            "title_tanglish": "Enna marunthu thelikkanum?",
            "answer_tanglish": "Mukkiya kurippu: Ithu BACTERIAL noi — fungicide spray pannina work aagathu! Fresh maattu saana karaisal (20%) thelikkavum, illa TNAU recommend panna Streptocycline (100mg) + Copper Oxychloride (2.5g) oru litre thannikku kalanthu spray pannunga.",
            "keywords_tanglish": ["marunthu enna", "enna marunthu adikkanum", "spray pannanum", "bacterial blight marunthu", "saana karaisal", "streptomycin", "cure", "treatment"]
        },
        "dosage": {
            "title_tanglish": "Marundhu alavu (Dosage) evvalavu?",
            "answer_tanglish": "Streptocycline 100 mg + Copper oxychloride 2.5 g oru litre thannikku kalakkanum (acre-ku 30g Streptocycline + 500g Copper oxychloride in 200L water). Maattu saanam na 20 kg saanatha 100L thannila kalanthu vadikatti thelikkavum.",
            "keywords_tanglish": ["dosage evvalavu", "alavu ethanai", "ethana gram", "quantity", "dosage", "alavu"]
        },
        "prevention": {
            "title_tanglish": "Adutha paruvathil varamal thaduppathu eppadi?",
            "answer_tanglish": "Vayalla thengi irukkira thanniya udane vadichudunga. Naatru nadumpothu ilai nuniyai killakoodathu. Pseudomonas (10g/kg) vidhai nerthi pannanum.",
            "keywords_tanglish": ["thadukka", "thadukkurathu", "prevention", "water drain", "vidhai nerthi", "stop panna"]
        },
        "harvest_safety": {
            "title_tanglish": "Aruvadai paadhukaappu",
            "answer_tanglish": "Copper spray panni irunthaal 10-14 naal kazhichu thaan aruvadai pannanum. Kadi ilai kaainju ponaal kathir padhar aaga vaaippundu.",
            "keywords_tanglish": ["aruvadai", "harvest", "padhar", "safety", "waiting period"]
        },
        "severity_meaning": {
            "title_tanglish": "Sedha sathavigam (Severity %) vilakkam",
            "answer_tanglish": "Severity sathavigam ilai karugal evvalavu thooram paravirukku nu kaattum: 1% kulla na Low, 1-10% na Moderate (thanniya udane vadikkanum), 10% mela na High (marunthu thelikkanum).",
            "keywords_tanglish": ["severity na enna", "percentage enna", "damage level", "score"]
        },
        "fertilizer_advice": {
            "title_tanglish": "Ura melaanmai",
            "answer_tanglish": "Urea top-dressing-a udane niruthunga! Potash (MOP) acre-ku 25 kg podunga. Potash cell wall-a thadikka vachu bacteria paravama thadukkum.",
            "keywords_tanglish": ["urea podalama", "potash podalama", "uram enna", "fertilizer", "nitrogen", "uram"]
        },
        "seed_variety_advice": {
            "title_tanglish": "BLB ethirppu nel ragangal",
            "answer_tanglish": "Improved Samba Mahsuri, TNAU CO 51, ADT 43 pondra BLB bacteria-vai ethirka koodiya ragangalai therdheduthu payiridavum.",
            "keywords_tanglish": ["ragam", "ethirpu ragam", "seeds", "variety", "cultivar"]
        }
    },
    "brown_spot": {
        "what_is_it": {
            "title_tanglish": "Brown Spot na enna?",
            "answer_tanglish": "Brown Spot (Pazhuppu Pulli Noi) oru poonjai noi. Ilaila el-vithai maathiri siriya vatta vadiva brown pulligal kaanapadum. Pulliyin naduvil saambal niramum sutrilum manjal valaiyamum irukkum.",
            "keywords_tanglish": ["brown spot na enna", "pazhuppu pulli na enna", "explain brown spot"]
        },
        "cause": {
            "title_tanglish": "Brown Spot vara kaaranam enna?",
            "answer_tanglish": "Ithu Bipolaris oryzae poonjaiyaal varuthu. Potash, Zinc, Silicon sathu kuraivaana man, varatchi, mattrum 25-30 °C veppam intha noi vara mukkiya kaaranangal.",
            "keywords_tanglish": ["kaaranam enna", "yen varuthu", "edhanala varuthu", "fungus kaaranam", "reason"]
        },
        "symptoms": {
            "title_tanglish": "Brown Spot arikurigalum ilai paathippum",
            "answer_tanglish": "Ilai mattrum thaaniyathil el pondra brown pulligal thondrum. Pulliyin naduvil grey center-um veliyil manjal halo-vum irukkum. Ennatra pulligal onna sernthu ilaiyai munkoottiye kaaya vaikkum.",
            "keywords_tanglish": ["epdi irukkum", "eppadi irukkum", "symptoms enna", "pulligal", "signs", "damage"]
        },
        "spread": {
            "title_tanglish": "Brown Spot eppadi paravum?",
            "answer_tanglish": "Ithu kaathula vara spores mattrum baadhikkapatta vidhaigal moolamavum paravum. Man sathu kuraivaga irukkum podhu noi vegama paravum.",
            "keywords_tanglish": ["eppadi paravum", "spread aagum", "paravuthu", "transmission", "spread"]
        },
        "favourable_weather": {
            "title_tanglish": "Saadhagamaana vaanaillai",
            "answer_tanglish": "25-30 °C veppam, athiga eerappatham (85-100%), megamootam mattrum varatchi azhutham intha noiyai thundukirathu.",
            "keywords_tanglish": ["weather enna", "eerappatham", "climate", "season"]
        },
        "treatment_spray": {
            "title_tanglish": "Enna marunthu thelikkanum?",
            "answer_tanglish": "Mancozeb (2g/L) illa Propiconazole (1ml/L) spray pannunga. Koodave 1% Potassium chloride (KCl) foliar spray panna ilaikku sarakkunu noi ethirppu kidaikkum.",
            "keywords_tanglish": ["marunthu enna", "spray pannanum", "brown spot marunthu", "mancozeb", "cure", "treatment", "marundu"]
        },
        "dosage": {
            "title_tanglish": "Marundhu alavu (Dosage) evvalavu?",
            "answer_tanglish": "Mancozeb na 2 gram oru litre thannikku (acre-ku 400g in 200L water). Propiconazole na 1 ml oru litre thannikku (acre-ku 200ml in 200L water).",
            "keywords_tanglish": ["dosage evvalavu", "alavu ethanai", "ethana gram", "quantity", "dosage", "alavu"]
        },
        "prevention": {
            "title_tanglish": "Adutha paruvathil varamal thaduppathu eppadi?",
            "answer_tanglish": "Man parikshai seithu sariyaana alavil Potash mattrum micro-nutrients idavum. Carbendazim (2g/kg) illa Pseudomonas kondu vidhai nerthi pannanum.",
            "keywords_tanglish": ["thadukka", "thadukkurathu", "prevention", "seed treatment", "stop panna"]
        },
        "harvest_safety": {
            "title_tanglish": "Aruvadai paadhukaappu",
            "answer_tanglish": "Thaaniyangalil karuppu pulligal (pecky rice) vara vaaippundu. Mancozeb spray panni 10-12 naal kazhichu aruvadai seiyavum.",
            "keywords_tanglish": ["aruvadai", "harvest", "pecky rice", "safety"]
        },
        "severity_meaning": {
            "title_tanglish": "Sedha sathavigam (Severity %) vilakkam",
            "answer_tanglish": "Severity sathavigam ilai parappil pulligalin alavai kaattum: 1% kulla na Low, 1-10% na Moderate (potash thelikkanum), 10% mela na High (fungicide spray thevai).",
            "keywords_tanglish": ["severity na enna", "percentage enna", "damage level", "score"]
        },
        "fertilizer_advice": {
            "title_tanglish": "Ura melaanmai",
            "answer_tanglish": "Brown spot mukkiyama Potash mattrum Zinc sathu kuraivaala varum. Samacheer NPK uram idavum; Potash mattrum Zinc sulphate (acre-ku 10kg) podavum.",
            "keywords_tanglish": ["uram enna", "potash", "zinc", "urea", "fertilizer", "uram"]
        },
        "seed_variety_advice": {
            "title_tanglish": "Thaangi valarum nel ragangal",
            "answer_tanglish": "ADT 36, ADT 44, CO 52 pondra thaangi valara koodiya saandrallikkapatta vidhai ragangalai therdheduthu payiridavum.",
            "keywords_tanglish": ["ragam", "ethirpu ragam", "seeds", "variety", "cultivar"]
        }
    },
    "healthy": {
        "what_is_it": {
            "title_tanglish": "Aarokkiyamaana nel ilai",
            "answer_tanglish": "Nalla seidhi! Unga nel ilai entha poonjai, bacteria illa virus noiyum illama romba aarokkiyama pacha pasael nu irukku.",
            "keywords_tanglish": ["healthy na enna", "nalla nel", "good crop", "health status"]
        },
        "cause": {
            "title_tanglish": "Payer aarokkiyamaaga irukka kaaranam",
            "answer_tanglish": "Sariyaana uram, nalla thanni paasanam mattrum sariyaana vidhai nerthi unga payirai noiyindri paadhukaathu irukku.",
            "keywords_tanglish": ["yen nalla irukku", "aarokkiyam kaaranam", "good health"]
        },
        "symptoms": {
            "title_tanglish": "Aarokkiyamaana ilai thotram",
            "answer_tanglish": "Seeraana dark green niram, surungal illatha sutthamaana ilai orangal mattrum entha pulligalum illatha mirudhuvaana ilai.",
            "keywords_tanglish": ["epdi irukkum", "thotram", "appearance", "green leaf"]
        },
        "spread": {
            "title_tanglish": "Adutha vayalil irunthu noi varuma?",
            "answer_tanglish": "Aam, pakkathu vayalla noi iruntha kaathu mattrum thanni vazhiyaaga vara vaaippundu. Thodarnthu vayalai kavanithu vaanga.",
            "keywords_tanglish": ["noi varuma", "adutha vayal", "spread risk", "danger"]
        },
        "favourable_weather": {
            "title_tanglish": "Kavanikka vendiya vaanaillai",
            "answer_tanglish": "Thodar megamootam, athiga pani mattrum mazhai kaalathil noi vara vaaippullathaal appothu kooduthal gavanam thevai.",
            "keywords_tanglish": ["weather risk", "mazhai kaalam", "pani kaalam"]
        },
        "treatment_spray": {
            "title_tanglish": "Ippo ethavathu spray pannanuma?",
            "answer_tanglish": "Ippo endha chemical marunthum thelikka vendiya thevai illa! Thevai illama chemical spray panna nanmai seyyum poochigal azhinjipodum. Bio-input-kku 3% Panchagavya spray pannalaam.",
            "keywords_tanglish": ["marunthu thelikkanuma", "spray pannanuma", "marunthu adikkanuma", "chemical spray thevaiya"]
        },
        "dosage": {
            "title_tanglish": "Panchagavya alavu",
            "answer_tanglish": "Iyarkkai payir oottachaathukku 3% Panchagavya (1 litre thannikku 30 ml) illa Pseudomonas (2g/L) thelikkalaam.",
            "keywords_tanglish": ["dosage", "alavu", "panchagavya alavu", "quantity"]
        },
        "prevention": {
            "title_tanglish": "Thodarnthu aarokkiyamaaga paadhukaappathu eppadi?",
            "answer_tanglish": "Kaaychalum paaichalumaaga (AWD) thanni paasanam pannunga. Varappula kalaigal illama clean-ah vachukonga. LCC card paathu urea-va piri-piriyaaga podunga.",
            "keywords_tanglish": ["eppadi maintain pannanum", "aarokkiyama vachuka", "tips", "care tips"]
        },
        "harvest_safety": {
            "title_tanglish": "Ethirpaarkkapadum magasool",
            "answer_tanglish": "Aarokkiyamaana ilai nalla oli-cherkkai seithu manigal nangu thirala vaikkum. Athiga magasool kidaikkum.",
            "keywords_tanglish": ["magasool", "yield", "harvest", "grain quality"]
        },
        "severity_meaning": {
            "title_tanglish": "Sedha sathavigam vilakkam",
            "answer_tanglish": "Unga scan 0% damage kaattuthu, ithu ilai muzhumaiyaaga nalamaga iruppathai uruthi seigirathu.",
            "keywords_tanglish": ["severity score", "zero percent", "damage level"]
        },
        "fertilizer_advice": {
            "title_tanglish": "Aarokkiyamaana payirukku uram alavu",
            "answer_tanglish": "Thaivana urea, phosphorus mattrum potash-a standard schedule-padi podunga: 25% adi uram, 50% thoor kattum paruvam, 25% kathir paruvam. Athiga urea podatheenga.",
            "keywords_tanglish": ["uram schedule", "fertilizer", "urea evvalavu", "uram podalama"]
        },
        "seed_variety_advice": {
            "title_tanglish": "Adutha scan eppo pannanum?",
            "answer_tanglish": "Oru vaarathukku oru murai marubadiyum scan panni paapom, pudhu ilaila pulli illa kottu varutha nu kavanikka.",
            "keywords_tanglish": ["eppa scan pannanum", "next scan", "monitoring", "scan schedule"]
        }
    },
    "other": {
        "what_is_it": {
            "title_tanglish": "Nel payir kolarugal",
            "answer_tanglish": "Ithu nel payiril thondrum idhara poonjai/bacteria noi illa saathu kuraipaadu aagum.",
            "keywords_tanglish": ["kolaru na enna", "intha noi enna", "other disease"]
        },
        "cause": {
            "title_tanglish": "Kaaranam enna?",
            "answer_tanglish": "Man sathu kuraipaadu, poonjai thotru illa thagatha vaanaillai kaaranamaaga thondrugirathu.",
            "keywords_tanglish": ["kaaranam enna", "yen varuthu", "reason"]
        },
        "symptoms": {
            "title_tanglish": "Arikurigalum ilai paathippum",
            "answer_tanglish": "Ilai manjalithal, karugal pulligal thondruthal, thoor kuraivathal pondra arikurigalaaga irukkum.",
            "keywords_tanglish": ["epdi irukkum", "symptoms enna", "damage"]
        },
        "spread": {
            "title_tanglish": "Eppadi paravum?",
            "answer_tanglish": "Kaathu, paasana thanni mattrum poochi kadigalaal parava vaaippundu.",
            "keywords_tanglish": ["eppadi paravum", "spread", "transmission"]
        },
        "favourable_weather": {
            "title_tanglish": "Saadhagamaana vaanaillai",
            "answer_tanglish": "Athiga eerappatham mattrum thengum thanni noiyai thundukirathu.",
            "keywords_tanglish": ["weather", "season", "climate"]
        },
        "treatment_spray": {
            "title_tanglish": "Enna marunthu thelikkanum?",
            "answer_tanglish": "Ilai pulli athigama irunthaal TNAU recommend panna broad-spectrum fungicide (Mancozeb 2g/L illa Carbendazim 1g/L) thelikkavum. Velanmai aluvalarai anugavum.",
            "keywords_tanglish": ["marunthu enna", "spray pannanum", "enna spray", "cure", "treatment", "marundu"]
        },
        "dosage": {
            "title_tanglish": "Marundhu alavu (Dosage)",
            "answer_tanglish": "Mancozeb 2g/L oru litre thannikku kalanthu spray pannunga.",
            "keywords_tanglish": ["dosage evvalavu", "alavu", "quantity"]
        },
        "prevention": {
            "title_tanglish": "Varaamal thaduppathu eppadi?",
            "answer_tanglish": "Vayalla thengaama thanni vadiya vachutu, samacheer uram idavum.",
            "keywords_tanglish": ["thadukka", "prevention", "stop panna"]
        },
        "harvest_safety": {
            "title_tanglish": "Aruvadai paadhukaappu",
            "answer_tanglish": "Marunthu thelichu 10-14 naal kazhichu aruvadai seiyavum.",
            "keywords_tanglish": ["aruvadai", "harvest", "safety"]
        },
        "severity_meaning": {
            "title_tanglish": "Sedha sathavigam vilakkam",
            "answer_tanglish": "Severity sathavigam ilaiyil kolaru evvalavu thooram paravirukku nu kaattum.",
            "keywords_tanglish": ["severity", "damage level", "score"]
        },
        "fertilizer_advice": {
            "title_tanglish": "Ura melaanmai",
            "answer_tanglish": "Samacheer NPK uram idavum. Athiga urea podatheenga.",
            "keywords_tanglish": ["uram enna", "fertilizer", "urea"]
        },
        "seed_variety_advice": {
            "title_tanglish": "Saandrallikkapatta ragangal",
            "answer_tanglish": "TNAU-vin saandrallikkapatta vidhai ragangalai mattume payiridavum.",
            "keywords_tanglish": ["ragam", "variety", "seeds"]
        }
    }
}

for d_key, t_dict in TANGLISH_DATA.items():
    if d_key in data:
        for top_key, top_vals in t_dict.items():
            if top_key in data[d_key]["topics"]:
                target_topic = data[d_key]["topics"][top_key]
                target_topic["title_tanglish"] = top_vals["title_tanglish"]
                target_topic["answer_tanglish"] = top_vals["answer_tanglish"]
                target_topic["keywords_tanglish"] = top_vals["keywords_tanglish"]

with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Enriched qa_knowledge.json with Tanglish answers and keywords successfully!")
