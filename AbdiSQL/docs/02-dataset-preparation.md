# Phase 2: Dataset Preparation & Baseline Generation (AbdiSQL)

## Overview
Download and extraction of the Spider cross-database text-to-SQL dataset, schema extraction, generation of a balanced training/evaluation subset across all schemas, and pre-fine-tuning zero-shot baseline computation on the held-out split.

## Dataset Sourcing
- **Dataset:** [Spider](https://yale-lily.github.io/spider) (cross-domain text-to-SQL benchmark)
- **Archive:** `spider_data.zip` (~196MB) downloaded from Hugging Face mirror (`HAL-9001/spider-databases`) and cached to Google Drive at `/content/drive/MyDrive/abdi/abdisql/spider_data.zip`.
- **Extracted Structure:**
  - `tables.json`: 166 database schemas with table names, column types, primary keys, and foreign keys.
  - `train_spider.json`: ~7,000 text-to-SQL query pairs.
  - `database/`: Folder of individual SQLite `.sqlite` databases matching each `db_id`.

## Schema Formatting & Balanced Sampling

### 1. Schema Representation
Constructed standardized schema strings per `db_id` matching inference expectations:
```text
Database Schema: <db_id>
Table <table_name>: (<col1> <type> (PRIMARY KEY), <col2> <type>, ...)
Foreign Keys: <table>.<col> = <ref_table>.<ref_col>; ...
```

### 2. Balanced Subset Sampling
- **Target Size:** 1,500 examples (within the 1,000–2,000 target specified in `BUILD_PLAN.md`).
- **Strategy:** Grouped Spider training data by `db_id` and sampled uniformly across all schemas with `random.seed(42)` to prevent overfitting to a small subset of database schemas.
- **Split:**
  - **Train Split (90%):** 1,350 examples saved to `/content/drive/MyDrive/abdi/abdisql/data/train_subset.json`
  - **Held-Out Eval Split (10%):** 150 examples saved to `/content/drive/MyDrive/abdi/abdisql/data/held_out_eval.json` (satisfies >100 minimum threshold).
  - *Spider Dev Set:* Kept completely untouched during this phase.

## Zero-Shot Baseline Computation
Before training, the loaded `Qwen2.5-Coder-1.5B-Instruct` model was evaluated zero-shot across all 150 held-out examples:
- **Prompt:** ChatML format with system prompt: `"You are AbdiSQL, a domain-expert language model specialized in generating precise SQLite queries from database schemas and questions."`
- **Inference:** Greedy generation (`do_sample=False`, `max_new_tokens=128`).
- **Saved Predictions:** `/content/drive/MyDrive/abdi/abdisql/eval_results/baseline_zero_shot_eval.json`.

## Checkpoint / Gate Outcome
- **Gate Requirement:** Balanced dataset saved to persistent storage, held-out set $\ge$ 100 examples, zero-shot baseline predictions saved before fine-tuning starts.
- **Status:** **PASS**
- **Artifacts:**
  - Train dataset: `data/train_subset.json` (1,350 items)
  - Held-out evaluation: `data/held_out_eval.json` (150 items)
  - Baseline predictions: `eval_results/baseline_zero_shot_eval.json` (150 items)
