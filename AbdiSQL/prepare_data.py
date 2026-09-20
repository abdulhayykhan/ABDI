"""
AbdiSQL - Phase 3: Dataset Preparation
Downloads Spider dataset, parses schema metadata, creates a balanced
multi-database subset (1,000–2,000 examples), formats into instruction pairs,
and splits into 90% train / 10% held-out evaluation sets.
"""

import os
import json
import random
import zipfile
import urllib.request
from collections import defaultdict
from typing import Dict, List, Tuple, Any

RANDOM_SEED = 42
TARGET_TOTAL_EXAMPLES = 1600  # Within 1,000-2,000 range per build plan
TRAIN_RATIO = 0.90            # ~1,440 train, ~160 held-out eval (>100 min)

# Spider dataset download mirrors
SPIDER_GDOWN_ID = "1_AckXtG_hrQUopoqqGXhgukslDeU0et4"
SPIDER_DIRECT_URL = "https://raw.githubusercontent.com/taoyds/spider/master"


def download_and_extract_spider(data_dir: str) -> Tuple[str, str, str]:
    """
    Ensures Spider dataset (train_spider.json, tables.json, database/) exists in data_dir.
    Returns paths to (train_spider.json, tables.json, database_dir).
    """
    os.makedirs(data_dir, exist_ok=True)
    train_file = os.path.join(data_dir, "spider", "train_spider.json")
    tables_file = os.path.join(data_dir, "spider", "tables.json")
    db_dir = os.path.join(data_dir, "spider", "database")

    if os.path.exists(train_file) and os.path.exists(tables_file) and os.path.exists(db_dir):
        print(f"[Dataset] Spider files already present in {data_dir}/spider")
        return train_file, tables_file, db_dir

    zip_path = os.path.join(data_dir, "spider.zip")

    print("[Dataset] Downloading Spider dataset...")
    # Attempt download via gdown (recommended for Colab)
    downloaded = False
    try:
        import gdown
        url = f"https://drive.google.com/uc?id={SPIDER_GDOWN_ID}"
        gdown.download(url, zip_path, quiet=False)
        if os.path.exists(zip_path) and os.path.getsize(zip_path) > 1024 * 1024:
            downloaded = True
    except Exception as e:
        print(f"[Dataset] gdown failed ({e}), falling back to direct Hugging Face / curl...")

    if not downloaded:
        # Fallback to downloading zip from Hugging Face datasets hub or alternative mirror
        hf_zip_url = "https://huggingface.co/datasets/xlangai/spider/resolve/main/spider.zip"
        try:
            urllib.request.urlretrieve(hf_zip_url, zip_path)
            downloaded = True
        except Exception as e:
            raise RuntimeError(
                f"Failed to download Spider dataset automatically: {e}. "
                f"Please manually place spider.zip in {data_dir}"
            )

    print(f"[Dataset] Extracting {zip_path}...")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(data_dir)

    assert os.path.exists(train_file), f"Expected {train_file} not found after extraction."
    assert os.path.exists(tables_file), f"Expected {tables_file} not found after extraction."
    assert os.path.exists(db_dir), f"Expected {db_dir} not found after extraction."

    print(f"[Dataset] Spider dataset successfully extracted to {data_dir}/spider")
    return train_file, tables_file, db_dir


def build_schema_lookup(tables_file: str) -> Dict[str, str]:
    """
    Parses Spider's tables.json into standardized schema string descriptions per db_id.
    Format:
      Database Schema: <db_id>
      Table: <table_name> (<col1> <type> [PK], <col2> <type>, ...)
      Foreign Keys: <table1>.<col1> -> <table2>.<col2>
    """
    with open(tables_file, "r", encoding="utf-8") as f:
        tables_data = json.load(f)

    schemas = {}
    for db in tables_data:
        db_id = db["db_id"]
        table_names = db["table_names_original"]
        col_names = db["column_names_original"]  # [table_idx, col_name]
        col_types = db["column_types"]
        pks = set(db["primary_keys"])
        fks = db["foreign_keys"]  # [[col_idx1, col_idx2], ...]

        # Group columns by table
        table_cols = defaultdict(list)
        for idx, (t_idx, c_name) in enumerate(col_names):
            if t_idx == -1:
                continue  # Skip '*' column
            t_name = table_names[t_idx]
            ctype = col_types[idx]
            is_pk = " [PRIMARY KEY]" if idx in pks else ""
            table_cols[t_name].append(f"{c_name} {ctype}{is_pk}")

        # Format foreign keys
        fk_strings = []
        for col1_idx, col2_idx in fks:
            t1_idx, c1_name = col_names[col1_idx]
            t2_idx, c2_name = col_names[col2_idx]
            if t1_idx >= 0 and t2_idx >= 0:
                fk_strings.append(
                    f"{table_names[t1_idx]}.{c1_name} -> {table_names[t2_idx]}.{c2_name}"
                )

        schema_lines = [f"Database Schema: {db_id}"]
        for t_name in table_names:
            cols_str = ", ".join(table_cols[t_name])
            schema_lines.append(f"Table {t_name}: ({cols_str})")
        if fk_strings:
            schema_lines.append(f"Foreign Keys: {', '.join(fk_strings)}")

        schemas[db_id] = "\n".join(schema_lines)

    return schemas


def create_balanced_subset(
    train_file: str,
    schema_lookup: Dict[str, str],
    target_count: int = TARGET_TOTAL_EXAMPLES,
    train_ratio: float = TRAIN_RATIO,
    seed: int = RANDOM_SEED
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Selects a balanced subset of training examples spanning all available db_id schemas.
    Formats each into:
      {
        "instruction": "<schema description>\n\nQuestion: <question>",
        "output": "<gold SQL query>",
        "db_id": "<db_id>",
        "gold_query": "<gold SQL query>"
      }
    Splits into train and held-out evaluation sets (~90% / ~10%).
    """
    random.seed(seed)
    with open(train_file, "r", encoding="utf-8") as f:
        all_train = json.load(f)

    # Group examples by database schema (db_id)
    by_db = defaultdict(list)
    for item in all_train:
        by_db[item["db_id"]].append(item)

    num_dbs = len(by_db)
    base_per_db = target_count // num_dbs
    remainder = target_count % num_dbs

    sampled_examples = []
    # Distribute sampling evenly across databases
    db_keys = sorted(list(by_db.keys()))
    random.shuffle(db_keys)

    for idx, db_id in enumerate(db_keys):
        examples = by_db[db_id]
        quota = base_per_db + (1 if idx < remainder else 0)
        selected = random.sample(examples, min(quota, len(examples)))
        sampled_examples.extend(selected)

    print(f"[Dataset] Sampled {len(sampled_examples)} examples across {num_dbs} distinct database schemas.")

    # Shuffle sampled examples
    random.shuffle(sampled_examples)

    # Split into train (90%) and held-out eval (10%)
    split_idx = int(len(sampled_examples) * train_ratio)
    raw_train = sampled_examples[:split_idx]
    raw_eval = sampled_examples[split_idx:]

    def format_item(item: Dict[str, Any]) -> Dict[str, Any]:
        db_id = item["db_id"]
        schema_desc = schema_lookup.get(db_id, f"Database: {db_id}")
        question = item["question"]
        gold_sql = item["query"]
        return {
            "instruction": f"{schema_desc}\n\nQuestion: {question}",
            "output": gold_sql,
            "db_id": db_id,
            "gold_query": gold_sql
        }

    formatted_train = [format_item(x) for x in raw_train]
    formatted_eval = [format_item(x) for x in raw_eval]

    print(f"[Dataset] Train set size: {len(formatted_train)} examples")
    print(f"[Dataset] Held-out eval set size: {len(formatted_eval)} examples (held-out gate check)")

    return formatted_train, formatted_eval


def save_splits(train_data: List[Dict[str, Any]], eval_data: List[Dict[str, Any]], output_dir: str):
    """Saves formatted train and held-out eval datasets to disk/Drive."""
    os.makedirs(output_dir, exist_ok=True)
    train_path = os.path.join(output_dir, "train.json")
    eval_path = os.path.join(output_dir, "eval_held_out.json")

    with open(train_path, "w", encoding="utf-8") as f:
        json.dump(train_data, f, indent=2)

    with open(eval_path, "w", encoding="utf-8") as f:
        json.dump(eval_data, f, indent=2)

    print(f"[Dataset] Saved training split to: {train_path}")
    print(f"[Dataset] Saved held-out eval split to: {eval_path}")


def prepare_dataset(data_dir: str, output_dir: str):
    train_file, tables_file, db_dir = download_and_extract_spider(data_dir)
    schemas = build_schema_lookup(tables_file)
    train_data, eval_data = create_balanced_subset(train_file, schemas)
    save_splits(train_data, eval_data, output_dir)
    print("[Dataset] Phase 3 preparation complete.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Prepare AbdiSQL dataset from Spider")
    parser.add_argument("--data_dir", type=str, default="/content/drive/MyDrive/abdi/abdisql/data")
    parser.add_argument("--output_dir", type=str, default="/content/drive/MyDrive/abdi/abdisql/data")
    args = parser.parse_args()
    prepare_dataset(args.data_dir, args.output_dir)
