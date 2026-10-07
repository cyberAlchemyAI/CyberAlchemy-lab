<!-- GENERATED FILE: canonical data is artifact.json. -->

# Artifact Type Artifact Type successor

- Type: `cal.artifact-type.artifact-type/v3`
- Version: `3.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Admitted predecessor: `cal.artifact-type.artifact-type/v2`
- Definition: `cal.definition.artifact-type@1.0.0-candidate.1`

## Distinct validation purpose

Defines the complete closed contract for one Artifact Type descriptor, including semantic Definition bindings, instance schema, generated projection, validation, ownership, lifecycle posture, relation surface, typed residue, predecessor lineage, and claim ceiling.

## Relation surface

- `source` `relation.carries-definition` with `definition`
- `target` `relation.declares-effect-on` with `decision`
- `source` `relation.governed-by` with `constitution`
- `source` `relation.originates-from` with `source`
- `source` `relation.successor-of` with `artifact-type`
- `target` `relation.successor-of` with `artifact-type`

## Orthogonality rules

- **AT3-TYPE-INSTANCE**: Artifact Type contract and artifact instance retain separate identities and lifecycle states.
- **AT3-DEFINITION-SCHEMA**: Semantic Definition, representation schema, validator, generated projection, admission decision, and activation remain separate governed artifacts and acts.
- **AT3-RELATION-SURFACE**: Reference-shaped fields do not create relations; only admitted Relation Kinds and exact Typed Relation instances connect endpoints.
- **AT3-SELF-APPLICATION**: Artifact Type/v3 may describe its own exact contract without inferring its admission, authority, or validity from self-description.

## Typed residue

- `AT3-R1` (role:artifact-type-owner): Artifact Type owner admission for this exact v3 successor. Consequence: v3 remains candidate-only and v2 remains admitted-current.
- `AT3-R2` (role:migration-consumer-owner): Successor registry refresh and explicit consumer adoption after admission. Consequence: No existing carrier or consumer is silently rebound to v3.

## Claim ceiling

This candidate defines Artifact Type/v3 and validates its bounded self-description. PASS proves the exact schema, predecessor, Definition binding, relation surface, hostile cases, and projections; it does not admit v3, transition v2, admit another Artifact Type or instance, or activate a consumer or runtime.
