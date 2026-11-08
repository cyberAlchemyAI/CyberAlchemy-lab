# Alch host lifecycle product review

Candidate: `5608619110a000e6b3564e1c1096c6fe04917dba06387d78bcd03dacea09cc03` (SHA-256 of candidate-manifest.json).
Product approval: pending Alch product owner review; no decision is manufactured.

The candidate adds read-only function health/delivery summaries, durable fenced
requests for drain/resume/restart, explicit lifecycle permissions, startup recovery,
and CLI/Python controls. Restart preserves selected code, storage and desired mode.

Product-test evidence (referenced result or source binding is not imported) records 45 passing test executions
across five completed runs. It includes real queued builds and isolated Rust hosts,
35-second drain timeout, controller exits at six persisted stages, killed-host
recovery, an in-flight invocation, and consumption-before-acknowledgment recovery.
The source inventory has 423 verified files; 403 predecessor files match
unchanged. Syntax and contract-schema checks passed. One interrupted combined run
is retained as non-completion evidence; its termination cause is unresolved and its
test cases were rerun successfully against the same frozen candidate.

Construction L1-L10 is complete for this local candidate. L11 remains owner review.
Existing-root migration, long-running service credentials and public deployment
remain deferred operational support with their owners in execution.json. The service
is loopback-only and requires a fresh lifecycle registry. Unknown control effects
require controller startup reconciliation before conflicting controls can proceed.
No force restart, stop, dead-letter redrive or new DomainSpec meta-type is included.

A product decision must bind the candidate digest above. Changed candidate bytes
require current tests and a new review epoch. Product approval grants no operational
authority, publication or deployment.

## Open Questions

See [the plan](PLAN.md#open-questions) for deferred capabilities. No current
implementation work remains in this bounded candidate.
