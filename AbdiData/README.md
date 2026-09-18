# AbdiData

**"Abdi data samjhta hai"** — Abdi understands the data.

## Domain
Data analysis / spreadsheet / tabular Q&A.

## Status
Planned — fifth in build order.

## Scope (v1)
- Input: a table/spreadsheet + a natural language question about it.
- Output: an answer, and ideally the operation used to derive it (similar spirit to AbdiSQL but over tabular data directly rather than via SQL).
- **Out of scope for v1:** data visualization generation, multi-table joins, spreadsheet formula writing (that may become part of AbdiSQL/AbdiCode scope instead — avoid overlap).

## Base model
TBD — likely a code/reasoning-capable small model given the structured-reasoning nature of the task.

## Dataset
[WikiTableQuestions](https://ppasupat.github.io/WikiTableQuestions/) and similar existing table-QA benchmarks — avoids building this from scratch.

## Fine-tuning method
QLoRA on Colab T4.

## Evaluation
Answer-match accuracy against benchmark ground truth — objective, similar in spirit to AbdiSQL's execution-accuracy approach.

## Notes
Moderate reasoning difficulty — expect this to be harder than AbdiCV/AbdiSQL but easier than AbdiMath.
