<!-- GENERATED FILE: canonical data is artifact.json. -->

# Capability Instance Artifact Type successor

- Type: `cal.artifact-type.capability-instance/v2`
- Version: `2.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Admitted predecessor: `cal.artifact-type.capability-instance/v1`
- Definition: `cal.definition.capability-instance@1.0.0-candidate.1`

## Distinct validation purpose

Proves an owner-local realization of one exact Product Capability while preserving parent/instance authority, contract, construction, conformance, recursion, and handoff separation.

## Relation surface

- `source` `relation.conforms-to` with `contract, governed-model`
- `source` `relation.inherits-contract` with `contract`
- `source` `relation.instance-of` with `governed-model, product-capability`
- `source` `relation.successor-of` with `capability-instance`
- `target` `relation.successor-of` with `capability-instance`

## Orthogonality rules

- **CAPABILITY-INSTANCE-SUCCESSION**: The successor and admitted predecessor remain exact separate contracts; admission may transition lifecycle but never rewrites predecessor bytes.
- **CAPABILITY-INSTANCE-SEMANTICS**: The carrier binds one exact current admitted Definition without redefining it.
- **CAPABILITY-INSTANCE-RELATIONS**: Only the declared closed relation roles are eligible and every Typed Relation remains a separate artifact.
- **CAPABILITY-INSTANCE-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, execution, migration, deletion, or runtime effect.

## Typed residue

- `CAPABILITY-INSTANCE-SUCCESSOR-R1` (role:artifact-type-owner): Artifact Type owner admission for this exact successor. Consequence: The successor remains candidate-only and the predecessor remains admitted-current.
- `CAPABILITY-INSTANCE-SUCCESSOR-R2` (role:migration-consumer-owner): A separately admitted instance and consumer activation decision. Consequence: No instance, relation, migration, deletion, consumer, or runtime effect occurs.

## Claim ceiling

This is the candidate immutable Capability Instance successor. PASS proves only its exact predecessor, Definition, schema, fixture, relation surface, hostile cases, and projections; it does not admit or activate the successor, transition the predecessor, create an instance, or authorize migration, deletion, or runtime effects.
