import urllib.request
import json
from pathlib import Path

DEST = Path(r"C:\Users\keert\paddy_dataset\app\static\disease_library")

# Curated direct Wikimedia Commons image URLs for specific rice diseases
CURATED_WIKI_FILES = {
    "sheath_blight": [
        "File:RiceSheathArk.jpg",
        "File:Rhizoctonia_solani.jpg"
    ],
    "sheath_rot": [
        "File:Rice_Sheath_Rot.jpg"
    ],
    "false_smut": [
        "File:Rice_grains_infected_with_false_smut.jpg",
        "File:Rice_false_smut.jpg",
        "File:False_smut_on_rice_in_central_Vietnam.jpg"
    ],
    "bakanae": [
        "File:Bakanae_Disease_sporulation_JIRCAS.jpg",
        "File:Bakane_Disease_Rice.jpg"
    ]
}

def get_wikimedia_direct_url(file_title: str) -> str | None:
    api = f"https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote(file_title)}&prop=imageinfo&iiprop=url&format=json"
    req = urllib.request.Request(api, headers={"User-Agent": "AgriVisionRiceBot/1.0 (contact@agri.ac.in)"})
    with urllib.request.urlopen(req, timeout=8) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        pages = data.get("query", {}).get("pages", {})
        for _, p in pages.items():
            ii = p.get("imageinfo", [{}])[0]
            return ii.get("url")
    return None

def test_fetch():
    for disease, files in CURATED_WIKI_FILES.items():
        for f_title in files:
            try:
                url = get_wikimedia_direct_url(f_title)
                print(f"[{disease}] {f_title} -> {url}")
            except Exception as e:
                print(f"[{disease}] Error {f_title}: {e}")

if __name__ == "__main__":
    test_fetch()
