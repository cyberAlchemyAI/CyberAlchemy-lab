Next: authentic byte/capture realization before source closure

The record-to-entry and retained-catalog staging bridges now exist. The original
supported source/profile, authentication and integration targets remain required.

1. Formalize the independent complete JSON document/byte meaning first. Resolve
   UTF-8, escapes, Unicode including surrogate behavior, duplicate decoded keys,
   complete consumption, whitespace and retained numeric lexemes explicitly. Reuse
   the complete exact JSON-number parser; do not normalize through floating point
   or silently narrow accepted decimal/exponent spellings. Distinguish unsupported
   profile data from malformed syntax and bounded resource refusal.
2. Implement the parser against that meaning and prove soundness/completeness and
   exact capture correspondence. Bind generated ASTs to the original byte sequence
   and exact length. Replace synthetic AST/byte pairs by captured actual records.
3. Implement the pinned digest-profile evaluator and prove the byte/digest bridge.
   Select the expected profile from authentic snapshot evidence; the current
   uniform-profile guard compares supplied values but does not own that selection.
4. Realize exact Schema/profile and authentic issuer/review evidence. Check all
   staged records and roots before using CatalogStage.catalog. Preserve full
   envelopes and versions in the evidence/certificate bundle. Do not replace these
   requirements with synthetic root membership or permissive provider predicates.
5. Feed the authenticated projections into the existing owned qualifier/payload/
   metadata/Selection pipeline. Realize all nineteen full K02 source-policy
   predicates and prove complete raw-source refinement under the supported profile.
6. Complete K02's two qualifier, record-effect and four whole-theory non-entailment
   obligations; obtain mandatory independent checking for selected closure proofs.
   Continue all remaining relation definitions, seven extension integrations,
   diagnostics/resources, exact 263-plus-90 audit and actual new use assessment.

K04 remains the pending one-by-one meaning review. Its absence does not prevent
reversible preparation of accepted K02's source bridge; it does prevent inferring
K04 or full N01 acceptance. N02 obligations and N03 admitted schemas/APIs remain
separate tasks with their original completion criteria.
