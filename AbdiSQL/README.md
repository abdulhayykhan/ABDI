# AbdiSQL

**"Abdi query banata hai"** — Abdi builds the query.

## Domain
Natural language → SQL query generation and explanation.

## Status
In progress — first model in the build order.

## Scope (v1)
- Input: a database schema + a natural language question.
- Output: a SQL query (+ optional plain-language explanation of what it does).
- Single dialect for v1 (SQLite or Postgres — not both).
- **Out of scope for v1:** multi-dialect support, query optimization, database schema design, query execution planning.

## Base model
Qwen2.5-Coder-1.5B-Instruct (fallback: Qwen2.5-Coder-0.5B if memory-constrained). Chosen for code/structured-output specialization and small footprint suitable for QLoRA 4-bit fine-tuning on a free-tier T4.

## Dataset
- Primary: [Spider](https://yale-lily.github.io/spider) (cross-domain text-to-SQL, ~10K examples).
- Supplementary: WikiSQL for simpler warm-up examples.
- v1 training subset: ~1000–2000 examples (not the full set) to keep training time reasonable on constrained compute.

## Fine-tuning method
QLoRA, 4-bit, via `transformers` + `peft` + `trl` (SFTTrainer). LoRA rank 8, targeting attention projection layers. Gradient accumulation + checkpointing to fit T4 memory.

## Evaluation
**Execution accuracy** — the generated SQL is run against the actual database and the result set is compared to ground truth. This is an objective, automatable metric (no manual grading required), which is why this model was chosen to go first: it validates the fine-tuning pipeline against a metric that can't be fudged.

Fine-tuned model is compared against the zero-shot base model on the same held-out set — if there's no measurable improvement, the fine-tune didn't work, regardless of how outputs look casually.
