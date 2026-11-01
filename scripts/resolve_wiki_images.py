import urllib.request
import urllib.parse
import json
import time

CANDIDATES = {
    "sheath_blight": ["RiceSheathArk.jpg", "Rhizoctonia_solani.jpg", "Rhizoctonia_solani_on_rice.jpg"],
    "sheath_rot": ["Rice_Sheath_Rot.jpg", "Sarocladium_oryzae.jpg"],
    "false_smut": ["Rice_grains_infected_with_false_smut.jpg", "Rice_false_smut.jpg", "False_smut_on_rice_in_central_Vietnam.jpg"],
    "bakanae": ["Bakanae_Disease_sporulation_JIRCAS.jpg", "Bakanae_disease_in_rice_field.jpg", "Bakane_Disease_Rice.jpg"],
    "bacterial_leaf_streak": ["Bacterial_leaf_streak_of_rice.jpg", "Bacterial_leaf_streak.jpg", "Xanthomonas_oryzae_pv._oryzicola.jpg"],
    "bacterial_panicle_blight": ["Burkholderia_glumae.JPG", "Bacterial_panicle_blight.jpg", "Panicle_blight_rice.jpg"],
    "stem_rot": ["Rice_stem_rot.jpg", "Sclerotium_oryzae.jpg", "Magnaporthe_salvinii.jpg"],
    "grain_discoloration": ["Dirty_panicle_disease_rice.jpg", "Grain_discoloration_rice.jpg", "Pecky_rice.jpg"],
    "grassy_stunt": ["Rice_grassy_stunt_virus.jpg", "Grassy_stunt_rice.jpg"],
    "ragged_stunt": ["Rice_ragged_stunt_virus.jpg", "Ragged_stunt_rice.jpg"],
    "zinc_deficiency": ["Zinc_deficiency_rice.jpg", "Khaira_disease_rice.jpg", "Zinc_deficiency_in_paddy.jpg"],
    "nitrogen_deficiency": ["Nitrogen_deficiency_rice.jpg", "Nitrogen_deficiency_in_rice.jpg", "Rice_nitrogen_deficiency.jpg"],
    "potassium_deficiency": ["Potassium_deficiency_rice.jpg", "Potassium_deficiency_in_rice.jpg"],
    "iron_toxicity": ["Iron_toxicity_rice.jpg", "Bronzing_disease_rice.jpg"]
}

def resolve_wiki_title(title):
    api = f"https://commons.wikimedia.org/w/api.php?action=query&titles=File:{urllib.parse.quote(title)}&prop=imageinfo&iiprop=url|size|mime&format=json"
    req = urllib.request.Request(api, headers={"User-Agent": "AgriVisionApp/2.0 (research@agri.edu)"})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            pages = data.get("query", {}).get("pages", {})
            for pid, p in pages.items():
                if int(pid) > 0 and "imageinfo" in p:
                    return p["imageinfo"][0].get("url")
    except Exception as e:
        pass
    return None

def search_wiki(term):
    api = f"https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(term)}&srnamespace=6&srlimit=5&format=json"
    req = urllib.request.Request(api, headers={"User-Agent": "AgriVisionApp/2.0 (research@agri.edu)"})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            results = data.get("query", {}).get("search", [])
            titles = [r["title"] for r in results if any(r["title"].lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png"])]
            return titles
    except Exception as e:
        return []

def main():
    found = {}
    for d, titles in CANDIDATES.items():
        found[d] = []
        for t in titles:
            url = resolve_wiki_title(t)
            if url:
                found[d].append((t, url))
        if not found[d]:
            # Try search
            search_res = search_wiki(f"{d.replace('_', ' ')} rice")
            for sr in search_res[:3]:
                url = resolve_wiki_title(sr.replace("File:", ""))
                if url:
                    found[d].append((sr, url))
            time.sleep(0.5)
        print(f"[{d}] found {len(found[d])} images: {[t for t, u in found[d]]}")

if __name__ == "__main__":
    main()
