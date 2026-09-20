# AbdiSQL-1.0

> **Domain:** Natural Language → SQLite Query Generation & Explanation  
> **Status:** **Complete & Published (v1.0)**  
> **Hugging Face Hub:** [`abdulhayykhan/AbdiSQL-1.0`](https://huggingface.co/abdulhayykhan/AbdiSQL-1.0)  
> **Kaggle Models:** [`abdulhayykhan/abdisql`](https://www.kaggle.com/models/abdulhayykhan/abdisql)  
> **Kaggle Starter Notebook:** [`abdulhayykhan/abdisql-starter`](https://www.kaggle.com/code/abdulhayykhan/abdisql-starter)  

---

## Executive Summary

**AbdiSQL-1.0** is an instruction-tuned, domain-expert Small Language Model (SLM) specialized in translating complex natural language questions into precise, executable **SQLite** queries based on provided database schemas.

It is **Model #1 of the ABDI Platform** (a 15-model ecosystem of specialized lightweight models), designed to prove domain-specialization efficiency on constrained hardware without requiring massive multi-GPU server infrastructure.

---

## Model Specifications

| Attribute | Specification |
| :--- | :--- |
| **Model Name** | AbdiSQL-1.0 |
| **Model Type** | Causal Decoder-Only Transformer (Instruction-Tuned) |
| **Base Model** | [`Qwen/Qwen2.5-Coder-1.5B-Instruct`](https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct) |
| **Target Dialect** | SQLite |
| **Total Parameters** | 1.54 Billion (1,543,714,816) |
| **Trainable Parameters** | 1,089,536 (0.0705% of base parameters via LoRA) |
| **Precision** | 16-bit Floating Point (`float16` merged release, 3.09 GB) |
| **Context Length** | 32,768 tokens |
| **Training Hardware** | 1x NVIDIA Tesla T4 GPU (16 GB VRAM) on Google Colab |
| **License** | Apache 2.0 |

---

## Scope (v1.0)

- **Input:** A database schema (DDL statements / table structures) + natural language question.
- **Output:** Syntactically valid SQLite query (+ optional explanation).
- **Single dialect for v1:** SQLite (matches Spider benchmark format).
- **Out of scope for v1:** Multi-dialect translation (Postgres/MySQL specific functions), DDL schema mutations (`ALTER`, `DROP`), query execution plan optimization.

---

## Dataset & Training Data

- **Primary Benchmark:** [Yale Spider Benchmark](https://yale-lily.github.io/spider/) (complex, cross-domain text-to-SQL).
- **Training Subset:** 1,350 instruction pairs balanced across 166 relational schemas.
- **Zero Schema Leakage:** Partitioned strictly by database (`db_id`), ensuring evaluation measures true generalization to unseen databases rather than memorization.

---

## Fine-Tuning Methodology

- **Technique:** QLoRA (Quantized Low-Rank Adaptation) in 4-bit NormalFloat (NF4).
- **LoRA Configuration:** Rank ($r$) = 8, Alpha ($\alpha$) = 16, Dropout = 0.05.
- **Target Modules:** All attention and MLP projections (`q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`).
- **Optimization:** Learning rate $1 \times 10^{-4}$ with Cosine decay, 2 epochs, batch size 2 with gradient accumulation.
- **Precision Safeguards:** Explicit FP32 casting for trainable LoRA weights to ensure numerical stability on Turing architecture (Tesla T4).

---

## Benchmark & Empirical Results

Evaluated using **Execution Accuracy**—the generated SQL queries were run against live SQLite database instances and the resulting record tables were strictly compared against ground-truth execution results:

| Metric | Zero-Shot Base (`Qwen2.5-Coder-1.5B`) | Fine-Tuned AbdiSQL-1.0 | Absolute Gain |
| :--- | :---: | :---: | :---: |
| **Held-Out Execution Accuracy (150 queries)** | 51.33% (77 / 150) | **54.67% (82 / 150)** | **+3.34%** |
| **Syntax Validity Rate** | 64.00% | **69.33% (104 / 150)** | **+5.33%** |
| **Spider Dev Split Execution Accuracy** | 43.00% | **47.00% (47 / 100)** | **+4.00%** |
| **Evaluation Gate Status** | — | **PASS** | — |

Detailed benchmark reports and analysis are documented in [`RESULTS.md`](RESULTS.md).

---

## Quick Start & Usage

### 1. Python (`transformers`)
```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

model_id = "abdulhayykhan/AbdiSQL-1.0"

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    device_map="auto"
)

schema = """
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name TEXT,
    department TEXT,
    salary INTEGER
);
"""
question = "Find all employees in Engineering earning more than 80000."

messages = [
    {
        "role": "system",
        "content": "You are AbdiSQL, a domain-expert language model specialized in generating precise SQLite queries from database schemas and questions."
    },
    {
        "role": "user",
        "content": f"{schema.strip()}\n\nQuestion: {question}"
    }
]

prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

with torch.no_grad():
    outputs = model.generate(**inputs, max_new_tokens=128, temperature=0.0)

print(tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True))
```

### 2. Standalone CLI Inference
```bash
python AbdiSQL/inference.py \
    --schema "Table employees (id, name, department, salary)" \
    --question "Find employees with salary over 80000"
```

---

## Directory Structure

```
AbdiSQL/
├── BUILD_PLAN.md             # Strict phase-by-phase build specification
├── RESULTS.md                # Quantitative evaluation and benchmark records
├── README.md                 # Domain documentation and usage guide (this file)
├── prepare_data.py           # Spider dataset downloading and ChatML formatting
├── inference.py              # CLI inference engine for local and 4-bit generation
├── abdisql_pipeline.ipynb    # End-to-end training and evaluation notebook
└── docs/                     # Detailed architectural logs
    ├── 00-environment-setup.md
    ├── 01-base-model-selection.md
    ├── 02-dataset-preparation.md
    ├── 03-fine-tuning.md
    ├── 04-merge-and-inference-prep.md
    ├── 05-evaluation.md
    └── 06-export.md
```
