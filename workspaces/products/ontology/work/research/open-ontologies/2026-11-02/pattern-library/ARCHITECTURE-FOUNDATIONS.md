# Architecture foundations

## Observed design

One Rust crate exposes transports and many domain services. Services share an
Oxigraph graph and SQLite metadata. Some tools interact with files, networks,
external solvers, model providers and subprocesses. The crate is modular in
files, but does not enforce a strict dependency layering policy.

The key separation is between finding a result and checking evidence for that
result. The forward/Horn paths use stable assertion selection to connect those
stages. Stable graph reads do not imply whole-operation isolation: temporal
metadata and assertions are not selected in one proven atomic step. An
unchecked result, a checked result under supplied assumptions, and a result
about built-in semantic rules are deliberately different.

Evidence: [CLI, HTTP, and daemon entrypoints](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/main.rs#L1), [MCP services over shared graph and state](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/server.rs#L1), [stable graph reads](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/graph.rs#L1245), [evidence-carrying verdicts](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/verdict.rs#L1).

## Design boundaries worth preserving

- A selected input is a value, not another live store read later in the run.
- Evidence is about exact bytes and a stated logical profile.
- Unknown, incomplete, unsupported and skipped are distinct from success.
- A proposed schema is an interpretation for review, not newly discovered truth.
- A measured slice and a theorem-backed claim have different warrants.

## Limits observed

The whole Rust engine is not verified. The mutable graph, SQLite snapshots and
best-effort lineage are not an event-sourced ontology authority model. Stable
per-run snapshots do not isolate sessions. Some historical documentation has
stale implementation notices; current source and tests take precedence.

The [Lab reuse assessment](../REUSE-ASSESSMENT.md) proposes a separate exact-cut
adapter and leaves canonical history and approvals in the Lab. That is our
recommendation, not an already enforced upstream boundary.
