# AbdiMed

**"Abdi samjhata hai"** — Abdi explains. *(Rescoped from the original "Abdi ilaj samjhata hai" / Abdi explains treatment.)*

## Domain
Medical/health information explanation — **rescoped from the original "medical/health info assistant" framing.**

## Status
Planned — last in build order, and the model most likely to be reconsidered entirely for a student portfolio project given its liability profile.

## ⚠️ Scope (v1) — rescoped for liability reasons
- **Original framing implied treatment guidance ("ilaj" = treatment). This was rejected.** A fine-tuned sub-3B model confidently producing wrong dosage/treatment/diagnosis information is a genuine safety risk, not just a quality problem — this is a different risk category from every other model on this platform.
- **Rescoped to: explaining medical terminology and lab report values in plain language.**
- **Explicitly out of scope, permanently: diagnosis, dosage guidance, treatment recommendations, or any advice intended to be acted on medically.**

## Mandatory requirement before this model ships
Same as AbdiLaw: reliable **refusal behavior** on diagnosis/treatment/dosage requests must be built into the training data itself, and verified as a separate, required evaluation pass before the model is considered shippable. A model that explains terminology well but fails to reliably refuse treatment questions does not ship.

## Open question
Whether this model belongs on the platform at all, or whether the liability profile is a poor fit even in its narrowed form for a student/portfolio/thesis project. To be revisited once AbdiLaw's refusal-behavior approach has been tested and proven (or not) — AbdiMed should not be attempted before AbdiLaw validates that this pattern actually works reliably at this model scale.

## Base model
TBD.

## Dataset
TBD — needs the same refusal-example construction approach as AbdiLaw, likely combined with public health-literacy/terminology explainer content.

## Fine-tuning method
QLoRA on Colab T4 (pending the open question above).

## Evaluation
Same two-part structure as AbdiLaw: correctness/clarity of explanations, plus a dedicated, required refusal-reliability evaluation on diagnosis/treatment-style requests.
