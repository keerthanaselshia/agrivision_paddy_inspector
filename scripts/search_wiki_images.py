import urllib.request
import urllib.parse
import json
import time

HEADERS = {"User-Agent": "AgriVisionStudentProject/1.0 (kongu_it_paddy@student.kongu.edu; Keerthana)"}

def search_and_get_url(query):
    api = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(query)}&gsrnamespace=6&format=json&prop=imageinfo&iiprop=url|size|mime"
    req = urllib.request.Request(api, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, p in pages.items():
                if int(pid) > 0 and "imageinfo" in p:
                    ii = p["imageinfo"][0]
                    mime = ii.get("mime", "")
                    if mime.startswith("image/"):
                        results.append((p.get("title"), ii.get("url"), ii.get("size")))
            return results
    except Exception as e:
        return [("error", str(e), 0)]

search_queries = {
    "bacterial_leaf_streak": ["Xanthomonas oryzae pv. oryzicola", "bacterial leaf streak rice"],
    "stem_rot": ["Magnaporthe salvinii", "Sclerotium oryzae", "rice stem rot"],
    "bacterial_panicle_blight": ["Burkholderia glumae", "panicle blight rice"],
    "grain_discoloration": ["glume blotch rice", "grain discoloration rice", "Curvularia oryzae"],
    "grassy_stunt": ["rice grassy stunt virus", "grassy stunt rice"],
    "ragged_stunt": ["rice ragged stunt virus", "ragged stunt rice"],
    "zinc_deficiency": ["zinc deficiency rice", "Khaira disease rice", "zinc deficiency leaf"],
    "nitrogen_deficiency": ["nitrogen deficiency rice", "nitrogen deficiency leaf"],
    "potassium_deficiency": ["potassium deficiency rice", "potassium deficiency leaf"],
    "iron_toxicity": ["iron toxicity rice", "bronzing disease rice"]
}

for d, q_list in search_queries.items():
    found = []
    for q in q_list:
        res = search_and_get_url(f"{q} filetype:bitmap")
        for t, u, s in res:
            if t != "error":
                found.append((t, u, s))
        time.sleep(1.5)
        if len(found) >= 3:
            break
    print(f"[{d}] found {len(found)} candidate images:")
    for t, u, s in found[:3]:
        print(f"   {t} ({s} bytes) -> {u}")
