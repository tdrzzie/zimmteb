# Public-source seed pilot — review pending

Draft version: `0.2.0-draft1`, prepared 21 September 2026. This is a local review
package, not an admitted dataset or a completed Phase 2 release.

The owner selected all eight domains, permitted public-source discovery, and chose
a volunteer invitation. The draft contains short manually selected Wikimedia text
excerpts with pinned source links, attribution, modification notes, excerpt hashes
and CC BY-SA 4.0 notices. Source HTML was not archived; reviewers should confirm
the excerpt against the pinned article revision. Questions and proposed positive
judgments are AI-drafted and unreviewed. No speaker approvals were fabricated.

| Coverage | Documents | Queries |
|---|---:|---:|
| English | 8 | 11 |
| Shona | 2 | 2 |
| Northern Ndebele | 1 | 1 |
| Synthetic English–Shona switching | 0 | 2 |
| Synthetic English–Ndebele switching | 0 | 1 |
| Total | 11 | 17 |

English queries include proposed cross-language retrieval into the Shona and
Northern Ndebele passages. No text is presented as parallel gold translation.
There are 11 source families, all in the test split; no training/dev partition or
statistical representativeness is claimed. This is below the planned 16-family pilot
target and should grow after reviewers assess the initial selection.

All eight domains have at least one document and query. Shona is limited to
agriculture and education; the Northern Ndebele passage concerns language and has
a broad education label requiring confirmation. Most non-English domain cells are
still missing. Excerpts are short and may be replaced with richer licensed passages.
Two English excerpts end before their original source sentences end.

## Local handoff

The packet is in `review-packages/public-pilot-v0.2.0-draft1/`, with a sibling ZIP.
Review packages are ignored by Git to keep pending judgments and future reviewer
details out of automatic pushes. Share a sanitized copy deliberately; review packets
are not installed as part of the Python package or included in the dataset registry.

The packet includes a reading copy, response template, editable review JSON and its
schema, source records, attribution, manifest, validation, coverage and instructions.
All 28 review decisions are blank. The source approval catalog is empty; machine
license inspection is not recorded as a human admission approval. Passing structural
validation does not mean the review/admission checker passes.

The [volunteer invitation](volunteer-invitation.md) was published with the owner's
approval as [GitHub issue #1](https://github.com/tdrzzie/zimmteb/issues/1).
[Recruitment routes](recruitment-routes.md) are leads, not participants.
Actual speaker review needs volunteers to opt in and return decisions. No contact
details, consent, affiliation, compensation promise or endorsement has been invented.

## Next review actions

1. Collect volunteer opt-ins through the published recruitment issue.
2. Agree on a small voluntary batch, language variety, contribution licensing and
   public attribution before accepting corrections.
3. Confirm source permissions and excerpts; review every proposed relevance label,
   including potential missing positives in other languages.
4. Adjudicate disagreements, version corrected data and re-export changed records.
5. Expand missing coverage, then admit a sanitized reviewed version with a dataset card.

No reviewed pilot can be claimed until that human work is completed.

The [AI review of draft 1](ai-review-draft1.md) finds it suitable for volunteer
review, with revisions required before benchmark admission. It records a
code-switch metadata issue and unresolved domain, relevance and source checks;
it supplies no human approvals.
