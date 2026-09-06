# Workflow Compensation v1

Status: canonical project-local runtime contract

This contract defines compensation without changing `DS-D1`, `DS-D8`, or the frozen Workflow v1
realization. It is admitted by the direct owner decision
`DSV2-OWNER-PRODUCT-ONTOLOGY-COMPENSATION-2026-08-29`. The moving current-baseline pointer is owned by
`definitions/meta-types/current-implementation.json` and is deliberately not embedded in this semantic contract.

## Formal voice

```text
WorkflowCompensation = (decision, intent?, plan, external executor)

workflow_evaluation_result in {not-required, recovery-required}
not-required      => no RecoveryIntent exists
recovery-required => exactly one RecoveryIntent exists

intent = (intent_id, workflow_execution_id, failure_occurrence_id,
          failed_step_id, completed_step_journal_digest, plan_digest)
intent.semantic_status = required
plan   = topological_order(selected forward-recovery Operations)
invocation_identity = H(intent_id, plan_digest, operation_id, plan_occurrence_id)
executor(plan) = preflight and invoke exactly the selected Operations

ordering:
  explicit Operation dependencies dominate;
  otherwise use reverse completed-step order;
  reverse completed-step order is also the deterministic tie-breaker.

authority boundary:
  Workflow evaluation may emit intent and plan but never executes compensation.
  A separate executor invokes the selected forward-recovery Operations.
  The in-process report is not a durable attempt or terminal disposition.
```

Every compensation target is an ordinary `Operation`. It therefore owns its declared reads, writes, effects,
guard-before-mutation, atomic state-and-outbox boundary, idempotent behavior, events, and failure continuation.
The executor owns only ordering, exact binding, invocation, and compensation state transitions.

## Plain-language voice

Compensation is forward recovery, not time travel and not a database rollback. When part of a Workflow fails,
the Workflow records what completed and asks a separate runner to perform specifically declared recovery
Operations. The runner refuses unknown substitutions and stops at the first failed recovery Operation.

## Domain-context voice

DomainSpec represents both forward steps and compensation targets with the existing
`Workflow --[orchestrates]--> Operation` relationship. A Workflow body maps completed step IDs to compensation
Operation IDs and may declare `operation:depends-on:operation` entries. Generated Workflow artifacts expose the
Workflow-result/Recovery-Intent split and the external executor boundary in TypeScript, Python, and Rust. Target conformance rejects
missing Operation relationships, undeclared executor ownership, direct Workflow execution, dependency cycles,
missing runtime bindings, and substituted Operation IDs.

## State ownership

```text
Workflow evaluation: not-required | recovery-required
Recovery Intent:     required | satisfied | unresolved
In-process report:   succeeded | failed
Durable disposition: completed | exhausted | escalated  (not implemented here)
```

The failure continuation is owned by the failed recovery Operation binding. Retrying must reuse the same
invocation identity; it may not create another semantic Recovery Intent. Only durable D44 evidence may move
an intent from `required` to `satisfied` or `unresolved`.

## Claim ceiling

This is a canonical project-local runtime contract. It does not change DS-D1 or DS-D8, grant publication,
release, deployment, or production authority, or prove durable dispatch and recovery after process restart.
