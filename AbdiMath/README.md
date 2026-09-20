# AbdiMath

## Domain
Math reasoning and tutoring.

## Status
Planned — seventh in build order.

## Scope (v1)
- Input: a math problem (arithmetic through basic algebra/word problems — scope to be tightened further once base model capability is tested).
- Output: step-by-step solution.
- **Out of scope for v1:** advanced/university-level math, proof-writing.

## Known risk
Small models (sub-3B) are structurally weak at multi-step reasoning. This model is expected to underperform relative to effort invested compared to earlier builds in the order — placed at #7 deliberately, after the pipeline is well-proven on easier domains, so a weak result here reads as "this domain is hard for small models" rather than "the pipeline is broken."

## Base model
TBD — likely needs to test multiple small models' baseline math performance before committing, since this varies more by model than by fine-tuning in this size range.

## Dataset
Public math-reasoning datasets (e.g. GSM8K for word problems) as a starting point.

## Fine-tuning method
QLoRA on Colab T4.

## Evaluation
Final-answer accuracy on held-out problems (objective) — but step-by-step reasoning quality also worth spot-checking manually, since a right answer with wrong reasoning is a worse outcome for a "tutoring" framing than for a pure answer-generator.
