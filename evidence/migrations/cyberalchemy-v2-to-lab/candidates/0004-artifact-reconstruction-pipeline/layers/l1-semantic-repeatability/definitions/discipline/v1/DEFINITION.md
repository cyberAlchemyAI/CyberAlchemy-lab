<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Discipline

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.discipline`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope.shared-authority`
- Lifecycle posture reference: `candidate:artifact-reconstruction-l1/v1`

## Scientific/formal voice

Discipline is the normalized definition identified by semantic.discipline, owned within scope.shared-authority, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D50 without silently merging it with another target.

Bound source-semantic basis:

A discipline is a **recurring, cross-capability practice** promoted to authority via
**discipline-governance** — cataloged in `../../disciplines/` with a steward/owner,
evidence that it already recurs, a maturity status (`candidate -> active-pattern ->
canonical`), and a named hardening route. Evidence of recurrence alone does **not**
self-promote a discipline; the owner route does.

```text
```text
Discipline = (practice, steward/owner, recurrence_evidence, maturity_status, hardening_move)
maturity_status in { candidate, active-pattern, canonical }
promotion: discipline-governance over the maturity ladder (never auto)
```

A discipline is valid only when it names its steward, recurrence evidence, maturity,
and hardening move; `CAV2-D38` bounds any claim of "canonical" to the evidence.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| semantic.discipline | Stable normalized identity for Discipline. |
| CAV2-D50 | Bound CyberAlchemy-v2 source-definition identity. |

### Boundary conditions

- A discipline is **not** a canonical term (definitions-governance owns terms), **not** a
sigil, **not** a spell, **not** an implementation task (AUTHORITY-MODEL Authority Kinds
"must not collapse into"), and **not** Craft method specifically (`CAV2-D20` is one
discipline). Per AUTHORITY-MODEL non-collapse rule 4: *a discipline can recommend a
route, but it cannot define a term or author a constitution.* It is **not** operational
work (`CAV2-D20` Craft work-state) — authoring a discipline may be work, but the
discipline-as-authority-kind is governance.

### Testable conditions

- The candidate identity remains cal.definition.discipline.
- Every selected source-section digest remains current.
- The machine record validates against Definition/v1.
- The human projection is regenerated exactly from the machine record.

## Plain-language voice

A habit the project does across many capabilities — named and hardened so it's done
consistently. It earns authority by recurring and being stewarded, not by being declared.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

In CyberAlchemy-lab migration work, Discipline is a prototype meaning reconstructed from CAL-NORMALIZE-01. It remains non-authoritative until the correct Lab owner admits a fully validated candidate.

Source context retained for reconstruction:

In CyberAlchemy v2, disciplines live as cards under `../../disciplines/` owned by
discipline-governance (e.g. `stable-repository-stewardship`, `provisional-model-stewardship`).
`CAV2-D20` Craft method is itself **a** discipline (an instance), not the genus. The
Arcanum discipline model (maturity ladder / growth rule) is the ancestral source
(Evidence posture).

### Examples

- Resolve semantic.discipline by its machine identity rather than its directory name.
- Challenge source drift through the L1 drift audit before relying on Discipline.

## Applicability

Use when a recurring practice spans capabilities and needs a steward + hardening path
(AUTHORITY-MODEL narrowest-owner rule: *"a recurring practice needs a steward and
hardening path → discipline-governance"*). It turns a habit into a governed, hardenable
practice rather than ad-hoc repetition.

### Exclusions

- Admission, activation, publication, release, deployment, and external effects.
- Meanings assigned to split or reclassified sibling targets unless explicitly referenced.

## Boundaries

- A discipline is **not** a canonical term (definitions-governance owns terms), **not** a
sigil, **not** a spell, **not** an implementation task (AUTHORITY-MODEL Authority Kinds
"must not collapse into"), and **not** Craft method specifically (`CAV2-D20` is one
discipline). Per AUTHORITY-MODEL non-collapse rule 4: *a discipline can recommend a
route, but it cannot define a term or author a constitution.* It is **not** operational
work (`CAV2-D20` Craft work-state) — authoring a discipline may be work, but the
discipline-as-authority-kind is governance.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cyberalchemy-v2:CAV2-D50 | ## CAV2-D50: Discipline | `ec5e8c9ac7c8bae64f8591d15fc9b60a9ab6b6146368212067381697d564e3a0` | `candidate-unadmitted` |

## Primary consumers

- semantic.constitution
- semantic.parent-instance-authority-separation-invariant

## Lookup and drift

- Index: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/registry.json` / `cal.definition.discipline@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.originates-from | cal.definition.discipline | cyberalchemy-v2:CAV2-D50 | role:definition-owner |

## Evidence

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/semantic/semantic-discipline/v1/artifact.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/receipts/validation.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/receipts/validation.json

## Residue

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json

## Claim ceiling

Candidate Definition reconstructed from an accepted normalization scaffold and exact CyberAlchemy-v2 source sections. It is not admitted and grants no implementation, migration, registry, publication, release, deployment, or external-effect authority.
