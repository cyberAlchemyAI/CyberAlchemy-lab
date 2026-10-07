<!-- GENERATED FILE: canonical data is artifact.json. -->

# Policy Artifact Type v1

- Type: `cal.artifact-type.policy/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.policy@1.0.0-candidate.1`

## Distinct validation purpose

A Policy is a versioned normative rule set issued within an exact authority scope that constrains or requires decisions, Actions, lifecycle transitions, evidence, or handling. A Policy does not execute itself, grant authority beyond its issuer, prove compliance, or replace a Decision.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.governed-by` | `target` | `context, ontology` |
| `relation.successor-of` | `source` | `policy` |
| `relation.successor-of` | `target` | `policy` |

## Non-collapse boundaries

- `policy` remains distinct from `constitution`.
- `policy` remains distinct from `contract`.

## Orthogonality rules

- **POLICY-IDENTITY**: A Policy instance retains its own identity and cannot be replaced by its owner, evidence, scope, schema, Definition, relation, or neighboring carrier.
- **POLICY-RELATIONS**: Only the exact declared Relation Kinds, direction, and counterpart kinds are eligible; every Typed Relation remains a separate artifact.
- **POLICY-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status cannot create admission, authority, truth, execution, or external effect.
- **POLICY-NON-COLLAPSE**: Policy remains distinct from constitution, contract.

## Typed residue

- `POLICY-R1` (role:artifact-type-owner): Artifact Type owner admission for this exact Policy/v1 candidate. Consequence: The carrier remains candidate-only.
- `POLICY-R2` (role:migration-consumer-owner): A separately admitted instance, admitted Relation Kinds and Typed Relations, and a consumer activation decision. Consequence: No relation, instance, consumer, or runtime becomes active.

## Claim ceiling

This is a candidate Policy/v1 carrier bound to one admitted Definition and the closed candidate relation-role surface. PASS proves only the exact schema, bindings, fixtures, hostile cases, and projections; it does not admit the type, instance, Relation Kind, Typed Relation, consumer, or runtime.
