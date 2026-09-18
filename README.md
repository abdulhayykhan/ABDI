# ABDI

**A platform of small, domain-expert language models (SLMs), each specialized for one task, with a general-purpose fallback model for everything else.**

> Status: early planning / build stage. Nothing below is final — build order, model sizes, and scope will change as real results come in. This document is a working plan, not a finished spec.

---

## What is ABDI?

ABDI is a collection of small (≈0.5B–3B parameter) fine-tuned language models, each an expert in one narrow domain, instead of one large general-purpose model trying to do everything. The naming convention follows a simple pattern in Urdu/Roman-Urdu: **"Abdi ___ karta hai"** (Abdi does ___) — each model's name states what it does.

The core bet: a small model, fine-tuned tightly on one domain with a clear evaluation metric, can outperform a general-purpose model of similar or even larger size *within that domain*, while being cheap enough to run on modest hardware.

### Why SLMs instead of one big LLM

- Cheaper to train and run — feasible on consumer/free-tier hardware (this project is being built on a 4GB integrated-GPU laptop + free-tier Google Colab T4).
- Narrower scope means narrower, objectively measurable evaluation — you can actually tell if a fine-tune improved something.
- Inspired partly by [Needle 2](https://cactuscompute.com/needle) (Cactus Compute) — a 45M-parameter tool-calling model shipped as a 14MB binary — as a reference point for how far small, tightly-scoped models can go on constrained hardware. ABDI is not a clone of Needle 2's architecture; it borrows the *philosophy* of narrow scope + small footprint, not the specific Simple Attention Network / Cactus Quants approach.

---

## Architecture

ABDI is **not** a true Mixture-of-Experts (MoE) system in the technical sense (no joint training, no shared embeddings, no learned token-level gating). It is a **dispatcher architecture**: independently trained, independently deployed SLMs, with a routing layer that decides which model handles a given query.

```
User query
    │
    ▼
[ Dispatcher / intent classifier ]
    │
    ├── confident match → route to the matching domain expert (e.g. AbdiSQL, AbdiWrite, ...)
    │
    └── no confident match → route to AbdiChat (general-purpose fallback)
```

- Each domain expert is scoped narrowly on purpose. A model that tries to do everything can't be evaluated meaningfully and stops being an "expert."
- **AbdiChat** exists specifically to catch queries that don't fit any domain expert — it is not meant to compete with the domain experts on their own turf, and it is not the platform's default answer for everything.
- The dispatcher itself (intent classification + routing) is a separate, not-yet-built component. Until it exists, each SLM is usable standalone.

---

## Build order and status

Models are built in an order chosen by **data availability, ease of objective evaluation, and how well the build validates the pipeline** — not by which name sounds best. Two domains (AbdiLaw, AbdiMed) carry real liability risk and are deliberately scoped narrow and built last, with mandatory refusal behavior as part of their training data, not just a UI disclaimer.

| # | Model | Domain | Status |
|---|-------|--------|--------|
| 1 | AbdiSQL | SQL query generation/explanation | In progress |
| 2 | AbdiWrite | Bilingual (Urdu/English) writing & grammar correction | Planned |
| 3 | AbdiTranslate | Urdu–English translation | Planned |
| 4 | AbdiCV | Resume / cover letter generation | Planned |
| 5 | AbdiData | Spreadsheet / tabular data Q&A | Planned |
| 6 | AbdiMarketing | Ad copy / SEO / marketing content | Planned |
| 7 | AbdiMath | Math reasoning & tutoring | Planned |
| 8 | AbdiCode | Code generation & debugging (scoped to 1–2 languages initially) | Planned |
| 9 | AbdiNews | News summarization | Planned |
| 10 | AbdiTeach | Education & tutoring | Planned |
| 11 | AbdiFinance | Invoice/accounting term explanation | Planned |
| 12 | AbdiSupport | Customer-support conversational assistant | Planned |
| 13 | AbdiLaw | Contract *clause explanation* only — no drafting | Planned, scoped narrow |
| 14 | AbdiMed | Medical terminology / lab-report explanation only — no diagnosis/treatment | Planned, scoped narrow |
| 15 | AbdiChat | General-purpose fallback model for the dispatcher | Planned |

See each folder's `README.md` for domain-specific scope, dataset plan, base model choice, and evaluation method.

---

## Hardware / compute

- Local: 4GB integrated GPU (Intel HD Graphics 620) — used for code editing/light testing only, **not** training (no CUDA support).
- Training: free-tier Google Colab (Tesla T4, confirmed working), via QLoRA 4-bit fine-tuning.
- Base models: existing small open-weight instruction-tuned models (e.g. Qwen2.5 family), fine-tuned with LoRA/QLoRA — this project does not pretrain models from scratch.

---

## Research / academic component

This project is also intended to form the basis of a thesis and potential publication. **The specific research question is not yet finalized** — candidate directions include domain-specialization efficiency vs. a general model at equal parameter budget, dispatcher/routing accuracy, and low-resource (Urdu) fine-tuning methodology. This section will be updated once the research question is locked, since it will determine what experiments and ablations are logged during training, not just the end results.

---

## Disclaimer

Everything in this repository is a work-in-progress research/learning project. Domains involving health (AbdiMed) and legal content (AbdiLaw) are explicitly scoped to information/explanation only and are not a substitute for professional medical or legal advice.
