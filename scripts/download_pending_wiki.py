import urllib.request
import time
from pathlib import Path

DEST_ROOT = Path(r"C:\Users\keert\paddy_dataset\app\static\disease_library")

PENDING = [
    ("false_smut", "ref_1.jpg", "https://upload.wikimedia.org/wikipedia/commons/5/53/Rice_grains_infected_with_false_smut.jpg"),
    ("false_smut", "ref_2.jpg", "https://upload.wikimedia.org/wikipedia/commons/f/fa/Rice_false_smut.jpg"),
    ("false_smut", "ref_3.jpg", "https://upload.wikimedia.org/wikipedia/commons/4/4f/False_smut_on_rice_in_central_Vietnam.jpg"),
    ("bakanae", "ref_1.jpg", "https://upload.wikimedia.org/wikipedia/commons/d/d1/Bakanae_Disease_sporulation_JIRCAS.jpg"),
    ("bacterial_panicle_blight", "ref_1.jpg", "https://upload.wikimedia.org/wikipedia/commons/b/b5/Burkholderia_glumae.JPG"),
]

headers = {
    "User-Agent": "AgriVisionStudentProject/1.0 (kongu_it_paddy@student.kongu.edu; Keerthana)"
}

for disease, ref_name, url in PENDING:
    out_dir = DEST_ROOT / disease
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / ref_name
    print(f"Downloading {disease}/{ref_name}...")
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp, open(target, "wb") as f:
            f.write(resp.read())
        print(f"  SUCCESS: {target.stat().st_size} bytes")
    except Exception as e:
        print(f"  FAILED: {e}")
    time.sleep(3)
