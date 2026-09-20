# AbdiWrite

## Domain
Bilingual (Urdu / English / Roman-Urdu) grammar and style correction, light rewriting.

## Status
Planned — second in build order.

## Scope (v1)
- Input: raw text (Urdu, English, or Roman-Urdu) with grammar/style issues.
- Output: corrected version + brief explanation of the fix.
- **Out of scope for v1:** long-form generation, translation (see AbdiTranslate), creative writing.

## Base model
Candidates: Qwen2.5-1.5B/3B-Instruct or Gemma-2-2B-it. Selection depends on which handles Urdu script tokenization better — to be tested with zero-shot prompts before committing.

## Dataset
- English portion: public grammar-correction datasets (e.g. JFLEG, Lang-8-derived sets), reformatted to instruction pairs.
- Urdu portion: scarce in public data — plan is semi-synthetic generation (inject common Urdu error types into clean sentences) plus LLM-assisted generation of error/correction pairs, manually reviewed for quality.
- Target size for v1: 500–1000 manually-reviewed pairs, not tens of thousands — quality over volume given manual review cost.

## Fine-tuning method
QLoRA on Colab T4, same pipeline as AbdiSQL.

## Evaluation
Held-out set of 100 sentences, manually scored (no automatic metric exists for "is this correction actually better and meaning-preserving" at the quality bar needed here). Compared against zero-shot base model performance on the same set.

## Notes
Bilingual/Urdu focus is the actual differentiator for this model — general grammar correction alone isn't novel, low-resource Urdu handling is.
