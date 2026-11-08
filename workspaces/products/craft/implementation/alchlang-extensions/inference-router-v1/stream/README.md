# Generated stream lifecycle

ISB-06 completed local candidate. Authority effect: none.
[Construction plan](PLAN.md); [evidence](evidence.json).

Validation: 91 inference/service tests (including 12 stream witnesses), six
DomainSpec contract tests and three existing service compatibility tests pass.

[provider-stream.alch](../provider-stream.alch) owns the state transitions,
provider event discriminators, public event names and byte bounds. The compiled
[start](../stream-start.alch), [delta](../stream-delta.alch),
[completion](../stream-complete.alch) and [failure](../stream-fail.alch) mappings
own public frame payloads. Completion reuses the existing provider decoder and
JSON completion/usage policy; failure reuses the compiled public stream error
policy. Delta reuses the existing provider delta module.

The dispatcher binds the generated session and forwards completion usage into
existing custody observations. `streaming.mjs` now exposes the generic runtime;
it contains no inference lifecycle decisions. Parsing and bounded frame writing
live in generic compiler adapters, described in [STREAMS.md](../../../alchlang/STREAMS.md).

```sh
TMPDIR=/dev/shm tools/toolchain/run node language/capabilities/alchlang/plans/general-compiler-v1/extensions/inference-router-v1/run.mjs test
TMPDIR=/dev/shm tools/toolchain/run node language/capabilities/alchlang/plans/general-compiler-v1/extensions/inference-router-v1/run.mjs build-stream /absolute/new/bundle
```

The response queue holds at most one bounded frame, with one event in processing.
A slow consumer stops further event reads. Completion commits when its frame is
accepted into the queue; cancellation before acceptance suppresses that completion.
Completion/failure/cancellation races produce one local terminal observation.
The session's local finish remains separate from actual HTTP settlement, preserving
occupied slots and remote uncertainty. Existing idempotency policy still rejects
stream replay.

The existing deadline-during-mapping regression now injects delay at the generated
completion module boundary. The missing-stream-binding regression targets the
generated session factory. Their outcome assertions remain intact. Launcher
compilation wait allows the larger bundle; provider deadlines remain unchanged.
A one-line TypeScript narrowing annotation in the existing application contract
was necessary to restore the compiler build; it changes no runtime behavior.

## Open Questions

No blocking choice for this local unit. Next is ISB-07, generated request custody
and idempotency binding. Full service reuse follows in ISB-08. Tenant authentication
and authorization remain last (ISB-09), as requested. Provider/tokenizer, durable
storage and deployment choices remain operator-owned in the [shared plan](../SERVICE-PLAN.md).
