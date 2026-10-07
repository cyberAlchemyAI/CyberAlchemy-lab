<!-- GENERATED FILE: canonical data is artifact.json. -->

# Challenge Event Artifact Type v1

- Type: `cal.artifact-type.challenge-event/v1`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic Definition: `cal.definition.challenge-event@1.0.0-candidate.1`

## Distinct validation purpose

A Challenge Event is an immutable attributable record that an eligible challenger contested one exact subject revision under one exact Challenge Contract with stated grounds and evidence. It is neither the challenged subject, a contradiction finding, resolution, Decision, nor automatic lifecycle transition.

## Closed relation roles

| Relation Kind | Direction | Counterpart kinds |
| --- | --- | --- |
| `relation.challenges` | `source` | `agent-action, agent-assignment, agent-capability, agent-instance, agent-profile, agent-reflection, agent-session, artifact-type, artifact-type-request, authority-claim, bounded-context, canonical-package-manifest, capability-instance, capability-realization-binding, challenge-contract, challenge-event, classification-assignment, classification-scheme, classification-value, communication-preference, constitution, context, context-lineage-record, context-map, context-migration-manifest, context-profile, context-request, context-view, contract, decision, decision-scope, definition, delegation, drift-assessment, effect, evaluation, evidence-set, experiment-design, experiment-run, failure-assessment, failure-control-binding, failure-mode, failure-occurrence, feedback-record, finding, generated-output, goal, governance-event-history, governed-model, hypothesis, identity-claim, implementation, improvement-signal, improvement-target, incident, intent-resolution, lesson-application, lesson-outcome-assessment, measurement-method, measurement-result, method, model-instance-binding, observation, ontology, ontology-cut, ontology-edge, ontology-manifest, ontology-node, ontology-package, ontology-view, operational-lesson, operational-observation, person, person-reference, policy, preference-application-assessment, principal, principal-reference, product, product-capability, product-thesis, project, project-state, relation-kind, research-inquiry, research-run, responsibility, review, role, role-assignment, schema, semantic-event-history, source, team, team-membership, tool, typed-relation, ubiquitous-language, work, work-outcome-assessment` |
| `relation.challenges` | `target` | `challenge-event` |
| `relation.declares-effect-on` | `target` | `decision` |
| `relation.evidence-bears-on` | `target` | `evidence-set, feedback-record, finding, measurement-result, observation, operational-observation` |
| `relation.governed-by` | `source` | `challenge-contract` |
| `relation.produces` | `target` | `agent-action` |
| `relation.successor-of` | `source` | `challenge-event` |
| `relation.successor-of` | `target` | `challenge-event` |

## Non-collapse boundaries

- `challenge-event` remains distinct from `decision`.
- `challenge-event` remains distinct from `finding`.

## Orthogonality rules

- **CHALLENGE-EVENT-IDENTITY**: A Challenge Event instance retains its own identity and cannot be replaced by its owner, evidence, scope, Definition, relation, or neighbor.
- **CHALLENGE-EVENT-RELATIONS**: Every connection requires one exact admitted Relation Kind and separate Typed Relation identity.
- **CHALLENGE-EVENT-AUTHORITY**: Schema validity, evidence, relation membership, and candidate status create no admission, authority, truth, execution, or external effect.
- **CHALLENGE-EVENT-NON-COLLAPSE**: Challenge Event remains distinct from decision, finding.

## Typed residue

- `CHALLENGE-EVENT-R1` (role:artifact-type-owner): Owner admission for exact Challenge Event/v1 bytes. Consequence: Carrier remains candidate-only.
- `CHALLENGE-EVENT-R2` (role:migration-consumer-owner): Separate Relation Kind, instance, Typed Relation, consumer, and runtime decisions. Consequence: No operational state changes.

## Claim ceiling

This candidate Challenge Event/v1 carrier binds one admitted Definition and the candidate definition-complete relation surface. PASS admits nothing.
