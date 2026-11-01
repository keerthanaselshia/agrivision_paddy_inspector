import argparse
import os
import hashlib
import csv
from pathlib import Path
from typing import List, Tuple, Dict
import imagehash
from PIL import Image
import numpy as np
import pandas as pd
import yaml

# Supported image extensions
IMG_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.webp'}

def is_image(file_path: Path) -> bool:
    return file_path.suffix.lower() in IMG_EXTENSIONS

def compute_md5(file_path: Path) -> str:
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def compute_phash(file_path: Path) -> str:
    try:
        img = Image.open(file_path).convert('RGB')
        return str(imagehash.phash(img))
    except Exception:
        return ""

def collect_images(root: Path) -> List[Tuple[Path, str, str]]:
    """Return list of (filepath, source_name, class_name)."""
    data = []
    for source_dir in root.iterdir():
        if not source_dir.is_dir():
            continue
        source_name = source_dir.name
        # handle special nested structure for mendeley and jay7080
        if source_name == "mendeley":
            # raw\mendeley\Rice Leaf Disease Images\{...}
            sub_root = source_dir / "Rice Leaf Disease Images"
        elif source_name == "jay7080":
            sub_root = source_dir / "rice leaf diseases dataset"
        else:
            sub_root = source_dir
        for class_dir in sub_root.iterdir():
            if not class_dir.is_dir():
                continue
            class_name = class_dir.name
            for file_path in class_dir.rglob('*'):
                if file_path.is_file() and is_image(file_path):
                    data.append((file_path, source_name, class_name))
    return data

def count_images(data: List[Tuple[Path, str, str]]) -> pd.DataFrame:
    rows = []
    for fp, src, cls in data:
        rows.append({"source": src, "class": cls, "path": str(fp)})
    df = pd.DataFrame(rows)
    return df.groupby(["source", "class"]).size().reset_index(name="count")

def compare_duplicate_mendeley_nirmal(mendeley_data: List[Tuple[Path, str, str]], nirmal_data: List[Tuple[Path, str, str]]) -> Tuple[float, float]:
    """Return (md5_overlap_pct, phash_overlap_pct) where pct = (matches / total_mendeley) * 100"""
    # Build hash sets for nirmal
    nirmal_md5 = set()
    nirmal_phash = set()
    for fp, _, _ in nirmal_data:
        md5 = compute_md5(fp)
        ph = compute_phash(fp)
        nirmal_md5.add(md5)
        if ph:
            nirmal_phash.add(ph)
    # Compare with mendeley images
    md5_matches = 0
    phash_matches = 0
    total = len(mendeley_data)
    for fp, _, _ in mendeley_data:
        md5 = compute_md5(fp)
        ph = compute_phash(fp)
        if md5 in nirmal_md5:
            md5_matches += 1
        if ph and ph in nirmal_phash:
            phash_matches += 1
    md5_pct = (md5_matches / total) * 100 if total else 0
    phash_pct = (phash_matches / total) * 100 if total else 0
    return md5_pct, phash_pct

def main():
    parser = argparse.ArgumentParser(description="Inspect raw image sources, count per class, and detect duplicates.")
    parser.add_argument('--raw-dir', type=str, default='raw', help='Root directory containing raw sources')
    parser.add_argument('--output', type=str, default='logs/sources.csv', help='CSV file to write summary')
    args = parser.parse_args()

    raw_root = Path(args.raw_dir)
    if not raw_root.is_dir():
        raise FileNotFoundError(f"Raw directory {raw_root} not found")

    # Gather all images
    all_data = collect_images(raw_root)
    counts_df = count_images(all_data)

    # Split data for duplicate comparison
    mendeley_data = [(fp, src, cls) for fp, src, cls in all_data if src == 'mendeley']
    nirmal_data = [(fp, src, cls) for fp, src, cls in all_data if src == 'nirmalsankalana']
    md5_pct, phash_pct = compare_duplicate_mendeley_nirmal(mendeley_data, nirmal_data)

    # Determine if mendeley should be excluded (>90% duplicate)
    exclude_mendeley = md5_pct > 90 or phash_pct > 90

    # Write CSV summary
    os.makedirs(Path(args.output).parent, exist_ok=True)
    with open(args.output, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['dataset', 'kaggle_slug', 'licence', 'image_count', 'notes'])
        # nirmalsankalana
        nirmal_count = sum(counts_df[counts_df['source'] == 'nirmalsankalana']['count'])
        writer.writerow(['nirmalsankalana', 'nirmalsankalana', 'CC0-1.0', nirmal_count, ''])
        # mendeley
        mendeley_count = sum(counts_df[counts_df['source'] == 'mendeley']['count'])
        notes = 'excluded due to >90% duplicate' if exclude_mendeley else ''
        writer.writerow(['mendeley', 'mendeley', 'CC0-1.0', mendeley_count, notes])
        # jay7080
        jay_count = sum(counts_df[counts_df['source'] == 'jay7080']['count'])
        writer.writerow(['jay7080', 'jay7080', 'Apache-2.0', jay_count, ''])

    # Print a concise report
    print('Image counts per source/class:')
    print(counts_df)
    print('\nDuplicate comparison (mendeley vs nirmalsankalana):')
    print(f'MD5 overlap: {md5_pct:.2f}%')
    print(f'Perceptual hash overlap: {phash_pct:.2f}%')
    if exclude_mendeley:
        print('=> mendeley will be excluded from later merging.')
    else:
        print('=> mendeley will be kept.')

if __name__ == '__main__':
    main()
