import json
from pathlib import Path

PROJECT_ROOT = Path(r"C:\Users\keert\paddy_dataset")
INFO_PATH = PROJECT_ROOT / "app" / "data" / "disease_info.json"
MANIFEST_PATH = PROJECT_ROOT / "app" / "static" / "disease_library" / "manifest.json"
STATIC_ROOT = PROJECT_ROOT / "app" / "static" / "disease_library"

with open(INFO_PATH, "r", encoding="utf-8") as f:
    info = json.load(f)

manifest = {}

for key, val in info.items():
    if key.startswith("_"):
        continue
    class_dir = STATIC_ROOT / key
    # Find all reference images
    if class_dir.exists():
        imgs = sorted([p.name for p in class_dir.glob("ref_*.jpg") or class_dir.glob("ref_*.JPG") or class_dir.glob("*.jpg")])
        if imgs:
            rel_imgs = [f"static/disease_library/{key}/{img_name}" for img_name in imgs]
            val["gallery_images"] = rel_imgs
            manifest[key] = rel_imgs
        else:
            val["gallery_images"] = [f"static/disease_library/{key}/ref_1.jpg"]
            manifest[key] = [f"static/disease_library/{key}/ref_1.jpg"]
    else:
        val["gallery_images"] = [f"static/disease_library/{key}/ref_1.jpg"]
        manifest[key] = [f"static/disease_library/{key}/ref_1.jpg"]

with open(INFO_PATH, "w", encoding="utf-8") as f:
    json.dump(info, f, indent=2, ensure_ascii=False)

with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print("Updated disease_info.json and manifest.json successfully!")
for k, v in manifest.items():
    print(f"  {k:<26} -> {v}")
