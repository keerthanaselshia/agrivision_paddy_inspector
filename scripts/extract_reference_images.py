"""
extract_reference_images.py
Selects 2-3 clear, high-quality, authentic reference leaf images per disease class
from local datasets (C:\\Users\\keert\\paddy_dataset) and copies them into
app/static/disease_library/<class_name>/.
"""

import json
import shutil
from pathlib import Path
import cv2
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATIC_LIB = PROJECT_ROOT / "app" / "static" / "disease_library"

# Candidate search directories in priority order
SOURCE_DIRS = {
    "blast": [
        PROJECT_ROOT / "raw" / "dedeikh" / "leaf_blast",
        PROJECT_ROOT / "raw" / "nirmalsankalana" / "Blast",
        PROJECT_ROOT / "final" / "train" / "blast",
    ],
    "blb": [
        PROJECT_ROOT / "raw" / "dedeikh" / "bacterial_leaf_blight",
        PROJECT_ROOT / "raw" / "nirmalsankalana" / "Bacterialblight",
        PROJECT_ROOT / "final" / "train" / "blb",
    ],
    "brown_spot": [
        PROJECT_ROOT / "raw" / "dedeikh" / "brown_spot",
        PROJECT_ROOT / "raw" / "nirmalsankalana" / "Brownspot",
        PROJECT_ROOT / "final" / "train" / "brown_spot",
    ],
    "healthy": [
        PROJECT_ROOT / "raw" / "dedeikh" / "healthy",
        PROJECT_ROOT / "final" / "train" / "healthy",
    ],
    "other": [
        PROJECT_ROOT / "raw" / "nirmalsankalana" / "Tungro",
        PROJECT_ROOT / "raw" / "dedeikh" / "leaf_scald",
        PROJECT_ROOT / "raw" / "dedeikh" / "narrow_brown_spot",
        PROJECT_ROOT / "final" / "train" / "other",
    ],
    "tungro": [
        PROJECT_ROOT / "raw" / "nirmalsankalana" / "Tungro",
    ],
    "leaf_scald": [
        PROJECT_ROOT / "raw" / "dedeikh" / "leaf_scald",
    ],
    "narrow_brown_spot": [
        PROJECT_ROOT / "raw" / "dedeikh" / "narrow_brown_spot",
    ],
}


def score_image_quality(file_path: Path) -> float:
    """Return a quality score based on image sharpness (Laplacian variance) and size."""
    try:
        img = cv2.imread(str(file_path))
        if img is None:
            return -1.0
        h, w = img.shape[:2]
        if h < 150 or w < 150:
            return -1.0
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        # Penalize over-exposed or pitch-black images
        mean_bright = float(np.mean(gray))
        if mean_bright < 30 or mean_bright > 230:
            return -1.0
        # Score blends sharpness and optimal brightness
        return sharpness
    except Exception:
        return -1.0


def extract_reference_images(num_per_class: int = 3):
    STATIC_LIB.mkdir(parents=True, exist_ok=True)
    manifest = {}

    for class_name, dir_list in SOURCE_DIRS.items():
        dest_dir = STATIC_LIB / class_name
        dest_dir.mkdir(parents=True, exist_ok=True)

        candidate_files = []
        for d in dir_list:
            if d.exists():
                for f in d.glob("*"):
                    if f.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                        candidate_files.append(f)

        if not candidate_files:
            print(f"Warning: No images found for {class_name}")
            continue

        # Score candidates to select top sharpest images
        scored = []
        # Sample up to 100 images to find best quickly
        sample = candidate_files[:100]
        for f in sample:
            score = score_image_quality(f)
            if score > 0:
                scored.append((score, f))

        scored.sort(key=lambda x: x[0], reverse=True)
        top_selected = [f for _, f in scored[:num_per_class]]

        # Fallback if scoring yielded fewer
        if len(top_selected) < num_per_class:
            for f in candidate_files:
                if f not in top_selected:
                    top_selected.append(f)
                if len(top_selected) >= num_per_class:
                    break

        copied_relative = []
        for idx, src_path in enumerate(top_selected, 1):
            ext = src_path.suffix.lower()
            dest_file = dest_dir / f"ref_{idx}{ext}"
            shutil.copy2(src_path, dest_file)
            rel_path = f"static/disease_library/{class_name}/{dest_file.name}"
            copied_relative.append(rel_path)
            print(f"[{class_name}] Copied {src_path.name} -> {dest_file.name}")

        manifest[class_name] = copied_relative

    manifest_path = STATIC_LIB / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nManifest saved to {manifest_path}")


if __name__ == "__main__":
    extract_reference_images(num_per_class=3)
