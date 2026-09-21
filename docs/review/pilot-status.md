# Public-source seed pilot — draft 2, review pending

Version `0.2.0-draft2`, prepared 21 September 2026. This is a local review package,
not an admitted dataset or completed Phase 2 release. Draft 1 remains preserved.

The active corpus has **10 documents and 14 AI-drafted queries across all eight
domains**, with 10 source families. There are 8 English and 2 Shona documents;
queries comprise 10 English, 2 Shona and 2 synthetic English–Shona examples.
Northern Ndebele has no active examples after excluding the language-description
passage and its 3 queries for weak education-domain suitability. Those 4 records
remain separately attributed in `excluded-records.json`; they are not evaluated.

## Corrections from the AI review

- Rephrased the mixed Shona questions as single definition requests. The native
  agriculture question now requests a definition rather than a broad activity list.
- Replaced undocumented switch estimates with explicit language spans and token
  counts. Both remaining examples have one English-to-Shona transition and 2/5
  secondary-language whitespace tokens. These are AI annotations, pending speakers.
- Added editorial ellipses to the two truncated English passages and recorded the
  modifications. Source text and displayed excerpt hashes are distinguished.
- Removed the weak Ndebele domain example from active coverage rather than counting
  language-description prose as established education-service coverage.
- Re-fetched all 11 original pinned pages successfully. Each source excerpt matched
  page text after whitespace normalization; each page's revision ID matched; each
  displayed a CC BY-SA 4.0 link. [Machine evidence](source-verification-draft2.json)
  records the URLs and response hashes. This verifies source binding, not factual
  accuracy, full licensing clearance, or human admission approval.
- Specified an answer-bearing relevance rule and inspected the active passages for
  proposed positives. Partial topical overlap alone is not a positive. Human
  adjudication and exhaustive relevance confirmation remain pending.

## Handoff and checks

Use `review-packages/public-pilot-v0.2.0-draft2.zip`. It includes a reading copy,
response template, reviewer guide, attribution, source evidence, coverage, manifest,
structured review packet and explicit excluded records. The directory and ZIP are
ignored by Git; no unreviewed dataset was released or added to the registry.

Dataset validation and exact review-packet binding pass. All **24** active review
items have blank decisions and the source approval catalog is empty. Admission
correctly fails. Draft 1 approvals or results must not be applied to draft 2.

The [volunteer recruitment issue](https://github.com/tdrzzie/zimmteb/issues/1) is
published. No reviewer participation or endorsement has been confirmed.

## Remaining work requiring new evidence

Recruit qualified speakers, verify naturalness and factual claims, adjudicate all
relevance labels, obtain source-admission decisions, and expand representative
Zimbabwean coverage. Generic definitions are labelled as such in metadata. There
are only 10 source families against the planned 16-family pilot target, no natural
code-switch data, no active Ndebele coverage and many missing language/domain cells.
All records are test-only. No benchmark-readiness or linguistic-quality approval
is implied by the fixes or machine checks.

The [draft 1 AI review](ai-review-draft1.md) remains an unchanged historical record;
this document records its subsequent corrections and remaining limitations.
