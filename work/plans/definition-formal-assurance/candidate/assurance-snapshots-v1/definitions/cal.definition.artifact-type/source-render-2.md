<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Artifact Type

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.artifact-type`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:artifact-type-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

An Artifact Type is a versioned contract T for one artifact kind. T binds at least one semantic Definition, a closed machine schema, canonical-source direction, deterministic human projection, validation rules, owner route, lifecycle posture, and claim ceiling. Registration of T neither defines its subject meaning nor admits T or any instance.

```text
T = (type_id, version, semantic_definition_refs, schema@digest, canonical_direction, projection_contract, validation_contract, owner_route, lifecycle, claim_ceiling); valid_new_registration(T) only if semantic_definition_refs(T) != empty; registered(T) =/=> admitted(T).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| T | One exact version of an Artifact Type contract. |
| semantic_definition_refs(T) | The admitted or candidate Definition identities whose meanings T operationalizes without redefining them. |

### Boundary conditions

- The Artifact Type and every artifact instance retain separate identities.
- A schema constrains representation but cannot supply missing semantic meaning.
- A candidate Definition reference may support candidate authoring but must be admitted before Artifact Type admission.

### Testable conditions

- Every new registration has at least one resolvable semantic Definition reference.
- The canonical machine file and generated human projection are explicitly directional.
- The schema, generator, owner, lifecycle, and claim ceiling are exact and inspectable.

## Plain-language voice

An Artifact Type is the contract for a kind of file: what it means, which machine shape is canonical, how people see it, how it is checked, and what a passing check does not prove.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

Artifact Type/v2 uses this Definition to require semantic Definition references for every new type registration while preserving the admitted v1 registrations by exact predecessor reference.

### Examples

- Product Identity can bind Product plus Identity Carrier Definitions.
- Method Binding can bind Method plus Identity Relation Definitions without inventing another global meaning.

## Applicability

The versioned contract that determines the admissible machine representation, semantic Definition bindings, generated human projection, validation surface, ownership, and claim ceiling for one artifact kind.

### Exclusions

- An artifact instance.
- A Definition of the artifact's subject meaning.
- An admission decision, validator execution, or authority grant.

## Boundaries

- Artifact Type is not Artifact instance.
- Artifact Type is not Schema alone.
- Artifact Type registration is not semantic definition, validation, conformance, or admission.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | whole-json | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| cal.artifact-type.artifact-type/v1 | whole-json | `143577e9efa793cdf7447e38f5e25013e3006df3b21e9aa3aec4b30d10c19e56` | `admitted` |
| domainspec-core:CAV2-D56 | lines:4116-4223 | `b675ec6ad0949edb8d8527ec3f352422889916f39aa74825269b7f81487f14ed` | `candidate-unadmitted` |

## Primary consumers

- cal.artifact-type.artifact-type/v2
- CAL-CML07-CRAFT-IDENTITY-CHAIN-0002

## Lookup and drift

- Index: `authority/definitions/candidates/0007-cml07-semantic-closure/DEFINITIONS-INDEX.md` / `cal.definition.artifact-type@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `authority/definitions/candidates/0007-cml07-semantic-closure/drift-audit-postimage.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

No typed relations declared.

## Evidence

- SC-003

## Residue

- Artifact Type/v2 remains candidate-unadmitted.

## Claim ceiling

This candidate defines Artifact Type semantics only. It does not admit Artifact Type/v2, retrofit v1 registrations, validate an instance, or grant authority.
