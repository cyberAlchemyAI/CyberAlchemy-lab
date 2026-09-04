<!-- GENERATED FILE: edit artifact.json and rerun generator.py. -->

# Context Map artifact type v1

> Generated from `artifact.json`; this view is not canonical.

- Artifact type: `cal.artifact-type.context-map/v1`
- Candidate version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Definition: `cal.definition.context-map`

## Representation contract

- Canonical machine file: `map.json`
- Generated human file: `MAP.md`
- Stable identity field: `context_map_id`
- Schema: `cal.schema.context-map/v1`

## Distinct validation purpose

Proves owned, typed, directional relationships between exact context references with explicit information and authority boundaries.

## Orthogonality rules

| Rule | Mode | Requirement |
| --- | --- | --- |
| `CTX01-CM-01` | `deterministic` | Every relationship has distinct explicit source and target context references. |
| `CTX01-CM-02` | `hybrid` | A relationship is never inferred from directories, imports, proximity, or shared labels. |
| `CTX01-CM-03` | `deterministic` | Dependent classifications are relations, not redundant canonical axes on endpoint contexts. |

## Four facets

### Classification

Map identity, relationship kind, endpoints, direction, owners, authority, and lifecycle remain separate dimensions.

### Schema

The closed schema requires two or more exact context refs and fully bounded directional relationship records.

### Human Continuation

MAP.md is generated and exposes contracts, translations, boundaries, evidence, residue, and drift route.

### Machine Checkable

Endpoint closure, non-reflexivity, schema, dependency, hostile fixture, and projection parity are executable.

## Remaining residue

- `CTX01-CM-R1` — No artifact-type-owner admission decision binds this candidate. Consequence: No Context Map instance may rely on this candidate as an admitted type.
- `CTX01-CM-R2` — The Governance to Ontology Lifecycle relationship pattern and owners remain unselected. Consequence: The first real Context Map remains blocked.

## Claim ceiling

This package is a Context Map/v1 artifact-type candidate. PASS does not admit the type, create a map, or select an integration pattern.
