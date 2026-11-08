# Lab API operation contracts

Exact public catalog SHA-256: `4193281b7cc0bae15e9b54861ee1186ee85db930e2bc5a0093b87a898eb996c1`.

These 34 pages document declared contracts. Current 34-operation runtime qualification is pending; catalog presence does not prove an operation succeeds.

| Operation | Branch | Declared effect | Qualification |
| --- | --- | --- | --- |
| [`context.get`](context-get.md) | Base | `read-only` | Pending |
| [`artifact.inspect`](artifact-inspect.md) | Base | `read-only` | Pending |
| [`artifact.query`](artifact-query.md) | Base | `read-only` | Pending |
| [`session.open`](session-open.md) | Base | `ephemeral-session` | Pending |
| [`session.close`](session-close.md) | Base | `ephemeral-session` | Pending |
| [`change.prepare`](change-prepare.md) | Base | `candidate-write` | Pending |
| [`change.validate`](change-validate.md) | Base | `candidate-write` | Pending |
| [`proposal.review`](proposal-review.md) | Base | `candidate-write` | Pending |
| [`checkpoint.resolve`](checkpoint-resolve.md) | Governance | `candidate-write` | Pending |
| [`admission.apply`](admission-apply.md) | Governance | `canonical-commit` | Pending |
| [`action.evaluate`](action-evaluate.md) | Action | `read-only` | Pending |
| [`action.dispatch`](action-dispatch.md) | Action | `local-action` | Pending |
| [`action.reconcile`](action-reconcile.md) | Action | `recovery` | Pending |
| [`workflow.transition`](workflow-transition.md) | Base | `workflow-write` | Pending |
| [`classification.prepare`](classification-prepare.md) | Base | `candidate-write` | Pending |
| [`failure.assess`](failure-assess.md) | Base | `candidate-write` | Pending |
| [`challenge.submit`](challenge-submit.md) | Base | `candidate-write` | Pending |
| [`challenge.resolve`](challenge-resolve.md) | Base | `candidate-write` | Pending |
| [`lesson.select`](lesson-select.md) | Base | `read-only` | Pending |
| [`lesson.apply`](lesson-apply.md) | Base | `candidate-write` | Pending |
| [`lesson.assess`](lesson-assess.md) | Base | `candidate-write` | Pending |
| [`ontology.project`](ontology-project.md) | Base | `ontology-representation` | Pending |
| [`projection.refresh`](projection-refresh.md) | Base | `projection-write` | Pending |
| [`files.materialize`](files-materialize.md) | Base | `managed-file-write` | Pending |
| [`package.export`](package-export.md) | Base | `managed-file-write` | Pending |
| [`package.import`](package-import.md) | Base | `candidate-write` | Pending |
| [`installation.execute`](installation-execute.md) | Base | `local-install` | Pending |
| [`lab.status`](lab-status.md) | Base | `read-only` | Pending |
| [`catalog.get`](catalog-get.md) | Base | `read-only` | Pending |
| [`session.inspect`](session-inspect.md) | Base | `read-only` | Pending |
| [`operation.inspect`](operation-inspect.md) | Base | `read-only` | Pending |
| [`typed.extension.prepare`](typed-extension-prepare.md) | Base | `candidate-write` | Pending |
| [`capability.adoption.prepare`](capability-adoption-prepare.md) | Governance | `candidate-write` | Pending |
| [`release.prepare`](release-prepare.md) | Base | `candidate-write` | Pending |
