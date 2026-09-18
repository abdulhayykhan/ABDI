# AbdiTeach

**"Abdi parhata hai"** — Abdi teaches.

## Domain
School/intermediate-level science concept explanation (Physics, Chemistry, Biology).

## Status
Planned — tenth in build order. Scope resolved below.

## Scope (v1)
- **Subjects: Physics, Chemistry, Biology at school/intermediate level.** Math is deliberately excluded — AbdiMath already owns problem-solving, and including it here would recreate the same overlap problem that AbdiSupport/AbdiChat had to be resolved for.
- **Level: school/intermediate (matric/intermediate-equivalent curriculum)**, not university-level — content and required pedagogy differ enough that mixing levels would blur the model's scope the same way "any language" blurred AbdiCode's.
- **Style: explanation-on-demand.** The model explains a concept clearly when asked; it does not do Socratic back-and-forth tutoring (a harder interactive-dialogue problem, out of scope for v1) and it does not solve homework problems (that overlaps with AbdiMath/AbdiData depending on subject).
- **Out of scope for v1:** math problem-solving, university-level content, multi-turn Socratic tutoring, homework-answer generation.

## Base model
TBD — candidate: a small instruction-tuned model already reasonably strong at science explanation (to be tested zero-shot before committing, same process used for AbdiWrite/AbdiSQL).

## Dataset
Curated science concept-explanation content (textbook-adjacent Q&A, not problem sets) for the three subjects at the target level. Likely needs synthetic generation (concept → plain-language explanation pairs) plus manual review, similar approach to AbdiWrite's Urdu data construction.

## Fine-tuning method
QLoRA on Colab T4.

## Evaluation
Manual review against a rubric (factual correctness, clarity, appropriate level) on a held-out set of concept-explanation prompts across the three subjects. Compared against zero-shot base model performance.
