<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Artifact Type Request

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.artifact-type-request`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:artifact-type-request`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

An Artifact Type Request Q is a candidate-only intake record created only after resolve_R(a) is empty and compatibility analysis rejects exact reuse. Q describes intended semantics, owner, package home, representation direction, validation purpose, and proposed dependencies, but Q is not a, not an Artifact Type, and has no authority effect.

```text
create(Q,a) only if matches_R(a)=empty and no_exact_fit(a); Q != a; Q != T; authority_effect(Q)=none; consumed_as_subject(Q)=false.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| Q | One Artifact Type Request. |
| a | The not-yet-authored subject kind being requested. |

### Boundary conditions

- The requested subject remains unauthored until its exact type exists.
- Draft schemas are attachments or declared request components, not admitted type contracts.
- The request expires or is superseded when resolved, rejected, or replaced.

### Testable conditions

- Every request includes an existing-type compatibility analysis.
- Every request declares no authority effect and cannot satisfy subject dependencies.
- Every accepted request produces a separately identified Artifact Type candidate.

## Plain-language voice

When no existing contract fits, write a typed request explaining the gap. Do not create the new kind of record first and hope to classify it later.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

A Runtime Binding or Source Closure that cannot resolve to an admitted type first receives an Artifact Type Request. The request can carry draft components but cannot stand in for the binding or closure.

### Examples

- Request a Runtime Binding type after recording why Method Binding and implementation components do not fit.
- Do not relabel Ontology Package/v1 as admitted merely because its candidate package exists.

## Applicability

Recording a non-authoritative request to define and test a genuinely new artifact kind after deterministic resolution finds no admitted fit.

### Exclusions

- Serving as the requested subject artifact.
- Self-registering or self-admitting a type.
- Widening an existing type by convenience.

## Boundaries

- Artifact Type Request is not requested artifact.
- Artifact Type Request is not admission request.
- Artifact Type Request is not Artifact Type registration.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | whole-json | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| cal.definition.artifact-type@1.0.0-candidate.1 | whole-json | `90c61c2fa5a5f1d5d0a96d8e6c1f4b1f902e8ad57d85ef1e315e549470abb69f` | `admitted` |
| cal.definition.validation@1.0.0-candidate.1 | whole-json | `f21ca27867379eb3389588313208a5db37cf0449b79bb5c7f644c3b9a89a2af8` | `admitted` |

## Primary consumers

- cal.artifact-type.artifact-type-request/v1
- authority/artifact-type-requests

## Lookup and drift

- Index: `authority/definitions/candidates/0009-artifact-surface-foundation/DEFINITIONS-INDEX.md` / `cal.definition.artifact-type-request@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `authority/definitions/candidates/0009-artifact-surface-foundation/drift-audit-postimage.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

No typed relations declared.

## Evidence

- ASF-RESEARCH-04

## Residue

- No real request instance is admitted by this candidate.

## Claim ceiling

This candidate defines unmatched-type intake semantics only. It does not authorize creation or use of a new subject artifact.
