# P06 resource-supervised qualification

`SupervisedQualifier(run_root, operator_policy).qualify(raw_bytes, cancel=event)` dispatches one fixed worker. Raw request parsing, typed normalization, source projection, dependency preparation, finite evaluation, all actual witness compilations, general submission, fresh same-kernel replay and exact saved inspection happen in the owned process group. The original request and resource policy are retained. The proof recipe is an exact operational adaptation of accepted P03, checked by reversing its documented edits.

The returned `relational.supervised-qualification/v3` envelope has `qualified_result: null`, no claims, no closure and no application authorization for every incomplete or refused run. Successful envelopes contain the closed P01 qualification result plus a supervisor-completion binding. Every result still has `application_authorized: false`. The CLI accepts raw request and operator-policy files; it performs only bounded transport acquisition before dispatch.

Inner compiler/helper streams are consumed with byte and atomic-stage limits and forwarded to the outer supervisor. The supervisor applies the whole-run clock, cancellation, bounded output and an owned-process concurrency lock. Returned metadata is bounded before allocation and counted as IPC. It terminates and reaps the owned group before an issued result is created. Worker intermediate records explicitly remain unissued.

`live_event(result)` requires this instance's private completion event, the exact complete result identity, current completion/result/run-record files and current worker source bindings. Reading a saved result or constructing another API instance does not create that event. This is a live qualification capability for future mediated shadow work, not application authorization.

## Memory policy

On this host the actual backend is advisory aggregate descendant RSS observation. The successful rich example measured approximately 97 seconds and 2.22 GiB sampled aggregate RSS. These observations do not establish a hard memory bound or recommended defaults. The required backend is unavailable and is refused before any worker starts.

A writable delegated cgroup v2 parent with enabled memory/pids controls can use the conditional required backend. It verifies memory.max and the explicit operator pids limit before releasing the bootstrap gate, keeps the original required policy and observes actual memory.events. This backend was not exercised on the current host. Cgroup memory means charged memory including descendants, with shared-page attribution; it is not a promise that every sampled RSS total is below memory.max.

## Review

The implementation passes 49 controls: eight actual process controls, 33 full-pipeline/identity/refusal controls and eight closed transport/CLI controls. The rich run freshly checks all 20 obligations and matches the accepted P03 normal forms, closure, certificates, observations and supports. Same-kernel replay remains the stated proof boundary. Required hard-memory behavior, independent checking, cache authority hardening and shadow commit behavior must not be inferred from this result.
