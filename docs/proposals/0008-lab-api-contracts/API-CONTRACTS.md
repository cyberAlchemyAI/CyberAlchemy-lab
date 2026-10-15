# API operations

Status: candidate local application contracts. Every operation receives the correlated [API call](schemas/api-call.schema.json) and an adapter-resolved [trusted context](schemas/trusted-call-context.schema.json); it returns an [API reply](schemas/api-reply.schema.json) or an eligible [transport error](schemas/transport-error.schema.json).

| Operation | Description | Effect | Idempotency key |
|---|---|---|---|
| [context.get](operations/context.get.json) | Deliver bounded Context and Ontology Views for one assignment | read-only | Must be null |
| [artifact.inspect](operations/artifact.inspect.json) | Inspect selected sections and independent status facets of one exact revision | read-only | Must be null |
| [artifact.query](operations/artifact.query.json) | Find eligible exact revisions and typed connections at a declared cut | read-only | Must be null |
| [session.open](operations/session.open.json) | Open one ephemeral machine Agent session for an exact assignment | ephemeral-session | Required |
| [session.close](operations/session.close.json) | Terminate a selected session and dispose of its short memory | ephemeral-session | Required |
| [change.prepare](operations/change.prepare.json) | Stage exact artifact effects in a candidate workspace | candidate-write | Required |
| [change.validate](operations/change.validate.json) | Validate a candidate proposal under exact contracts and required obligations | candidate-write | Required |
| [proposal.review](operations/proposal.review.json) | Assemble the exact package for the final owner checkpoint | candidate-write | Required |
| [checkpoint.resolve](operations/checkpoint.resolve.json) | Verify and record actual owner outcomes for exact reviewed members | candidate-write | Required |
| [admission.apply](operations/admission.apply.json) | Apply one exact authorized canonical artifact transaction | canonical-commit | Required |
| [action.evaluate](operations/action.evaluate.json) | Evaluate current authority for one bounded tool action | read-only | Must be null |
| [action.dispatch](operations/action.dispatch.json) | Run one currently permitted local tool action | local-action | Required |
| [action.reconcile](operations/action.reconcile.json) | Reconcile selected uncertain effects or verified recovery residue | recovery | Required |
| [workflow.transition](operations/workflow.transition.json) | Apply one permitted coordination transition with observed satisfaction | workflow-write | Required |
| [classification.prepare](operations/classification.prepare.json) | Prepare an axis-qualified Classification Assignment | candidate-write | Required |
| [failure.assess](operations/failure.assess.json) | Prepare evidenced failure assessment and response scope | candidate-write | Required |
| [challenge.submit](operations/challenge.submit.json) | Prepare an eligible challenge under its exact Challenge Contract | candidate-write | Required |
| [challenge.resolve](operations/challenge.resolve.json) | Prepare consequences of an actual challenge resolution Decision | candidate-write | Required |
| [lesson.select](operations/lesson.select.json) | Select applicable lessons for the current bounded assignment | read-only | Must be null |
| [lesson.apply](operations/lesson.apply.json) | Prepare a recorded application of an exact lesson revision | candidate-write | Required |
| [lesson.assess](operations/lesson.assess.json) | Prepare assessment of a recorded lesson application | candidate-write | Required |
| [ontology.project](operations/ontology.project.json) | Apply selected ontology representations with an independent cut | ontology-representation | Required |
| [projection.refresh](operations/projection.refresh.json) | Build and select a complete disposable SQLite generation | projection-write | Required |
| [files.materialize](operations/files.materialize.json) | Generate selected managed byte exports or pinned rendered files | managed-file-write | Required |
| [package.export](operations/package.export.json) | Export selected portable original content and complete dependencies | managed-file-write | Required |
| [package.import](operations/package.import.json) | Prepare selected source import/adaptation in a candidate workspace | candidate-write | Required |
| [installation.execute](operations/installation.execute.json) | Install/upgrade/rollback a selected local package under exact authority | local-install | Required |
| [lab.status](operations/lab.status.json) | Discover the selected source profile, cut and available implementation surface | read-only | Must be null |
| [catalog.get](operations/catalog.get.json) | Read current/historical artifact contracts and declared relation signatures | read-only | Must be null |
| [session.inspect](operations/session.inspect.json) | Read session metadata and unresolved action references | read-only | Must be null |
| [operation.inspect](operations/operation.inspect.json) | Read the scoped invocation/idempotency record after uncertainty | read-only | Must be null |
| [typed.extension.prepare](operations/typed.extension.prepare.json) | Prepare a declared typed connection extension for owner review | candidate-write | Required |
| [capability.adoption.prepare](operations/capability.adoption.prepare.json) | Prepare exact capability realization and owner-local adoption declarations | candidate-write | Required |
| [release.prepare](operations/release.prepare.json) | Prepare an exact candidate release for its final review | candidate-write | Required |

## context.get

Deliver bounded Context and Ontology Views for one assignment.

- Request: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/context-query.schema.json).
- Result: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/context-delivery.schema.json).
- Caller route: `bounded-reader` plus actual authority evaluation.
- Effects: `read-only`.
- Cut selectors: `/source_cut`.

### Preconditions

- Resolve assignment, Work and one-Goal Coordination Context.
- Verify included sources, exclusions, lesson applicability, privacy and budgets.

### Observed result

- Ready requires actual view bindings and enforced scope.
- Context grants no authority; blocked delivery may have no views.

[Invocation](examples/context.get/request.json) · [Domain request](examples/context.get/message.json) · [Result](examples/context.get/response.json) · [Error](examples/context.get/error-response.json). These are shape illustrations with placeholder authority and handler references.

Allowed application errors: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`.

## artifact.inspect

Inspect selected sections and independent status facets of one exact revision.

- Request: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/artifact-inspect-request.schema.json).
- Result: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/artifact-inspect-result.schema.json).
- Caller route: `bounded-reader` plus actual authority evaluation.
- Effects: `read-only`.
- Cut selectors: `/source_cut`.

### Preconditions

- Resolve exact artifact identity, revision, carrier and bytes.
- Authorize each selected section; excluded sections carry no body or bindings.

### Observed result

- Included sections are a subset of the request, with disclosed authorized omissions.
- Body/header/contract identities agree; effective admission is evidence-derived.

[Invocation](examples/artifact.inspect/request.json) · [Domain request](examples/artifact.inspect/message.json) · [Result](examples/artifact.inspect/response.json) · [Error](examples/artifact.inspect/error-response.json). These are shape illustrations with placeholder authority and handler references.

Allowed application errors: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`, `invalid-connection`, `noncollapse-failed`.

## artifact.query

Find eligible exact revisions and typed connections at a declared cut.

- Request: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/artifact-query.schema.json).
- Result: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/artifact-query-result.schema.json).
- Caller route: `bounded-reader` plus actual authority evaluation.
- Effects: `read-only`.
- Cut selectors: `/source_cut`.

### Preconditions

- Apply scope, carrier, identity, relation, depth, paging and byte limits.
- A projection must verify its generation and disclose its applied cut; stale use requires allow-stale.

### Observed result

- Return canonical or projected read basis and requested/applied cut and freshness.
- A cursor binds the actual cut, generation, selectors, caller and scope.

[Invocation](examples/artifact.query/request.json) · [Domain request](examples/artifact.query/message.json) · [Result](examples/artifact.query/response.json) · [Error](examples/artifact.query/error-response.json). These are shape illustrations with placeholder authority and handler references.

Allowed application errors: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`, `invalid-cursor`, `invalid-connection`, `noncollapse-failed`.

## session.open

Open one ephemeral machine Agent session for an exact assignment.

- Request: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/agent-session-open.schema.json).
- Result: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/agent-session-result.schema.json).
- Caller route: `assigned-agent-or-operator` plus actual authority evaluation.
- Effects: `ephemeral-session`.
- Cut selectors: `/source_cut`.

### Preconditions

- Verify profile/implementation/capabilities, authority envelope, assignment and delivered context.
- Verify context and authority expiration and effective budgets.

### Observed result

- Active creation returns a new session/instance and observed timestamps.
- Blocked creation returns no created identity; short memory is never durable.

[Invocation](examples/session.open/request.json) · [Domain request](examples/session.open/message.json) · [Result](examples/session.open/response.json) · [Error](examples/session.open/error-response.json). These are shape illustrations with placeholder authority and handler references.

Allowed application errors: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`, `conflict`, `idempotency-conflict`, `expired-authority`, `revoked-authority`, `gate-required`, `indeterminate`, `recovery-required`.

## session.close

Terminate a selected session and dispose of its short memory.

- Request: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/agent-session-close.schema.json).
- Result: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/agent-session-close-receipt.schema.json).
- Caller route: `assigned-agent-or-operator` plus actual authority evaluation.
- Effects: `ephemeral-session`.
- Cut selectors: Outer cut and exact referenced state/package/session bindings.

### Preconditions

- Verify current session binding and actual caller ownership or delegated termination authority.
- Identify unresolved actions; closing a session does not resolve their effects.

### Observed result

- Closed requires observed termination and memory disposal.
- Retain only eligible audit references and unresolved residue.

[Invocation](examples/session.close/request.json) · [Domain request](examples/session.close/message.json) · [Result](examples/session.close/response.json) · [Error](examples/session.close/error-response.json). These are shape illustrations with placeholder authority and handler references.

Allowed application errors: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `conflict`, `idempotency-conflict`, `expired-authority`, `revoked-authority`, `gate-required`, `indeterminate`, `recovery-required`.

## change.prepare

Stage exact artifact effects in a candidate workspace.

- Request: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/change-proposal.schema.json).
- Result: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/proposal-review.schema.json).
- Caller route: `assigned-agent-or-operator` plus actual authority evaluation.
- Effects: `candidate-write`.
- Cut selectors: `/base_cut`.

### Preconditions

- Verify workspace, current profile, exact targets/predecessors and complete schema closure.
- Verify typed connections or return an explicit gap; candidate staging grants no admission.

### Observed result

- Return exact proposal review bindings, examples and declared consequences.
- No canonical head or admission status changes.

[Invocation](examples/change.prepare/request.json) · [Domain request](examples/change.prepare/message.json) · [Result](examples/change.prepare/response.json) · [Error](examples/change.prepare/error-response.json). These are shape illustrations with placeholder authority and handler references.

Allowed application errors: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`, `conflict`, `idempotency-conflict`, `expired-authority`, `revoked-authority`, `gate-required`, `indeterminate`, `recovery-required`, `invalid-connection`, `noncollapse-failed`.

## change.validate

Validate a candidate proposal under exact contracts and required obligations.

- Request: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/change-proposal.schema.json).
- Result: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/validation-report.schema.json).
- Caller route: `assigned-agent-or-operator` plus actual authority evaluation.
- Effects: `candidate-write`.
- Cut selectors: `/base_cut`.

### Preconditions

- Pin validators, source cut and candidate closure.
- Select the checks required for this use; authoring checks cannot satisfy operational checks.

### Observed result

- Return attributable pass/fail/not-evaluable checks, unresolved references and claim ceiling.
- Persist only eligible candidate evidence under caller-authorized workspace scope.

[Invocation](examples/change.validate/request.json) · [Domain request](examples/change.validate/message.json) · [Result](examples/change.validate/response.json) · [Error](examples/change.validate/error-response.json). These are shape illustrations with placeholder authority and handler references.

Allowed application errors: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`, `conflict`, `idempotency-conflict`, `expired-authority`, `revoked-authority`, `gate-required`, `indeterminate`, `recovery-required`, `invalid-connection`, `noncollapse-failed`.

## proposal.review

Assemble the exact package for the final owner checkpoint.

- Request: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/proposal-review.schema.json).
- Result: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/review-package.schema.json).
- Caller route: `assigned-agent-or-operator` plus actual authority evaluation.
- Effects: `candidate-write`.
- Cut selectors: `/source_cut`.

### Preconditions

- Verify actual materialized targets, stable Decision cores, examples, validation and private/public review.
- Resolve the Workflow Decision Profile and all independently required owner roles.

### Observed result

- Return one complete review package with exact member bindings and invalidation conditions.
- It contains no fabricated authorization, pilot results or future unknown targets.

[Invocation](examples/proposal.review/request.json) · [Domain request](examples/proposal.review/message.json) · [Result](examples/proposal.review/response.json) · [Error](examples/proposal.review/error-response.json). These are shape illustrations with placeholder authority and handler references.

Allowed application errors: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`, `conflict`, `idempotency-conflict`, `expired-authority`, `revoked-authority`, `gate-required`, `indeterminate`, `recovery-required`.

## checkpoint.resolve

Verify and record actual owner outcomes for exact reviewed members.

- Request: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/checkpoint-resolution.schema.json).
- Result: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/validation-report.schema.json).
- Caller route: `accountable-owner` plus actual authority evaluation.
- Effects: `candidate-write`.
- Cut selectors: Outer cut and exact referenced state/package/session bindings.

### Preconditions

- Verify the actual authorization channel and provenance for each required member owner.
- Match exact package, core order, scope, target bytes and current cut; do not infer authorization from caller text.

### Observed result

- Return a validation report for the recorded resolution.
- All-required-authorized is true only when every required member approves its exact effect.

[Invocation](examples/checkpoint.resolve/request.json) · [Domain request](examples/checkpoint.resolve/message.json) · [Result](examples/checkpoint.resolve/response.json) · [Error](examples/checkpoint.resolve/error-response.json). These are shape illustrations with placeholder authority and handler references.

Allowed application errors: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `conflict`, `idempotency-conflict`, `expired-authority`, `revoked-authority`, `gate-required`, `indeterminate`, `recovery-required`.

## admission.apply

Apply one exact authorized canonical artifact transaction.

- Request: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/commit-request.schema.json).
- Result: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/commit-receipt.schema.json).
- Caller route: `authorized-application-adapter` plus actual authority evaluation.
- Effects: `canonical-commit`.
- Cut selectors: `/expected_cut`.

### Preconditions

- Verify proposal/package/resolution, owner authority, complete closure and expected current head.
- Serialize publication and bind local versus repository authority; zero activation and external effects.

### Observed result

- Commit exact immutable content/events and publish one canonical head or report uncertainty.
- Projection/file outcomes are separately reported and cannot undo a committed transaction.

[Invocation](examples/admission.apply/request.json) · [Domain request](examples/admission.apply/message.json) · [Result](examples/admission.apply/response.json) · [Error](examples/admission.apply/error-response.json). These are shape illustrations with placeholder authority and handler references.

Allowed application errors: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`, `conflict`, `idempotency-conflict`, `expired-authority`, `revoked-authority`, `gate-required`, `indeterminate`, `recovery-required`.

## action.evaluate

Evaluate current authority for one bounded tool action.

- Request: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/action-request.schema.json).
- Result: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/authority-evaluation.schema.json).
- Caller route: `assigned-agent-or-operator` plus actual authority evaluation.
- Effects: `read-only`.
- Cut selectors: `/source_cut`.

### Preconditions

- Resolve adapter/input contracts, assignment, scopes, gates, revocation and expiry.
- Bind actual authenticated caller; self-declared capability or role does not permit an action.

### Observed result

- Return permitted/denied/gate-required/indeterminate with exact check evidence.
- No dispatch or admission occurs.

[Invocation](examples/action.evaluate/request.json) · [Domain request](examples/action.evaluate/message.json) · [Result](examples/action.evaluate/response.json) · [Error](examples/action.evaluate/error-response.json). These are shape illustrations with placeholder authority and handler references.

Allowed application errors: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`, `expired-authority`, `revoked-authority`, `gate-required`, `indeterminate`.

## action.dispatch

Run one currently permitted local tool action.

- Request: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/action-request.schema.json).
- Result: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/action-receipt.schema.json).
- Caller route: `assigned-agent-or-operator` plus actual authority evaluation.
- Effects: `local-action`.
- Cut selectors: `/source_cut`.

### Preconditions

- Re-evaluate authority and bounds immediately before dispatch.
- Verify adapter retry/recovery scope; forbid network/external/activation effects and writes to admission state outside its publisher.

### Observed result

- Observe actual outputs and completion/failure/uncertainty.
- Indeterminate effects require reconciliation before another dispatch.

[Invocation](examples/action.dispatch/request.json) · [Domain request](examples/action.dispatch/message.json) · [Result](examples/action.dispatch/response.json) · [Error](examples/action.dispatch/error-response.json). These are shape illustrations with placeholder authority and handler references.

Allowed application errors: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`, `conflict`, `idempotency-conflict`, `expired-authority`, `revoked-authority`, `gate-required`, `indeterminate`, `recovery-required`.

## action.reconcile

Reconcile selected uncertain effects or verified recovery residue.

- Request: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/recovery-request.schema.json).
- Result: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/recovery-receipt.schema.json).
- Caller route: `authorized-recovery-actor` plus actual authority evaluation.
- Effects: `recovery`.
- Cut selectors: `/expected_cut`.

### Preconditions

- Authorize only the selected recovery contract and allowed residue.
- Observe the actual state; do not replay a non-idempotent action to discover its outcome.

### Observed result

- Return observed recovery bindings or preserved uncertainty.
- Never delete committed history or infer a failed action had no effect.

[Invocation](examples/action.reconcile/request.json) · [Domain request](examples/action.reconcile/message.json) · [Result](examples/action.reconcile/response.json) · [Error](examples/action.reconcile/error-response.json). These are shape illustrations with placeholder authority and handler references.

Allowed application errors: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`, `conflict`, `idempotency-conflict`, `expired-authority`, `revoked-authority`, `gate-required`, `indeterminate`, `recovery-required`.

## workflow.transition

Apply one permitted coordination transition with observed satisfaction.

- Request: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/workflow-transition.schema.json).
- Result: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/workflow-transition-receipt.schema.json).
- Caller route: `assigned-agent-or-operator` plus actual authority evaluation.
- Effects: `workflow-write`.
- Cut selectors: `/source_cut`.

### Preconditions

- Resolve actual lifecycle mappings, decision profile, actor routes and all transition checks.
- Match current run revision/state and satisfaction evidence; block unbound template workflows.

### Observed result

- Record observed transition and candidate outputs under the selected coordination authority.
- No automatic output admission; indeterminate transition requires recovery.

[Invocation](examples/workflow.transition/request.json) · [Domain request](examples/workflow.transition/message.json) · [Result](examples/workflow.transition/response.json) · [Error](examples/workflow.transition/error-response.json). These are shape illustrations with placeholder authority and handler references.

Allowed application errors: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`, `conflict`, `idempotency-conflict`, `expired-authority`, `revoked-authority`, `gate-required`, `indeterminate`, `recovery-required`, `invalid-connection`, `noncollapse-failed`.

## classification.prepare

Prepare an axis-qualified Classification Assignment.

- Request: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/classification-request.schema.json).
- Result: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/change-proposal.schema.json).
- Caller route: `assigned-agent-or-operator` plus actual authority evaluation.
- Effects: `candidate-write`.
- Cut selectors: `/source_cut`.

### Preconditions

- Verify exact subject, scheme, value, axis, applicability and basis.
- Do not merge independent classification dimensions or claim causality.

### Observed result

- Return an exact candidate change proposal for the assignment.

[Invocation](examples/classification.prepare/request.json) · [Domain request](examples/classification.prepare/message.json) · [Result](examples/classification.prepare/response.json) · [Error](examples/classification.prepare/error-response.json). These are shape illustrations with placeholder authority and handler references.

Allowed application errors: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`, `conflict`, `idempotency-conflict`, `expired-authority`, `revoked-authority`, `gate-required`, `indeterminate`, `recovery-required`.

## failure.assess

Prepare evidenced failure assessment and response scope.

- Request: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/failure-assessment-request.schema.json).
- Result: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/change-proposal.schema.json).
- Caller route: `assigned-agent-or-operator` plus actual authority evaluation.
- Effects: `candidate-write`.
- Cut selectors: `/source_cut`.

### Preconditions

- Verify occurrence, mode assignment, evidence, cause hypotheses and incident threshold.
- Separate observation, classification, cause and control/recovery conclusions.

### Observed result

- Return a bounded candidate assessment proposal with explicit evidence and uncertainty.

[Invocation](examples/failure.assess/request.json) · [Domain request](examples/failure.assess/message.json) · [Result](examples/failure.assess/response.json) · [Error](examples/failure.assess/error-response.json). These are shape illustrations with placeholder authority and handler references.

Allowed application errors: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`, `conflict`, `idempotency-conflict`, `expired-authority`, `revoked-authority`, `gate-required`, `indeterminate`, `recovery-required`.

## challenge.submit

Prepare an eligible challenge under its exact Challenge Contract.

- Request: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/challenge-request.schema.json).
- Result: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/change-proposal.schema.json).
- Caller route: `eligible-challenger` plus actual authority evaluation.
- Effects: `candidate-write`.
- Cut selectors: `/source_cut`.

### Preconditions

- Verify challenged revision, eligibility, grounds, evidence and contract routes.
- Disclose only information allowed by the challenger scope.

### Observed result

- Return a candidate Challenge Event proposal preserving the original subject and history.

[Invocation](examples/challenge.submit/request.json) · [Domain request](examples/challenge.submit/message.json) · [Result](examples/challenge.submit/response.json) · [Error](examples/challenge.submit/error-response.json). These are shape illustrations with placeholder authority and handler references.

Allowed application errors: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`, `conflict`, `idempotency-conflict`, `expired-authority`, `revoked-authority`, `gate-required`, `indeterminate`, `recovery-required`.

## challenge.resolve

Prepare consequences of an actual challenge resolution Decision.

- Request: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/challenge-resolution.schema.json).
- Result: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/change-proposal.schema.json).
- Caller route: `accountable-owner` plus actual authority evaluation.
- Effects: `candidate-write`.
- Cut selectors: `/source_cut`.

### Preconditions

- Verify actual resolution Decision authority and Challenge Contract obligations.
- Keep semantic and governance consequences distinct.

### Observed result

- Return candidate exact effects with unresolved gaps; no automatic authority promotion.

[Invocation](examples/challenge.resolve/request.json) · [Domain request](examples/challenge.resolve/message.json) · [Result](examples/challenge.resolve/response.json) · [Error](examples/challenge.resolve/error-response.json). These are shape illustrations with placeholder authority and handler references.

Allowed application errors: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`, `conflict`, `idempotency-conflict`, `expired-authority`, `revoked-authority`, `gate-required`, `indeterminate`, `recovery-required`.

## lesson.select

Select applicable lessons for the current bounded assignment.

- Request: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/context-query.schema.json).
- Result: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/lesson-selection.schema.json).
- Caller route: `bounded-reader` plus actual authority evaluation.
- Effects: `read-only`.
- Cut selectors: `/source_cut`.

### Preconditions

- Use the Context Query assignment and exclusions; resolve its active session from trusted context.
- Verify applicability, expiry, conflicts and instruction precedence.

### Observed result

- Return selected/omitted/blocked lesson revisions with reasons.
- Selection is neither application nor proof of effectiveness.

[Invocation](examples/lesson.select/request.json) · [Domain request](examples/lesson.select/message.json) · [Result](examples/lesson.select/response.json) · [Error](examples/lesson.select/error-response.json). These are shape illustrations with placeholder authority and handler references.

Allowed application errors: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`.

## lesson.apply

Prepare a recorded application of an exact lesson revision.

- Request: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/lesson-application-request.schema.json).
- Result: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/change-proposal.schema.json).
- Caller route: `assigned-agent-or-operator` plus actual authority evaluation.
- Effects: `candidate-write`.
- Cut selectors: `/source_cut`.

### Preconditions

- Verify session, selection, applicability and any conflict override basis.
- Keep lesson instructions within actual delegated action bounds.

### Observed result

- Return a candidate Lesson Application proposal with attribution.

[Invocation](examples/lesson.apply/request.json) · [Domain request](examples/lesson.apply/message.json) · [Result](examples/lesson.apply/response.json) · [Error](examples/lesson.apply/error-response.json). These are shape illustrations with placeholder authority and handler references.

Allowed application errors: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`, `conflict`, `idempotency-conflict`, `expired-authority`, `revoked-authority`, `gate-required`, `indeterminate`, `recovery-required`.

## lesson.assess

Prepare assessment of a recorded lesson application.

- Request: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/lesson-assessment-request.schema.json).
- Result: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/change-proposal.schema.json).
- Caller route: `assigned-agent-or-operator` plus actual authority evaluation.
- Effects: `candidate-write`.
- Cut selectors: `/source_cut`.

### Preconditions

- Resolve application and observed evidence/counterevidence.
- Bind outcome method and causal claim ceiling.

### Observed result

- Return an outcome assessment proposal; broader effectiveness needs its own evidence.

[Invocation](examples/lesson.assess/request.json) · [Domain request](examples/lesson.assess/message.json) · [Result](examples/lesson.assess/response.json) · [Error](examples/lesson.assess/error-response.json). These are shape illustrations with placeholder authority and handler references.

Allowed application errors: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`, `conflict`, `idempotency-conflict`, `expired-authority`, `revoked-authority`, `gate-required`, `indeterminate`, `recovery-required`.

## ontology.project

Apply selected ontology representations with an independent cut.

- Request: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/ontology-project-request.schema.json).
- Result: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/ontology-projection-receipt.schema.json).
- Caller route: `authorized-representation-actor` plus actual authority evaluation.
- Effects: `ontology-representation`.
- Cut selectors: `/lab_source_cut`, `/ontology_expected_cut`.

### Preconditions

- Verify represented source revisions, mapping/profile closure and ontology authority.
- Global typed relation projections remain read-only; local edges obey their own declared profile.

### Observed result

- Return observed represented references, ontology watermark/view or pending/blocked/uncertain state.
- Ontology representation confers no Lab admission authority.

[Invocation](examples/ontology.project/request.json) · [Domain request](examples/ontology.project/message.json) · [Result](examples/ontology.project/response.json) · [Error](examples/ontology.project/error-response.json). These are shape illustrations with placeholder authority and handler references.

Allowed application errors: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`, `conflict`, `idempotency-conflict`, `expired-authority`, `revoked-authority`, `gate-required`, `indeterminate`, `recovery-required`, `invalid-connection`, `noncollapse-failed`.

## projection.refresh

Build and select a complete disposable SQLite generation.

- Request: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/projection-refresh-request.schema.json).
- Result: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/projection-query-status.schema.json).
- Caller route: `projection-builder` plus actual authority evaluation.
- Effects: `projection-write`.
- Cut selectors: `/source_cut`.

### Preconditions

- Resolve projector, exact schema/catalog, source verification and expected generation.
- Verify complete generation, foreign keys, integrity, watermarks and compatibility before switching visibility.

### Observed result

- Return observed ready/stale/building/invalidated generation metadata.
- Canonical history remains the replay source; projection failure is not canonical rollback.

[Invocation](examples/projection.refresh/request.json) · [Domain request](examples/projection.refresh/message.json) · [Result](examples/projection.refresh/response.json) · [Error](examples/projection.refresh/error-response.json). These are shape illustrations with placeholder authority and handler references.

Allowed application errors: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`, `conflict`, `idempotency-conflict`, `expired-authority`, `revoked-authority`, `gate-required`, `indeterminate`, `recovery-required`.

## files.materialize

Generate selected managed byte exports or pinned rendered files.

- Request: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/file-materialization-request.schema.json).
- Result: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/file-materialization-receipt.schema.json).
- Caller route: `authorized-export-actor` plus actual authority evaluation.
- Effects: `managed-file-write`.
- Cut selectors: `/source_cut`.

### Preconditions

- Verify exact byte closure or renderer, output scope, paths/symlinks and privacy.
- Preserve unmanaged files and exclude session memory; pin complete managed output selection.

### Observed result

- Stage/publish a managed generation with observed output hashes or report failure/uncertainty.
- Generated files grant no admission and are not the canonical replay source.

[Invocation](examples/files.materialize/request.json) · [Domain request](examples/files.materialize/message.json) · [Result](examples/files.materialize/response.json) · [Error](examples/files.materialize/error-response.json). These are shape illustrations with placeholder authority and handler references.

Allowed application errors: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`, `conflict`, `idempotency-conflict`, `expired-authority`, `revoked-authority`, `gate-required`, `indeterminate`, `recovery-required`, `path-collision`, `private-material-excluded`.

## package.export

Export selected portable original content and complete dependencies.

- Request: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/package-export-request.schema.json).
- Result: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/file-materialization-receipt.schema.json).
- Caller route: `authorized-export-actor` plus actual authority evaluation.
- Effects: `managed-file-write`.
- Cut selectors: `/source_cut`.

### Preconditions

- Verify selected original bytes and the complete required dependency closure.
- Resolve export destination from the exact export contract; exclude credentials/session memory.

### Observed result

- Return a managed generation receipt binding exported package bytes and dependencies.
- Exported source admission evidence does not admit the package in another target.

[Invocation](examples/package.export/request.json) · [Domain request](examples/package.export/message.json) · [Result](examples/package.export/response.json) · [Error](examples/package.export/error-response.json). These are shape illustrations with placeholder authority and handler references.

Allowed application errors: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`, `conflict`, `idempotency-conflict`, `expired-authority`, `revoked-authority`, `gate-required`, `indeterminate`, `recovery-required`, `path-collision`, `private-material-excluded`.

## package.import

Prepare selected source import/adaptation in a candidate workspace.

- Request: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/package-import-request.schema.json).
- Result: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/change-proposal.schema.json).
- Caller route: `authorized-import-actor` plus actual authority evaluation.
- Effects: `candidate-write`.
- Cut selectors: `/target_base_cut`.

### Preconditions

- Verify source package, source admission basis, mapping, disposition and dependency closure.
- Apply target custody/privacy rules and preserve exact source provenance.

### Observed result

- Return a candidate target proposal with complete selected-item accounting.
- No automatic admission or source retirement.

[Invocation](examples/package.import/request.json) · [Domain request](examples/package.import/message.json) · [Result](examples/package.import/response.json) · [Error](examples/package.import/error-response.json). These are shape illustrations with placeholder authority and handler references.

Allowed application errors: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`, `conflict`, `idempotency-conflict`, `expired-authority`, `revoked-authority`, `gate-required`, `indeterminate`, `recovery-required`.

## installation.execute

Install/upgrade/rollback a selected local package under exact authority.

- Request: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/install-request.schema.json).
- Result: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/installation-receipt.schema.json).
- Caller route: `authorized-local-operator` plus actual authority evaluation.
- Effects: `local-install`.
- Cut selectors: Outer cut and exact referenced state/package/session bindings.

### Preconditions

- Verify exact release approval, profile, environment, authority, preimage and recovery contract.
- Keep credentials in private custody; activation/external effects are zero.

### Observed result

- Return observed installed/rolled-back/failed/indeterminate postimage evidence.
- Installation does not infer a running service or operational acceptance.

[Invocation](examples/installation.execute/request.json) · [Domain request](examples/installation.execute/message.json) · [Result](examples/installation.execute/response.json) · [Error](examples/installation.execute/error-response.json). These are shape illustrations with placeholder authority and handler references.

Allowed application errors: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `conflict`, `idempotency-conflict`, `expired-authority`, `revoked-authority`, `gate-required`, `indeterminate`, `recovery-required`, `path-collision`, `private-material-excluded`.

## lab.status

Discover the selected source profile, cut and available implementation surface.

- Request: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/lab-status-request.schema.json).
- Result: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/lab-status-result.schema.json).
- Caller route: `bounded-reader` plus actual authority evaluation.
- Effects: `read-only`.
- Cut selectors: `/source_cut`.

### Preconditions

- Authorize inspection of all selected scopes.
- A null cut selects the current scoped cut at read start; a supplied cut selects an exact historical read.

### Observed result

- Return the captured cut and exact catalog/profile bindings.
- Distinguish declared operations from observed implemented support.

[Invocation](examples/lab.status/request.json) · [Domain request](examples/lab.status/message.json) · [Result](examples/lab.status/response.json) · [Error](examples/lab.status/error-response.json). These are shape illustrations with placeholder authority and handler references.

Allowed application errors: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`.

## catalog.get

Read current/historical artifact contracts and declared relation signatures.

- Request: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/catalog-request.schema.json).
- Result: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/catalog-result.schema.json).
- Caller route: `bounded-reader` plus actual authority evaluation.
- Effects: `read-only`.
- Cut selectors: `/source_cut`.

### Preconditions

- Bind cursor to principal, scope, request selectors and exact cut.
- An empty carrier selection requests all eligible catalog entries within the page budget.

### Observed result

- Return pinned schema/descriptor bindings and current/historical posture.
- Return only eligible relation signatures when requested.

[Invocation](examples/catalog.get/request.json) · [Domain request](examples/catalog.get/message.json) · [Result](examples/catalog.get/response.json) · [Error](examples/catalog.get/error-response.json). These are shape illustrations with placeholder authority and handler references.

Allowed application errors: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`, `invalid-cursor`.

## session.inspect

Read session metadata and unresolved action references.

- Request: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/session-inspect-request.schema.json).
- Result: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/session-inspect-result.schema.json).
- Caller route: `session-owner-or-authorized-auditor` plus actual authority evaluation.
- Effects: `read-only`.
- Cut selectors: Outer cut and exact referenced state/package/session bindings.

### Preconditions

- Authorize session ownership or an exact audit scope.
- Never expose short memory, private credentials or a session dump.

### Observed result

- Return observed metadata/receipt references; absence is scoped not-found.
- Expired and uncertain states remain distinct from verified closed.

[Invocation](examples/session.inspect/request.json) · [Domain request](examples/session.inspect/message.json) · [Result](examples/session.inspect/response.json) · [Error](examples/session.inspect/error-response.json). These are shape illustrations with placeholder authority and handler references.

Allowed application errors: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`.

## operation.inspect

Read the scoped invocation/idempotency record after uncertainty.

- Request: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/operation-inspect-request.schema.json).
- Result: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/operation-inspect-result.schema.json).
- Caller route: `operation-owner-or-authorized-auditor` plus actual authority evaluation.
- Effects: `read-only`.
- Cut selectors: Outer cut and exact referenced state/package/session bindings.

### Preconditions

- Resolve by exact call binding or principal-scoped operation/key.
- Authorize operation owner or selected auditor; no cross-principal enumeration.

### Observed result

- Return known pending/completed/failed/indeterminate result and effect evidence.
- Lookup never redispatches the operation; unknown records return scoped not-found.

[Invocation](examples/operation.inspect/request.json) · [Domain request](examples/operation.inspect/message.json) · [Result](examples/operation.inspect/response.json) · [Error](examples/operation.inspect/error-response.json). These are shape illustrations with placeholder authority and handler references.

Allowed application errors: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`.

## typed.extension.prepare

Prepare a declared typed connection extension for owner review.

- Request: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/typed-extension-request.schema.json).
- Result: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/change-proposal.schema.json).
- Caller route: `assigned-agent-or-operator` plus actual authority evaluation.
- Effects: `candidate-write`.
- Cut selectors: `/source_cut`.

### Preconditions

- Verify Relation Kind candidate, unique semantic question, orthogonal axis and exact pair/qualifier contracts.
- Resolve noncollapse evidence, writable authority, owner review and impacted Artifact Type successors.

### Observed result

- Return explicit candidate extension effects.
- Unregistered new connections remain non-writable until exact required admission.

[Invocation](examples/typed.extension.prepare/request.json) · [Domain request](examples/typed.extension.prepare/message.json) · [Result](examples/typed.extension.prepare/response.json) · [Error](examples/typed.extension.prepare/error-response.json). These are shape illustrations with placeholder authority and handler references.

Allowed application errors: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`, `conflict`, `idempotency-conflict`, `expired-authority`, `revoked-authority`, `gate-required`, `indeterminate`, `recovery-required`, `invalid-connection`, `noncollapse-failed`.

## capability.adoption.prepare

Prepare exact capability realization and owner-local adoption declarations.

- Request: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/capability-adoption-request.schema.json).
- Result: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/change-proposal.schema.json).
- Caller route: `assigned-agent-or-operator` plus actual authority evaluation.
- Effects: `candidate-write`.
- Cut selectors: `/source_cut`.

### Preconditions

- Verify capability, realization binding, nonempty implementations, conformance and scoped owner authority.
- Bind actual observation contract and operational scope; no activation in this operation.

### Observed result

- Return candidate exact adoption/binding effects.
- Actual operational usefulness must be observed under separately valid action scope.

[Invocation](examples/capability.adoption.prepare/request.json) · [Domain request](examples/capability.adoption.prepare/message.json) · [Result](examples/capability.adoption.prepare/response.json) · [Error](examples/capability.adoption.prepare/error-response.json). These are shape illustrations with placeholder authority and handler references.

Allowed application errors: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`, `conflict`, `idempotency-conflict`, `expired-authority`, `revoked-authority`, `gate-required`, `indeterminate`, `recovery-required`.

## release.prepare

Prepare an exact candidate release for its final review.

- Request: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/release-manifest.schema.json).
- Result: [exact schema](../../../docs/proposals/0007-lab-integrated-schema-package/schemas/proposal-review.schema.json).
- Caller route: `assigned-agent-or-operator` plus actual authority evaluation.
- Effects: `candidate-write`.
- Cut selectors: Outer cut and exact referenced state/package/session bindings.

### Preconditions

- Require candidate posture and actual package, acceptance, pilot, privacy, environment and installation bindings.
- A candidate missing any required evidence remains blocked; do not fabricate release approval.

### Observed result

- Return a candidate proposal review; release Decision remains independently required.
- No publication, installation, external effect or activation occurs.

[Invocation](examples/release.prepare/request.json) · [Domain request](examples/release.prepare/message.json) · [Result](examples/release.prepare/response.json) · [Error](examples/release.prepare/error-response.json). These are shape illustrations with placeholder authority and handler references.

Allowed application errors: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `conflict`, `idempotency-conflict`, `expired-authority`, `revoked-authority`, `gate-required`, `indeterminate`, `recovery-required`.
