<!-- GENERATED FILE: canonical data is artifact.json. -->

# Context Lineage Record Artifact Type successor

- Type: `cal.artifact-type.context-lineage-record/v2`
- Version: `2.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Admitted predecessor: `cal.artifact-type.context-lineage-record/v1`
- Definition: `cal.definition.context-lineage-record@1.0.0-candidate.1`

## Distinct validation purpose

Proves immutable, typed predecessor/successor identity history while explicitly denying inferred equivalence, admission, aliases, and deletion authority.

## Relation surface

- No Relation Kind in the closed candidate relation model currently names this carrier as an endpoint.

## Orthogonality rules

- **CONTEXT-LINEAGE-RECORD-SUCCESSION**: The successor and admitted predecessor remain exact separate contracts; admission may transition lifecycle but never rewrites predecessor bytes.
- **CONTEXT-LINEAGE-RECORD-SEMANTICS**: The carrier binds one exact current admitted Definition without redefining it.
- **CONTEXT-LINEAGE-RECORD-RELATIONS**: Only the declared closed relation roles are eligible and every Typed Relation remains a separate artifact.
- **CONTEXT-LINEAGE-RECORD-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, execution, migration, deletion, or runtime effect.

## Typed residue

- `CONTEXT-LINEAGE-RECORD-SUCCESSOR-R1` (role:artifact-type-owner): Artifact Type owner admission for this exact successor. Consequence: The successor remains candidate-only and the predecessor remains admitted-current.
- `CONTEXT-LINEAGE-RECORD-SUCCESSOR-R2` (role:migration-consumer-owner): A separately admitted instance and consumer activation decision. Consequence: No instance, relation, migration, deletion, consumer, or runtime effect occurs.

## Claim ceiling

This is the candidate immutable Context Lineage Record successor. PASS proves only its exact predecessor, Definition, schema, fixture, relation surface, hostile cases, and projections; it does not admit or activate the successor, transition the predecessor, create an instance, or authorize migration, deletion, or runtime effects.
