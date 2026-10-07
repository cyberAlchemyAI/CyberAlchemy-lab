<!-- GENERATED FILE: canonical data is artifact.json. -->

# Definition Artifact Type successor

- Type: `cal.artifact-type.definition/v2`
- Version: `2.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Admitted predecessor: `cal.artifact-type.definition/v1`
- Definition: `cal.definition.definition@1.0.0-candidate.1`

## Distinct validation purpose

Carries one versioned semantic Definition with three synchronized voices, explicit scope, boundaries, provenance, consumers, drift route, evidence, residue, and Typed Relations restricted to the closed Relation Kind model.

## Relation surface

- `target` `relation.carries-definition` with `artifact-type`
- `target` `relation.declares-effect-on` with `decision`
- `source` `relation.governed-by` with `constitution`
- `source` `relation.originates-from` with `source`
- `source` `relation.successor-of` with `definition`
- `target` `relation.successor-of` with `definition`

## Orthogonality rules

- **DEF2-MEANING-CARRIER**: Definition meaning, Definition artifact instance, Definition Artifact Type, schema, source, and admission decision remain separate identities.
- **DEF2-VOICE-SYNC**: Scientific, plain-language, and domain-context voices express one meaning and cannot create independent authority axes.
- **DEF2-TYPED-RELATIONS**: Every embedded relation reference resolves to one of the 23 closed candidate Relation Kinds; embedding a reference does not create a Typed Relation instance.
- **DEF2-AUTHORITY**: Schema validity, source provenance, evidence, or candidate status cannot imply admission, truth, implementation, activation, or external effect.

## Typed residue

- `DEF2-R1` (role:artifact-type-owner): Artifact Type owner admission for this exact Definition/v2 successor. Consequence: Definition/v2 remains candidate-only and Definition/v1 remains admitted-current.
- `DEF2-R2` (role:definition-owner): Migration decisions for existing Definition/v1 instances and consumer adoption. Consequence: Existing Definitions remain governed by their current exact contracts until separately migrated.

## Claim ceiling

This candidate defines Definition/v2 with a closed 23-kind relation vocabulary. PASS proves the exact predecessor, schema, Definition binding, fixtures, and projections; it does not admit v2, transition v1, migrate any Definition, admit a Typed Relation, or activate a consumer or runtime.
