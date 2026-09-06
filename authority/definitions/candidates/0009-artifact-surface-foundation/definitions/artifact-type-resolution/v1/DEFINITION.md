<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Artifact Type Resolution

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.artifact-type-resolution`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:artifact-type-resolution`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

Artifact Type Resolution is the deterministic partial function resolve_R(a) that returns exactly one admitted type t when artifact a carries an explicit type reference or one registry-declared discriminator matching t. Zero or multiple admitted matches fail closed; paths, filenames, and labels are not resolution evidence.

```text
resolve_R(a)=t iff admitted_R(t) and (explicit_ref(a)=t xor discriminator_R(t) matches a) and cardinality(matches_R(a))=1; otherwise unresolved.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| a | One candidate canonical machine carrier. |
| resolve_R | Resolution using exact registry R. |

### Boundary conditions

- An explicit candidate type reference does not become admitted by resolution.
- A schema_version may be a discriminator only when registered for exactly one type.
- Successful resolution is not schema validation or admission.

### Testable conditions

- Directory movement does not change resolution.
- Unknown and ambiguous discriminators fail closed.
- Resolution returns the exact lifecycle state recorded by the registry overlay.

## Plain-language voice

A file gets its contract only from an exact registered reference or discriminator. If the answer is missing or ambiguous, the system stops instead of guessing.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

goal.json and project.json can resolve through their registered schema_version values even though their current instance schemas do not carry a separate artifact_type_ref field.

### Examples

- cyberalchemy-lab-product-identity/v1 resolves to cal.artifact-type.product-identity/v1.
- A new cyberalchemy-lab-runtime-binding/v1 discriminator remains unresolved until its type is admitted.

## Applicability

Resolving a canonical machine carrier to exactly one admitted Artifact Type through explicit classification or a registry-declared discriminator.

### Exclusions

- Directory or filename inference.
- Nearest-name matching.
- Treating an unadmitted candidate type as usable.

## Boundaries

- Resolution is not validation.
- Resolution is not conformance.
- Resolution cannot use directory placement.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | whole-json | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| cal.definition.artifact-type@1.0.0-candidate.1 | whole-json | `90c61c2fa5a5f1d5d0a96d8e6c1f4b1f902e8ad57d85ef1e315e549470abb69f` | `admitted` |
| cal.definition.validation@1.0.0-candidate.1 | whole-json | `f21ca27867379eb3389588313208a5db37cf0449b79bb5c7f644c3b9a89a2af8` | `admitted` |

## Primary consumers

- tooling/validators/artifact_surface.py
- cal.artifact-type.artifact-type-request/v1

## Lookup and drift

- Index: `authority/definitions/candidates/0009-artifact-surface-foundation/DEFINITIONS-INDEX.md` / `cal.definition.artifact-type-resolution@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `authority/definitions/candidates/0009-artifact-surface-foundation/drift-audit-postimage.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

No typed relations declared.

## Evidence

- ASF-RESEARCH-03

## Residue

- Resolution cannot become enforcing until its registry and validator product are approved and separately adopted.

## Claim ceiling

This candidate defines deterministic lookup semantics only. It does not establish repository conformance or make the candidate registry current.
