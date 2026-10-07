<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Incident

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.incident`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:incident-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

An Incident is a governed response and accountability envelope for related Failure Occurrences whose impact or uncertainty requires coordinated ownership, timeline, containment, recovery, communications, decisions, evidence, and closure. Closure does not erase occurrences, residue, unknown delivery, causal uncertainty, or follow-up obligations.

```text
Incident(x) => governed_identity_or_record(x) and bounded_scope(x); Incident(x) =/=> authority_effect(x).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| x | One subject evaluated under the Incident Definition. |

### Boundary conditions

- An Incident is a governed response and accountability envelope for related Failure Occurrences whose impact or uncertainty requires coordinated ownership, timeline, containment, recovery, communications, decisions, evidence, and closure.
- Closure does not erase occurrences, residue, unknown delivery, causal uncertainty, or follow-up obligations.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

### Testable conditions

- Every use of Incident resolves to this exact Definition version or an admitted successor.
- Every claimed instance or use stays within the applicability statement and exclusions.
- No consumer infers admission, authority, success, identity equivalence, or external effect from the term alone.

## Plain-language voice

An Incident is a governed response and accountability envelope for related Failure Occurrences whose impact or uncertainty requires coordinated ownership, timeline, containment, recovery, communications, decisions, evidence, and closure. Closure does not erase occurrences, residue, unknown delivery, causal uncertainty, or follow-up obligations.

## Domain-context voice

Workspace: `/home/vlad_/projects/CyberAlchemy-lab`

In the Lab, Incident supplies one distinct semantic responsibility in the integrated model. Its carrier and relations remain separate governed contracts.

### Examples

- INC-09 groups three failed registry admissions that blocked a release and coordinates rollback, owner communication, and closure evidence.

## Applicability

An Incident is a governed response and accountability envelope for related Failure Occurrences whose impact or uncertainty requires coordinated ownership, timeline, containment, recovery, communications, decisions, evidence, and closure.

### Exclusions

- Closure does not erase occurrences, residue, unknown delivery, causal uncertainty, or follow-up obligations.
- This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect.

## Boundaries

- Closure does not erase occurrences, residue, unknown delivery, causal uncertainty, or follow-up obligations.
- The term supplies meaning only; carrier shape, relation availability, runtime behavior, and authority effect require separate admitted contracts.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.source.failure-model-review@2026-10-05 | whole-file | `032df6404218ae298af16a8796597c0c766825a2f76ead0e6dad21bf365cc839` | `candidate-unadmitted` |

## Primary consumers

- .arcanum/ontology-vault/2026-10-05-lab-integrated-model.md

## Lookup and drift

- Index: `authority/definitions/candidates/0013-integrated-lab-definition-model/DEFINITIONS-INDEX.md` / `cal.definition.incident@1.0.0-candidate.1`
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

This candidate defines Incident for review only. It does not admit the Definition or any carrier, instance, relation, Policy, Decision, runtime behavior, authority, publication, release, deployment, or external effect.
