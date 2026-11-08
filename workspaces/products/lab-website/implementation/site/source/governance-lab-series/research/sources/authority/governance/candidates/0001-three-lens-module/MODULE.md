# Governance module candidate 0001

**State:** candidate, unadmitted. **Effect:** none. The machine-readable composition contract is [module.json](module.json); [sources.json](sources.json) binds exact admitted source bytes. The read-only [projector](project.py) and [posture schema](posture.schema.json) make the interpretation inspectable. See [research](RESEARCH.md), [drift audit](DRIFT-AUDIT.md), the [Product Capability example](examples/product-capability-posture.json), and the [Project State successor example](examples/project-state-successor-posture.json).

The [repository integration map](REPOSITORY-MAP.md) extends these lenses over every file in the existing repository inventory. It provides path-complete navigation and exact status lookup routes without treating file presence as admission.

## Purpose and governing rule

For a governed subject, answer three questions together: **who may decide what counts**, **where the subject and its claims came from**, and **which state transitions actually occurred**. Authority, Provenance, and Lifecycle are three inspection lenses. They do not replace the admitted seven-part governance-axis independence invariant: kind, status, evidence confidence, commitment, provenance, owner, and residue must stay independently reportable. A change to one never silently changes another.

| Lens | Question | Output boundary |
| --- | --- | --- |
| Authority | Who has a bounded right to decide for this subject, scope, operation, and effect? | An admission overlay can establish effective record state. Owner text alone does not authorize an action; policy applicability does not prove conformance. |
| Provenance | Which exact source, revision, operation, and typed lineage produced the record? | Digests and relations establish traceability. Traceability does not prove truth, sufficiency, or inherited authority. |
| Lifecycle | Which contract, instance, domain, and runtime states changed? | Each layer is reported separately. A type admission, an instance admission, domain fulfillment, and runtime activation are different effects. |

The module is a **composition and projection contract**, not a new Definition, Artifact Type, Relation Kind, permission evaluator, event carrier, or admission decision. It reads exact admitted sources and emits a derived view with no authority effect. If a bound file changes, projection fails until a new candidate version deliberately rebinds it.

## How it integrates with Lab

1. The admitted Definition registry supplies semantics for Authority, Provenance, Evidence, Policy, Decision, Project State, Project event histories, Challenge Contract, and the independence invariant. The D72 Artifact Type registry and D70 Relation Kind registry supply contract and connection states.
2. An owner-qualified Decision can admit an exact artifact instance through an overlay. The source bytes retain their original candidate fields as provenance. The overlay determines the effective instance admission state.
3. Typed Relations express declared connections on admitted axes. `relation.derives-from` supplies lineage; it does not mean `relation.successor-of`, permission, or fulfillment.
4. Project State is the durable state boundary. Its Context and Ontology Views are derived, source-bound projections. An Agent is ephemeral; session memory is short-lived, while durable memory belongs to Project State and the views reconstructed from it.
5. Semantic and governance histories have distinct purposes. D71 declared both logical streams empty at cursor 0. D72 admitted Project-specific history contracts, one semantic event and one governance event at cursor 1, and the successor Project State through Decision 0071. The initial state is historical. Decision 0072 is not included in that successor; a later governed successor must record it.
6. A Challenge Contract provides an explicit route to dispute a subject. A challenge requires a disposition; it does not automatically suspend or reverse the subject.

## Explicit bridges

The contract enumerates candidate-to-admitted, evidence-to-assessment, lineage-to-successor, decision-to-runtime, and challenge-to-revision bridges. Each lists required inputs, what may change, and what must be preserved. These are transition constraints for future implementations, not a claim that the transitions already happened. In particular, a provenance relation alone cannot authorize a successor or activate a runtime.

## Worked example: Governed Knowledge Lifecycle

The D71 Product Capability instance is **admitted-current as a record**. Its own capability posture is **draft**, its `realization_binding_refs` is empty, and D71 records **zero runtime activations**. The copied source still says `candidate-unadmitted`; that field is source provenance, while the admission overlay supplies effective state. Its exact `relation.derives-from` points to the Product Thesis, but does not make the capability fulfilled. Evidence confidence remains unassessed; the owner is a declared role, not a permission grant. Its residue explicitly records the missing realization binding.

The D72 successor Project State is **admitted-current** and `relation.successor-of` points to the D71 initial state, now **admitted-historical**. The two Project histories have one event each. The governance event references the exact semantic event. The successor state includes decisions through 0071; its own admission Decision 0072 awaits a later successor. This demonstrates a real lifecycle transition without collapsing the two history streams or granting runtime authority.

Run the read model from repository root:

```bash
python3 authority/governance/candidates/0001-three-lens-module/project.py --subject product-capability:cyberalchemy-lab:governed-knowledge-lifecycle
```

Omit `--subject` for all twelve D71–D72 artifact views. The fifteen admitted Typed Relation records are checked as source inputs; this version emits artifact views, not relation-subject views.

Add `--summary` for a compact inventory of identity, kind, effective instance state, domain status, owner, and source bundle.

## Review and validation

`python3 authority/governance/candidates/0001-three-lens-module/validate.py` checks module and output schemas, fourteen current Definition bindings, D70–D72 source digests, both bundle manifests and overlays, closed relation endpoints, the history transition, all twelve views, and parity with both saved examples. It does not decide admission or prove runtime behavior.

No Definition registry or canonical Definition index changed because this candidate introduces no Definition. The [drift audit](DRIFT-AUDIT.md) records the follow-up needed before a live governance writer or permission evaluator can be claimed.
