# Checked callable ports for profiles

Status: PE01 contract investigation completed against real generated artifacts. This establishes a supported adapter design; the production application adapter and final profile dispatcher remain PE14/PE08 work.

## Exact supported pair

The Alch function export is `invoke` from the generated quote function's `app/function/index.mjs`. Its checked schemas are `QuoteRequest` and `QuoteResponse`: request ID/SKU/quantity enters; quoted/unavailable status and exact minor-unit total leaves. Invocation is asynchronous, with explicit environment and injected fetch/signal ports. Failures are thrown `FunctionFault` codes; the wrapper returns those codes in an explicit boundary-failure branch. The tested export's bytes are pinned in the PE01 receipt.

The Craft export is `operationReceiveNotice` from the generated `features/commerce/application/operations/receive-notice.ts`. Its exact exported input is `{request:{id:bigint|number|string}}`; the owned value is `{id:bigint}`. Dependencies supply `store.begin()`, then the typed read/commit/rollback transaction ports. It returns an awaited explicit `committed` value or `rejected`/`failed`/`indeterminate` outcome with stage, code, continuation and cleanupFailed. The actual generated descriptor says state-and-outbox, no provider durability claim, no publication and no automatic retry on uncertainty. The wrapper preserves that entire failure outcome rather than turning uncertainty into success or an ordinary exception.

These business types are different and are not interchangeable. A common generic invocation protocol can host them with exact individual input/value/port/failure contracts. Joining their business values requires an authored checked Mapping, not matching labels or an arbitrary profile wrapper.

## Adapter-owned invocation contract

`Callable<Input,Value,Ports,Failure>` takes the typed input and ports, optionally a bounded context, and returns `Promise<{status:"returned",value:Value}|{status:"not-returned",failure:Failure}>`. A trusted registered adapter owns each conversion. Packages can select supported adapters, not provide evaluator hooks or invent new conversion code.

For a function, the adapter validates its unknown legacy JavaScript result against the pinned output schema before exposing a typed value. A conservative declaration of that legacy export returns unknown; it is not evidence that the implementation body is statically typed. PE08 must check all final generated wrappers/dispatch/imports with exact checker coverage plus runtime falsifiers.

For an Operation, `committed` exposes the exact owned value; every other outcome is retained in full. Store/transaction ownership remains explicit. No wrapper begins a real database, publishes an event, retries or fabricates a rollback success. Fake transaction observations establish only their finite cases.

Observation context is an optional read-only adapter lifecycle callback (start/return/failure). It is not a fabricated trace of internal Operation stages, accounted telemetry, proof or ORODI admission. Observer errors cannot alter the business outcome. The actual Operation outcome retains its own stage/continuation/cleanup semantics.

## Cancellation and compatibility result

Function invocation supports its existing abort signal and bounded outbound-read cancellation. The current Operation supports a preflight abort check only; it cannot guarantee in-flight transaction cancellation. A caller requiring in-flight cancellation receives `PROFILE_OPERATION_CANCELLATION_UNSUPPORTED` before beginning effects. An already aborted signal returns `FUNCTION_CANCELLED` before begin. A live signal under explicit preflight semantics does not promise that later abort cancels settlement.

PE01's investigation outcome is **compatible for value invocation through these registered typed adapters with the explicit cancellation capability boundary**. It does not declare equivalent business schemas, universal Operation cancellation, a completed generated application composition path or live readiness. PE14 must implement the registered adapter, integrate it with an authored application binding and type-check/invoke the final service path. Unsupported required cancellation remains a real selection blocker rather than disappearing from a profile.

## Verification

The conformance probe compiles the actual generated Operation/provider dependencies and typed wrappers using TypeScript 6.0.3; imports actual generated function/Operation exports; verifies function success/input/environment/provider-shape failures, Operation committed/rejected/indeterminate/input/begin outcomes, preserved failure metadata, preflight/required cancellation and adapter observations. Five native negative controls reject wrong input/value/ports/environment and missing exports. During runtime qualification, traps observe zero real fetch/http/net/listen/process attempts; all dependencies are injected fakes. The native compiler process is a separate allowed qualification stage.

The original test assumption that identifier zero would violate `identity-valid` was rejected by source inspection: that fixture Rule compares its normalized identity to itself. The corrected probe uses actual commit rejection and malformed UInt64 input as failure cases; it does not rewrite the Rule or claim a nonexistent guard policy.

## Open Questions

PE14 owns the production adapter and actual service-to-Operation composition; PE08 owns final glue coverage; PE19 owns frozen extension qualification. Other Operation conventions, cancellation guarantees, providers or new value/effect semantics need separately qualified core support. Local hosting, TDE, EVF and publication remain deferred.
