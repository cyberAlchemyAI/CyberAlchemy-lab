<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Artifact Type Resolution

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.artifact-type-resolution`
- Version: `1.0.0-candidate.2`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:artifact-type-resolution`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

Artifact Type Resolution is an executable deterministic operation resolve_R(a) over one canonical machine carrier and one exact registry. An explicit exact reference may select an admitted-current or admitted-historical type; discriminator-only evidence selects admitted-current types. The operation returns resolved for exactly one match, unresolved for zero, and ambiguous for multiple distinct matches. Paths, filenames, extensions, and nearest-name similarity are excluded evidence.

```text
M_R(a)=explicit_matches_admitted_R(a) union discriminator_matches_current_R(a); resolve_R(a)={resolved(t,state_R(t)) if |M|=1, unresolved if |M|=0, ambiguous(M) if |M|>1}; authority_effect(resolve_R)=none.
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

- The reusable resolver accepts an artifact and exact registry and emits one structured result.
- Directory movement does not change the match set.
- Unknown discriminators return unresolved and conflicting evidence returns ambiguous.
- An exact explicit historical reference resolves with its recorded historical lifecycle state while discriminator-only lookup selects current entries.
- Every result carries the exact registry identity and no authority effect.

## Plain-language voice

One reusable operation reads the file and registry, reports one exact contract or a clear unresolved/ambiguous result, and never guesses from the path.

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
| cal.definition.artifact-type-resolution@1.0.0-candidate.1 | whole-json | `348f3bf980d48a1c83f01620bf46bd634a266a1c224d5a2ff493a60b7be7cbc6` | `candidate-unadmitted` |

## Primary consumers

- tooling/validators/artifact_surface_candidate_2.py
- cal.artifact-type.artifact-type-request/v1

## Lookup and drift

- Index: `authority/definitions/candidates/0010-artifact-surface-foundation-revision/DEFINITIONS-INDEX.md` / `cal.definition.artifact-type-resolution@1.0.0-candidate.2`
- Drift owner: `role:definition-owner`
- Audit: `authority/definitions/candidates/0010-artifact-surface-foundation-revision/drift-audit-postimage.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.successor-of | cal.definition.artifact-type-resolution@1.0.0-candidate.2 | cal.definition.artifact-type-resolution@1.0.0-candidate.1 | role:definition-owner |

## Evidence

- ASF-REVISION-REVIEW-01

## Residue

- The resolver remains candidate product code until the enclosing product candidate is approved and separately admitted or activated.

## Claim ceiling

This candidate defines deterministic lookup semantics only. It does not establish repository conformance or make the candidate registry current.
