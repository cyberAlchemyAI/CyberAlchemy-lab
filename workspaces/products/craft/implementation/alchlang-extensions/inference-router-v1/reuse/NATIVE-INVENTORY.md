# Native responsibility audit

18 files; 738 physical lines, including comments and imports.
Exact hashes and complete spans: [native-inventory.json](native-inventory.json).

| Source | Lines | Role | Responsibility |
| --- | ---: | --- | --- |
| [host.mjs](../host.mjs) | 50 | operator-binding | Validate and snapshot operator catalogs; shared public scope; supply estimates; adapt arguments and call compiled admission/discovery/custody. Configured strategy vocabulary and estimator validation remain an explicit inference operator contract, not generic runtime policy. |
| [dispatch.mjs](../dispatch.mjs) | 13 | dependency-binding | Wire generated invocation and stream factories to fixed HTTP dependency; forward pre-attempt gate and transport observations. |
| [idempotency.mjs](../idempotency.mjs) | 7 | dependency-binding | Bind sibling DomainSpec memory custody; optional legacy handler injection only for compatibility tests. |
| [streaming.mjs](../streaming.mjs) | 3 | compatibility-export | Re-export the generic generated stream session runtime; no native frame policy. |
| [serve.mjs](../serve.mjs) | 22 | process-lifecycle | Load exact operator config, build candidate bundles, listen on numeric loopback, close resources. |
| [run.mjs](../run.mjs) | 27 | build-tooling | Verify compiler hashes and launch bounded build/test/serve commands. |
| [build-public-policy.mjs](../build-public-policy.mjs) | 28 | build-tooling | Build authored policy/service/invocation/stream/custody modules and expose their generated entry points. |
| [service-runtime.ts](../../../alchlang/src/service-runtime.ts) | 56 | generic-runtime | Execute generated route plan; request bytes/media/deadline, typed operation boundary and authored error mapper. |
| [node-service-host.ts](../../../alchlang/src/node-service-host.ts) | 41 | generic-runtime | Bridge Node sockets to Web Request/Response with bounded backpressure and disconnect propagation. |
| [outbound-runtime.ts](../../../alchlang/src/outbound-runtime.ts) | 58 | generic-runtime | Execute normalized sequential composition; local modules, one bound HTTP attempt, deadline/concurrency and actual settlement. |
| [http-invocation-adapter.ts](../../../alchlang/src/http-invocation-adapter.ts) | 35 | generic-runtime | Resolve operator URLs/secrets and exact versions; one HTTP fetch with manual redirects; independent resource settlement. |
| [stream-runtime.ts](../../../alchlang/src/stream-runtime.ts) | 43 | generic-runtime | Execute authored state/frame contract; terminal latch, mapping invocation and independent cancellation. |
| [sse-adapter.ts](../../../alchlang/src/sse-adapter.ts) | 33 | generic-runtime | Incremental UTF-8/SSE framing, byte caps and bounded downstream capacity. |
| [custody-runtime.ts](../../../alchlang/src/custody-runtime.ts) | 50 | generic-runtime | Canonical JSON/hash encoding, authored identity/default configuration, memory port calls and lifecycle observation ordering. |
| [boundary-runtime.ts](../../../alchlang/src/boundary-runtime.ts) | 127 | generic-runtime | Generic generated-function schema/transport boundary, local-only module invocation and cancellation. |
| [query-iteration-runtime.ts](../../../alchlang/src/query-iteration-runtime.ts) | 26 | generic-runtime | Bounded pure iteration according to authored field selectors and module mappings. |
| [invocation-trace.ts](../../../alchlang/src/invocation-trace.ts) | 65 | generic-runtime | Generic source-linked invocation observations and tracing. |
| request-custody.ts (source binding requires reconciliation) | 54 | generic-memory-port | Atomic memory reservation; copied values; store-local opaque tokens; write-once outcome; independent transport settlement; bounded records/queue and expiry. |

Compiler/lowering source, generated output, test code and historical prototype
artifacts are explicitly distinguished in the machine inventory. The generated
bundle inventories bind emitted code separately.

## Open Questions

Owned by [the reuse artifact](README.md#open-questions).
