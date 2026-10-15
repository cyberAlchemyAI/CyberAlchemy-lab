<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Artifact Surface Classification

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.artifact-surface-classification`
- Version: `1.0.0-candidate.2`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:artifact-surface-classification`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

Every governed file f in package P, including P's package.json manifest, has exactly one declared surface role from canonical-instance, declared-component, generated-projection, evidence, fixture, or transient-state. The manifest self-entry is a canonical instance of Canonical Package Manifest/v1. Every canonical instance resolves to exactly one admitted Artifact Type; every other role cannot silently become canonical.

```text
for all f in governed(P), exists exactly one role_P(f) in {I,C,G,E,F,T}; role_P(package.json)=I and type(package.json)=CanonicalPackageManifest/v1; role_P(f)=I => |resolve_R(f)|=1; role_P(f)!=I => not canonical_subject(f).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| P | One declared canonical package home. |
| f | One governed file within or referenced by P. |

### Boundary conditions

- A directory is not a surface role.
- A schema or validator may be a declared component without being an independent artifact instance.
- Transient state cannot satisfy canonical dependencies.

### Testable conditions

- Every governed file has exactly one manifest-declared role.
- The package manifest classifies package.json exactly once as its own canonical instance.
- Every canonical instance resolves to exactly one admitted Artifact Type.
- No generated, fixture, evidence, or transient file is accepted as a canonical subject.

## Plain-language voice

Every important file needs one declared job, and the manifest must list itself too. Its location never decides its role.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

The repository validator classifies product.json as a typed canonical instance, schema.json as a declared component, PRODUCT.md as generated, receipts as evidence, fixtures as tests, and Rust target outputs as transient.

### Examples

- product/products/ontology/v1/product.json is a canonical Product Identity candidate.
- runtime/target/ is transient and cannot become a source of truth.

## Applicability

Classifying every governed file by its explicit role in one canonical package without inferring meaning from its path or extension.

### Exclusions

- Treating every file as an independent artifact instance.
- Inferring authority or identity from directory placement.
- Allowing an unexplained governed file to affect validation or execution.

## Boundaries

- Surface classification is not Artifact Type resolution.
- A declared component is not automatically an Artifact instance.
- Classification is not admission or conformance.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | whole-json | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| cal.definition.artifact-type@1.0.0-candidate.1 | whole-json | `90c61c2fa5a5f1d5d0a96d8e6c1f4b1f902e8ad57d85ef1e315e549470abb69f` | `admitted` |
| cal.definition.canonical-package-home@1.0.0-candidate.1 | whole-json | `c810597968723991449fe78458254679cc6dc87b2b81e54e16a9aa599c59f8ca` | `admitted` |
| cal.definition.artifact-surface-classification@1.0.0-candidate.1 | whole-json | `f801be74e31963a363ed0a2c8ee1aa3e15f7c2e6b8205b1d8c1af9aa67cb49ee` | `candidate-unadmitted` |

## Primary consumers

- cal.artifact-type.canonical-package-manifest/v1
- tooling/validators/artifact_surface.py

## Lookup and drift

- Index: `authority/definitions/candidates/0010-artifact-surface-foundation-revision/DEFINITIONS-INDEX.md` / `cal.definition.artifact-surface-classification@1.0.0-candidate.2`
- Drift owner: `role:definition-owner`
- Audit: `authority/definitions/candidates/0010-artifact-surface-foundation-revision/drift-audit-postimage.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.successor-of | cal.definition.artifact-surface-classification@1.0.0-candidate.2 | cal.definition.artifact-surface-classification@1.0.0-candidate.1 | role:definition-owner |

## Evidence

- ASF-REVISION-REVIEW-01

## Residue

- Repository-wide package manifests remain unauthored; this successor only closes the manifest self-classification rule.

## Claim ceiling

This candidate defines file-role classification only. It does not classify the live repository, admit an Artifact Type, or authorize file movement.
