# Step 6 — revised profile meanings

These are unadmitted semantic candidates. Continuing the review does not record acceptance or admission.

## Definition Evaluation Profile

A Definition Evaluation Profile is a reusable, owner-qualified, version-exact contract declaring how an Evaluation assesses one exact Definition version and its declared review package within a named scope and phase. It binds the subject and input selection, applicable governing contracts, required checks, evidence requirements, permitted outcomes, causal blockers, phase-specific aggregation, pre-decision eligibility and claim limits. It specifies the rules for producing and interpreting evaluation evidence; a declared profile does not establish that an Evaluation occurred, that its criteria passed, that an owner selected admission or that an effect was applied.

[Full three-voice candidate](definitions/definition-evaluation-profile/DEFINITION.md).

## Definition Lifecycle Profile

A Definition Lifecycle Profile is a reusable, owner-qualified, version-exact contract declaring the initial posture, permitted states and directed transitions for one exact Definition version under selected governing contracts. It binds each transition to its required evaluation and review evidence, applicable owner authority, intended effect, invalidation conditions and history-preservation rules. It separates satisfied gates, recorded review, selected admission and confirmed application. Declaring the profile or satisfying a gate does not itself record a new state, select an owner Decision, apply an effect or prove that a transition occurred.

[Full three-voice candidate](definitions/definition-lifecycle-profile/DEFINITION.md).

## The same incident, three different questions

| Subject | Question | Current example |
| --- | --- | --- |
| Export evidence | Are all required IDs present for Northstar/status=active/S-1042/E-1042? | Proposed criterion would fail: 200 missing required IDs. |
| Definition evaluation | What checks/evidence establish representation or admission readiness? | Representation/projection pass; required semantic/review evidence remains not evaluable. |
| Definition lifecycle | What state is actually recorded, and what must happen to change it? | Candidate-authored; no transition or admission performed. |

The Evaluation Profile declares the checks and phase aggregates. Applying it produces a separate evidence record. The Lifecycle Profile declares transition gates; an actual transition still needs its applicable evidence, owner authority, attributable record and confirmed effect.

## Revisions from the previous drafts

- Bootstrap through admitted v1 mechanics is documented as a representation/review choice, outside normative applicability.
- Each profile now has its own complete notation and operational interpretation.
- Evaluation reports all declared checks while aggregating only the selected phase. Later Decision/application checks can remain pending before admission.
- Lifecycle gate satisfaction is distinct from an actual recorded/applied transition.
- Legacy profile sources use exact `/checks`, `/admission_rule`, `/transitions` and `/separation_invariants` selectors. A lone slash would address an empty-key member, not the whole JSON document.
- Existing staged carrier bindings point to the exact revised candidates; historical step-5 bytes remain unchanged.

## Proposed compatibility handling

Preserve the predecessor owner/source references in history. The successor retains owner accountability in its scoped owner field and exact source-admission provenance in its source/lineage fields. No Definition-to-Role global governed-by edge or inferred Source endpoint is created. These dispositions still need the exact owner determination.

## Current preparation standing

Exact v1 schema and generated projection checks pass. Five close-neighbor comparisons are author analysis only. Formal assurance, source-use/fidelity review, postimages and independent carrier/profile adoption remain pending. This package is not admission-ready.

The practical guide changed since the last capture; it was reread and captured at its new digest. Prior receipts retain their original byte bindings.

- [Example flow](example.json)
- [Formal operational interpretation](interpretation.json)
- [Distinction and compatibility review](distinction-review.json)
- [Source capture](source-selection.json)
- [Structural review checks](review-checks.json)
- [Queue](../../DEFINITIONS-INDEX.md)

Next: required formal/source/fidelity evidence and exact review postimages. The new meanings and compatibility choices must still be reviewed before admission.
