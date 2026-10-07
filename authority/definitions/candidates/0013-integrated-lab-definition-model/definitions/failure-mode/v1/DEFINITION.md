<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Failure Mode

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.failure-mode`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:failure-mode-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Failure Mode is a versioned reusable design-time contract for one distinct way a declared subject kind can fail an exact boundary under stated conditions. A Failure Mode can predate occurrences and does not establish that any occurrence happened.

```text
FailureMode(x) => governed_identity_or_record(x) and bounded_scope(x); FailureMode(x) =/=> authority_effect(x).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| x | One subject evaluated under the Failure Mode Definition. |

### Boundary conditions

- A Failure Mode is a versioned reusable design-time contract for one distinct way a declared subject kind can fail an exact boundary under stated conditions.
- A Failure Mode can predate occurrences and does not establish that any occurrence happened.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

### Testable conditions

- Every use of Failure Mode resolves to this exact Definition version or an admitted successor.
- Every claimed instance or use stays within the applicability statement and exclusions.
- No consumer infers admission, authority, success, identity equivalence, or external effect from the term alone.

## Plain-language voice

A Failure Mode is a versioned reusable design-time contract for one distinct way a declared subject kind can fail an exact boundary under stated conditions. A Failure Mode can predate occurrences and does not establish that any occurrence happened.

## Domain-context voice

Workspace: `/home/vlad_/projects/CyberAlchemy-lab`

In the Lab, Failure Mode supplies one distinct semantic responsibility in the integrated model. Its carrier and relations remain separate governed contracts.

### Examples

- FM-QUAL-OPEN describes a Relation Kind accepting undeclared qualifier strings, its detection validator, impacts, controls, and recovery expectations.

## Applicability

A Failure Mode is a versioned reusable design-time contract for one distinct way a declared subject kind can fail an exact boundary under stated conditions.

### Exclusions

- A Failure Mode can predate occurrences and does not establish that any occurrence happened.
- This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect.

## Boundaries

- A Failure Mode can predate occurrences and does not establish that any occurrence happened.
- The term supplies meaning only; carrier shape, relation availability, runtime behavior, and authority effect require separate admitted contracts.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.source.failure-model-review@2026-10-05 | whole-file | `032df6404218ae298af16a8796597c0c766825a2f76ead0e6dad21bf365cc839` | `candidate-unadmitted` |

## Primary consumers

- .arcanum/ontology-vault/2026-10-05-lab-integrated-model.md

## Lookup and drift

- Index: `authority/definitions/candidates/0013-integrated-lab-definition-model/DEFINITIONS-INDEX.md` / `cal.definition.failure-mode@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `authority/definitions/candidates/0013-integrated-lab-definition-model/drift-audit-postimage.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

No typed relations declared.

## Evidence

- .arcanum/ontology-vault/2026-10-05-failure-mode-model-review.md
- .arcanum/ontology-vault/2026-10-05-lab-integrated-model.md
- .arcanum/ontology-vault/2026-10-06-lab-semantic-gap-audit.md

## Residue

- Definition-owner review and exact admission remain required.
- Artifact Type carrier, relation, qualifier, ontology, runtime, and consumer decisions remain separate.

## Claim ceiling

This candidate defines Failure Mode for review only. It does not admit the Definition or any carrier, instance, relation, Policy, Decision, runtime behavior, authority, publication, release, deployment, or external effect.
