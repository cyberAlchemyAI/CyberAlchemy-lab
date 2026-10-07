<!-- GENERATED FILE: canonical data is artifact.json. -->

# Bounded Context Artifact Type successor

- Type: `cal.artifact-type.bounded-context/v3`
- Version: `3.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Admitted predecessor: `cal.artifact-type.bounded-context/v2`
- Definition: `cal.definition.bounded-context@2.0.0-candidate.1`

## Distinct validation purpose

Proves explicit versioned semantic-boundary identity, model, language, owner, scope, and contracts while rejecting canonical Context Map backreferences.

## Relation surface

- `target` `relation.frames` with `context`
- `source` `relation.successor-of` with `bounded-context`
- `target` `relation.successor-of` with `bounded-context`

## Orthogonality rules

- **BOUNDED-CONTEXT-SUCCESSION**: The successor and admitted predecessor remain exact separate contracts; admission may transition lifecycle but never rewrites predecessor bytes.
- **BOUNDED-CONTEXT-SEMANTICS**: The carrier binds one exact current admitted Definition without redefining it.
- **BOUNDED-CONTEXT-RELATIONS**: Only the declared closed relation roles are eligible and every Typed Relation remains a separate artifact.
- **BOUNDED-CONTEXT-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, execution, migration, deletion, or runtime effect.

## Typed residue

- `BOUNDED-CONTEXT-SUCCESSOR-R1` (role:artifact-type-owner): Artifact Type owner admission for this exact successor. Consequence: The successor remains candidate-only and the predecessor remains admitted-current.
- `BOUNDED-CONTEXT-SUCCESSOR-R2` (role:migration-consumer-owner): A separately admitted instance and consumer activation decision. Consequence: No instance, relation, migration, deletion, consumer, or runtime effect occurs.

## Claim ceiling

This is the candidate immutable Bounded Context successor. PASS proves only its exact predecessor, Definition, schema, fixture, relation surface, hostile cases, and projections; it does not admit or activate the successor, transition the predecessor, create an instance, or authorize migration, deletion, or runtime effects.
