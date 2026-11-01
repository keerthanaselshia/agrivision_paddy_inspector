import argparse
import os
import json
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.model_selection import GroupShuffleSplit
import yaml
import shutil
from tqdm import tqdm

# Load config
def load_config(cfg_path: str) -> dict:
    with open(cfg_path, 'r') as f:
        return yaml.safe_load(f)

def load_metadata(meta_path: str) -> pd.DataFrame:
    return pd.read_csv(meta_path)

def compute_phash_int(phash_str: str) -> int:
    # Convert hex string to integer for hamming distance
    return int(phash_str, 16) if phash_str else 0

def hamming_distance(a: int, b: int) -> int:
    return bin(a ^ b).count('1')

def cluster_groups(df: pd.DataFrame, max_dist: int) -> pd.Series:
    """Assign a group_id to each image based on perceptual hash clustering.
    Returns a Series aligned with df index containing group_id strings.
    """
    phashes = df['phash'].fillna('').apply(lambda x: int(x, 16) if x else 0)
    n = len(df)
    group_ids = [-1] * n
    current_gid = 0
    for i in range(n):
        if group_ids[i] != -1:
            continue
        group_ids[i] = current_gid
        for j in range(i + 1, n):
            if group_ids[j] != -1:
                continue
            if hamming_distance(phashes[i], phashes[j]) <= max_dist:
                group_ids[j] = current_gid
        current_gid += 1
    return pd.Series(group_ids, index=df.index).astype(str)

def parse_field_group_id(filepath: str) -> str:
    # Expected pattern: Fxx_Pyy_... e.g., F03_P12_blast_001.jpg
    name = Path(filepath).stem
    parts = name.split('_')
    if len(parts) >= 2:
        return f"{parts[0]}_{parts[1]}"
    return name

def main():
    parser = argparse.ArgumentParser(description='Group images and split dataset')
    parser.add_argument('--processed-dir', default='processed', help='Directory with cleaned class folders')
    parser.add_argument('--metadata', default='metadata.csv', help='Metadata CSV from merge_and_clean')
    parser.add_argument('--my-field-dir', default='my_field', help='Directory with field images')
    parser.add_argument('--final-dir', default='final', help='Output splits directory')
    parser.add_argument('--config', default='config.yaml', help='Config file')
    parser.add_argument('--split-summary', default='logs/split_summary.csv', help='CSV summary output')
    args = parser.parse_args()

    cfg = load_config(args.config)
    group_dist = cfg.get('phash_group_dist', 10)
    split_ratios = cfg.get('split_ratios', {'train': 0.7, 'val': 0.15, 'test': 0.15})
    seed = cfg.get('seed', 42)

    meta_df = load_metadata(args.metadata)
    # Add group_id for public images based on clustering
    public_df = meta_df[~meta_df['source'].isin(['my_field'])].copy()
    public_df['group_id'] = cluster_groups(public_df, group_dist)

    # Add group_id for my_field images based on filename parsing
    field_paths = []
    for root, _, files in os.walk(args.my_field_dir):
        for f in files:
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.webp')):
                field_paths.append(Path(root) / f)
    field_records = []
    for p in field_paths:
        gid = parse_field_group_id(str(p))
        field_records.append({
            'new_filename': p.name,
            'original_path': str(p),
            'source': 'my_field',
            'class': p.parent.name,  # assume folder per class already created manually
            'width': None,
            'height': None,
            'md5': None,
            'phash': None,
            'group_id': gid,
        })
    field_df = pd.DataFrame(field_records)
    # Combine
    combined_df = pd.concat([public_df, field_df], ignore_index=True)

    # Prepare split arrays
    groups = combined_df['group_id'].values
    splitter = GroupShuffleSplit(n_splits=1, test_size=split_ratios['test'] + split_ratios['val'], random_state=seed)
    train_idx, temp_idx = next(splitter.split(combined_df, groups=groups))
    # Now split temp into val and test preserving groups
    temp_groups = combined_df.iloc[temp_idx]['group_id'].values
    val_ratio = split_ratios['val'] / (split_ratios['val'] + split_ratios['test'])
    splitter_val = GroupShuffleSplit(n_splits=1, test_size=val_ratio, random_state=seed)
    val_idx, test_idx = next(splitter_val.split(combined_df.iloc[temp_idx], groups=temp_groups))
    val_idx = temp_idx[val_idx]
    test_idx = temp_idx[test_idx]

    splits = {
        'train': combined_df.iloc[train_idx],
        'val': combined_df.iloc[val_idx],
        'test': combined_df.iloc[test_idx],
    }

    # Ensure final directory structure
    for split_name, df_split in splits.items():
        split_root = Path(args.final_dir) / split_name
        for _, row in tqdm(df_split.iterrows(), total=len(df_split), desc=f'Copying {split_name}'):
            src = Path(row['original_path'])
            if not src.is_file():
                continue
            class_dir = split_root / row['class']
            class_dir.mkdir(parents=True, exist_ok=True)
            dest = class_dir / src.name
            # copy file (preserve original filename to keep traceability)
            shutil.copy2(src, dest)

    # Create empty folders for missing classes in each split
    target_classes = ['healthy', 'blast', 'brown_spot', 'blb', 'other', 'background']
    for split_name in splits.keys():
        for cls in target_classes:
            (Path(args.final_dir) / split_name / cls).mkdir(parents=True, exist_ok=True)

    # Write split summary CSV
    summary_rows = []
    for split_name, df_split in splits.items():
        counts = df_split['class'].value_counts().reindex(target_classes, fill_value=0)
        for cls, cnt in counts.items():
            summary_rows.append([split_name, cls, cnt])
    summary_df = pd.DataFrame(summary_rows, columns=['split', 'class', 'count'])
    os.makedirs(Path(args.split_summary).parent, exist_ok=True)
    summary_df.to_csv(args.split_summary, index=False)

    # Print table
    print('Split summary:')
    print(summary_df.pivot(index='class', columns='split', values='count').fillna(0).astype(int))

    # Warn if test set does not have at least 50% my_field images
    test_df = splits['test']
    field_test_cnt = (test_df['source'] == 'my_field').sum()
    total_test_cnt = len(test_df)
    if total_test_cnt > 0 and field_test_cnt / total_test_cnt < 0.5:
        print('WARNING: Field images constitute less than 50% of the test set.')
    else:
        print('Field image proportion in test set is satisfactory.')

if __name__ == '__main__':
    main()
