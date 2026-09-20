# Dataset design

`datasets/manifests/tiny-synthetic.yaml` points to normalized document and query JSONL.
The manifest checksum hashes both raw byte streams with an eight-byte length prefix
per stream. JSONL is marked `-text` in `.gitattributes` to prevent checkout newline
conversion from changing checksums. Reproduce unreleased fixture bytes with
`python scripts/generate_fixture.py`; version before changing a released fixture.

Documents carry text/title, language, domain, ID and provenance. Queries reference
positive/negative document IDs and include split, difficulty and optional switching
metadata. Pydantic validates record shapes, required fields and provenance evidence.
Review records preserve reviewer pseudonym, status, revision/date, comments,
corrections and previous version. Manifest admission requires license and source.

`zimmteb datasets validate` checks counts, checksums, references, registries, duplicate
IDs/text, Unicode, short/long text, positive/negative conflicts, code-switch partners,
cross-split near-duplicate queries and overlapping/near-duplicate positive documents.
It exports both JSON and Markdown and returns nonzero for errors. Length warnings
and translation-review warnings are heuristics. It cannot certify translation accuracy,
natural switching, PII absence or semantic separation across languages.

The current O(n²) leakage audit is intentionally small-data tooling. Future source
and translation-family IDs, candidate indexing, bilingual review and adjudicated
multi-positive judgments are prerequisites for larger benchmark releases.
