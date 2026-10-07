<!-- GENERATED FILE: canonical data is artifact.json. -->

# Policy Artifact Type v1

- Type: `cal.artifact-type.policy/v2`
- Version: `2.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.policy@1.0.0-candidate.1`

## Distinct validation purpose

A Policy is a versioned normative rule set issued within an exact authority scope that constrains or requires decisions, Actions, lifecycle transitions, evidence, or handling. A Policy does not execute itself, grant authority beyond its issuer, prove compliance, or replace a Decision.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.challenges` | `target` | `challenge-event` |
| `relation.governed-by` | `target` | `admission-transaction, agent-action, agent-instance, agent-profile, agent-session, authority-boundary, challenge-contract, classification-assignment, communication-preference, context, decision-bundle, decision-checkpoint, failure-assessment, failure-control-binding, failure-mode, failure-occurrence, feedback-record, incident, ontology, ontology-edge, ontology-node, operational-lesson, user-decision-preference, workflow-decision-profile` |
| `relation.successor-of` | `source` | `policy` |
| `relation.successor-of` | `target` | `policy` |
| `relation.violates` | `target` | `failure-occurrence` |

## Non-collapse boundaries

- `policy` remains distinct from `constitution`.
- `policy` remains distinct from `contract`.

## Orthogonality rules

- **POLICY-IDENTITY**: A Policy instance retains its own identity and cannot be replaced by its owner, evidence, scope, schema, Definition, relation, or neighboring carrier.
- **POLICY-RELATIONS**: Only the exact declared Relation Kinds, direction, and counterpart kinds are eligible; every Typed Relation remains a separate artifact.
- **POLICY-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status cannot create admission, authority, truth, execution, or external effect.
- **POLICY-NON-COLLAPSE**: Policy remains distinct from constitution, contract.

## Typed residue

- `POLICY-V2-R1` (role:artifact-type-owner): Owner admission for this exact endpoint-role successor. Consequence: The admitted v1 carrier remains current.

## Claim ceiling

This candidate Policy/v2 successor widens only the exact closed relation-role surface required by the governance transaction extension. It admits nothing.
