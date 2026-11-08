# Generated provider invocation

ISB-05 completed local candidate. Authority effect: none.
[Construction boundary](PLAN.md); [evidence](evidence.json).

Validation: 79 inference/service tests, 14 DomainSpec contract/composition tests
and three existing service compatibility tests pass.

[provider-invocation.alch](../provider-invocation.alch) now owns the sequence:
validate complete input, select an eligible provider, resolve the pinned binding,
map its request, invoke HTTP once, decode the provider response and map the public
completion. invocation-completion.alch (result record excluded) owns JSON
usage provenance and public identity projection. Local stages use the existing
DomainSpec declarative compiler; raw provider JSON needs no business status.

The Node dispatcher is dependency wiring for the generated invocation, fixed
operator HTTP bindings and the existing stream lifecycle. It no longer contains
selection/request/JSON-response orchestration. `serve.mjs` builds and imports the
invocation bundle. Public routes continue through the generated public service;
`ExecuteInference` still binds the operator estimator and native request custody.

```sh
TMPDIR=/dev/shm tools/toolchain/run node language/capabilities/alchlang/plans/general-compiler-v1/extensions/inference-router-v1/run.mjs test
TMPDIR=/dev/shm tools/toolchain/run node language/capabilities/alchlang/plans/general-compiler-v1/extensions/inference-router-v1/run.mjs build-invocation /absolute/new/bundle
```

The shared [compiler/runtime contract](../../../alchlang/OUTBOUND.md)
explains bounds, typed interfaces, fail-closed reference checks, clock domains and
custody. `HttpAttempt.response` and `settled` are independent. A failed response,
deadline or acknowledged cancel does not release an unsettled attempt's slot.
Rejected settlement also keeps the slot occupied. Resolved settlement can release
it even when cancellation acknowledgment remains pending. Local release never
proves remote execution stopped; automatic retry remains forbidden.

The selector/request/response modules now opt into the existing portability
profile so their schemas can be imported by the composition. The old nonempty
message regex is expressed as a nonempty-content rule, preserving multiline
messages and rejection before transport. This does not claim Rust service parity.
The launcher compilation wait was increased to accommodate the larger generated
bundle; provider deadlines and authored limits remain unchanged.

## Open Questions

No blocking choice remains for ISB-05. ISB-06 owns generated stream transitions,
ISB-07 owns custody, ISB-08 owns independent full-service reuse, and ISB-09 owns
tenant authentication and authorization last. Live providers/tokenizers, durable
storage and deployment remain operator choices in the [shared plan](../SERVICE-PLAN.md).
