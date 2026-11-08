<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Identity Carrier

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.identity-carrier`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:identity-carrier-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

An Identity Carrier K is a canonical artifact for exactly one subject identity. K binds a stable subject identifier, subject kind Definition, owner route, lifecycle identity, and provenance while keeping related identities external through typed relations. Neither placement nor relation membership may synthesize, merge, or replace the carried identity.

```text
K = (carrier_id, subject_id, subject_kind_definition_ref, owner_route, lifecycle_ref, provenance_refs); carries(K,x) and related(x,y) does not imply x=y; path(K) =/=> identity(x).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| K | One Identity Carrier artifact. |
| x | The independently identified subject carried by K. |

### Boundary conditions

- One carrier has one primary subject identity.
- The subject kind resolves through a semantic Definition reference.
- Relations preserve endpoint identity and authority.

### Testable conditions

- The subject ID and kind are explicit rather than inferred from path or name.
- Every related object has an independent identity and typed relation.
- Removing a graph or projection does not erase the canonical carried identity.

## Plain-language voice

An Identity Carrier is the canonical file that says which exact thing this is. Its folder, name, owner, or connections cannot silently turn it into another thing.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

CML-07 will use specialized carriers for Product, Project, Goal, and binding or lineage subjects while keeping their identities and authority separate.

### Examples

- Craft Product and Craft Project need different carriers even if the same person owns both.
- An identity graph references carriers; it does not become their identity source.

## Applicability

A canonical artifact whose distinct validation purpose is to preserve one subject identity, subject kind, owner route, lifecycle identity, and exact semantic Definition bindings across representations and relations.

### Exclusions

- The subject's semantic Definition.
- A directory, filename, shared label, owner, or relation from which identity is inferred.
- A graph index or projection that duplicates or replaces the carrier's canonical identity fields.

## Boundaries

- Identity Carrier is not the carried subject's Definition.
- Identity Carrier is not a directory-derived identity.
- Identity Carrier is not Identity Graph membership, relation, owner identity, or admission.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | whole-json | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| candidate:cal.definition.product@1.0.0-candidate.1 | whole-json | `19c6b3bdb5e4c8515837d40c2b0a98b0fecb6edc3698aab359fa2a0d64d9a1cd` | `candidate-unadmitted` |
| candidate:cal.definition.identity-relation@1.0.0-candidate.1 | whole-json | `cf6a40999ffab4e25f8766d1cd3f6085b7b3ab9468828539521c18e9ca30f28e` | `candidate-unadmitted` |

## Primary consumers

- authority/artifact-types/product-identity/v1
- authority/artifact-types/project-identity/v1
- authority/artifact-types/goal/v1
- CAL-CML07-CRAFT-IDENTITY-CHAIN-0002

## Lookup and drift

- Index: `authority/definitions/candidates/0007-cml07-semantic-closure/DEFINITIONS-INDEX.md` / `cal.definition.identity-carrier@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `authority/definitions/candidates/0007-cml07-semantic-closure/drift-audit-postimage.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

No typed relations declared.

## Evidence

- SC-002

## Residue

- Specialized CML-07 carrier Artifact Types remain unauthored.

## Claim ceiling

This candidate defines Identity Carrier semantics only. It creates no carrier, subject identity, relation, ownership, or admission.
