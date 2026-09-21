# Volunteer review guide

## Purpose and current status

Review linguistic quality and proposed relevance judgments, not model scores.
The seed pilot has 11 short public-source excerpts and 17 AI-drafted queries.
All decisions are pending. It has no training split or approved benchmark release.
The passages are intentionally brief; reviewers may recommend replacing them with
longer, independently sourced and appropriately licensed material.

## Before starting

Agree with the maintainer on language variety, batch size, public attribution
(including a pseudonym if preferred), and contribution licensing. The excerpts are
CC BY-SA 4.0; modifications need compatible licensing. Participation is unpaid and
optional. Do not claim expertise outside your languages or include personal data.
The maintainer should explain public release and withdrawal limits before work begins.

The local packet has `READING-COPY.md`, `review.json`, `review.schema.json`,
`documents.jsonl`, `queries.jsonl`, source links, attribution, and coverage counts.
Use the reading copy first. The maintainer can transfer plain-language decisions
to JSON; volunteers do not need to edit code or structured files.

## Review each passage

1. Follow its pinned article link and confirm the excerpt, language and attribution.
   Check facts against suitable primary sources where necessary. Do not infer that
   encyclopedia content is automatically reliable or natural in local usage.
2. Check spelling, grammar, meaning, dialect and register. Preserve legitimate
   variation; record the variety rather than silently standardizing it away.
3. Decide whether its domain label is useful. The Northern Ndebele excerpt concerns
   language itself; its education label is broad and needs explicit confirmation.
4. Flag sensitive information, questionable licensing, inadequate context, stale
   statements or misleading truncation. The mobile-payment and telecommunications
   excerpts stop before the end of the original sentence.

## Review each question and judgment

1. Is the question understandable and answerable from the proposed passage?
2. Is it natural for its intended users? AI-drafted code switching is not evidence
   of naturally occurring language use. Correct or reject it as appropriate.
3. Inspect other passages, not just the proposed positive. Add all relevant IDs;
   flag ambiguous or incomplete judgments. Do not assume unjudged documents are
   truly irrelevant, particularly across languages.
4. Cross-language judgments need coverage of both query and document languages.
   Declare limitations. A language tag alone does not establish reviewer competence.
5. Record `approved`, `needs-revision`, or `rejected` with a short explanation. Use
   `needs-revision` for uncertainty; the system does not require you to approve an item.

## Recording and adjudication

The maintainer fills each packet item's `decision` using an actual reviewer
pseudonym, review date, status, `languages_reviewed`, comments, `privacy_checked`
and, for queries, `judgments_checked`. These attestations describe work actually
performed. Automated tools cannot provide human approvals.

Keep the original packet and decisions. Correct source records in a **new dataset
version**, export a new packet and review the changed content again. Editing the
packet's source text invalidates its content binding. Review software does not
automatically promote the underlying dataset to human-reviewed status.

For disagreements, retain both independent reviews in separate files and ask a
qualified second reviewer to adjudicate. The current checker accepts one final
decision per item; it does not merge multiple reviewers or resolve conflicts.
Document adjudication before producing a canonical reviewed release.

## Completion criteria

Speaker competence and consent are established; passages and questions are checked;
multi-positive judgments and source-family links are resolved; permissions and
attribution are recorded; structural and review checks pass; a maintainer inspects
the final version. Missing language/domain cells remain marked as missing.
