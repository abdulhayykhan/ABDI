# Phase 1 — Dataset Preparation

## Goal
Build a bilingual grammar/style correction dataset with ~900 high-quality pairs
(~500 English from JFLEG + ~400 Urdu/Roman-Urdu synthetic).

## Steps

### 1. Open Google Colab and mount Drive
```python
from google.colab import drive
drive.mount('/content/drive')
```

### 2. Clone the ABDI repo (or upload prepare_data.py)
```bash
!git clone https://github.com/abdulhayykhan/ABDI.git /content/ABDI
```

### 3. Install dependencies
```bash
!pip install datasets
```

### 4. Run dataset preparation
```bash
!python /content/ABDI/AbdiWrite/prepare_data.py \
  --output_dir /content/drive/MyDrive/abdi/abdiwrite/data
```

### 5. Verify output
```python
import json
with open("/content/drive/MyDrive/abdi/abdiwrite/data/train.json") as f:
    train = json.load(f)
print(f"Train pairs: {len(train)}")
print(train[0])
```

### 6. Manual Urdu review
Open `train.json`, filter `"source": "synthetic_urdu"` entries, and:
- Verify the injected error is realistic (not gibberish)
- Verify the explanation is accurate
- Flag any entries to remove (delete from JSON manually or add to a blocklist)

Target: review all ~130–200 synthetic Urdu pairs before Phase 3 training.
