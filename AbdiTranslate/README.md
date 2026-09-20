# AbdiTranslate

## Domain
Urdu ⇄ English translation.

## Status
Planned — third in build order.

## Scope (v1)
- Sentence/paragraph-level translation, Urdu ↔ English.
- **Out of scope for v1:** document-level translation, other language pairs, real-time/streaming translation.

## Base model
TBD — will reuse learnings from AbdiWrite's base-model tokenization testing on Urdu script.

## Dataset
Public parallel corpora — primarily [OPUS](https://opus.nlpl.eu/). Existing large-scale resource, unlike AbdiWrite's Urdu data, which had to be semi-synthetically built.

## Fine-tuning method
QLoRA on Colab T4.

## Evaluation
BLEU / chrF — established automatic translation metrics, reducing reliance on manual grading (advantage over AbdiWrite's eval, which needed manual review).

## Notes
Natural follow-on from AbdiWrite given the shared bilingual focus and reusable tokenizer/base-model findings.
