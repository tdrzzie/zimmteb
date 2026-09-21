# AI review of public pilot draft 1

Reviewed 21 September 2026 by OpenAI Codex (AI, not a human speaker reviewer).
Scope: the 11 documents, 17 questions, proposed positive judgments, provenance
records and review packet in local version `0.2.0-draft1`.

**Decision: suitable for volunteer review; needs revision before benchmark admission.**
This is a technical/editorial assessment, not speaker approval or source permission
approval. No human decision or approved-source entry was filled in.

## Verified

- Dataset structure validates, and the exported review packet matches the dataset
  checksum and every record. All 28 human decisions remain blank.
- The admission check correctly fails without speaker and source approvals.
- All eight domains are represented, with 8 English, 2 Shona and 1 Northern Ndebele
  documents. The 11 source families remain below the planned 16-family pilot.
- Each of the eight English-to-English questions is answerable from its proposed
  excerpt. This assesses passage support, not the independent truth of each claim.
- The packet discloses AI-drafted questions, synthetic code switching, unreviewed
  status, source links and excerpt modifications. No obvious personal records or
  private contact information appear in the passages or questions.

## Findings requiring resolution

1. **Code-switch metadata needs revision.** `q-cs-sna-agriculture` contains English,
   then “kurima”, then English, then Shona. Its stored single switch and `eng->sna`
   direction do not describe those apparent three transitions under span-based
   counting. A speaker should resolve borrowing versus switching and document the
   counting convention. All three switch ratios are 0.4 without a documented
   token-count method; treat these as unverified estimates, not measured labels.
2. **Domain suitability needs review.** `d-nde-education` describes a language's
   speakers and relationship to another language. Its broad education label does
   not establish useful education-service coverage. Replace it or justify the label.
   Several English definitions likewise offer little Zimbabwe-specific context.
3. **Question scope and relevance need adjudication.** The synthetic Shona
   agriculture question asks broadly about farming activities; the English crop
   excerpt may be partially relevant as well. The mixed Shona education question
   asks both for a definition and how knowledge is acquired, while the excerpt
   offers only a brief school-focused definition. These are candidates for revised
   wording or additional relevance labels, not confirmed missing positives.
4. **Source re-verification is incomplete.** Attempts during this review to open
   the pinned Kurima, Dzidzo and Northern Ndebele revisions failed in the browsing
   tool. That does not establish that the URLs are invalid. Their exact text and
   revision binding remain unconfirmed in this review. The other eight pinned
   revisions were not re-fetched in this pass. Existing attribution records alone
   are insufficient to assert a completed source-admission review.
5. **Human language review remains outstanding.** Naturalness, variety, factual
   reliability and exhaustive multilingual relevance cannot be certified by this
   AI review. Short excerpts and the two truncated English sentences also need
   contextual assessment before use in a released benchmark.

## Disposition

Continue volunteer recruitment and share the clearly marked draft for criticism.
Preserve draft 1 and its bound packet. Apply accepted corrections in a new version,
re-export its packet, and obtain actual reviewer decisions and source approvals
before admission. Do not treat this report as a completed review of Phase 2.
