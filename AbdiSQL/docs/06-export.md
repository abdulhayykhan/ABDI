# Phase 6: Export & Quantization (AbdiSQL)

## Overview
Artifact packaging, deployment export documentation, and quantization instructions for AbdiSQL v1.

## Completed Artifacts (Google Drive)
All artifacts are preserved on persistent storage at `/content/drive/MyDrive/abdi/abdisql/`:

| Artifact | Path | Description |
|---|---|---|
| **Merged Model** | `/content/drive/MyDrive/abdi/abdisql/merged_model/` | Standalone Hugging Face FP16 model weights (`model.safetensors`, 3.09 GB) and tokenizer files. |
| **LoRA Adapter** | `/content/drive/MyDrive/abdi/abdisql/final_adapter/` | Standalone PEFT adapter weights (`adapter_model.safetensors`, ~4.4 MB). |
| **Training Checkpoints** | `/content/drive/MyDrive/abdi/abdisql/checkpoints/` | Intermediate step checkpoints. |
| **Evaluation Records** | `/content/drive/MyDrive/abdi/abdisql/eval_results/` | Zero-shot baseline outputs and evaluation logs. |
| **Benchmark Summary** | `/content/drive/MyDrive/abdi/abdisql/RESULTS.md` | Consolidated metrics report. |

---

## Quantization for Edge & Local Serving (GGUF / llama.cpp)

To serve AbdiSQL locally or on resource-constrained hardware (e.g. CPU or mobile) via `llama.cpp`:

```bash
# 1. Clone llama.cpp conversion tools
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp
pip install -r requirements.txt

# 2. Convert Hugging Face directory to Q4_K_M GGUF
python convert_hf_to_gguf.py \
    /content/drive/MyDrive/abdi/abdisql/merged_model \
    --outfile abdisql-v1-q4_k_m.gguf \
    --outtype q4_k_m
```
- **Estimated GGUF size:** ~1.1 GB (easily executable on 4GB RAM/GPU consumer laptops).

---

## Standalone Inference Script
A standalone Python script is provided in the repository at `AbdiSQL/inference.py` to allow direct command-line query generation without requiring a Jupyter environment:
```bash
python AbdiSQL/inference.py --schema "Table employees (id, name, salary)" --question "Who earns the highest salary?"
```

## Checkpoint / Gate Outcome
- **Gate Requirement:** Exported model saved to Drive, documentation complete, standalone inference path established.
- **Status:** **PASS**
- **AbdiSQL Build Status:** **Complete (v1 Gate Passed)**
