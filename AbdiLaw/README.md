# AbdiLaw

## Domain
Legal document explanation — **rescoped from the original "legal drafting, contracts, agreements" framing.**

## Status
Planned — thirteenth in build order (deliberately last among the standard experts, before AbdiMed).

## ⚠️ Scope (v1) — rescoped for liability reasons
- **Original framing (legal *drafting*) was rejected.** A small fine-tuned model producing subtly wrong binding legal text is a worse outcome than producing nothing — errors in generated legal drafts have real consequences a hobby/student project should not be generating.
- **Rescoped to: explaining what a contract clause means, and flagging commonly risky/unusual terms in a document the user provides.**
- **Explicitly out of scope, permanently, not just for v1: drafting or finalizing binding legal agreements.**

## Mandatory requirement before this model ships
The model must reliably **refuse drafting requests** and redirect to "explain, don't draft" behavior. This refusal behavior must be built into the fine-tuning dataset itself (explicit refusal examples included in training data), not bolted on as a UI-level disclaimer after the fact. **This is a separate evaluation category from the domain's normal correctness eval** — the model does not ship until refusal behavior is verified to work reliably in testing, independent of how good its explanations are.

## Base model
TBD.

## Dataset
TBD — needs careful curation given the stakes; likely a mix of public legal-explainer content plus a deliberately constructed refusal-example set (see above).

## Fine-tuning method
QLoRA on Colab T4.

## Evaluation
Two separate evaluations, both required to pass:
1. Explanation correctness/clarity — manual review against a legal-accuracy rubric.
2. Refusal reliability — a dedicated held-out set of drafting-style requests, checking the model consistently declines and redirects rather than attempting to draft.
