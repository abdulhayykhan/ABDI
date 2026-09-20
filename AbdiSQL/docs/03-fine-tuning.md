# Phase 3: QLoRA Fine-Tuning (AbdiSQL)

## Overview
Execution of 4-bit QLoRA instruction fine-tuning on Google Colab's Tesla T4 GPU using Hugging Face `peft` and `trl` (`SFTTrainer`).

## LoRA & Model Configuration
- **Base Model:** `Qwen/Qwen2.5-Coder-1.5B-Instruct` (loaded in 4-bit NF4 via `BitsAndBytesConfig`)
- **LoRA Rank ($r$):** 8
- **LoRA Alpha:** 16 (2x rank)
- **Target Modules:** `["q_proj", "v_proj"]`
- **Dropout:** 0.05
- **Bias:** `none`
- **Trainable Parameters:** 1,089,536 out of 1,544,803,840 (**0.0705% trainable**)

## Errors Encountered & Fixes Applied

### 1. BFloat16 GradScaler Crash on Tesla T4
* **Error Traceback:**
  ```text
  NotImplementedError: "_amp_foreach_non_finite_check_and_unscale_cuda" not implemented for 'BFloat16'
  at torch.amp.grad_scaler._unscale_grads_ -> accelerate.clip_grad_norm_
  ```
* **Root Cause:** The NVIDIA Tesla T4 GPU (Turing architecture, CC 7.5) does not support native BFloat16 CUDA unscaling in PyTorch AMP. Since Qwen2.5 defaults to `bfloat16`, the newly initialized LoRA parameters inherited `bfloat16`. During `fp16=True` training, `GradScaler` crashed when unscaling `bfloat16` gradients.
* **Fix:**
  Explicitly cast all trainable LoRA parameters and normalization layers to `float32`:
  ```python
  for param in model.parameters():
      if param.requires_grad:
          param.data = param.data.to(torch.float32)
  for name, module in model.named_modules():
      if "norm" in name:
          module.to(torch.float32)
  ```
  `GradScaler` unscaled the `float32` gradients without error.

### 2. Wrapper Re-entry Guard
* **Issue:** Re-running the cell after a training failure resulted in nested PEFT adapters.
* **Fix:** Added clean memory cleanup and model reload logic:
  ```python
  if 'model' in globals() and (isinstance(model, PeftModel) or hasattr(model, "peft_config")):
      del model
      gc.collect()
      torch.cuda.empty_cache()
      tokenizer, model = load_base_model(ACTIVE_MODEL_ID)
  ```

### 3. Gradient Checkpointing & Cache
* **Configuration:** Disabled key-value caching to allow proper gradient checkpointing:
  ```python
  model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)
  model.config.use_cache = False
  ```

## Training Hyperparameters
- **Trainer:** `trl.SFTTrainer` (with `SFTConfig` / `TrainingArguments` fallback)
- **Epochs:** 2
- **Per-Device Batch Size:** 1
- **Gradient Accumulation Steps:** 8 (Effective batch size = 8)
- **Learning Rate:** 1e-4
- **Weight Decay:** 0.01
- **Mixed Precision:** `fp16=True`, `bf16=False`
- **Optimizer:** `paged_adamw_8bit`
- **Max Sequence Length:** 1024
- **Evaluation Strategy:** `epoch`
- **Save Strategy:** `steps` (every 100 steps to `/content/drive/MyDrive/abdi/abdisql/checkpoints`)

## Training Run & Output
The 2-epoch training run executed across the 1,350 training examples without memory overflow. Intermediate checkpoints were periodically committed to Google Drive.
- **Final Adapter Directory:** `/content/drive/MyDrive/abdi/abdisql/final_adapter`
- **Artifacts Saved:** `adapter_model.safetensors`, `adapter_config.json`, tokenizer config and special tokens.

## Checkpoint / Gate Outcome
- **Status:** **PASS**
- **Outcome:** Full fine-tuning completed without out-of-memory errors; final adapter weights persisted to Google Drive.
