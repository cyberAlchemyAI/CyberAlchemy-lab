# JSON inference dispatch prototype

Status: tested local candidate. Owner: Alch language and inference implementation owner.
Authority effect: none. No paid inference, deployment or real model evaluation.

The trusted host now composes the compiled provider selector, an Alch-authored
request mapper, a bounded JSON POST transport and an Alch-authored response mapper.
`dispatch.mjs` exports `createDispatcher`. Supply the three generated handlers,
fixed operator bindings, internal token and limits. Its returned function accepts
normalized routing input, a trusted tenant catalog, messages and an optional
AbortSignal. `dispatch.test.mjs` demonstrates the complete construction and use.

The two `.alch` mapper sources compile through the exact DomainSpec binding in
`compiler-binding.json`. Request mapping supplies messages, configured remote
model, max_tokens and stream:false. Response mapping converts answer/stop_reason
and optional prompt/completion token fields into canonical result fields.
The adapter removes only the mapper's internal HTTP status marker and packages
usage provenance. Provider schema translation stays in the compiled mappings.

This is an exact local fixture protocol, not asserted OpenAI, Anthropic or
Telegraph API compatibility. A real provider needs a separately selected contract
and corresponding mapper. Both tested fixture providers use this protocol.

## Behavior and trust boundary

- Fixed provider URL, credential, public alias and binding version come from
  trusted operator configuration. Selected alias/version must match that binding.
- HTTPS is required; numeric loopback HTTP is available only with the explicit
  fixture flag. Redirects are not followed and provider diagnostics are not returned.
- Each request makes at most one POST. Unknown execution outcomes never trigger
  fallback. Authentication, tenant derivation, strategy ranking and tokenizer
  estimates remain trusted-host responsibilities described in PROTOTYPE.md.
- Request/response bodies, elapsed time and concurrency are bounded. A deadline
  aborts local transport and returns an error; it does not prove remote cancellation.
  A transport that ignores cancellation retains its slot until it settles.
- Usage counts remain null/unavailable when omitted. Present counts are labeled
  provider-reported. This is neither billing nor settlement evidence.
- Streaming requests reject explicitly. There is no public inference listener,
  tenant rate limiter, durable attempt store or idempotency implementation yet.

## Verification

From this directory, with Node 26.8.1:

```sh
node run.mjs test
```

21 tests pass: six parser/schema tests, seven compiled selector tests and eight
dispatch tests. The dispatch suite builds all three handlers through the real
Alch/DomainSpec path and sends requests to two loopback HTTP fixture endpoints.
Other cases cover missing usage, malformed messages/responses, fixed binding
versions, no eligible provider, redirect/status/transport errors without retry,
byte caps, deadline/overload behavior and explicit streaming rejection.
`dispatch-evidence.json` records this exact source snapshot. The earlier
execution-evidence.json remains the historical selector-only snapshot.

## Construction and operational lanes

Product frontier: D6 JSON dispatch and mapping locally tested; D7 streaming,
usage persistence, cancellation refinement, safe fallback and idempotency remain.
Runnable next: define the stream contract and implement/test incremental output
without provider switching. No external provider configuration blocks local work.

Operational support: inference operator/product owner selects actual providers,
credentials, aliases, quotas and budgets before live integration; operator sets
production deadlines and retention before candidate freeze; product/VPS owners
own later exact deployment. These are deferred operational tasks, not current
local construction blockers. No operational effect is granted by these tests.

The D65 prototype chain retains the candidate Definition Pack, business/product
scaffolds, authored Alch mappings, DomainSpec-generated handlers, explicit native
transport binding and exact local execution tests. This component evidence does
not complete the full inference product or imply owner acceptance.

## Open Questions

The original questions remain in the Define result (result record excluded).
Progress on OQ-COMPILER: Node selection and JSON request/response mapping now have
real compiled execution evidence; SSE and full public-host integration remain.

- Which real provider contracts and public aliases should the first adapters use?
- Which provider outcomes, if any, prove execution did not start and permit fallback?
- What stream framing, cancellation and partial-failure behavior must each provider expose?
- What production concurrency, deadline, byte-limit and retention targets apply?
- Which idempotency and replay guarantees must survive restart?
- Is durable Define-session continuity needed beyond the working in-memory CLI?

Real-provider decisions affect live integration; fallback/stream/idempotency
semantics affect their respective D7 work. None is silently answered by fixtures.

## ISB-05 generated invocation

The current provider sequence is authored in [provider-invocation.alch](provider-invocation.alch).
[Invocation evidence and open questions](invocation/README.md) describe the typed
HTTP dependency and separate response/settlement custody. Existing evidence in
this document remains historical; stream lifecycle and custody generation follow.

## ISB-06 generated stream lifecycle

The current stream is authored in [provider-stream.alch](provider-stream.alch).
[Generated stream evidence and open questions](stream/README.md) supersede the
handwritten lifecycle while preserving earlier receipts as historical evidence.
Generic adapters now enforce bounded downstream capacity; custody generation is next.
