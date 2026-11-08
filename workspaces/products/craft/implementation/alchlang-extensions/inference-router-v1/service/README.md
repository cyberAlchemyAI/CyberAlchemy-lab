# Generated public service assembly

Status: ISB-04 completed local candidate. Authority effect: none.
[Plan](PLAN.md) -> [service source](../public-service.alch) ->
[compiler realization](../../../alchlang/SERVICE.md) ->
[evidence](evidence.json). The existing [multi-entry source](../service.alch)
and its compiler remain supported; `assembly public-routes-v1` is explicit.

The authored service now assembles:

| Route | Generated behavior | Supplied context or binding |
| --- | --- | --- |
| GET /healthz | [Health query](health.alch), public `{status:"ok"}` | Internal Unit carrier; no provider probe |
| GET /v1/models | Compiled bounded model discovery | Snapshotted provider rows |
| GET /v1/capabilities | Compiled capability projection | Providers, strategies and retention |
| POST /v1/inference | JSON boundary, compiled normalization, typed native call, JSON result validation (result record excluded) or SSE | `ExecuteInference` |

The service generates method/path dispatch, media validation, request/read/response
limits, error policy invocation and cancellation forwarding. The remaining
[host binding](../host.mjs) validates operator configuration, adapts catalog
containers and supplies the inference callable. That callable still chooses the
configured strategy, checks model availability, calls the estimator and runs the
existing provider/custody pipeline. Those policies are ISB-05..07 work.

The build uses existing DomainSpec-backed function compilation plus the bounded
query iteration added in ISB-03. No DomainSpec compiler source or frozen definition
was changed. Source and type bindings appear in the generated route manifest and
assembly trace, linked to each child compilation manifest.

Use the existing verified compiler binding from the parent directory:

```sh
node run.mjs build-service /absolute/new/bundle
node run.mjs serve /absolute/operator-config.mjs 3000
node run.mjs test
```

The launcher builds the service and existing native-operation functions, then
serves through a generic Node socket adapter. Its regression fixture allows up to
60 seconds for compilation; request and provider deadlines are not increased.
Operator configurations still use the public host shape documented in
[HOST.md](../HOST.md). The generated standalone factory requires the declared
context values and typed native operation implementation before it can serve.

Verification covers all 59 prior tests plus ten new service witnesses: typed
normalization/output validation, missing/extra bindings, no execution on invalid
input, cancellation before/during work, stalled body reads, invalid stream modes,
compiler rejection cases, manifest/source bindings, changed authored routes,
response byte limits and generated function signal propagation. The original
multi-entry service suite is checked separately for compatibility.

The native-binding boundary preserves JSON plain-data representation; direct
compiled records must not change existing request fingerprints. The tests retain
idempotency replay/conflict, streaming, client disconnect and chunked 413 behavior.

## Open Questions

- ISB-05 must generate provider selection/request/call/response composition behind
  the declared native dependency, preserving one-attempt and settlement semantics.
- ISB-06 owns SSE event/lifecycle typing and ISB-07 owns custody realization.
- Live provider/tokenizer selection, durable storage and deployment remain future
  operator decisions. No local construction blocker is known.
- Tenant authentication and authorization remain ISB-09, last. Rust service
  assembly is not claimed by this Node candidate.
