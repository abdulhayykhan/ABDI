# AbdiCode

**"Abdi code karta hai"** — Abdi codes.

## Domain
Code generation and debugging.

## Status
Planned — eighth in build order.

## Scope (v1)
- **Deliberately scoped to 1–2 languages (Python + JavaScript) for v1**, despite the platform-level name implying "any language." At small model scale (sub-3B), attempting broad multi-language coverage produces shallow, unreliable results across all of them rather than real competence in any — this contradicts the "domain expert" premise the whole platform is built on. Broader language support is a post-v1 goal once the narrow version is proven, not a v1 requirement.
- Input: a coding task or buggy code snippet.
- Output: generated/fixed code + brief explanation.
- **Out of scope for v1:** full application scaffolding, multi-file projects, any language beyond Python/JS.

## Base model
Qwen2.5-Coder (same family as AbdiSQL) — code-specialized, small footprint.

## Dataset
Existing code-instruction datasets (e.g. CodeAlpaca-style sets), not raw scraped GitHub (licensing/noise issues).

## Fine-tuning method
QLoRA on Colab T4.

## Evaluation
Pass rate on a held-out benchmark subset (e.g. a filtered subset of HumanEval/MBPP for Python) — objective, executable evaluation, similar philosophy to AbdiSQL's execution accuracy.
