# Data governance

ZimMTEB scores do not establish that a model is safe or appropriate for high-stakes deployment.

## Admission and provenance

Every dataset needs an ID, version, exact content checksum, source, license,
creation method, review status, language/domain coverage, split counts and citation.
Every query and document carries provenance. Record license evidence before admission;
an upstream package's license does not license its weights or source documents.
Allowed sources are original data, public-domain material, explicitly licensed open
data and properly licensed translations. Public availability alone is insufficient.

Never ingest confidential employer information, bank customer records, telecom or
government private records, personal conversations, leaked data or unreviewed scraping.
Do not put personal data in examples, annotations, logs or model artifacts.

## Synthetic and translated material

The shipped fixture is AI-drafted, synthetic and unreviewed. Its Shona, Northern
Ndebele and code-switched text may contain errors. It is not native-speaker data,
authenticated translation, natural conversation or evidence of representativeness.
Switch ratios are rough author estimates, not validated token annotations.
Distinguish synthetic generation, machine translation, human translation,
human authorship and human review; review does not change authorship.
Keep generator/version/parameters, source language and translation method.

## Human review

Before linguistic claims or a representative release, recruit qualified speakers,
agree on consent and compensation, and record reviewer pseudonyms, dates, revisions,
comments, corrected text and prior versions. Review accuracy, dialect, spelling,
natural switching, domain relevance, ambiguous queries and missing positive judgments.
Use the schema's unreviewed, machine-checked, human-reviewed, approved, rejected and
needs-revision states. No reviewer identities or approvals may be invented.

## Leakage and revisions

Keep training, development and evaluation partitions independent at source-document,
semantic and translation-family levels. Exact and heuristic near-duplicate checks
are guards, not proof of no contamination. Phase 1 is test-only. Translation clusters
and human semantic leakage review are required before training datasets are added.
Never mine negatives from held-out evaluation data for training.

Meaningful content changes create a new dataset version, checksum and compatible
benchmark version. Keep a changelog. Freeze released manifests; do not regenerate
the fixture under the same released version. A correction that changes judgments
invalidates direct score comparisons with the earlier test set.

## Removal and privacy

Until a public repository/contact is configured, report concerns privately to the
repository owner. Once hosted, enable private security reporting. Give a dataset
ID/version and record IDs without redistributing sensitive text. Quarantine affected
versions, investigate license/consent, remove downstream caches and artifacts where
possible, publish a sanitized tombstone/change record and issue a corrected version.

## Bias and misuse

Coverage is narrow and synthetic. Zimbabwean dialects, orthography, rural/urban
registers, English influence and spontaneous switching are not represented reliably.
The presence of a language tag does not prove model language competence. Publish
language, domain and code-switch slices alongside aggregate scores. Do not treat
an embedding score as a language fluency test, demographic assessment or deployment
approval. Document selection bias and incomplete relevance judgments in each release.
