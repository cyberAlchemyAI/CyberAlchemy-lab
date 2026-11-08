# DomainSpec Product Ontology — System View

This is a human projection of the system branch. Status is explicit: `implemented`, `evidence-bound`,
`canonical`, or `designed`.

- `dsv2.system.baseline-v10` — immutable selected implementation with baseline-independent recovery closure, provider-neutral D45-D49 formation, and non-cyclic current-pointer boundaries.
- `dsv2.system.instantiation-cli` — closed input, deterministic plan, atomic publication, receipt, and reread.
- `dsv2.system.target-observer` — independent bounded observation and fail-closed comparison.
- `dsv2.system.instantiation-receipt` — exact input, selection, output, and observation binding.
- `dsv2.system.operation-runtime` — state-changing behavior and its effect perimeter.
- `dsv2.system.workflow-runtime` — ordered orchestration with a Recovery Intent-only compensation boundary, observed in generated TypeScript, Python, and Rust targets.
- `dsv2.system.compensation-planner` — deterministic recovery selection, ordering, Intent identity, occurrence identity, and Invocation Identity in all three language profiles.
- `dsv2.system.compensation-executor` — three-language exact-binding preflight and in-process Operation invocation.
- `dsv2.system.recovery-architecture-profile` — canonical portable durable-recovery @2 properties and findings.
- `dsv2.system.recovery-coordination-repository-contract` — implemented provider-neutral concern-specific contract formation; no adapter or storage proof.
- `dsv2.system.recovery-coordination-unit-of-work-contract` — implemented provider-neutral local atomicity contract formation; no provider transaction proof.
- `dsv2.system.operation-binding-resolver-contract` — implemented exact frozen-plan Operation binding preflight contract in TypeScript, Python, and Rust.
- `dsv2.system.recovery-persistence-binding` — implemented closed, digest-bound Repository-to-target-supplied-adapter binding formation.
- `dsv2.system.recovery-transaction-guarantee-binding` — implemented closed local guarantee-binding formation with exact participants.
- `dsv2.system.recovery-failure-outcome-binding` — implemented closed classifier formation with hostile continuation rejection.
- `dsv2.system.durable-workflow-runtime-binding` — implemented closed D49 manifest formation and three-language contract generation; provider runtime open.
- `dsv2.system.recovery-coordination-store` — designed provider adapter for the Repository and Unit of Work contracts.
- `dsv2.system.recovery-claim-authority` — designed version-CAS Claim acquisition and monotonic fencing.
- `dsv2.system.recovery-lease-service` — designed latest-generation bounded Claim validity.
- `dsv2.system.durable-recovery-worker` — designed fenced, replaceable dispatch-advancement worker.
- `dsv2.system.recovery-attempt-journal` — designed durable D39 execution-episode store.
- `dsv2.system.operation-invocation-ledger` — designed Operation-owned D40 replay-result store.
- `dsv2.system.recovery-retry-scheduler` — designed persisted bounded D43 scheduler.
- `dsv2.system.recovery-terminal-recorder` — designed evidence-bound D44 recorder.
- `dsv2.system.recovery-restart-reconciler` — designed expiry, unknown-outcome, takeover, and resume component.
- `dsv2.system.dispatch-outbox-publisher` — designed at-least-once publisher of committed coordination Events.
- `dsv2.system.recovery-clock-contract` — implemented responsibility-specific generated contract formation; runtime clock open.
- `dsv2.system.recovery-wakeup-contract` — implemented polling-or-notification contract formation with no state authority; delivery open.
- `dsv2.system.recovery-telemetry-contract` — designed observation-only recovery telemetry contract.
- `dsv2.system.contract-tests` — positive, hostile, and three-language parity evidence, including generated-target closure.

The system view reports implementation evidence. The three-language recovery profile is candidate-local and
does not alter the selected baseline. It does not redefine business intent or authorize release.
Designed nodes make the remaining target runtime navigable but are not implementation evidence. Implemented
formation nodes remain bound to explicit provider-runtime residue. Contract, binding, and adapter nodes remain distinct; none implies a universal
`Port`, mandatory DomainSpec Interface, database, ORM, broker, or dependency-injection framework.

The contract and binding topology cites the exact infrastructure-binding Tower, System Integration Contract
Layer Revision 2, owner admission, and live provider-neutral package/CLI evidence. The package now validates,
generates, receipts, and statically observes D45-D49 formations in TypeScript, Python, and Rust. Research and
formation evidence are not provider, transaction, runtime, or deployment evidence.
