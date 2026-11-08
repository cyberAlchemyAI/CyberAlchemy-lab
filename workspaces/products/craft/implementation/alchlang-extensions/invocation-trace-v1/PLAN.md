# Invocation explanations

User-authorized continuation, 2026-09-05. Product construction scope: opt-in observations from generated declarative behavior, linked to its source-derived ontology, with local execution over supplied JSON input. No new meta-type or registry effects.

## Definitions and prototype stages

An invocation trace records evaluated declaration outcomes; it does not turn authored meaning into an observed fact. A query-row observation records its source collection index, candidate value and composite predicate result. It does not claim every subexpression ran: short-circuit semantics remain intact. An explanation joins observations to exact source/ontology/contract digests and source clauses. Missing observations are not successes. Bounded capture is explicitly complete or truncated independently from execution success/failure.

Product/business prototype: explain why a quote, ambiguity or no-price result occurred for the supplied snapshot; preserve all pricing semantics. DomainSpec prototype: optional observer hooks in generated Mapping, Query, Rule, Calculation, assertion and result-case evaluation. Compiled-system prototype: an invokeWithTrace export and JSON-safe receipts with exact bigint encoding. Implementation prototype: local CLI execution and source-linked answers, plus parity and failure tests.

## Product construction lane

Initial frontier: static source explanations and generated ontology are tested; invocation evidence is absent. Runnable tasks: add optional generated observation hooks, implement bounded per-invocation capture, add a local command requiring provided integration inputs, test success/failure/concurrency/truncation, and record one exact candidate. No causal blocker at entry.

## Operational support lane

No operational task blocks the local prototype. The local CLI must not fetch remote snapshots or load credentials. HTTP traces are not exposed on the public endpoint. Deployment, trace retention/access policies, registry admission and whole-project certification remain deferred to their respective owners and stages. Historical candidates are not refreshed.

## Open questions

Receipts are local observations, not signed attestations or tamper-proof historical evidence. Opt-in trace values can contain application data; this slice neither persists traces automatically nor establishes a production retention policy. Composite query outcomes do not yet expose every quantified witness or short-circuited subexpression. Future persisted-receipt verification requires a separate contract.

## Current frontier

The local product candidate is implemented and tested: 109 Alch tests and 26 focused DomainSpec tests pass. Typecheck and builds pass. All 20 pricing fixtures agree between ordinary and traced invocation on the final bundle. Quote, ambiguity, no-price and overflow receipts are saved. Product approval remains pending owner review; operational tasks remain deferred.
