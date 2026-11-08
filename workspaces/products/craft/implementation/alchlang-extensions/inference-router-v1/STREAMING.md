# Inference SSE streaming prototype

Status: local Node candidate. Owner: inference implementation owner. Authority effect: none.

`createDispatcher` now accepts a compiled deltaMapper handler. With stream:true,
the compiled request mapper emits a streaming provider request and the dispatcher
returns a Response with text/event-stream content. JSON callers retain their
existing result shape. Without deltaMapper, streaming rejects explicitly.

Build provider-stream-delta.alch using the same Alch/DomainSpec compiler binding
as the selector and other mappers; supply its handler to createDispatcher.
The complete construction is demonstrated in dispatch.test.mjs. Native transport
code lives in streaming.mjs; payload schemas and mapping remain authored in Alch.
This is the local fixture protocol, not a claim of compatibility with a live vendor.

## Provider contract and public events

The selected provider returns HTTP 2xx with text/event-stream and UTF-8 SSE frames.
Each event contains JSON data; LF and CRLF separators and split UTF-8 are tested.
Comment lines are ignored and multiple data lines join with newline.

- Provider delta: {"text":"fragment"}. The compiled delta mapper rejects other fields.
- Provider completed: {"stop_reason":"stop"}, with optional nullable prompt_tokens
  and completion_tokens. Completion maps through provider-response.alch.
- Provider error: any JSON object; diagnostics are discarded and mapped to a fixed code.

The caller receives started, zero or more delta events, and one completed or error
while the connection remains writable. Every event carries the pinned request_id
and public model alias. Completion contains finish_reason and usage provenance,
without repeating prior text. Missing counts remain null/unavailable.

The first valid completion terminates and cancels the upstream reader; subsequent
bytes are not consumed. EOF before a terminal event, unknown event names, malformed
JSON or UTF-8, invalid mapped fields and excessive payloads produce an error.
An empty or partial stream is never silently completed. No provider switch or
retry occurs, including after partial output.

## Resource and cancellation behavior

The request deadline spans transport reads and asynchronous mapping. Expiry emits
a terminal error and attempts upstream cancellation. Consumer cancellation closes
local output and aborts/cancels upstream without trying to write to a closed client.
Neither action proves remote execution or billing stopped.

The existing total response byte limit applies; an SSE frame is additionally
limited to 16 KiB. The bounded stream pumps eagerly rather than offering
provider-level backpressure. Slow readers can buffer at most the configured
bounded response plus local framing overhead; unbounded live generations are
outside this candidate. Concurrency remains occupied through upstream reader
cleanup. There is no automatic retry, stream resumption or restart-safe deduplication.

## Verification and construction state

Run `node run.mjs test` with the compiler/toolchain bindings described in PROTOTYPE.md.
The suite compiles four Alch handlers and tests actual loopback SSE, incremental
read visibility before completion, split UTF-8/CRLF, partial failures, premature
EOF, invalid content types, oversized frames, cancellation and deadlines including
a deadline during completion mapping. JSON and selector regression tests remain.
`streaming-evidence.json` pins the tested files and result counts.

The D65 chain carries the existing candidate definitions and product/business
scaffolds into authored Alch request/delta/completion mappings, compiled DomainSpec
handlers, explicit native SSE transport and local product tests. This is D7
component evidence, not full product conformance, deployment or owner approval.

Product frontier: incremental JSON/SSE dispatch is locally testable. Runnable
next work: bounded idempotency and request/attempt tracking, followed by public
host integration. No live provider or durable Define-session choice blocks those
local prototypes. Safe fallback stays disabled until a provider-specific
pre-execution rejection contract has evidence.

Operational support: inference operator owns real providers, credentials and paid
budgets for live verification; operator/product owner chooses production limits
and retention before candidate freeze; VPS/product owners own later deployment.
These tasks remain deferred and grant no current external effect.

## Open Questions

- Which actual provider wire protocols, aliases and model deployments should bind?
- What production deadline, output-size, concurrency and slow-reader policies apply?
- Which provider outcomes prove non-execution and permit a safe second attempt?
- What request identity, retention and replay guarantees must survive restart?
- Is durable Define continuity needed beyond its current in-memory workflow?

The earlier Define question about compiler support now has local evidence for
selection and JSON/SSE mapping. Full public host integration remains pending.
Earlier evidence files are historical snapshots, not receipts for these changed bytes.

## ISB-06 generated stream lifecycle

The current stream is authored in [provider-stream.alch](provider-stream.alch).
[Generated stream evidence and open questions](stream/README.md) supersede the
handwritten lifecycle while preserving earlier receipts as historical evidence.
Generic adapters now enforce bounded downstream capacity; custody generation is next.
