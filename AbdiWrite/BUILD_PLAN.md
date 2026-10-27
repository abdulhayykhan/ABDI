# AbdiWrite — Build Plan

## Domain
Bilingual (Urdu / English / Roman-Urdu) grammar and style correction.

## Status
**In progress — Phase 1 (Dataset Preparation)**

---

## Phases

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Dataset preparation (JFLEG + synthetic Urdu) | **Active** |
| 2 | Base model selection (zero-shot Urdu test) | Pending |
| 3 | QLoRA fine-tuning on Colab T4 | Pending |
| 4 | Merge adapter + inference prep | Pending |
| 5 | Evaluation on held-out set | Pending |
| 6 | Export + publish (HF + Kaggle) | Pending |

---

## Phase 1 — Dataset

### English component (JFLEG)
- **Source:** [`jfleg`](https://huggingface.co/datasets/jfleg) on Hugging Face
- **Splits used:** validation + test (~1,500 pairs total)
- **Filtering:** drop pairs where source == correction (no error)
- **Gold output:** first human reference correction
- **Target after filtering:** ~500 pairs

### Urdu / Roman-Urdu component (Synthetic)
- **Source:** 40 handcrafted clean seed sentences (Urdu script + Roman-Urdu)
- **Error injection types:**
  - Izafat (possessive particle) omission — کا/کی/کے dropped
  - Verb tense mismatch — ہے ↔ تھا, ہیں ↔ تھے swapped
  - Unnatural word order — adjacent words swapped
  - Punctuation drop — ۔ removed from sentence end
  - Roman-Urdu informal spelling — `hai→he`, `main→mein`, etc.
- **Target:** ~400 pairs
- **Explanation language:** Urdu (for Urdu-script inputs), English (for Roman-Urdu inputs)

### Final dataset
- **Total target:** ~900 pairs
- **Split:** 90% train (~810) / 10% held-out eval (~90)
- **Format:** `{"instruction", "input", "output", "lang", "source"}`
- **Encoding:** UTF-8 with `ensure_ascii=False` (Urdu script preserved)

### Expanding the Urdu component (manual review step)
The synthetic Urdu set is intentionally small (40 seeds × ~4–5 error types ≈ 140–200 raw pairs).
After running `prepare_data.py`, manually review `train.json` Urdu entries and:
1. Add more clean Urdu seed sentences to `URDU_SEED_SENTENCES` in `prepare_data.py`
2. Fix any injections that produce unnatural or misleading errors
3. Re-run the script to regenerate

---

## Phase 2 — Base Model Selection

Test both candidates on **zero-shot Urdu correction** before committing to fine-tuning:

| Candidate | Params | Urdu tokenization | Notes |
|-----------|--------|-------------------|-------|
| `Qwen/Qwen2.5-1.5B-Instruct` | 1.5B | Good (multilingual BPE) | Preferred for consistency with AbdiSQL base family |
| `google/gemma-2-2b-it` | 2B | Moderate | Larger, may generalise better but slower on T4 |

Zero-shot test prompt:
```
Correct the grammar and writing style of the following Urdu text.

Text: وہ بازار سے سبزیاں لایا تھا
```

Select whichever model produces more natural, meaning-preserving Urdu output.

---

## Phase 3 — Fine-Tuning (QLoRA, Colab T4)

Same pipeline as AbdiSQL:
- 4-bit quantization (BitsAndBytesConfig)
- LoRA rank 8, alpha 16, target modules: q_proj, v_proj
- Learning rate: 1e-4, 2 epochs
- Batch size: 4 with gradient accumulation 4 (effective 16)
- Max sequence length: 512 tokens

---

## Phase 5 — Evaluation

**Metric:** No fully automatic metric exists for "is this correction meaning-preserving and natural."

Evaluation procedure:
1. Run model on held-out eval set (`eval_held_out.json`)
2. Manually score each output 0–2:
   - **2** = correction is better than source AND meaning is preserved
   - **1** = partially correct (some improvement, minor issues remain)
   - **0** = no improvement or meaning changed
3. Report: `mean score`, `% scored ≥ 1`, `% scored = 2`
4. Compare against zero-shot base model on the same set
