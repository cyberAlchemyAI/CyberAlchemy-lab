<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Artifact Type Registry

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.artifact-type-registry`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:artifact-type-registry`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

An Artifact Type Registry R is a canonical reference index over immutable Artifact Type contracts and lifecycle-decision overlays. Each entry binds one type version to its exact artifact, schema, discriminator, semantic definitions, lifecycle state, and decision evidence. R references but does not redefine or admit its entries.

```text
entry_R(t)=(artifact@digest,schema@digest,discriminator,definitions,decision,state); registered_R(t) =/=> admitted(t); current_R(t) only by exact owner decision overlay.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| R | The canonical Artifact Type Registry. |
| t | One exact versioned Artifact Type identity. |

### Boundary conditions

- Candidate and admitted entries are never collapsed.
- Historical admitted versions remain visible when a successor becomes current.
- Shared bootstrap schema selectors are valid exact bindings and need not be moved.

### Testable conditions

- Every registry entry has exact contract, schema, and decision bindings.
- Every instance discriminator resolves to at most one admitted current type.
- The registry contains references rather than duplicate canonical carriers.

## Plain-language voice

The registry is the single catalog that tells tools which file contracts really exist, where their exact bytes live, and which decision—if any—made each one usable.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

The initial candidate reconstructs 25 admitted type versions from six decisions, including seven Foundation types that use selectors in a shared schema rather than dedicated type directories.

### Examples

- Product Identity/v1 maps its schema_version discriminator to its admitted contract.
- Ontology Package/v1 stays candidate and cannot appear in the admitted entries list.

## Applicability

Maintaining one exact machine registry that maps Artifact Type identities and instance discriminators to immutable contracts and owner decisions.

### Exclusions

- Replacing admission decisions.
- Registering a candidate as admitted.
- Duplicating canonical Artifact Type package bytes.

## Boundaries

- Registry is not admission decision.
- Registry is not Artifact Type definition.
- Registry currentness is not inferred from candidate status fields.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | whole-json | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| cal.definition.artifact-type@1.0.0-candidate.1 | whole-json | `90c61c2fa5a5f1d5d0a96d8e6c1f4b1f902e8ad57d85ef1e315e549470abb69f` | `admitted` |

## Primary consumers

- cal.artifact-type.artifact-type-registry/v1
- cal.definition.artifact-type-resolution@1.0.0-candidate.1

## Lookup and drift

- Index: `authority/definitions/candidates/0009-artifact-surface-foundation/DEFINITIONS-INDEX.md` / `cal.definition.artifact-type-registry@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `authority/definitions/candidates/0009-artifact-surface-foundation/drift-audit-postimage.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

No typed relations declared.

## Evidence

- ASF-RESEARCH-02

## Residue

- Initial registry postimage remains candidate-unadmitted.

## Claim ceiling

This candidate defines Artifact Type Registry semantics only. It does not create a live registry or alter any type lifecycle state.
