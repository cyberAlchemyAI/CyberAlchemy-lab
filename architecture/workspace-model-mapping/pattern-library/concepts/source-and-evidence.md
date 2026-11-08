# Functional source and execution evidence

Meaning: current authored inputs and observed results require different selection rules.

Evidence: the [Craft current-import plan](../../../../docs/migration-plans/0007-craft-current-import-20261104/PLAN.md) retains detailed source/tests/fixtures and explicitly selects limited current evidence while excluding historical result archives from the functional export.

Use: keep test code, synthetic fixtures, schemas, templates and expected vectors with implementation. Preserve actual logs, receipts, saved snapshots and outcomes with their producing execution and source cut. Current evidence can be explicitly selected without importing every historical run.

Failure to avoid: deleting useful functional files because they are JSON or named evidence, or moving frozen proof/source archives as if they were current authored code.
