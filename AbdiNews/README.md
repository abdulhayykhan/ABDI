# AbdiNews

## Domain
News summarization.

## Status
Planned — ninth in build order.

## Scope (v1)
- Input: a news article.
- Output: a concise, accurate summary.
- **Out of scope for v1:** real-time news aggregation, multi-article synthesis, opinion/bias analysis.

## Known infrastructure difference from other models
Unlike most other ABDI models, this domain implicitly assumes access to *current* news content, which is a live-data-pipeline problem, not just a training problem — the model itself doesn't need updating often, but the input pipeline (fetching current articles) is a separate piece of infrastructure not required by e.g. AbdiSQL or AbdiCV. This needs to be scoped explicitly: is AbdiNews summarizing arbitrary user-provided articles (no live pipeline needed), or actively surfacing current news (live pipeline required)? Defaulting to the former for v1 to avoid taking on unrelated infrastructure work.

## Base model
TBD.

## Dataset
Public summarization datasets (e.g. CNN/DailyMail, XSum) as a starting point.

## Fine-tuning method
QLoRA on Colab T4.

## Evaluation
ROUGE score against reference summaries (automatic), plus manual spot-check for factual accuracy — ROUGE alone doesn't catch hallucinated facts, which matters more in a "news" context than most other domains.
