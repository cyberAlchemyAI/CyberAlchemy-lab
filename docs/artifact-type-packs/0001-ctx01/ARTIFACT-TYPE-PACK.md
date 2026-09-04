<!-- GENERATED FILE: edit artifact-type-pack.json and rerun render.py. -->

# CTX01 context metamodel artifact-type candidates

> Generated from `artifact-type-pack.json`; this view is not canonical.

- Pack: `CAL-ARTIFACT-TYPE-PACK-CTX01-0001`
- Status: `candidate-authored-awaiting-aggregate-validation-and-owner-review`
- Authority effect: `none`

## Candidate artifact types

| Wave | Artifact type | Definition | Identity field | Machine candidate |
| --- | --- | --- | --- | --- |
| `identity` | `cal.artifact-type.bounded-context/v1` | `cal.definition.bounded-context` | `context_id` | `authority/artifact-types/bounded-context/v1/artifact.json` |
| `identity` | `cal.artifact-type.ubiquitous-language/v1` | `cal.definition.ubiquitous-language` | `language_id` | `authority/artifact-types/ubiquitous-language/v1/artifact.json` |
| `identity` | `cal.artifact-type.capability-instance/v1` | `cal.definition.capability-instance` | `capability_instance_id` | `authority/artifact-types/capability-instance/v1/artifact.json` |
| `relationships` | `cal.artifact-type.coordination-context/v1` | `cal.definition.coordination-context` | `coordination_context_id` | `authority/artifact-types/coordination-context/v1/artifact.json` |
| `relationships` | `cal.artifact-type.context-map/v1` | `cal.definition.context-map` | `context_map_id` | `authority/artifact-types/context-map/v1/artifact.json` |
| `migration-evidence` | `cal.artifact-type.context-migration-manifest/v1` | `cal.definition.context-migration-manifest` | `migration_manifest_id` | `authority/artifact-types/context-migration-manifest/v1/artifact.json` |
| `migration-evidence` | `cal.artifact-type.context-lineage-record/v1` | `cal.definition.context-lineage-record` | `lineage_record_id` | `authority/artifact-types/context-lineage-record/v1/artifact.json` |

## Cross-type invariants

- `CTX01-X01` — Every package has a unique artifact-type ref, semantic kind, Definition binding, instance identity field, and direct non-duplicating path.
- `CTX01-X02` — Bounded Context and Coordination Context schemas do not share identity or model-ownership fields.
- `CTX01-X03` — Context Map owns directional dependency relations; endpoint contexts do not gain redundant canonical classification axes.
- `CTX01-X04` — Capability Instance preserves separate parent and instance identities and authority claims.
- `CTX01-X05` — Migration Manifest is future intent without execution authority; Lineage Record is historical identity evidence without inferred equivalence or admission.

## Promotion boundary

one exact decision must bind all seven immutable candidates, schemas, generated projections, receipts, shared mechanics, and aggregate evidence

Candidate construction, validation, or pack membership does not admit any artifact type.

## Claim ceiling

This pack binds seven CTX01 artifact-type candidates and evidence only. It does not register or admit them, bind operational owners, create contexts or languages, select a Context Map pattern, authorize migration, publish, deploy, or establish a stable release.
