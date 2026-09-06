<!-- GENERATED FILE: edit prototype-artifacts.schema.json and run ../build.py. -->

# Prototype Artifact Machine Contracts

> Human projection of the P0 machine schema.

- Schema: `https://cyberalchemy.local/schemas/craft-first-capability/prototype-artifacts/v1`

| Contract | Required fields | Closed |
| --- | --- | --- |
| `prototypeDefinition` | `definition_id`, `version`, `term`, `aliases`, `classification`, `lifecycle_posture`, `authority_effect`, `applicability`, `exclusions`, `voices`, `boundaries`, `source_refs`, `four_facets` | `True` |
| `prototypeDefinitionRegistry` | `schema_version`, `registry_id`, `artifact_type`, `prototype_epoch`, `status`, `canonicality`, `authority_effect`, `semantic_contributor_route`, `source_bindings`, `definitions`, `source_direction`, `claim_ceiling` | `True` |
| `prototypePackage` | `schema_version`, `prototype_id`, `artifact_type`, `prototype_epoch`, `stage_id`, `lane`, `state`, `authority_effect`, `chain_binding`, `selected_dependencies`, `artifacts`, `stage_transition`, `source_direction`, `claim_ceiling` | `True` |

## Direction

Machine JSON is canonical inside this prototype epoch. Markdown views are generated only and cannot redefine the records.
