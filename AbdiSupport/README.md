# AbdiSupport

**"Abdi baat karta hai"** — Abdi talks.

## Domain
Customer support conversation — **for third-party products/businesses**, not for the ABDI platform itself.

## Status
Planned — twelfth in build order.

## Scope resolved — distinction from AbdiChat
This model was originally ambiguous against AbdiChat (both looked like "general conversation" models). Resolved as follows, not left as a soft "reconsider if they converge" note:

- **AbdiSupport** is a template/base model meant to be fine-tuned or configured *per external product* — e.g. a business wants a support bot for their own FAQ/product knowledge base. Its output is business-specific, grounded in a provided knowledge base, and follows support-conversation conventions (ticket-style resolution, escalation phrasing, tone).
- **AbdiChat** is ABDI's *own internal* fallback model inside the platform's dispatcher — it has no external knowledge base, no business-specific grounding, and exists purely to catch queries none of the 14 domain experts confidently own.

Different consumer (external business vs. ABDI's own dispatcher), different grounding (a provided knowledge base vs. none), different deployment context (fine-tuned per customer vs. a single shared fallback). If future testing shows their outputs still converge despite this, the fix is to make AbdiSupport's knowledge-base grounding a hard requirement at inference time (it must refuse to answer without a provided KB), not to merge the two models.

## Scope (v1)
- Input: a user support query + a provided knowledge base/FAQ context (required — see above).
- Output: a resolution response in appropriate support tone/format, grounded in the provided context.
- **Out of scope for v1:** open-ended general conversation without a knowledge base (refuse rather than improvise), ticket-system integration.

## Base model
TBD.

## Dataset
Public customer-support dialogue datasets, reformatted to require KB-grounded answers (input includes both the query and a context passage, not just the query alone).

## Fine-tuning method
QLoRA on Colab T4.

## Evaluation
Two-part: (1) resolution correctness/tone against a manual rubric, (2) grounding reliability — a held-out set of queries with no matching KB content, checking the model declines rather than fabricating an answer.
