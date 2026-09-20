---
language: [en, sn, nd]
license: cc0-1.0
task_categories: [text-retrieval]
pretty_name: ZimMTEB synthetic infrastructure fixture
---

# ZimMTEB dataset card — unpublished draft

## Summary and intended use

Original AI-drafted fixture for retrieval software testing, not a representative
Zimbabwean benchmark. Do not use scores to select high-stakes systems or claim fluency.

## Languages, tasks and domains

English, chiShona, Northern Ndebele, English–Shona and English–Ndebele artificial
switch tracks. Retrieval only. Manifest domains do not imply query coverage everywhere.

## Construction, provenance and license

Static generator in `scripts/generate_fixture.py`; per-record source, generator
version and parameters included. No private records or external source dataset.
CC0-1.0 for original fixture content; models and code have separate licenses.
Not native-speaker-authored, authenticated translation or natural conversation.

## Splits and schema

Version 0.1.0: test-only, 13 queries and 16 documents. Normalized documents with
ID-linked query judgments. No training/development split. Exact checksum in manifest.
Content changes require new versions. Record exact Hub revision when published.

## Human review, bias and limitations

All records unreviewed. Generated grammar, spelling and switching may be incorrect.
Dialect, region, register and domain coverage are narrow. Relevance is incomplete;
valid other-language answers may be unjudged. Speaker review and multi-positive
adjudication are prerequisites for scientific use. Human review must not be invented.

## Out-of-scope uses

Fluency claims, deployment approval, demographic inference, training on held-out
benchmark examples, or presenting synthetic scores as real-world retrieval quality.
ZimMTEB scores do not establish safety for high-stakes deployment.

## Citation and publication

Cite software version/commit and dataset version/checksum. No DOI exists. Before
upload, choose the owner/repository, replace draft status, verify rights/review
claims and explicitly approve publication. Do not upload automatically.
