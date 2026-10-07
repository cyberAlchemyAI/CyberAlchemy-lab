<!-- GENERATED FILE: canonical data is artifact.json. -->

# Evidence Set Artifact Type v1

- Type: `cal.artifact-type.evidence-set/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.evidence-set@1.0.0-candidate.1`

## Distinct validation purpose

It is the organized body of evidence for a question, including what pushes against the answer and where the evidence is weak.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.derives-from` | `source` | `experiment-run, research-run` |
| `relation.derives-from` | `target` | `finding` |
| `relation.evidence-bears-on` | `source` | `authority-claim, finding, hypothesis, identity-claim` |
| `relation.member-of` | `source` | `project` |

## Non-collapse boundaries

- `evidence-set` remains distinct from `finding`.
- `evidence-set` remains distinct from `observation`.

## Orthogonality rules

- **EVIDENCE-SET-IDENTITY**: A Evidence Set instance retains its own identity and cannot be replaced by its owner, evidence, scope, schema, Definition, relation, or neighboring carrier.
- **EVIDENCE-SET-RELATIONS**: Only the exact declared Relation Kinds, direction, and counterpart kinds are eligible; every Typed Relation remains a separate artifact.
- **EVIDENCE-SET-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status cannot create admission, authority, truth, execution, or external effect.
- **EVIDENCE-SET-NON-COLLAPSE**: Evidence Set remains distinct from finding, observation.

## Typed residue

- `EVIDENCE-SET-R1` (role:artifact-type-owner): Artifact Type owner admission for this exact Evidence Set/v1 candidate. Consequence: The carrier remains candidate-only.
- `EVIDENCE-SET-R2` (role:migration-consumer-owner): A separately admitted instance, admitted Relation Kinds and Typed Relations, and a consumer activation decision. Consequence: No relation, instance, consumer, or runtime becomes active.

## Claim ceiling

This is a candidate Evidence Set/v1 carrier bound to one admitted Definition and the closed candidate relation-role surface. PASS proves only the exact schema, bindings, fixtures, hostile cases, and projections; it does not admit the type, instance, Relation Kind, Typed Relation, consumer, or runtime.
