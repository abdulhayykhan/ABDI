# Phase 0: Environment Setup (AbdiSQL)

## Overview
Initial environment setup and hardware verification for AbdiSQL on Google Colab (free tier).

## Hardware & Runtime
- **Platform:** Google Colab Free Tier
- **GPU:** NVIDIA Tesla T4 (15,360 MiB total VRAM)
- **Driver Version:** 580.82.07
- **CUDA Version:** 13.0
- **Local Machine Constraints:** 4GB integrated GPU (Intel HD 620, no CUDA) — strictly reserved for local code editing and repository management.

## Setup Steps Executed

### 1. Workspace Persistence (Google Drive)
Mounted Google Drive to maintain persistent storage across Colab session disconnections (checkpoints, datasets, and merged adapters):
```python
from google.colab import drive
import os

drive.mount('/content/drive')
DRIVE_DIR = '/content/drive/MyDrive/abdi/abdisql'
os.makedirs(DRIVE_DIR, exist_ok=True)
```
- **Mount Point:** `/content/drive`
- **Working Directory:** `/content/drive/MyDrive/abdi/abdisql`

### 2. GPU Verification
Ran `nvidia-smi` and PyTorch CUDA check:
```python
import torch
assert torch.cuda.is_available(), "CUDA not available! Ensure Colab runtime is set to T4 GPU."
print(f"Active GPU: {torch.cuda.get_device_name(0)}")
```
- **Result:** Confirmed active device `Tesla T4`.

### 3. Dependencies Installation
Upgraded `pip` and installed core fine-tuning libraries:
```bash
pip install -q --upgrade pip
pip install -q -U bitsandbytes transformers peft trl accelerate datasets gdown
```
- Upgraded `bitsandbytes` to the latest release to prevent `No module named triton.ops` errors observed on newer Python/Triton runtimes.
- Confirmed installation of `transformers`, `peft`, `trl`, `accelerate`, and `datasets`.

## Checkpoint / Gate Outcome
- **Status:** **PASS**
- **Outcome:** Colab T4 environment validated, persistent Drive directory initialized, and all required packages installed without conflicts.
