# AbdiMarketing

**"Abdi marketing karta hai"** — Abdi does the marketing.

## Domain
Ad copy, marketing content, SEO writing.

## Status
Planned — sixth in build order.

## Scope (v1)
- Input: product/service description + target platform (e.g. social ad, product listing, SEO blurb).
- Output: marketing copy suited to that format.
- **Out of scope for v1:** full campaign strategy, ad performance prediction, image/visual ad generation.

## Base model
TBD.

## Dataset
TBD — likely needs scraped/curated real ad-copy examples plus synthetic generation; public high-quality marketing-copy datasets are less standardized than e.g. Spider or OPUS.

## Fine-tuning method
QLoRA on Colab T4.

## Evaluation
**Known weak point for this domain:** "is this good ad copy" is inherently subjective — no clean automatic metric exists (unlike AbdiSQL's execution accuracy or AbdiTranslate's BLEU). Plan is manual rubric-based scoring (clarity, persuasiveness, format-fit) on a held-out set, acknowledging this is a softer evaluation than earlier models in the build order.
