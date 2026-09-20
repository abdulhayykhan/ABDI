# ABDI Platform Documentation Index

This directory contains platform-level architecture notes and the global tracking index for all ABDI models. Model-specific build logs, experiments, and phase checkpoint records are located directly inside each model's respective folder (e.g. `AbdiSQL/docs/`).

---

## Model Build Status Index

Build order is strictly sequenced by data availability, objectivity of evaluation metrics, and pipeline validation value, concluding with the highest-liability models requiring verified refusal behavior.

| # | Model | Domain | Current Status | Primary Evaluation Gate | Model Build Docs |
|---|---|---|---|---|---|
| 1 | **[AbdiSQL](../AbdiSQL/README.md)** | Text-to-SQL query generation & explanation | **Complete & Published (v1.0)** | Execution accuracy vs. zero-shot baseline (+3.34% gain achieved) | [AbdiSQL/docs/](../AbdiSQL/docs/) • [HF](https://huggingface.co/abdulhayykhan/AbdiSQL-1.0) • [Kaggle](https://www.kaggle.com/models/abdulhayykhan/abdisql) |
| 2 | **AbdiWrite** | Bilingual (Urdu/English) grammar & style correction | **Planned** | Manual rubric scoring vs. baseline | *None (Planned)* |
| 3 | **AbdiTranslate** | Urdu ⇄ English sentence translation | **Planned** | BLEU / chrF vs. baseline | *None (Planned)* |
| 4 | **AbdiCV** | Resume / cover letter drafting | **Planned** | Manual rubric scoring vs. baseline | *None (Planned)* |
| 5 | **AbdiData** | Spreadsheet / tabular Q&A | **Planned** | Answer-match accuracy vs. ground truth | *None (Planned)* |
| 6 | **AbdiMarketing** | Ad copy / SEO / marketing snippets | **Planned** | Manual rubric scoring vs. baseline | *None (Planned)* |
| 7 | **AbdiMath** | Step-by-step math reasoning & tutoring | **Planned** | Final-answer accuracy + manual reasoning spot-check | *None (Planned)* |
| 8 | **AbdiCode** | Code generation & debugging (Python + JS only) | **Planned** | Pass rate on held-out executable benchmark | *None (Planned)* |
| 9 | **AbdiNews** | Single-article summarization | **Planned** | ROUGE + manual factual accuracy spot-check | *None (Planned)* |
| 10 | **AbdiTeach** | Secondary science concept explanation (Physics, Chem, Bio) | **Planned** | Manual rubric scoring vs. baseline | *None (Planned)* |
| 11 | **AbdiFinance** | Invoice terms & accounting concept explanation | **Planned** | Manual rubric scoring vs. baseline | *None (Planned)* |
| 12 | **AbdiSupport** | FAQ/KB-grounded customer support assistant | **Planned** | Rubric scoring + ungrounded query refusal test | *None (Planned)* |
| 13 | **AbdiLaw** | Contract clause explanation (no drafting) | **Planned** | Dual gate: Explanation correctness + Refusal reliability | *None (Planned)* |
| 14 | **AbdiMed** | Medical term & lab report explanation (no diagnosis) | **Planned** | Dual gate: Explanation correctness + Refusal reliability | *None (Planned)* |
| 15 | **AbdiChat** | General-purpose platform fallback | **Planned** | Conversational quality + Dispatcher integration test | *None (Planned)* |

---

## Model Spotlight: AbdiSQL-1.0 Summary
- **Status:** **Gate Passed & Publicly Released**
- **Base Model:** `Qwen/Qwen2.5-Coder-1.5B-Instruct`
- **Method:** QLoRA 4-bit on Google Colab T4 GPU
- **Execution Accuracy (Held-out Split):** **54.67%** (vs. 51.33% zero-shot baseline, **+3.34% gain**)
- **Execution Accuracy (Spider Dev Set):** **47.0%**
- **Syntax Validity:** **69.33%**
- **Public Registries:**
  - Hugging Face Model: [`abdulhayykhan/AbdiSQL-1.0`](https://huggingface.co/abdulhayykhan/AbdiSQL-1.0) (3.09 GB FP16)
  - Kaggle Model: [`abdulhayykhan/abdisql`](https://www.kaggle.com/models/abdulhayykhan/abdisql)
  - Kaggle Starter Notebook: [`abdulhayykhan/abdisql-starter`](https://www.kaggle.com/code/abdulhayykhan/abdisql-starter)
- **Detailed Build History:** [AbdiSQL/docs/](../AbdiSQL/docs/) | [Results Benchmark](../AbdiSQL/RESULTS.md)

---

## Platform Architecture Status

- **Dispatcher / Routing Layer:** **Not yet built.** Currently, no intent classifier, routing logic, or orchestration service exists. All models are trained and tested as standalone artifacts.
- **AbdiChat Fallback:** Will be designed and integrated in tandem with the dispatcher once domain models are established.
- **Thesis Research Component:** The primary research question remains **under formulation**. Candidate directions include specialization efficiency vs. a general LLM at equal parameter budgets, low-resource Urdu instruction-tuning dynamics, and dispatcher routing precision.

---

## Documentation Policy

1. **Only Executed Work is Documented:** No doc files are created for future or unexecuted phases. A model with status `Planned` contains no `docs/` folder until active execution starts.
2. **Decentralized Model Logs:** Model-specific execution logs, configurations, and gate results live in `<ModelName>/docs/` (e.g. `00-environment-setup.md` through `06-export.md`).
3. **Strict Evaluation Gates:** Models must demonstrate measurable improvement over their zero-shot base models on held-out datasets. High-liability models (AbdiLaw, AbdiMed) additionally require an independently verified refusal-reliability evaluation pass before shipping.
