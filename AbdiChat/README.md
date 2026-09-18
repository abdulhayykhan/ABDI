# AbdiChat

**General-purpose fallback model — not one of the 14 domain experts.**

## Role — read this before assuming AbdiChat is "just another domain"
AbdiChat is architecturally different from every other folder in this repo. It is not a domain expert and was never meant to be — general conversation isn't a narrow, evaluable specialty the way SQL generation or translation is. Its only job is to **handle queries that the dispatcher can't confidently route to a domain expert.**

It exists to solve a specific gap: without a fallback, a dispatcher-based system has no answer for out-of-domain queries, which would otherwise mean either (a) silently misrouting a query to the wrong specialist (e.g. a medical question landing on AbdiWrite), or (b) refusing to answer anything outside the 14 domains, which defeats the point of a general platform.

## Status
Planned — build order position (#15) is intentionally late but **not "whenever, at the end."** This was previously proposed as "build a general LLM at the end after all experts are done," which was rejected as too vague to be a real milestone. AbdiChat should be scoped and built once the dispatcher's routing logic is being built, since the two are designed together — not deferred indefinitely.

## Scope (v1)
- General conversational ability, sufficient to handle any query the dispatcher doesn't confidently route elsewhere.
- Kept as a **small** model (SLM, not a large general LLM) — consistent with the rest of the platform's hardware constraints and design philosophy. A full-size general LLM is explicitly not part of this plan; that was considered and set aside in favor of this fallback-SLM approach.

## Relationship to the dispatcher
AbdiChat and the dispatcher (intent classifier + router) are two parts of the same system and should be designed together:
- Dispatcher: routes confidently-classified queries to the matching domain expert.
- AbdiChat: catches everything else.
A weak dispatcher makes AbdiChat's role larger than intended (too much traffic falling through to it); a weak AbdiChat makes the fallback path itself unreliable. Both need to be evaluated together, not just independently.

## Base model
TBD.

## Dataset
General-purpose instruction-tuning data (existing public instruction datasets) — this is the one model on the platform that doesn't need a narrow, curated domain dataset, by design.

## Fine-tuning method
QLoRA on Colab T4, consistent with the rest of the platform.

## Evaluation
- General conversational quality (manual review, broad rubric).
- **Also requires dispatcher-integration testing**, not just standalone eval — specifically, testing that AbdiChat's presence doesn't cause the dispatcher to under-route to domain experts out of "just send it to AbdiChat, it's easier" laziness in the routing logic.
