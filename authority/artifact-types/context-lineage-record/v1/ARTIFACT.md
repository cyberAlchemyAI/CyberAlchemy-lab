<!-- GENERATED FILE: edit artifact.json and rerun generator.py. -->

# Context Lineage Record artifact type v1

> Generated from `artifact.json`; this view is not canonical.

- Artifact type: `cal.artifact-type.context-lineage-record/v1`
- Candidate version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Definition: `cal.definition.context-lineage-record`

## Representation contract

- Canonical machine file: `lineage.json`
- Generated human file: `LINEAGE.md`
- Stable identity field: `lineage_record_id`
- Schema: `cal.schema.context-lineage-record/v1`

## Distinct validation purpose

Proves immutable, typed predecessor/successor identity history while explicitly denying inferred equivalence, admission, aliases, and deletion authority.

## Orthogonality rules

| Rule | Mode | Requirement |
| --- | --- | --- |
| `CTX01-LR-01` | `deterministic` | Lineage records historical identity relation; it is not a migration plan or Context Map. |
| `CTX01-LR-02` | `deterministic` | Lineage never infers semantic equivalence or admission. |
| `CTX01-LR-03` | `deterministic` | Every successor has an exact destination version and preserved and changed scopes remain separate. |

## Four facets

### Classification

Lineage identity, disposition, equivalence, admission, authority, and lifecycle remain explicit independent axes.

### Schema

The closed schema requires exact predecessor/successors, versions, lineage kind, scope deltas, decision, boundary, challenge route, and false inference flags.

### Human Continuation

LINEAGE.md is generated and exposes preserved meaning, changed meaning, evidence, residue, and challenge route.

### Machine Checkable

Schema, version cardinality, inference denial, dependency, fixture, and projection checks are executable.

## Remaining residue

- `CTX01-LR-R1` — No artifact-type-owner admission decision binds this candidate. Consequence: No lineage record may rely on this candidate as an admitted type.
- `CTX01-LR-R2` — No lineage owner or exact predecessor and successor context identities are bound. Consequence: No real lineage statement can be authored.

## Claim ceiling

This package is a Context Lineage Record/v1 artifact-type candidate. PASS does not admit the type, establish lineage or equivalence, or permit migration or deletion.
