<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Axiom

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.axiom`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope.shared-authority`
- Lifecycle posture reference: `candidate:artifact-reconstruction-l1/v1`

## Scientific/formal voice

Axiom is the normalized definition identified by semantic.axiom, owned within scope.shared-authority, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D53 without silently merging it with another target.

Bound source-semantic basis:

An axiom is a **foundational proposition taken as given** — bedrock the system does
not derive further within itself and holds as true (high commitment/veracity) —
**from which a family of premises, invariants, and constitution rules derives**,
such that revising it forces rethinking everything built on it. Its defining
subject is the **world or domain** the system operates in: an axiom states *why*
the system is shaped as it is, and the system is **built around** it rather than
made to satisfy it. It is **not** a constraint on the system's own behavior — that
is an invariant (`CAV2-D54`).

```text
```text
axiom A:  taken-as-given(A) ∧ ¬derives-within-system(A) ∧ veracity(A) = high
          ∧ fan_out(A) = { premises, invariants, constitution-rules derived from A }
subject(A) = world/domain          (not the system's own behavior)
system can violate A?  No — if A is false, the premise was wrong, not the code buggy
genesis:       invariant → "why must this hold?" → A     (discovery order)
justification: A → invariant → constitution rule          (top-down order)
```

The **fan-out** is the axiom's signature: a proposition that grounds only one
downstream item, and nothing else, is not an axiom but the restatement of a single
invariant.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| semantic.axiom | Stable normalized identity for Axiom. |
| CAV2-D53 | Bound CyberAlchemy-v2 source-definition identity. |

### Boundary conditions

- An axiom is **not** an invariant (`CAV2-D54`): the invariant is a must-hold on the
*system*; the axiom is a given truth about the *world* the system is built around.
It is **not** a premise: a premise is a working bet held at low veracity
(`veracidade: low`), an axiom is held true. It is **not** a constitution
(`CAV2-D58`): the constitution is the authoritative scoped rulebook; the axiom
is the reason behind it. It is **not** a definition (`CAV2-D33`): a definition assigns meaning to
a term, an axiom asserts a foundational truth. An axiom and the invariants it
grounds enforce nothing by themselves. A constitution authorizes and scopes
constraints; a selected validator or gate checks or performs enforcement.

### Testable conditions

- The candidate identity remains cal.definition.axiom.
- Every selected source-section digest remains current.
- The machine record validates against Definition/v1.
- The human projection is regenerated exactly from the machine record.

## Plain-language voice

A truth you build on, not a rule you obey. "Creatives are fat-tailed" is true about
the world; you design around it. If it turned out false, your plan was wrong — not
your code.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

In CyberAlchemy-lab migration work, Axiom is a prototype meaning reconstructed from CAL-NORMALIZE-01. It remains non-authoritative until the correct Lab owner admits a fully validated candidate.

Source context retained for reconstruction:

In CyberAlchemy v2, axiom is the top of the `axiom → invariant → constitution →
validator` justification chain and the *why* reached by asking backward from an
invariant in the `invariant → axiom` discovery direction. It is distinct from
the specific invariant-definitions
already promoted (`CAV2-D16`/`D29`/`D38`/`D49`), which are invariants, not axioms.
Evidence corpora: maestro-trama `creative-axioms` (clean descriptive axioms);
ZefraHub / maestro-trama `system-axioms` (mostly invariants mislabeled as axioms;
`AX-SYS-3` and `AX-ONT-7` are premises).

### Examples

- Resolve semantic.axiom by its machine identity rather than its directory name.
- Challenge source drift through the L1 drift audit before relying on Axiom.

## Applicability

Use "axiom" for the load-bearing truths a project stands on and reasons *from* —
the ones that justify why a whole area, method, or rule family exists. Three tests:
(1) can the system make it false? If yes, it is an invariant, not an axiom. (2) Is
it actually believed true, or is it a bet? A bet (`veracidade: low`) is a
**premise**, not an axiom. (3) Does a family derive from it? If nothing does, it is
inert.

### Exclusions

- Admission, activation, publication, release, deployment, and external effects.
- Meanings assigned to split or reclassified sibling targets unless explicitly referenced.

## Boundaries

- An axiom is **not** an invariant (`CAV2-D54`): the invariant is a must-hold on the
*system*; the axiom is a given truth about the *world* the system is built around.
It is **not** a premise: a premise is a working bet held at low veracity
(`veracidade: low`), an axiom is held true. It is **not** a constitution
(`CAV2-D58`): the constitution is the authoritative scoped rulebook; the axiom
is the reason behind it. It is **not** a definition (`CAV2-D33`): a definition assigns meaning to
a term, an axiom asserts a foundational truth. An axiom and the invariants it
grounds enforce nothing by themselves. A constitution authorizes and scopes
constraints; a selected validator or gate checks or performs enforcement.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cyberalchemy-v2:CAV2-D53 | ## CAV2-D53: Axiom | `2cd16ef68301c84dcf563b9ec9e661bf0890344e219101d27de43d0826693fde` | `candidate-unadmitted` |

## Primary consumers

- semantic.constitution
- semantic.hypothesis
- semantic.invariant
- semantic.premise
- semantic.schema

## Lookup and drift

- Index: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/registry.json` / `cal.definition.axiom@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.originates-from | cal.definition.axiom | cyberalchemy-v2:CAV2-D53 | role:definition-owner |

## Evidence

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/semantic/semantic-axiom/v1/artifact.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/receipts/validation.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/receipts/validation.json

## Residue

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json

## Claim ceiling

Candidate Definition reconstructed from an accepted normalization scaffold and exact CyberAlchemy-v2 source sections. It is not admitted and grants no implementation, migration, registry, publication, release, deployment, or external-effect authority.
