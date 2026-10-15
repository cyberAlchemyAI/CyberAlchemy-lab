# Integrated workflow transition contracts

Status: candidate design. Ten workflows, exact input/output schema bindings and independently declared workflow states. Actual principal assignments, implemented checks, relation instances and lifecycle mappings are required before execution.

## State and authority

Intent states express requested direction. Intent Resolution binds exact target subjects. Work goals retain their admitted shape. Coordination Context/v2 has one goal_ref. Product describes durable value and capabilities; Project bounds coordinated work. Workflow phase is separate from carrier lifecycle, commitment, admission and outcome satisfaction.

Machine Agents are ephemeral. Durable knowledge comes from exact Project State, Context View and Ontology View; short memory belongs to one session and is erased on closure. Lessons require evidenced application and outcome assessment.

Each transition requires authenticated assignment, bounded authority, original-byte input/output bindings, independently executed satisfaction evidence, exact ordered relation signatures and explicit failure disposition. Owner checkpoint and operation authority are evaluated separately.

## Workflows

### agent-context

| Transition | Satisfaction predicate | Selected exact signatures |
| --- | --- | --- |
| requested → context-ready | Assignment and Delegation resolve a current principal, represented scope and revocation status; Context and Ontology Views share the selected Project State cut. | Per-run closure required; no inferred connection |
| context-ready → session-ready | Session context is bounded, binds its source/head/configuration, and is rejected when stale; short memory starts empty and is erased on close or expiry. | Per-run closure required; no inferred connection |

### challenge-handling

| Transition | Satisfaction predicate | Selected exact signatures |
| --- | --- | --- |
| submitted → eligible | Challenge Event resolves the challenged claim and the exact Challenge Contract eligibility, owner and response route. | Per-run closure required; no inferred connection |
| eligible → responded | Response binds current authority, source evidence and outcome scope; a pending contest is not silently closed. | Per-run closure required; no inferred connection |
| responded → resolved | Resolution records the responsible owner outcome, remaining contests and any exact required Decision; no implied admission. | Per-run closure required; no inferred connection |

### engineering

| Transition | Satisfaction predicate | Selected exact signatures |
| --- | --- | --- |
| prepared → designed | Design output binds the exact resolved Intent, Work, implementation revision and acceptance obligations; declared dependencies resolve. | Per-run closure required; no inferred connection |
| designed → implemented | Implementation output binds original bytes, generator identity, source references and executed checks; proposal/admission status is separate. | Per-run closure required; no inferred connection |
| implemented → assessed | Work Outcome Assessment evaluates each declared satisfaction obligation with evidence and limitations; acceptance is independent of admission. | work-outcome-assessment — relation.evaluates → work |

### failure-assessment

| Transition | Satisfaction predicate | Selected exact signatures |
| --- | --- | --- |
| observed → classified | Occurrence evidence is immutable; Classification Assignment binds a selected classification rule and its version rather than inventing free text authority. | Per-run closure required; no inferred connection |
| classified → assessed | Failure Assessment distinguishes observed occurrence, hypothesized failure mode and causal confidence; scope and evidence are explicit. | Per-run closure required; no inferred connection |
| assessed → response-assessed | Failure Control Binding and assessment record actual control application and observed response; recommendations are not effective controls. | Per-run closure required; no inferred connection |

### intent-framing

| Transition | Satisfaction predicate | Selected exact signatures |
| --- | --- | --- |
| framed → resolved | Intent Resolution resolves every claimed subject to its exact revision and records unresolved subjects; no completion is inferred. | Per-run closure required; no inferred connection |
| resolved → prepared | Work references the resolved Intent and declared Goal; the Coordination Context has exactly one goal_ref. | Per-run closure required; no inferred connection |

### ontology-migration

| Transition | Satisfaction predicate | Selected exact signatures |
| --- | --- | --- |
| selected → mapped | Mapping binds node meaning, original admitted source references and exact existing relation signatures; no carrier/instance or concept/source collapse. | Per-run closure required; no inferred connection |
| mapped → candidate-validated | Candidate validation checks all node/edge identities, evidence lineage, selected policy and local/global scope; a local edge never extends global coupling. | Per-run closure required; no inferred connection |
| candidate-validated → selected-scope-assessed | Migration Manifest compares declared scope with actual selected records and preserves exclusions, byte evidence and recoverability; selection assessment is not complete migration. | Per-run closure required; no inferred connection |

### operational-learning

| Transition | Satisfaction predicate | Selected exact signatures |
| --- | --- | --- |
| observed → lesson-prepared | Lesson references actual observation and outcome evidence, describes applicability and limitations; a pattern is not an instruction grant. | Per-run closure required; no inferred connection |
| lesson-prepared → application-recorded | Lesson Application binds one lesson revision to actual selected Work/context and records why it applies; selection alone is not application. | lesson-application — relation.applies-lesson → operational-lesson |
| application-recorded → outcome-assessed | Lesson Outcome Assessment binds actual application results; Improvement Signal is a candidate proposal, never automatic memory or governance mutation. | lesson-application — relation.applies-lesson → operational-lesson; lesson-outcome-assessment — relation.evaluates → lesson-application |

### product-adoption-release

| Transition | Satisfaction predicate | Selected exact signatures |
| --- | --- | --- |
| scoped → candidate-assessed | Candidate assessment binds Product identity, capability realization, exact implementation revision and relevant acceptance results; Project scope remains distinct. | Per-run closure required; no inferred connection |
| candidate-assessed → pilot-assessed | Pilot assessment records actual human observations and limitations from a real run; automated fixtures cannot prove usefulness. | Per-run closure required; no inferred connection |
| pilot-assessed → release-reviewed | Release review binds exact capability adoption and operational evidence under actual owner authority; no stable release from candidate status alone. | Per-run closure required; no inferred connection |

### research

| Transition | Satisfaction predicate | Selected exact signatures |
| --- | --- | --- |
| prepared → designed | Experiment Design declares hypothesis, protocol, variables, controls, measurements, resource bounds and intended interpretation before execution. | experiment-design — relation.engages-inquiry → research-inquiry; experiment-design — relation.tests-hypothesis → hypothesis |
| designed → executed | Experiment Run and Measurement Results bind the design revision, real executor, actual inputs and observations; planned observations cannot become evidence. | experiment-design — relation.engages-inquiry → research-inquiry; experiment-design — relation.tests-hypothesis → hypothesis; experiment-run — relation.realizes → experiment-design |
| executed → evaluated | Finding and Evaluation retain uncertainty, negative results and evidence lineage; evaluation does not prove Product adoption. | experiment-design — relation.engages-inquiry → research-inquiry; experiment-design — relation.tests-hypothesis → hypothesis; experiment-run — relation.realizes → experiment-design; finding — relation.engages-inquiry → research-inquiry |

### review-admission

| Transition | Satisfaction predicate | Selected exact signatures |
| --- | --- | --- |
| prepared → review-ready | Review closure binds exact members, postimages, source cuts, validation evidence, principal roles and per-member effect scope. | Per-run closure required; no inferred connection |
| review-ready → owner-resolved | Checkpoint resolution preserves actual human member outcomes, including reject/revise/defer, against the unchanged exact bundle; no simulated owner outcome. | Per-run closure required; no inferred connection |
| owner-resolved → applied | Admission applies only members with current positive exact authority; compare-and-swap preconditions and transaction journal bind the poststate; uncertain effects require inspection. | Per-run closure required; no inferred connection |

## Extension and recovery gaps

Project/Product representation and Method carrier closure remain exact semantic members for R08. W02/W03 bind runtime actor, check, qualifier and domain lifecycle evidence. C14 handles new exact pairs or semantic questions; existing pairs never grant an edge or permission. Known invalid transitions are rejected before mutation. Uncertain effects are recorded as indeterminate and inspected before scoped reconciliation.

## Schema boundary

workflow-run.schema.json preserves original reference contracts through the exact vendored common.schema.json dependency. It adds a workflow discriminator with workflow-specific closed state domains and explicit independent status axes. It is a protocol record, not a newly admitted domain artifact. Transition-contracts.json carries semantic predicates requiring runtime checks; JSON shape validation alone cannot prove them.
