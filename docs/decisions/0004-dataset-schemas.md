# 0004 — Typed records and normalized document storage

Status: accepted.

Pydantic v2 schemas reject unknown fields, empty required values and contradictory
judgments. Separate JSONL documents from query records; query positives and negatives
refer to document IDs. YAML manifests identify exact raw bytes using length-framed
SHA-256. JSON-shaped YAML is intentional and portable.

Semantic validation supplements record validation: registries, references, duplicate
text/IDs, cross-split overlap and near duplicates. Large-data indexing and bilingual
semantic review are deferred; the quadratic audit is appropriate only for small data.
