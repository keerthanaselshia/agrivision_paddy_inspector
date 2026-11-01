import argparse
import os
import random
import shutil
from pathlib import Path
import pandas as pd
from tqdm import tqdm
import yaml
import albumentations as A
from PIL import Image
import numpy as np

# Load config

def load_config(cfg_path: str) -> dict:
    with open(cfg_path, 'r') as f:
        return yaml.safe_load(f)

def get_image_paths(split_dir: Path) -> pd.DataFrame:
    records = []
    for class_dir in split_dir.iterdir():
        if not class_dir.is_dir():
            continue
        class_name = class_dir.name
        for img_path in class_dir.rglob('*'):
            if img_path.is_file() and img_path.suffix.lower() in {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.webp'}:
                records.append({
                    'path': img_path,
                    'class': class_name,
                })
    return pd.DataFrame(records)

def augment_image(image_path: Path, aug, out_path: Path):
    img = Image.open(image_path).convert('RGB')
    arr = np.array(img)
    auged = aug(image=arr)['image']
    Image.fromarray(auged).save(out_path, format='JPEG')


def main():
    parser = argparse.ArgumentParser(description='Augment training set to balance classes')
    parser.add_argument('--train-dir', default='final/train', help='Directory containing training images organized by class')
    parser.add_argument('--output-dir', default='final/train_augmented', help='Directory to store augmented images')
    parser.add_argument('--config', default='config.yaml', help='Config file with augmentation settings')
    args = parser.parse_args()

    cfg = load_config(args.config)
    # Define augmentation pipeline (can be adjusted via config later)
    aug = A.Compose([
        A.RandomRotate90(p=0.5),
        A.HorizontalFlip(p=0.5),
        A.VerticalFlip(p=0.5),
        A.Transpose(p=0.5),
        A.RandomBrightnessContrast(p=0.5),
        A.GaussianBlur(p=0.2, sigma_limit=(0.0, 1.0)),
        A.RandomScale(scale_limit=0.1, p=0.5),
        A.ShiftScaleRotate(shift_limit=0.0625, scale_limit=0.1, rotate_limit=15, p=0.5),
        A.HueSaturationValue(p=0.3),
    ])

    train_path = Path(args.train_dir)
    out_path = Path(args.output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    df = get_image_paths(train_path)
    # Compute class counts
    class_counts = df['class'].value_counts()
    max_count = class_counts.max()
    # Oversample minority classes up to max_count
    for cls, cnt in class_counts.items():
        needed = max_count - cnt
        if needed <= 0:
            continue
        cls_images = df[df['class'] == cls]['path'].tolist()
        if not cls_images:
            continue
        print(f"Augmenting class '{cls}' from {cnt} to {max_count} (need {needed} images)")
        # Randomly pick images to augment
        for i in tqdm(range(needed), desc=f"Augmenting {cls}"):
            src_path = random.choice(cls_images)
            # Preserve original filename and add _aug suffix with index
            stem = src_path.stem
            aug_name = f"{stem}_aug_{i}.jpg"
            dest_path = out_path / cls / aug_name
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            augment_image(src_path, aug, dest_path)

    print('Augmentation complete.')

if __name__ == '__main__':
    main()

