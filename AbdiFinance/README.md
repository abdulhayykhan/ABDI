# AbdiFinance

## Domain
Finance / accounting / invoicing — **deliberately narrowed from the original broader "finance, accounting, invoicing" framing.**

## Status
Planned — eleventh in build order.

## Scope (v1)
- **Rescoped to: explaining invoice terms and basic accounting/finance concepts.**
- **Explicitly out of scope: preparing taxes, giving investment advice, or producing binding financial documents/filings.** Real-money correctness stakes make this domain risky in the same category (though less severe) as AbdiLaw/AbdiMed — narrow scope now rather than discover the liability problem after building something broader.

## Base model
TBD.

## Dataset
TBD — likely a mix of public finance-explainer content and synthetic Q&A generation, similar approach to AbdiCV.

## Fine-tuning method
QLoRA on Colab T4.

## Evaluation
Manual review against a factual-accuracy rubric — finance terminology explanations need correctness verification, not just fluency.
