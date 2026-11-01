import urllib.request
import urllib.parse
import json
import shutil
from pathlib import Path

DEST_ROOT = Path(r"C:\Users\keert\paddy_dataset\app\static\disease_library")

VERIFIED_WIKI_IMAGES = {
    "sheath_blight": [
        "https://upload.wikimedia.org/wikipedia/commons/1/15/RiceSheathArk.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/9/91/Rhizoctonia_solani.jpg"
    ],
    "sheath_rot": [
        "https://upload.wikimedia.org/wikipedia/commons/c/c6/Rice_Sheath_Rot.jpg"
    ],
    "false_smut": [
        "https://upload.wikimedia.org/wikipedia/commons/5/53/Rice_grains_infected_with_false_smut.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/f/fa/Rice_false_smut.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/4/4f/False_smut_on_rice_in_central_Vietnam.jpg"
    ],
    "bakanae": [
        "https://upload.wikimedia.org/wikipedia/commons/d/d1/Bakanae_Disease_sporulation_JIRCAS.jpg"
    ],
    "bacterial_panicle_blight": [
        "https://upload.wikimedia.org/wikipedia/commons/b/b5/Burkholderia_glumae.JPG"
    ]
}

def download_images():
    for disease, urls in VERIFIED_WIKI_IMAGES.items():
        out_dir = DEST_ROOT / disease
        out_dir.mkdir(parents=True, exist_ok=True)
        for idx, url in enumerate(urls, start=1):
            target = out_dir / f"ref_{idx}.jpg"
            print(f"Downloading {disease} ref_{idx}.jpg from {url}...")
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            try:
                with urllib.request.urlopen(req, timeout=15) as resp, open(target, "wb") as f:
                    f.write(resp.read())
                print(f"  Saved {target} ({target.stat().st_size} bytes)")
            except Exception as e:
                print(f"  Error downloading {url}: {e}")

if __name__ == "__main__":
    download_images()
