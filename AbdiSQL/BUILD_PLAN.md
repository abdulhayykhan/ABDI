# AbdiSQL — Complete Build Plan

**Audience:** a coding agent executing this build. Follow phases in order. Do not skip evaluation to reach export faster — an unevaluated model is not a finished model on this project.

**Do not deviate from the locked decisions below without flagging it back to the human first.** Several ambiguities present at planning time have been resolved here; treat them as fixed unless explicitly told otherwise.

---

## 0. Locked decisions (do not re-litigate these)

| Decision | Value | Why |
|---|---|---|
| SQL dialect | **SQLite** | Matches Spider's native format exactly — no server, no auth, no infra overhead. |
| Base model | **Qwen2.5-Coder-1.5B-Instruct** | Code-specialized, fits QLoRA 4-bit on a T4 with room to spare. Fallback: Qwen2.5-Coder-0.5B if 1.5B proves unworkable in practice (see Phase 2 gate). |
| Fine-tuning method | **QLoRA, 4-bit** | Only realistic method given hardware (see Phase 1). |
| Training environment | **Google Colab, T4 GPU, native browser notebook** | Confirmed working. Do not attempt to route training through a secondary IDE/agent-connected kernel — use the native Colab notebook directly for the actual training run. |
| Dataset | **Spider**, subset of 1000–2000 examples for v1 | Full 10K deferred until v1 pipeline is proven. |
| Eval metric | **Execution accuracy** (generated SQL run against the real DB, result set compared to ground truth) | Objective, automatable — no manual grading needed. |

---

## 1. Environment setup

1. Open a **new** Colab notebook (do not reuse/append to an unrelated existing notebook — start clean).
2. Runtime → Change runtime type → **T4 GPU**. Confirm before installing anything:
   ```
   !nvidia-smi
   ```
   Must return a Tesla T4 with driver/CUDA info. If this fails, stop — do not proceed to installs on a CPU runtime.
3. Install dependencies (pin versions to avoid breaking-change surprises mid-project):
   ```
   !pip install -q transformers peft trl bitsandbytes accelerate datasets sqlite3
   ```
   (`sqlite3` is stdlib in Python but included here as a reminder it's required — no extra Colab install needed for it specifically.)
4. Verify GPU is visible to PyTorch, not just the OS:
   ```python
   import torch
   assert torch.cuda.is_available(), "CUDA not visible to PyTorch — stop and debug before continuing"
   print(torch.cuda.get_device_name(0))
   ```

---

## 2. Base model selection (gate check)

1. Load **Qwen2.5-Coder-1.5B-Instruct** in 4-bit via `bitsandbytes`.
2. Run 5–10 zero-shot SQL generation prompts (schema + question → SQL) before any fine-tuning, to establish a baseline and confirm the model loads/runs within T4 memory.
3. **Gate:** if loading or a short generation run OOMs or is unworkably slow, fall back to **Qwen2.5-Coder-0.5B** and re-run this step. Do not proceed to Phase 3 until a model is confirmed loadable and generating output within reasonable time (a few seconds per generation, not minutes).
4. Save these zero-shot outputs — they are the baseline you compare the fine-tuned model against in Phase 6. Do not skip saving this; re-generating a "baseline" after fine-tuning defeats the point of a baseline.

---

## 3. Dataset preparation

1. Download **Spider** (train + dev splits): https://yale-lily.github.io/spider/
2. From Spider's training set, select a **1000–2000 example subset**. Selection should span multiple databases/schemas, not just the first N rows — check Spider's structure and sample across `db_id` values to avoid overfitting to a handful of schemas.
3. Reformat each example into an instruction-tuning format:
   ```json
   {
     "instruction": "<schema description>\n\nQuestion: <natural language question>",
     "output": "<gold SQL query>"
   }
   ```
   Use Spider's provided schema/table info to construct the schema description consistently across all examples — the format of the schema string in training must match what you'll provide at inference time.
4. Split this subset: **~90% train / ~10% held-out eval** (held-out set should be ~100 examples minimum, per the original eval plan — do not shrink this to save time, it's the only thing that tells you if this worked).
5. **Do not use Spider's dev set for anything in this phase** — reserve it as a fully independent sanity check to run only after Phase 6 passes, in case the manually-split held-out set was accidentally too easy or leaked schema overlap with training.
6. Save the prepared dataset (train + held-out) to disk/Drive so it survives a Colab session disconnect — do not regenerate it from scratch each session.

---

## 4. Fine-tuning

1. Load base model in 4-bit (`bitsandbytes`), prepare for QLoRA via `peft`.
2. LoRA config:
   - rank: 8
   - target modules: `q_proj`, `v_proj` (add `k_proj`, `o_proj` only if memory allows after confirming rank-8/2-module config trains without OOM)
   - alpha: 16 (standard 2x rank starting point)
   - dropout: 0.05
3. Training config (`trl` SFTTrainer):
   - epochs: 2–3 (start with 2, only extend to 3 if validation loss is still clearly decreasing)
   - learning rate: 1e-4 to 2e-4 — start at 1e-4
   - batch size: 1–2, with gradient accumulation to reach an effective batch size of ~8
   - gradient checkpointing: **on** — required to fit on T4 with this config
4. **Checkpoint every N steps** (e.g. every 100 steps, or every ~10% of an epoch) to Drive — Colab free-tier sessions can disconnect; do not lose a multi-hour run to a dropped session.
5. Monitor validation loss during training, not just training loss — if validation loss starts climbing while training loss keeps falling, that's overfitting; stop early rather than continuing to the planned epoch count.
6. Save the final LoRA adapter weights (not just a checkpoint mid-run) to Drive at completion.

---

## 5. Merge and prepare for inference

1. Merge the trained LoRA adapter into the base model weights (`peft`'s merge_and_unload or equivalent) to produce a single deployable model — do this as a separate, explicit step, not implicitly at inference time, so the merged model can be saved/reused independently of the training environment.
2. Save the merged model to Drive.

---

## 6. Evaluation

1. On the held-out set from Phase 3 (the ~100-example split, NOT Spider's dev set yet):
   - For each example: generate SQL from the fine-tuned model, **execute it against the actual SQLite database**, compare the result set to the result set of the gold query executed against the same database.
   - Record: execution accuracy = (# examples where result sets match) / (total examples).
   - Also record: syntax validity rate (does the query even parse/run without error, separate from whether the result is correct) — useful diagnostic if accuracy is low, to distinguish "wrong queries" from "broken queries."
2. Run the **same held-out set through the Phase 2 zero-shot baseline outputs** (already saved — do not re-run the base model, use the saved baseline) and compute the same execution accuracy.
3. **Gate — this is the actual pass/fail check for the whole build:**
   - If fine-tuned execution accuracy is not meaningfully higher than the zero-shot baseline, the fine-tune did not work. Do not proceed to export. Return to Phase 4 and reconsider: more/better training data, different LoRA rank/target modules, more epochs, or check for a data formatting bug (most common cause of silent fine-tuning failure).
4. Only after the gate passes: run the model against Spider's **dev set** (untouched until now) as an independent confirmation the held-out result wasn't a fluke of the manual split. Record this number too — report both.

---

## 7. Export (only after Phase 6 passes)

1. Quantize the merged model to GGUF via `llama.cpp`'s conversion tooling, or export via `bitsandbytes` int4/int8 for lighter-weight serving — pick based on intended deployment target (llama.cpp/GGUF if targeting CPU/edge inference later; bitsandbytes quant if staying in a Python-serving context for now).
2. Save the exported artifact to Drive, and document (in this file or a follow-up `RESULTS.md`) the final execution accuracy numbers, model size, and any deviations from this plan that were made during the actual build.

---

## 8. Definition of done

AbdiSQL v1 is complete when all of the following exist and are true:
- A merged, fine-tuned model saved to Drive.
- A held-out-set execution accuracy number that is meaningfully higher than the zero-shot baseline on the same set.
- A dev-set execution accuracy number, run once, after the held-out gate passed.
- A callable inference path: given (schema, question) → SQL, runnable as a script, not just inline notebook cells.
- An exported, quantized artifact.

Nothing outside this list is in scope for v1 — no dispatcher integration, no multi-dialect support, no UI. Those are explicitly deferred, per the root ABDI README's build order.
