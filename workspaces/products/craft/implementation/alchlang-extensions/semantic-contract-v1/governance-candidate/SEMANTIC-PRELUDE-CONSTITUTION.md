# Alch Semantic Prelude Constitution

Status: candidate
Constitution ID: `ALCH-CONSTITUTION-SEMANTIC-PRELUDE`
Version: `1-candidate`
Owner: AlchLang language owner
Governance reviewer: CyberAlchemy v2 governance-model owner
Authority level: capability-local candidate Constitution
Selectors: `profile:semantic-contract-v1`
Authority effect: none
Enforcement effect: none

## Scope

This candidate Constitution governs the meaning-preserving use of the compiled
Alch semantic prelude by consumers that explicitly bind
`profile:semantic-contract-v1`. It covers semantic operation identity,
non-collapse, orthogonality, compatibility, degraded behavior, and evidence
posture. It does not govern consumer-specific routing, intent, or Define policy.

The `.alch` source is the declaration surface. This document supplies the
human-reviewable rules for its existing `governed-by` reference; neither
artifact adopts or activates the other.

## Rules

### ALCH-SPC-1. Declared Source And Compiled Runtime Stay Bound

Validation mode: deterministic

A consumer may claim this profile only when the exact declared `.alch` source,
compiled runtime, and binding manifest match their accepted digests. A compiled
projection cannot replace or redefine the source declaration.

Example: a consumer imports the shared adapter whose runtime digest matches the
candidate manifest.

Non-example: a consumer copies the operation into host JavaScript and calls the
copy semantically equivalent.

### ALCH-SPC-2. Token And Phrase Meanings Do Not Collapse

Validation mode: deterministic

Token and phrase matching must preserve complete normalized token boundaries.
A substring inside a larger token cannot satisfy a semantic match.

Example: `define` matches `define a system` but not `predefined system`.

Non-example: raw substring search is treated as evidence of the declared token.

### ALCH-SPC-3. Semantic Dimensions Remain Orthogonal

Validation mode: deterministic

Each operation changes only the dimension named by its contract. In particular,
reason accumulation preserves reason text and does not invoke normalization.

Example: appending `Needs Review` preserves those bytes and prior reason order.

Non-example: appending a reason lowercases it as an undocumented side effect.

### ALCH-SPC-4. Shared Mechanism Does Not Centralize Consumer Authority

Validation mode: hybrid

Consumers may share compiled semantic mechanisms, but Define quality policy,
Router route selection, and ARE objective-transition policy remain owned by
their respective contracts. A semantic match is evidence, not an authority
decision.

Example: Router uses `contains-phrase` but the verified route profile still
owns route selection.

Non-example: the semantic prelude selects a route or declares a Definition Pack
ready.

### ALCH-SPC-5. Compatibility Is Exact And Explicit

Validation mode: deterministic

Compatibility follows `compatibility-policy.json`. Any source or runtime byte
change requires a new binding digest and revalidation. Breaking semantic or
operation-shape changes require a new profile version rather than silent reuse
of `semantic-contract-v1`.

Example: an added fixture revalidates every bound consumer and refreshes exact
evidence before the candidate is reconsidered.

Non-example: changing separator semantics while retaining the accepted runtime
digest or profile identity.

### ALCH-SPC-6. Degraded Operation Fails Closed

Validation mode: deterministic

The behavior in `degraded-mode-policy.json` applies when the compiled artifact
is missing, stale, unloadable, or fails validation. No consumer may silently
fall back to a host-local semantic implementation.

Example: Define withholds language-readiness claims when the semantic runtime
cannot be verified.

Non-example: Router falls back to substring matching when the shared runtime is
unavailable.

### ALCH-SPC-7. Evidence Cannot Adopt Or Activate Governance

Validation mode: hybrid

Passing fixtures, parity suites, compilation, and digest checks are candidate
evidence only. Adoption requires an explicit owner selection over exact bytes.
Admission, activation, and enforcement remain later and separate decisions.

Example: the adoption request remains `awaiting-owner-decision` after all local
checks pass.

Non-example: a passing validator sets `constitution_adopted` to true.

## Validation Adapters

| Rule | Adapter |
| --- | --- |
| ALCH-SPC-1 | Governance manifest digest closure and `.alch` binding checks. |
| ALCH-SPC-2 | Semantic fixtures plus Router and ARE substring witnesses. |
| ALCH-SPC-3 | Semantic operation orthogonality fixtures. |
| ALCH-SPC-4 | Exact consumer binding checks plus owner-boundary review. |
| ALCH-SPC-5 | Compatibility-policy structure and digest currentness checks. |
| ALCH-SPC-6 | Degraded-mode structure plus hostile silent-fallback test. |
| ALCH-SPC-7 | Adoption-request state and authority-ceiling checks. |

## Promotion Boundary

This candidate may be proposed for capability-local adoption only after its
manifest and validator pass over current bytes. Adoption, if selected, would
adopt only these exact rules for the exact selector. It would not admit the
compiler, runtime, ontology, consumer implementations, or enforcement binding.

## Retirement Or Split Triggers

- Split deployment behavior into a runtime Constitution if a service boundary
  is introduced.
- Issue a new profile and Constitution version for breaking operation meaning
  or signature changes.
- Retire this candidate if the AlchLang language owner rejects the exact
  adoption request.

## Open Questions

- Which runtime owner may later propose an admitted enforcement binding?
- Should property-based evidence become a required compatibility check in a
  successor version?

