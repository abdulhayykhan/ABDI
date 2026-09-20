# Phase 4: Model Merging & Standalone Weight Export (AbdiSQL)

## Overview
Fusion of the trained LoRA adapter weights into the base model parameters (`Qwen2.5-Coder-1.5B-Instruct`) to produce a single, standalone deployable model that operates without PEFT wrappers.

## Merging Strategy & Hardware Management
Merging 16-bit float model weights on the GPU alongside active training states frequently triggers CUDA out-of-memory errors on a 15 GB T4. To eliminate memory pressure, merging was offloaded to system RAM / CPU:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch
import gc

# 1. Clean up GPU memory
if 'model' in globals(): del model
if 'trainer' in globals(): del trainer
torch.cuda.empty_cache()
gc.collect()

# 2. Load base model on CPU in FP16
base_model = AutoModelForCausalLM.from_pretrained(
    ACTIVE_MODEL_ID,
    torch_dtype=torch.float16,
    device_map="cpu",
    trust_remote_code=True
)

# 3. Attach trained LoRA adapter from Drive
peft_model = PeftModel.from_pretrained(base_model, FINAL_ADAPTER_DIR)

# 4. Fuse weights into base layers
merged_model = peft_model.merge_and_unload()

# 5. Persist merged model to Google Drive
merged_model.save_pretrained(MERGED_MODEL_DIR)
tokenizer.save_pretrained(MERGED_MODEL_DIR)
```

## Dependency Fix
- **Issue:** Shared library warnings (`_C_cutlass_90a.abi3.so`, `_C_mxfp8.cpython`) from `torchao` during weight serialization.
- **Fix:** Ran `!pip install -U torchao` (upgraded to `torchao-0.18.0`) to provide clean PyTorch 2.x tensor serialization.

## Checkpoint / Gate Outcome
- **Gate Requirement:** Merged weights saved to Drive, loadable independently of PEFT.
- **Status:** **PASS**
- **Output Path:** `/content/drive/MyDrive/abdi/abdisql/merged_model`
- **Artifacts:** Standalone `model.safetensors` (~3.09 GB), complete tokenizer vocabulary (`vocab.json`, `merges.txt`, `tokenizer.json`), and model configuration files.
