# 0010 — Freeze data and include full identities in caches

Status: accepted.

Version package, result schema, dataset and benchmark separately. Content changes
require a new dataset version and benchmark compatibility decision. Preserve old
manifests; do not reuse version labels. Byte hashes catch unintentional edits.

Cache identity includes exact data/text, model revision and local content hash,
prompts, normalization, precision, split, configuration, package versions and source
checksum. This is deliberately conservative: some harmless changes cause a miss.
Resume reuses only a complete result with identical identity. Interrupted runs can
reuse completed embedding cache entries in a fresh output directory.
