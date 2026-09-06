<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Repository Migration Manifest

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.repository-migration-manifest`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:repository-migration-manifest-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Repository Migration Manifest M binds source snapshot S, target baseline T0, total accounting partition A=(C,E), injective mapping f:C->P, expected postimage T1, validation set V, and rollback set R. M is well formed only when every observed source entry occurs exactly once in C or E, every selected regular file has one digest-bound destination, f has no divergent collision with T0, execution_authority=false, and R equals the set of paths that an authorized additive execution may create.

```text
M=(S,T0,C,E,f,T1,V,R); C disjoint E; C union E=entries(S); injective(f); collision(f(C),T0)=empty; authorize(M)=false; R=create_set(M).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| S | Exact observed source repository snapshot. |
| T0 | Exact target repository baseline before migration. |
| f | Unique mapping from selected source files to target paths. |
| R | Exact rollback set for paths created by authorized execution. |

### Boundary conditions

- Every source entry is accounted for without an ambient glob at execution time.
- Divergent existing target bytes block rather than overwrite.
- Imported bytes remain non-authoritative until separately classified and admitted.
- Runtime installations are reconstructed from canonical profiles and locks.

### Testable conditions

- Source selection and exclusion counts close over the observed filesystem.
- All selected file digests and target-baseline digests are current.
- Mapping is total for selected files, unique, traversal-free, and collision-free.
- Dry-run and isolated rehearsal create no declared-target effects.
- Rollback identifies exactly the paths an authorized execution could create.

## Plain-language voice

This is the sealed moving list for one repository migration: every source item is counted, every file to copy has one destination and digest, collisions stop the move, and the rollback list says exactly what the move could create. The list itself never performs or approves the move.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

The CyberAlchemy-v2 to CyberAlchemy-lab candidate preserves the Lab architecture and copies selected v2 bytes only into plane-local imports/cyberalchemy-v2 boundaries. Imported paths are evidence, not automatic authority or activation.

### Examples

- authority/foo.json maps to authority/imports/cyberalchemy-v2/foo.json without replacing Lab authority.
- node_modules and Rust target trees are accounted as excluded reconstructible state.

## Applicability

An immutable, exact-byte, source-to-target repository migration envelope that binds complete source accounting, exclusions, unique mappings, a target baseline, a copy allowlist, an expected postimage, validation obligations, and rollback boundaries.

### Exclusions

- Context-local semantic succession, which remains owned by Context Migration Manifest.
- Source admission, target activation, product approval, execution authorization, source deletion, overwrite, publication, release, or deployment.
- Installed dependencies, build products, caches, or host-specific runtime state reconstructed from profiles and locks.

## Boundaries

- Repository Migration Manifest and Context Migration Manifest are related but not interchangeable scopes.
- A manifest is a candidate artifact, not an execution authorization.
- Copy selection is not semantic admission; imported material requires later type- and owner-specific review.
- Rollback permission is separate from rollback description.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | whole-json | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| cal.definition.context-migration-manifest@1.0.0-candidate.1 | whole-json | `bcfadcf568fe77a4e410e96ca86ba76f34bf8fdefdff2dfeb8cd12ac67022beb` | `admitted` |
| cal.definition.validation@1.0.0-candidate.1 | whole-json | `f21ca27867379eb3389588313208a5db37cf0449b79bb5c7f644c3b9a89a2af8` | `admitted` |

## Primary consumers

- cal.artifact-type.repository-migration-manifest/v1
- CAL-CYBERALCHEMY-V2-TO-LAB-MIGRATION-0001

## Lookup and drift

- Index: `authority/definitions/candidates/0011-repository-migration-manifest/DEFINITIONS-INDEX.md` / `cal.definition.repository-migration-manifest@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `authority/definitions/candidates/0011-repository-migration-manifest/drift-audit-postimage.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.originates-from | cal.definition.repository-migration-manifest@1.0.0-candidate.1 | cal.definition.context-migration-manifest@1.0.0-candidate.1 | role:definition-owner |

## Evidence

- CAL-CYBERALCHEMY-V2-TO-LAB-MIGRATION-0001

## Residue

- CAL-MIGRATION-R1
- CAL-MIGRATION-R2

## Claim ceiling

This candidate defines a repository migration manifest only. It does not approve or execute migration, admit imported bytes, delete sources, overwrite target bytes, commit, push, publish, release, or deploy.
