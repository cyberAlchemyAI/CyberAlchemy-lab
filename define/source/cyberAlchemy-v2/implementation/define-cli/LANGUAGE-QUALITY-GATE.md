# Define Language Quality Gate

This candidate gate prevents a conversational Define intake from presenting
scope as ready or constructing a Definition Pack while its structured language
evidence contains a known semantic-quality defect.

## Implemented plan

1. The conversational agent emits exact user-language grounding, every
   unordered candidate-term comparison, and any applicable classification axes.
2. The JavaScript host collects evidence facts for grounding coverage,
   collisions, option-to-scope consistency, term pairs, axis pairs, and typed
   couplings. Normalization and boundary-aware phrase containment are declared
   in the Alch semantic prelude and consumed from its compiled runtime. The host
   does not select their disposition.
3. `GroundingEvidence`, `NonCollapseEvidence`, and `OrthogonalityEvidence`
   classify each evidence posture. Independent `SemanticGrounding`,
   `NonCollapse`, and `Orthogonality` Alch entries aggregate those facts.
   `LanguageReadiness` aggregates the dimensions and
   requires explicit user confirmation. `ScopeReadiness`,
   `ConceptDisposition`, and `PackReadiness` carry the decision boundary into
   the rest of the Define lifecycle.
4. `alch/define-runtime.ontology-selection.json` freezes the selected candidate
   business/system records and bridge claims. Every entry is lowered to a
   source-linked composition ontology, a Craft/DomainSpec project, and compiled
   code before the service assembly is emitted.
5. A blocked result returns to discovery. Candidate inference produces review
   posture until explicit user confirmation. Only a pass is retained with the
   candidate Definition Pack.

`scripts/verify-alch-runtime.mjs` fails closed unless the canonical `.alch`
sources, ontology selection, derived ontologies, Craft projects, compiler
certificates, generated service manifest, executable decisions, and a fresh
byte-identical recompilation all agree. Handwritten adapter code cannot satisfy
this gate by itself.

## D65 construction boundary

| Lane | Current state |
| --- | --- |
| Product frontier | Ten AlchLang-declared decision entries plus compiled semantic-key and contains-phrase intrinsics integrated with inventoried thin conversational and session adapters. |
| Runnable product work | Source/ontology/Craft/compiler closure verification plus unit, adversarial conversation, schema, integration, and exact-binding tests. |
| Operational work | Later owner selection for production telemetry, retention, and model-quality monitoring. |
| Exact affected stages | Evidence extraction, `.alch` declarations, selected and derived ontology, Craft project lowering, compiled service assembly, scope confirmation, disposition acceptance, and Definition Pack construction. |
| Causal blockers | None for local candidate testing. Canonical promotion and runtime admission remain separate owner gates. |
| Deferred residue | Independent semantic assessor, multilingual normalization policy, empirical synonym detection, and owner-approved quality thresholds. |

## Claim boundary

The gate proves deterministic construction continuity and rejects concrete
structural contradictions. Pairwise differences and grounding rationales remain
agent-proposed evidence reviewed by the user; a pass is not proof of semantic
truth, canonical status, conformance, or downstream authority.

## Open Questions

- Should a later layer use an independently dispatched semantic assessor rather
  than the conversational model's proposed evidence?
- Which multilingual normalization and synonym resources may be selected
  without leaking private domain language?
- Which quality signals should be retained after the candidate pack leaves the
  local Define session?
