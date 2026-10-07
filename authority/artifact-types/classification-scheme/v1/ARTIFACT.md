<!-- GENERATED FILE: canonical data is artifact.json. -->

# Classification Scheme Artifact Type v1

- Type: `cal.artifact-type.classification-scheme/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.classification-scheme@1.0.0-candidate.1`

## Distinct validation purpose

A Classification Scheme is a versioned governed contract of axes, allowed values, definitions, cardinality, applicability, exclusions, assignment and evidence rules, hierarchy, mappings, compatibility, owner, and challenge route. A new Scheme version does not silently reinterpret or reclassify assignments made under an older version.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.challenges` | `target` | `challenge-event` |
| `relation.governed-by` | `target` | `classification-assignment` |
| `relation.member-of` | `target` | `classification-value` |
| `relation.successor-of` | `source` | `classification-scheme` |
| `relation.successor-of` | `target` | `classification-scheme` |

## Non-collapse boundaries

- `classification-scheme` remains distinct from `schema`.
- `classification-scheme` remains distinct from `classification-assignment`.

## Orthogonality rules

- **CLASSIFICATION-SCHEME-IDENTITY**: A Classification Scheme instance retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **CLASSIFICATION-SCHEME-RELATIONS**: Every connection requires one exact admitted Relation Kind and separate Typed Relation identity.
- **CLASSIFICATION-SCHEME-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **CLASSIFICATION-SCHEME-NON-COLLAPSE**: Classification Scheme remains distinct from schema, classification-assignment.

## Typed residue

- `CLASSIFICATION-SCHEME-R1` (role:artifact-type-owner): Owner admission for exact Classification Scheme/v1 bytes. Consequence: Carrier remains candidate-only.
- `CLASSIFICATION-SCHEME-R2` (role:migration-consumer-owner): Separate Relation Kind, instance, Typed Relation, consumer, and runtime decisions. Consequence: No operational state changes.

## Claim ceiling

This candidate Classification Scheme/v1 carrier binds one admitted Definition and the candidate definition-complete relation surface. PASS admits nothing.
