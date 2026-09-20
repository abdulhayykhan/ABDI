# AbdiCV

## Domain
Resume / CV and cover letter generation.

## Status
Planned — fourth in build order (deliberately chosen as a low-risk, high-confidence "quick win" after two harder builds).

## Scope (v1)
- Input: user's raw work/education details + target role.
- Output: formatted resume content and/or a cover letter draft.
- **Out of scope for v1:** visual/PDF formatting/design (content generation only), ATS-optimization scoring.

## Base model
TBD — likely reuses AbdiWrite's base model given overlapping "writing quality" requirements.

## Dataset
Templated/structured — good candidate for synthetic data generation (structured input → structured output is easy to generate at scale and cheap to validate), unlike domains needing scraped real-world examples.

## Fine-tuning method
QLoRA on Colab T4.

## Evaluation
Manual review against a rubric (completeness, relevance, tone) — templated domain makes this faster to grade than open-ended writing tasks.
