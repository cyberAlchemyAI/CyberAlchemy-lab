<!-- GENERATED FILE: edit artifact-type-pack.json and rerun render.py. -->

# CTX07 normalized Bounded Context and Context Map artifact-type candidates

> Generated from `artifact-type-pack.json`; this view is not canonical.

- Pack: `CAL-ARTIFACT-TYPE-PACK-CTX07-0002`
- Status: `candidate-authored-awaiting-aggregate-validation-and-owner-review`
- Authority effect: `none`

## Candidate artifact types

| Artifact type | Definition | Predecessor | Machine candidate |
| --- | --- | --- | --- |
| `cal.artifact-type.bounded-context/v2` | `cal.definition.bounded-context@2.0.0-candidate.1` | `cal.artifact-type.bounded-context/v1` | `authority/artifact-types/bounded-context/v2/artifact.json` |
| `cal.artifact-type.context-map/v2` | `cal.definition.context-map@2.0.0-candidate.1` | `cal.artifact-type.context-map/v1` | `authority/artifact-types/context-map/v2/artifact.json` |

## Cross-type invariants

- `CTX07-X01` — Bounded Context/v2 and Context Map/v2 bind their exact admitted current v2 Definitions and preserve their admitted v1 artifact-type predecessors.
- `CTX07-X02` — Bounded Context/v2 forbids context_map_refs and equivalent canonical map-membership fields.
- `CTX07-X03` — Context Map/v2 solely owns exact endpoint membership and typed directional relationships.
- `CTX07-X04` — Reverse membership is a deterministic, digest-bound, noncanonical machine projection generated only from exact map.json inputs.
- `CTX07-X05` — Each candidate satisfies the four-facet contract and generates its human projection from machine-canonical JSON.

## Promotion boundary

One exact decision must bind both immutable v2 candidates, schemas, projections, receipts, shared mechanics, aggregate evidence, and conformance receipt.

Candidate construction, validation, pack membership, or conformance PASS does not admit either artifact type or tooling runtime.

## Claim ceiling

This pack binds two CTX07 artifact-type candidates and their evidence only. It does not admit either type or shared tooling, revise contexts or maps, authorize migration, publish, deploy, or establish a stable release.
