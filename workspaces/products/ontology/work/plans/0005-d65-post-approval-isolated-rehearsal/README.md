# D65 post-approval isolated rehearsal plan

`CAL-PLAN-0005` continues from the exact epoch-002 product approved by `CAL-D65PAPP-0033`.

The plan runs continuously through isolation-contract authoring, rehearsal-harness construction, deterministic replay, mutation testing, rollback proof, and candidate freezing. Its only owner gate is the final exact admission decision. That decision may admit the rehearsed product without activation or cutover, reject it, defer it, or require amendment.

Canonical events remain the replay source. Node snapshots, relation snapshots, context projections, and challenge-contract projections are calculated state and never become replay sources.

This package is a planning candidate only. It neither executes the rehearsal nor authorizes admission, activation, migration, cutover, publication, release, deployment, or external effects.

Validate it with:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 docs/plans/0005-d65-post-approval-isolated-rehearsal/validate.py --write-receipt
```
