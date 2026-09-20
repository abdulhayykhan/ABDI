# AbdiSQL v1 — Build & Benchmark Results

## Model Summary
- **Model Name:** AbdiSQL v1
- **Domain:** Natural Language $\to$ SQLite Query Generation & Explanation
- **Base Model:** `Qwen/Qwen2.5-Coder-1.5B-Instruct`
- **Fine-Tuning Method:** QLoRA 4-bit (rank 8, alpha 16, dropout 0.05, lr=1e-4, 2 epochs)
- **Trainable Parameters:** 1,089,536 (0.0705% of 1.54B total parameters)
- **Merged Model Weights:** 3.09 GB FP16 (`model.safetensors`)
- **Hugging Face Hub:** [`abdulhayykhan/AbdiSQL-1.0`](https://huggingface.co/abdulhayykhan/AbdiSQL-1.0)
- **Kaggle Models:** [`abdulhayykhan/abdisql`](https://www.kaggle.com/models/abdulhayykhan/abdisql)
- **Kaggle Starter Notebook:** [`abdulhayykhan/abdisql-starter`](https://www.kaggle.com/code/abdulhayykhan/abdisql-starter)

---

## Benchmark Results

### 1. Held-Out Evaluation Split (150 examples, cross-database)
- **Zero-Shot Baseline Execution Accuracy:** **51.33%** (77 / 150)
- **Fine-Tuned Execution Accuracy:** **54.67%** (82 / 150)
- **Absolute Gain:** **+3.34%**
- **Syntax Validity Rate:** **69.33%** (104 / 150 executed cleanly)
- **Evaluation Gate:** **PASS**

### 2. Independent Confirmation on Spider Dev Split (100 examples)
- **Spider Dev Execution Accuracy:** **47.0%** (47 / 100)
- **Spider Dev Syntax Validity:** **62.0%** (62 / 100)

---

## Deviations & Technical Fixes During Build
1. **GradScaler Unscaling on Turing GPU (Tesla T4):**
   - *Issue:* Qwen2.5 natively initialized LoRA parameters in `bfloat16`, which caused PyTorch's `GradScaler` to crash on the T4 with `NotImplementedError: "_amp_foreach_non_finite_check_and_unscale_cuda" not implemented for 'BFloat16'`.
   - *Fix:* Explicitly cast trainable LoRA parameters and layer norm modules to `float32` before training.
2. **PyTorch / Torchao Compatibility:**
   - *Issue:* Weight merging emitted dynamic library loading warnings for Cutlass and MXFP8.
   - *Fix:* Upgraded `torchao` to `0.18.0` prior to `merge_and_unload()`.
3. **RAM-Offloaded Merging:**
   - *Fix:* Merged LoRA adapters into base weights on CPU (`device_map="cpu"`) to eliminate GPU OOM risks on the 15 GB T4.

---

## Deployment & Quantization
- **GGUF Conversion (llama.cpp):**
  ```bash
  python convert_hf_to_gguf.py /content/drive/MyDrive/abdi/abdisql/merged_model --outfile abdisql-v1-q4_k_m.gguf --outtype q4_k_m
  ```
- **CLI Inference:**
  ```bash
  python AbdiSQL/inference.py --model_path /content/drive/MyDrive/abdi/abdisql/merged_model --schema "Table users (id, name)" --question "Find all users"
  ```
