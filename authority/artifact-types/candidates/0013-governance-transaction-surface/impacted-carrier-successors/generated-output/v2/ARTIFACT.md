<!-- GENERATED FILE: canonical data is artifact.json. -->

# Generated Output Artifact Type v1

- Type: `cal.artifact-type.generated-output/v2`
- Version: `2.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.generated-output@1.0.0-candidate.1`

## Distinct validation purpose

A Generated Output is a reproducible product derived from exact canonical inputs by an exact governed generator version and bound to lineage and parity checks. It is not a second semantic authority and is canonical only when an explicit Artifact Type contract says so.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.affects` | `target` | `failure-occurrence, incident` |
| `relation.challenges` | `target` | `challenge-event` |
| `relation.derives-from` | `source` | `source` |
| `relation.materializes-consequence` | `target` | `admission-transaction` |
| `relation.produces` | `target` | `agent-action` |
| `relation.successor-of` | `source` | `generated-output` |
| `relation.successor-of` | `target` | `generated-output` |

## Non-collapse boundaries

- `generated-output` remains distinct from `source`.
- `generated-output` remains distinct from `evidence-set`.

## Orthogonality rules

- **GENERATED-OUTPUT-IDENTITY**: A Generated Output instance retains its own identity and cannot be replaced by its owner, evidence, scope, schema, Definition, relation, or neighboring carrier.
- **GENERATED-OUTPUT-RELATIONS**: Only the exact declared Relation Kinds, direction, and counterpart kinds are eligible; every Typed Relation remains a separate artifact.
- **GENERATED-OUTPUT-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status cannot create admission, authority, truth, execution, or external effect.
- **GENERATED-OUTPUT-NON-COLLAPSE**: Generated Output remains distinct from source, evidence-set.

## Typed residue

- `GENERATED-OUTPUT-V2-R1` (role:artifact-type-owner): Owner admission for this exact endpoint-role successor. Consequence: The admitted v1 carrier remains current.

## Claim ceiling

This candidate Generated Output/v2 successor widens only the exact closed relation-role surface required by the governance transaction extension. It admits nothing.
