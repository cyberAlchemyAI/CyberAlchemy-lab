<!-- GENERATED FILE: edit artifact.json and rerun generator.py. -->

# Context Map artifact type v2

> Generated from `artifact.json`; this view is not canonical.

- Artifact type: `cal.artifact-type.context-map/v2`
- Candidate version: `2.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Definition: `cal.definition.context-map@2.0.0-candidate.1`
- Predecessor type: `cal.artifact-type.context-map/v1`

## Representation contract

- Canonical machine file: `map.json`
- Generated human file: `MAP.md`
- Stable identity field: `context_map_id`
- Schema: `cal.schema.context-map/v2`

## Distinct validation purpose

Proves sole canonical ownership of exact endpoint membership and typed directional relationships, while producing a deterministic noncanonical reverse-membership projection.

## Orthogonality rules

| Rule | Mode | Requirement |
| --- | --- | --- |
| `CTX07-CM-01` | `deterministic` | Every relationship has distinct explicit source and target context references contained in the same map's exact endpoint set. |
| `CTX07-CM-02` | `hybrid` | A relationship is never inferred from directories, imports, proximity, shared labels, or endpoint backreferences. |
| `CTX07-CM-03` | `deterministic` | The Context Map solely owns endpoint membership and directional relations. |
| `CTX07-CM-04` | `deterministic` | Reverse membership is a generated noncanonical projection built only from exact map records. |

## Four facets

### Classification

Map identity, endpoint membership, relationship kind, direction, owners, authority, and lifecycle remain explicit dimensions owned by the map.

### Schema

The closed v2 schema requires exact context refs and fully bounded directional relationships; endpoint contexts are not part of the map representation.

### Human Continuation

MAP.md is deterministically generated from map.json and exposes endpoints, translations, information and authority boundaries, evidence, residue, and drift route.

### Machine Checkable

Endpoint closure, endpoint-set exactness, non-reflexivity, unique relationship identity, Definition currentness, hostile fixtures, reverse-index determinism, and projection parity are executable.

## Generated projection contract

Provide reverse lookup from exact context versions to the Context Maps that canonically contain them without adding endpoint backreferences.

- Canonical inputs: `Exact Context Map/v2 map.json records and their SHA-256 digests only.`
- Generated machine projection: `context-map-membership-index.json`
- Authority effect: `none`

## Remaining residue

- `CTX07-CM-R1` — No artifact-type-owner admission decision binds this v2 candidate. Consequence: No Context Map instance may rely on v2 as an admitted type.
- `CTX07-CM-R2` — No normalized successor context endpoints or successor Governance-to-Ontology-Lifecycle map are authored. Consequence: The fixture proves mechanics only and cannot become a real relationship decision.

## Claim ceiling

This package is a Context Map/v2 artifact-type candidate. PASS proves only its exact schema, dependency, predecessor, fixture, relation-ownership, generated-index, and projection checks; it does not admit the type, create or revise a map, select an integration relationship, authorize migration, or establish a stable release.
