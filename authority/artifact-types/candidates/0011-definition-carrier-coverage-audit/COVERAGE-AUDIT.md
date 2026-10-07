<!-- GENERATED FILE: canonical data is audit.json. -->

# Integrated 60 Definition carrier coverage audit

- Integrated Definitions: `60`
- Carrier backed: `20`
- Carrier required and missing: `34`
- No standalone carrier: `6`
- Projected carrier backed after actions: `54`
- Projected Decision 0069 admission set: `93`
- Authority effect: `none`

## Complete coverage matrix

| Definition | Family | Posture | Artifact Type or realization |
| --- | --- | --- | --- |
| `cal.definition.actor@1.0.0-candidate.1` | `actor` | `no-standalone-carrier` | Represent each concrete participant through its governed carrier, then classify the exact revision through Classification Scheme, Classification Value, and Classification Assignment. |
| `cal.definition.agent@1.0.0-candidate.1` | `actor` | `no-standalone-carrier` | Represent concrete operation through Agent Instance inside Agent Session, then classify the exact instance through the governed Agent actor-kind Scheme and Assignment. |
| `cal.definition.principal@1.0.0-candidate.1` | `actor` | `carrier-required-missing` | `cal.artifact-type.principal/v1` |
| `cal.definition.agent-profile@1.0.0-candidate.1` | `actor` | `carrier-required-missing` | `cal.artifact-type.agent-profile/v1` |
| `cal.definition.agent-capability@1.0.0-candidate.1` | `actor` | `carrier-required-missing` | `cal.artifact-type.agent-capability/v1` |
| `cal.definition.agent-instance@1.0.0-candidate.1` | `actor` | `carrier-required-missing` | `cal.artifact-type.agent-instance/v1` |
| `cal.definition.agent-session@1.0.0-candidate.1` | `actor` | `carrier-required-missing` | `cal.artifact-type.agent-session/v1` |
| `cal.definition.project-state@1.0.0-candidate.1` | `actor` | `carrier-required-missing` | `cal.artifact-type.project-state/v1` |
| `cal.definition.session-memory@1.0.0-candidate.1` | `actor` | `no-standalone-carrier` | Closed Session Memory schema embedded in Agent Session runtime; persistence is forbidden and no durable Artifact Type instance is permitted. |
| `cal.definition.ontology-view@1.0.0-candidate.1` | `actor` | `carrier-backed` | `cal.artifact-type.ontology-view/v1` |
| `cal.definition.agent-action@1.0.0-candidate.1` | `actor` | `carrier-required-missing` | `cal.artifact-type.agent-action/v1` |
| `cal.definition.agent-assignment@1.0.0-candidate.1` | `actor` | `carrier-required-missing` | `cal.artifact-type.agent-assignment/v1` |
| `cal.definition.delegation@1.0.0-candidate.1` | `actor` | `carrier-required-missing` | `cal.artifact-type.delegation/v1` |
| `cal.definition.agent-reflection@1.0.0-candidate.1` | `learning` | `carrier-required-missing` | `cal.artifact-type.agent-reflection/v1` |
| `cal.definition.operational-lesson@1.0.0-candidate.1` | `learning` | `carrier-required-missing` | `cal.artifact-type.operational-lesson/v1` |
| `cal.definition.lesson-application@1.0.0-candidate.1` | `learning` | `carrier-required-missing` | `cal.artifact-type.lesson-application/v1` |
| `cal.definition.lesson-outcome-assessment@1.0.0-candidate.1` | `learning` | `carrier-required-missing` | `cal.artifact-type.lesson-outcome-assessment/v1` |
| `cal.definition.improvement-target@1.0.0-candidate.1` | `learning` | `carrier-required-missing` | `cal.artifact-type.improvement-target/v1` |
| `cal.definition.operational-learning-cycle@1.0.0-candidate.1` | `learning` | `no-standalone-carrier` | Represent the selected method through Governed Model or Workflow plus its concrete Lesson, Application, Assessment, and Improvement artifacts. |
| `cal.definition.classification@1.0.0-candidate.1` | `classification` | `no-standalone-carrier` | Classification Scheme defines the contract; Classification Assignment records the governed result; Classification Value supplies allowed answers. |
| `cal.definition.classification-scheme@1.0.0-candidate.1` | `classification` | `carrier-required-missing` | `cal.artifact-type.classification-scheme/v1` |
| `cal.definition.classification-value@1.0.0-candidate.1` | `classification` | `carrier-required-missing` | `cal.artifact-type.classification-value/v1` |
| `cal.definition.classification-assignment@1.0.0-candidate.1` | `classification` | `carrier-required-missing` | `cal.artifact-type.classification-assignment/v1` |
| `cal.definition.failure@1.0.0-candidate.1` | `failure` | `no-standalone-carrier` | Failure Mode defines the possible boundary violation; Failure Occurrence records evidence of an episode; Failure Assessment evaluates it. |
| `cal.definition.failure-mode@1.0.0-candidate.1` | `failure` | `carrier-required-missing` | `cal.artifact-type.failure-mode/v1` |
| `cal.definition.failure-occurrence@1.0.0-candidate.1` | `failure` | `carrier-required-missing` | `cal.artifact-type.failure-occurrence/v1` |
| `cal.definition.failure-assessment@1.0.0-candidate.1` | `failure` | `carrier-required-missing` | `cal.artifact-type.failure-assessment/v1` |
| `cal.definition.failure-control-binding@1.0.0-candidate.1` | `failure` | `carrier-required-missing` | `cal.artifact-type.failure-control-binding/v1` |
| `cal.definition.incident@1.0.0-candidate.1` | `failure` | `carrier-required-missing` | `cal.artifact-type.incident/v1` |
| `cal.definition.intent-resolution@1.0.0-candidate.1` | `integrated` | `carrier-required-missing` | `cal.artifact-type.intent-resolution/v1` |
| `cal.definition.implementation@1.0.0-candidate.1` | `integrated` | `carrier-backed` | `cal.artifact-type.implementation/v1` |
| `cal.definition.relation-kind@1.0.0-candidate.1` | `interaction` | `carrier-backed` | `cal.artifact-type.relation-kind/v1`, `cal.artifact-type.relation-kind/v2` |
| `cal.definition.typed-relation@1.0.0-candidate.1` | `interaction` | `carrier-backed` | `cal.artifact-type.typed-relation/v1`, `cal.artifact-type.typed-relation/v2` |
| `cal.definition.ontology-node@1.0.0-candidate.1` | `interaction` | `carrier-backed` | `cal.artifact-type.ontology-node/v1`, `cal.artifact-type.ontology-node/v2` |
| `cal.definition.ontology-edge@1.0.0-candidate.1` | `interaction` | `carrier-backed` | `cal.artifact-type.ontology-edge/v1` |
| `cal.definition.ontology-manifest@1.0.0-candidate.1` | `interaction` | `carrier-backed` | `cal.artifact-type.ontology-manifest/v1` |
| `cal.definition.ontology-cut@1.0.0-candidate.1` | `interaction` | `carrier-backed` | `cal.artifact-type.ontology-cut/v1` |
| `cal.definition.semantic-event-history@1.0.0-candidate.1` | `interaction` | `carrier-backed` | `cal.artifact-type.semantic-event-history/v1` |
| `cal.definition.governance-event-history@1.0.0-candidate.1` | `interaction` | `carrier-backed` | `cal.artifact-type.governance-event-history/v1` |
| `cal.definition.work@1.0.0-candidate.1` | `integrated` | `carrier-backed` | `cal.artifact-type.work/v1` |
| `cal.definition.tool@1.0.0-candidate.1` | `integrated` | `carrier-required-missing` | `cal.artifact-type.tool/v1` |
| `cal.definition.generated-output@1.0.0-candidate.1` | `integrated` | `carrier-backed` | `cal.artifact-type.artifact-type-registry/v2`, `cal.artifact-type.generated-output/v1`, `cal.artifact-type.ontology-package/v1` |
| `cal.definition.principal-reference@1.0.0-candidate.1` | `actor` | `carrier-required-missing` | `cal.artifact-type.principal-reference/v1` |
| `cal.definition.governed-model@1.0.0-candidate.1` | `integrated` | `carrier-backed` | `cal.artifact-type.governed-model/v1` |
| `cal.definition.policy@1.0.0-candidate.1` | `integrated` | `carrier-backed` | `cal.artifact-type.policy/v1` |
| `cal.definition.decision@1.0.0-candidate.1` | `integrated` | `carrier-backed` | `cal.artifact-type.decision/v1` |
| `cal.definition.contract@1.0.0-candidate.1` | `integrated` | `carrier-backed` | `cal.artifact-type.contract/v1` |
| `cal.definition.decision-scope@1.0.0-candidate.1` | `integrated` | `carrier-backed` | `cal.artifact-type.decision-scope/v1` |
| `cal.definition.effect@1.0.0-candidate.1` | `integrated` | `carrier-backed` | `cal.artifact-type.effect/v1` |
| `cal.definition.review@1.0.0-candidate.1` | `integrated` | `carrier-backed` | `cal.artifact-type.review/v1` |
| `cal.definition.source@1.0.0-candidate.1` | `integrated` | `carrier-backed` | `cal.artifact-type.source/v1` |
| `cal.definition.challenge-contract@1.0.0-candidate.1` | `interaction` | `carrier-required-missing` | `cal.artifact-type.challenge-contract/v1` |
| `cal.definition.challenge-event@1.0.0-candidate.1` | `interaction` | `carrier-required-missing` | `cal.artifact-type.challenge-event/v1` |
| `cal.definition.operational-observation@1.0.0-candidate.1` | `learning` | `carrier-required-missing` | `cal.artifact-type.operational-observation/v1` |
| `cal.definition.work-outcome-assessment@1.0.0-candidate.1` | `learning` | `carrier-required-missing` | `cal.artifact-type.work-outcome-assessment/v1` |
| `cal.definition.feedback-record@1.0.0-candidate.1` | `learning` | `carrier-required-missing` | `cal.artifact-type.feedback-record/v1` |
| `cal.definition.communication-preference@1.0.0-candidate.1` | `learning` | `carrier-required-missing` | `cal.artifact-type.communication-preference/v1` |
| `cal.definition.preference-application-assessment@1.0.0-candidate.1` | `learning` | `carrier-required-missing` | `cal.artifact-type.preference-application-assessment/v1` |
| `cal.definition.drift-assessment@1.0.0-candidate.1` | `learning` | `carrier-required-missing` | `cal.artifact-type.drift-assessment/v1` |
| `cal.definition.improvement-signal@1.0.0-candidate.1` | `learning` | `carrier-required-missing` | `cal.artifact-type.improvement-signal/v1` |

## 6 definitions without standalone carriers

### `cal.definition.actor@1.0.0-candidate.1`

Classification: `abstract-participation-class`

The admitted Definition explicitly says Actor is an abstract participation classification and does not require one universal Actor carrier.

Realization: Represent each concrete participant through its governed carrier, then classify the exact revision through Classification Scheme, Classification Value, and Classification Assignment.

### `cal.definition.agent@1.0.0-candidate.1`

Classification: `abstract-operational-actor-class`

The admitted Definition explicitly says Agent is an operational Actor classification and concrete operation requires Agent Instance plus Agent Session.

Realization: Represent concrete operation through Agent Instance inside Agent Session, then classify the exact instance through the governed Agent actor-kind Scheme and Assignment.

### `cal.definition.session-memory@1.0.0-candidate.1`

Classification: `ephemeral-runtime-value`

The Definition makes Session Memory ephemeral, owned by one Session, and expired at termination.

Realization: Closed Session Memory schema embedded in Agent Session runtime; persistence is forbidden and no durable Artifact Type instance is permitted.

### `cal.definition.operational-learning-cycle@1.0.0-candidate.1`

Classification: `governed-method`

The cycle is a method connecting record types rather than an independently versioned occurrence record.

Realization: Represent the selected method through Governed Model or Workflow plus its concrete Lesson, Application, Assessment, and Improvement artifacts.

### `cal.definition.classification@1.0.0-candidate.1`

Classification: `abstract-act-and-result`

A separate Classification record would duplicate the Assignment identity and result.

Realization: Classification Scheme defines the contract; Classification Assignment records the governed result; Classification Value supplies allowed answers.

### `cal.definition.failure@1.0.0-candidate.1`

Classification: `abstract-condition`

A separate Failure artifact would collapse the design-time mode, observed occurrence, and assessment axes.

Realization: Failure Mode defines the possible boundary violation; Failure Occurrence records evidence of an episode; Failure Assessment evaluates it.

## Decision 0069 impact

After owner approval and carrier materialization, replace the provisional 53-entry review with one definition-complete 93-entry Artifact Type admission review: six Step 7 additions plus 34 remaining Definition carriers, while preserving all pre-admission predecessors and exclusions.

## Claim ceiling

This audit classifies carrier coverage for the exact 60 admitted integrated Definitions against current candidate material. It does not materialize the 34 remaining carriers, amend Decision 0069, admit anything, create instances or relations, or activate a runtime.
