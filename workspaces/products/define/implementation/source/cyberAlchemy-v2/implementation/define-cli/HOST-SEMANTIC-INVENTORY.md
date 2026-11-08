# Define host semantic inventory

Status: L1 candidate implementation inventory

This inventory distinguishes meaning-bearing decisions, which belong in
compiled Alch, from mechanical evidence work, which remains in the host. It
covers the three adapters selected by the L1 migration layer.

## Classification rule

A condition is semantic when changing it changes what a declared posture means
or which disposition follows from otherwise identical facts. A condition is
mechanical when it establishes shape, identity, location, coverage, equality,
or delivery of facts without choosing their meaning.

## `language-quality.mjs`

| Host condition | Classification | Current owner |
| --- | --- | --- |
| NFKC, case, separator normalization and phrase containment | Semantic operation | Compiled semantic prelude (`semantic-key`, `contains-phrase`) |
| Grounding posture acceptance and candidate-inference review | Semantic classification | Compiled `GroundingEvidence` entry |
| `distinct`, `related`, `collapsed`, and `unresolved` term-pair meaning | Semantic classification | Compiled `NonCollapseEvidence` entry |
| `independent`, `coupled`, `redundant`, and `unresolved` axis-pair meaning; required coupling type, owner, and effect | Semantic classification | Compiled `OrthogonalityEvidence` entry |
| Aggregate grounding, non-collapse, orthogonality, and confirmation dispositions | Semantic classification | Existing compiled quality and readiness entries |
| Array traversal, integer/range checks, duplicate detection, expected-pair enumeration, coverage sets, option alignment, and reason-code addressing | Mechanical evidence collection | Host adapter |
| Comparing normalized values and definitions for equality | Mechanical application of compiled keys | Host adapter |
| Turning compiled `repair_focus` into stable addressed reason codes | Mechanical projection | Host adapter |

## `conversation-runtime.mjs`

| Host condition | Classification | Current owner |
| --- | --- | --- |
| Scope-ready and next-focus selection | Semantic workflow decision | Existing compiled `ScopeReadiness` entry |
| Language-quality repair focus | Semantic workflow decision | Existing compiled `LanguageReadiness` entry |
| Yes/action token parsing | Interface vocabulary | Host adapter; bounded CLI syntax, not domain meaning |
| Prompt rendering, list formatting, turn limit, option iteration, and agent/RPC calls | Mechanical interaction orchestration | Host adapter |
| Concept ID hashing and exact scope/context construction | Mechanical identity and projection | Host adapter |
| Human confirmation and option actions | External evidence supplied by the user | Host records; Alch does not manufacture confirmation |

## `session-runtime.mjs`

| Host condition | Classification | Current owner |
| --- | --- | --- |
| Action-to-disposition meaning and required disposition evidence | Semantic workflow decision | Existing compiled `ConceptDisposition` entry |
| Definition Pack validity, open-meaning posture, and handoff readiness | Semantic workflow decision | Existing compiled `PackReadiness` entry |
| String trimming, default construction, digest IDs, sorting, index joins, exact disposition counts, and canonical serialization | Mechanical validation/construction | Host adapter |
| Error/reason-code addressing and candidate pack assembly | Mechanical projection | Host adapter |
| Candidate authority ceiling and blocked uses | Declared contract data | Host construction constrained by compiled `PackReadiness`; governance admission remains separate |

## L1 result

All identified host-side meaning choices in these files are now either compiled
Alch decisions or explicitly bounded interface vocabulary. Mechanical host work
does not gain permission to override a compiled disposition. The eleven-entry
service remains candidate evidence with `authority_effect: none`.

## Open Questions

- Should Router and ARE bind directly to the semantic prelude or consume a
  separately versioned service entry in L2?
- Should CLI action tokens later become a declared interface grammar if another
  adapter needs the same vocabulary?
