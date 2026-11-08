# RPOS to CyberAlchemy v2 Define semantic-improvement handoff

Status: candidate-unadmitted. Authority effect: none.

This handoff asks the Define owner to evaluate reusable product improvements
discovered while refining the RPOS semantic kernel. It is not a construction
handoff and does not create a `ConstructionBinding`.

## Result from the consumer

RPOS now has 58 bounded concepts: the original 24 kernel concepts, 20 semantic
dependency concepts, and 14 relation meanings. Every concept is materialized as
a candidate Definition/v1 record with subject, goal, operational interpretation,
use cases, boundary, formalization posture, and semantic tests. Claim is closed
at candidate level through explicit Claim Class and Evidence Standard semantics.
Authority-bearing concepts now require an identified Project context; Claim and
Inference bind exact Review references; Knowledge Records use the bounded states
candidate, durable, superseded, and withdrawn; and the stable Steward definition
ID presents the human-facing term Accountable Coordinator. The explanatory
`RPOS-DEFINITION-MODEL-GUIDE.md` shows how all definitions compose through the
first workflow without becoming a second semantic authority.

RPOS also exposed a portability and formalization problem. Its first adapter
loaded Definition/v1 contracts directly from a neighboring Lab checkout, and
all materialized definitions used a null formal expression. RPOS now carries a
frozen 14-definition Lab foundation snapshot, 51 formal expressions, and seven
structured-invariant postures. RPOS also implements 88 checked dependency edges
as a consumer-side reference implementation. Define should
preserve and validate those distinctions without acquiring their meaning.

## Requested Define improvements

1. Add a concept-reasoning surface: subject, goal, operational use, use cases,
   boundary, owner route, sources, and open questions.
2. Preserve structured open-question text and owner routes across adapters,
   rather than reducing them to concept IDs.
3. Validate the internal material bindings of a current validation receipt,
   not only the receipt file's outer digest.
4. Add distinction fixtures for concepts with different subjects but similar
   names, such as Project State, Portfolio State, and RPOS System State.
5. Retain consumer semantic ownership. RPOS is a fixture and evidence source,
   not vocabulary that Define may absorb.
6. Add exact semantic dependency bindings for internal and external definitions,
   including relation, version, digest, and required lifecycle posture.
7. Preserve whether a concept requires a formal expression, intentionally uses
   structured invariants, or remains formally open.
8. Support portable, digest-bound external foundation snapshots so validation
   does not require the donor repository to remain installed.

## Acceptance boundary

A successor passes only if legacy packs have an explicit compatibility story,
open questions retain their actionable content, stale inner receipts fail, and
negative fixtures reject subject-scope, dependency, and formalization-posture
collapse. No result may promote an
external definition or authorize planning, construction, publication, release,
deployment, or external action.

## Open questions

- Should the reasoning surface be required by the next pack version or added as
  an optional compatible profile first?
- Are distinction checks core behavior or consumer-profile behavior?
- Which receipt contracts should be eligible for transitive verification?
- Should portable foundation snapshots be a Define artifact or a separately
  governed semantic-foundation export contract?
- Which concept classes require formal expressions, and which may explicitly
  use structured invariants?

The machine-readable handoff is
`SEMANTIC-IMPROVEMENT-HANDOFF.json`.
