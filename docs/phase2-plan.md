# Phase 2: language tracks and directional retrieval

Status: **in progress**, started 21 September 2026. The user selected all eight
domains and public sources; no licensed collection or speaker reviewers were supplied.
This is not a v0.2 dataset release or a claim of completed linguistic review.

## First implementation milestone

- `benchmark run --document-language CODE` evaluates against every document in that
  target language, retaining distractors across domains. `--language` selects query
  language. Only queries with target-language positives are eligible; other queries
  are listed in `queries_without_target_positives`. Positive judgments are restricted
  to the target corpus. An empty direction fails before loading a model.
- Native MTEB task names distinguish target corpora. Run configs, identities and
  reports record the target language. Comparisons across different target corpora
  are rejected even when query IDs match. Query-only filters still retain all documents.
- Optional provenance fields `source_id`, `source_document_id` and
  `translation_family_id` enable source-family leakage checks across train/dev/test.
  Positive, ordinary negative and hard-negative references all count. Source document
  IDs are scoped by source; translation-family IDs must be globally unique.
- `datasets review-export` writes an unapproved packet of documents and queries.
  `datasets review-check` checks recorded source permissions, review coverage, privacy
  attestations and relevance review. Dataset and record hashes reject stale approvals.
  The checker does not authenticate reviewers, apply corrections, publish data or
  promote the canonical review status automatically.

Existing Phase 1 JSONL, manifests and measured results are unchanged. New provenance
fields are optional for old data but required by the review checker. No synthetic
record becomes human-authored merely because it later receives a review.

## Domain and source work

The [public-source inventory](research/phase2-public-sources.md) records inspected
candidate pages and revision IDs for all eight domains. These are discovery leads,
not approved benchmark documents. Encyclopedia prose provides a starting point;
it is not a substitute for representative Zimbabwean questions or service documents.

| Domain | English candidate | Shona candidate | Northern Ndebele | Code switching |
|---|---|---|---|---|
| Financial services | Identified | Needed | Needed | Needed |
| Mobile payments | Identified | Needed | Needed | Needed |
| Telecommunications | Identified | Needed | Needed | Needed |
| Agriculture | Identified | Identified | Needed | Needed |
| Education | Identified | Identified | Needed | Needed |
| Public information | Identified | Needed | Needed | Needed |
| Customer support | Identified | Needed | Needed | Needed |
| Technology support | Identified | Needed | Needed | Needed |

The Northern Ndebele Incubator is a verified discovery location, not evidence of
domain coverage. Natural code switching has no approved source yet. Do not replace
missing cells with generated translations while presenting them as natural text.

For the first review pilot, target two independent source families per domain
(16 total), then expand according to coverage and reviewer capacity. This is an
operational target, not a statistically sufficient benchmark size. Track each of
the five language tracks independently, including missing cells. Start with
English↔Shona and English↔Northern Ndebele judgments as sources become available;
add other directions only when there is actual relevance evidence.

## Intake and review procedure

1. Inspect a specific source revision. Record its URL/history, license evidence,
   redistribution scope and any imported-text attribution obligations. Exclude
   private records, personal conversations and material with unresolved rights.
2. Record actual source approval in a private working copy of
   `configs/curation/sources.yaml`. Each entry needs `source_id`, `source`, `license`,
   `license_evidence`, `permission_scope`, `approved_by`, `approval_date` and
   `redistribution_allowed: true`. Use reviewer pseudonyms, not contact details.
   The supplied catalog is intentionally empty; no approvals have been invented.
3. Curate documents and queries in a new, versioned dataset. Preserve article
   attribution and modification history. Assign common family IDs to translations,
   paraphrases and derived queries. Unknown equivalence requires human review;
   different IDs alone do not prove independence.
4. Export a packet. Reviewers inspect the included documents and all judgments.
   Query reviewers should mark every relevant document, resolve ambiguous requests,
   and check negatives. Code-switch reviewers cover both constituent languages;
   translations require source and target language coverage.
5. Fill each item's `decision` with `reviewer_id`, ISO `review_date`, `status`
   (`approved`, `needs-revision`, `rejected`), `languages_reviewed`, substantive
   `comments`, `privacy_checked` and, for queries, `judgments_checked`.
   Keep the `record` payload unchanged. Corrections go into the source dataset,
   create a new version/checksum and require a fresh review packet.
6. Run structural and review checks. Resolve rejected/pending records and verify
   actual reviewer competence separately. Archive original packets and decisions.
   Integrate canonical review history in a separately reviewed version before release.
7. Assign whole connected source/translation families to splits before adding
   training data. Manually audit semantic leakage and keep training corpora separate
   from held-out documents. The validator catches declared family overlap; it cannot
   infer every relationship or certify privacy or linguistic accuracy.

```sh
uv run zimmteb datasets review-export --dataset tiny-synthetic --output .cache/curation/review.json
uv run zimmteb datasets review-check --dataset tiny-synthetic --packet .cache/curation/review.json --sources configs/curation/sources.yaml --output .cache/curation/check.json
```

The second command deliberately exits 1 on the unreviewed fixture. This demonstrates
pending work, not a broken pipeline. Export refuses to overwrite an existing packet.
Keep drafts in `.cache/curation`; publish only sanitized, approved artifacts.

The shipped fixture has no cross-language positive judgments. A working same-language
target-corpus smoke command is:

```sh
uv run zimmteb benchmark run --model test-hash --language sna --document-language sna --output runs/phase2-target-smoke
```

For a future admitted dataset, replace the dataset/config with its new manifest and
version, choose a real model, and select different query and document languages.
The integration tests use explicitly artificial cross-language judgments to exercise
this path; they are not linguistic evidence and are not added to the shipped data.

## Remaining milestone gates

- Pin, extract and review public-source passages across the eight domains, preserving
  licenses separately from the existing CC0 synthetic fixture.
- Recruit Shona and Northern Ndebele speakers and agree on review scope, consent,
  compensation and disagreement adjudication. No reviewer outreach has been sent.
- Produce a versioned, reviewed pilot with multi-positive and directional judgments,
  coverage accounting, source-family splits and an updated dataset card.
- Run and report real-model directional evaluation on that pilot. No Phase 2 model
  scores are claimed yet. Broader baseline comparisons remain the subsequent milestone.
- Resolve the GitHub account billing restriction and run the full hosted CI matrix.
  This remains an external Phase 1 verification gap, not a passing CI claim.

Local verification for the initial implementation: 61 offline tests passed with
90% statement coverage; lint, type checks and package build passed. Real-model Phase 1 CPU evidence
remains available. GPU and hosted CI were not executed for this milestone.
