import shutil
from pathlib import Path
import cv2
import numpy as np

PROJECT_ROOT = Path(r"C:\Users\keert\paddy_dataset")
DEST_ROOT = PROJECT_ROOT / "app" / "static" / "disease_library"

LOCAL_SOURCES = {
    "blast": PROJECT_ROOT / "raw" / "dedeikh" / "leaf_blast",
    "blb": PROJECT_ROOT / "raw" / "dedeikh" / "bacterial_leaf_blight",
    "brown_spot": PROJECT_ROOT / "raw" / "dedeikh" / "brown_spot",
    "healthy": PROJECT_ROOT / "raw" / "dedeikh" / "healthy",
    "leaf_scald": PROJECT_ROOT / "raw" / "dedeikh" / "leaf_scald",
    "narrow_brown_spot": PROJECT_ROOT / "raw" / "dedeikh" / "narrow_brown_spot",
    "tungro": PROJECT_ROOT / "raw" / "nirmalsankalana" / "Tungro",
    "other": PROJECT_ROOT / "raw" / "jay7080" / "rice leaf diseases dataset" / "Leafsmut",
}

def score_sharpness(f: Path) -> float:
    try:
        img = cv2.imread(str(f))
        if img is None:
            return -1.0
        h, w = img.shape[:2]
        if h < 200 or w < 200:
            return -1.0
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        var = cv2.Laplacian(gray, cv2.CV_64F).var()
        mean = np.mean(gray)
        if mean < 30 or mean > 225:
            return -1.0
        return float(var)
    except Exception:
        return -1.0

def main():
    for label, src_dir in LOCAL_SOURCES.items():
        if not src_dir.exists():
            print(f"Directory not found: {src_dir}")
            continue
        out_dir = DEST_ROOT / label
        out_dir.mkdir(parents=True, exist_ok=True)
        
        all_imgs = [p for p in src_dir.glob("*") if p.suffix.lower() in [".jpg", ".jpeg", ".png"]]
        print(f"[{label}] Scanning {len(all_imgs)} images from {src_dir.name}...")
        
        # Score sample of 150 images to find 3 sharpest
        sample = all_imgs[:150]
        scored = []
        for img_p in sample:
            s = score_sharpness(img_p)
            if s > 0:
                scored.append((s, img_p))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        top3 = scored[:3]
        
        for idx, (score, path) in enumerate(top3, start=1):
            dest_file = out_dir / f"ref_{idx}.jpg"
            shutil.copy2(path, dest_file)
            print(f"  Saved ref_{idx}.jpg from {path.name} (sharpness={score:.1f})")

if __name__ == "__main__":
    main()
