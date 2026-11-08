# ISB-06 stream lifecycle construction

Completed owner-directed local candidate; authority effect: none.

Reuse [Define-backed stream meanings and transitions](../service-contracts-v1/README.md)
and their D65 business/product scaffolds. DomainSpec owns closed normalized state
and frame-interface validation. Alch owns the authoring, lowering, compiled frame
mappings and generated session. Generic adapters own incremental UTF-8/SSE parsing,
byte bounds, downstream capacity and transport cancellation.

Move started/delta/completed/error payloads, provider event selection and lifecycle
transitions into authored declarations. One terminal state wins completion/failure/
cancellation races. A cancelled downstream receives no additional frame. Deadlines
must suppress late completion. Finished stream work and actual HTTP settlement
remain separate; remote completion is unknown on failure/cancel and replay stays
forbidden by existing custody policy.

Verify the 79 preceding service/inference tests, typed contract negatives,
UTF-8/CRLF and EOF bounds, slow-consumer backpressure, delayed mapping/cancellation
races, exactly one terminal observation and generated source/build bindings.
Advance both Craft contexts only after fresh tests. Runnable frontier is ISB-06;
ISB-07 custody remains next, with tenant authentication/authorization last (ISB-09).
Compiler owners own local toolchains. Operators own future provider, storage and
deployment choices; none blocks this bounded unit.

## Open Questions

No blocking operator choice for the local candidate. Custody generation, durable
storage, independent full-service reuse and final tenant security remain in the
[shared plan](../SERVICE-PLAN.md#open-questions).
