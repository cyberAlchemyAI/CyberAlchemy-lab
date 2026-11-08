# Define semantic-runtime migration layers

## Target

Move semantic evidence extraction out of handwritten Define host code and into
declared, compiled Alch operations without moving transport, persistence, or
authority into the language runtime.

## L0 - Compiled semantic extraction

Decision question: After this layer, we know whether one real Define quality
path can consume compiled Alch semantic operations without changing its intended
confirmation and repair behavior.

Minimum working unit: `semantic-key` and boundary-aware `contains-phrase` are
declared in the semantic prelude, compiled through ontology and Craft/DomainSpec,
and consumed by `language-quality.mjs`.

Included: Unicode NFKC/lowercase/separator normalization, phrase-boundary
matching, source and generated-artifact verification, readiness confirmation
regression tests. Deferred: transport, persistence, rendering, clocks, locks,
hashing, model interaction, and authority activation.

Exit evidence: semantic fixtures pass; Define separator equivalence passes;
substring grounding fails; `user_confirmed: false` cannot pass readiness; both
generated bundles recompile byte-identically.

Promotion decision: advance only if the complete Define package tests pass.

## L1 - Remaining semantic extraction inventory

Decision question: After this layer, we know whether every remaining host-side
meaning decision has either moved into Alch or has an explicit mechanical-host
classification.

Minimum working unit: inventory every condition in `language-quality.mjs`,
`conversation-runtime.mjs`, and `session-runtime.mjs`; migrate only semantic
classification, keeping fact collection and orchestration in adapters.

Implemented: `HOST-SEMANTIC-INVENTORY.md` classifies the three hosts. Grounding
posture, non-collapse relation posture, and orthogonality/coupling posture now
compile from the `GroundingEvidence`, `NonCollapseEvidence`, and
`OrthogonalityEvidence` Alch entries. Structural indexing, coverage, exact-value
comparison, reason addressing, rendering, and lifecycle orchestration remain
mechanical host responsibilities.

Exit evidence: the ten-entry service compiles through source-linked ontology
and Craft/DomainSpec projects; direct entry witnesses and integrated quality
tests preserve the L0 normalization, phrase-boundary, confirmation, repair, and
authority guarantees.

Deferred: new language-wide syntax and theorem proving. Earlier L0 matching and
confirmation guarantees must remain true.

## L2 - Cross-consumer reuse

Decision question: After this layer, we know whether Router and ARE can consume
the same compiled semantic contract without duplicating Define-specific policy.

Minimum working unit: introduce explicit consumer bindings and parity fixtures
for Router, ARE, and Define while retaining their separate route authority.

Implemented: `semantic-contract-v1/consumer-runtime.mjs` provides the shared
compiled operations. Define consumes it directly for grounding; Router consumes
it directly for signal normalization and phrase non-collapse; ARE request
intent consumes the same bytes through its explicit Module Port adapter for
new-work cue normalization. The binding manifest and parity fixtures preserve
consumer-specific policy, localized unavailability, and `authority_effect: none`.

Exit evidence: shared parity fixtures, Router separator/substring witnesses,
ARE separator-normalized greenfield intake, the full Define suite, and exact
consumer-source binding all pass.

Deferred: runtime admission and mandatory enforcement.

## L3 - Governance candidate

Decision question: After this layer, an owner can decide whether the validated
contract is suitable for a separately governed Constitution proposal.

Minimum working unit: conformance evidence, compatibility policy, degraded-mode
behavior, and an explicit adoption request. No earlier candidate artifact grants
admission or enforcement.

Implemented: the target-local `semantic-contract-v1/governance-candidate/`
package binds the existing Alch Constitution reference to seven scoped rules,
an exact compatibility policy, fail-closed degraded behavior, local evidence,
an unselected three-option adoption request, and positive plus hostile
validation. Local validation can pass while governed conformance remains
`not_evaluable`.

Exit evidence: exact candidate and dependency digests pass; a digest-valid
silent fallback and a digest-valid implicit adoption both block.

Deferred: owner selection, canonical Constitution promotion, compiler or
runtime admission, degraded-mode implementation, activation, and enforcement.

## L4 - Definition Pack Alch handoff

Decision question: After this layer, we know whether one fully reviewed
Definition Pack can become canonical `.alch` source for that candidate and pass
through ontology, Craft/DomainSpec, and executable projection without bypassing
the independent language-quality decisions.

Minimum working unit: add `AlchHandoffReadiness` as the eleventh compiled Define
entry and expose `define compile --input <result> --out <new-directory>`. The
mechanical host adapter renders exact reviewed concepts, scope, and the
no-authority boundary into a deterministic semantic contract, then invokes the
pinned Alch compiler and emits a digest-bound handoff receipt.

Included: exact proposed, reused, and specialized concept representation; an
explicit new-output condition; semantic-grounding, non-collapse, and
orthogonality gates; source, ontology, Craft project, DomainSpec certificate,
runtime projection, finite fixtures, deterministic recompilation, and concise
user-facing success or repair responses.

Exit evidence: the eleven-entry service freshly recompiles byte-identically;
two compilations of the same realistic reviewed pack have identical source,
compiler manifest, and receipt bytes; missing quality, a non-collapse defect,
open meaning, and output overwrite all block; the complete Define test suite
passes.

Deferred: automatic application behavior generation, Plan or Implement route
selection, definition promotion, ontology admission, Constitution adoption,
runtime activation, publication, and deployment.

## Recommended next layer

Exercise the complete new-work path from an actual Router/ARE `define-intake`
decision through conversation and the explicit compile command, then decide
whether the compiled receipt should become a required input to a separately
routed Plan request. Do not make compile imply planning or implementation.

## Open Questions

- What degraded-mode behavior is required before any separately admitted
  service or mandatory runtime binding can be proposed?
- Which named Plan consumer should accept the compiled handoff receipt first?
