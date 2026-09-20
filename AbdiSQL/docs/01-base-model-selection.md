# Phase 1: Base Model Selection & Zero-Shot Verification (AbdiSQL)

## Overview
Model selection, 4-bit quantization setup, and zero-shot baseline latency/VRAM verification on the Tesla T4 GPU.

## Model Candidates
- **Primary Target:** `Qwen/Qwen2.5-Coder-1.5B-Instruct`
- **Fallback Alternative:** `Qwen/Qwen2.5-Coder-0.5B-Instruct` (to be triggered automatically if 1.5B OOMs or exhibits generation latency > 20s)

## Configuration
Loaded model via Hugging Face `transformers` using `BitsAndBytesConfig`:
```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

BASE_MODEL_ID = "Qwen/Qwen2.5-Coder-1.5B-Instruct"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True
)

tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_ID, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL_ID,
    quantization_config=bnb_config,
    device_map="auto",
    torch_dtype=torch.float16,
    trust_remote_code=True
)
```

## Real Measurements

### 1. Memory Footprint
- **VRAM Allocated:** 1.07 GB
- **VRAM Reserved:** 1.12 GB
- **Headroom:** ~13.8 GB free on the 15 GB Tesla T4. No memory pressure detected. Fallback to 0.5B was not required.

### 2. Zero-Shot Generation & Latency Check
Ran a warmup pass (`SELECT 1;`) followed by 3 schema-grounded zero-shot generation prompts:

* **Prompt 1 (Filter on department & salary):**
  * *Schema:* `company` (`employees`: `emp_id`, `name`, `department`, `salary`)
  * *Question:* "Find the names of all employees in the 'Sales' department who earn more than 50000."
  * *Generated SQL:* `SELECT name FROM employees WHERE department = 'Sales' AND salary > 50000;`
  * *Latency:* 12.84s

* **Prompt 2 (Aggregate count):**
  * *Schema:* `school` (`students`, `courses`)
  * *Question:* "How many students are enrolled in 'Math'?"
  * *Generated SQL:* `SELECT COUNT(student_id) FROM courses WHERE course_name = 'Math'`
  * *Latency:* 1.49s

* **Prompt 3 (Ordering and inequality filter):**
  * *Schema:* `library` (`books`: `book_id`, `title`, `author`, `year`)
  * *Question:* "List all book titles published after 2020 ordered by year descending."
  * *Generated SQL:* `SELECT title FROM books WHERE year > 2020 ORDER BY year DESC;`
  * *Latency:* 10.28s

* **Average Generation Latency:** **8.20s per generation**

## Gate / Checkpoint Outcome
- **Gate Requirement:** Average generation latency < 20.0s, no CUDA out-of-memory errors.
- **Status:** **PASS**
- **Decision:** Committed `Qwen/Qwen2.5-Coder-1.5B-Instruct` as the base model for AbdiSQL fine-tuning. Fallback to 0.5B was not triggered.

## Resumption Notes
The next pending phase is **Phase 2: Dataset Preparation** (`02-dataset-preparation.md`), which requires downloading the Spider dataset, extracting the SQLite databases, creating the balanced ~1,000–2,000 example training subset, and computing zero-shot baseline execution accuracy on the held-out evaluation set.
