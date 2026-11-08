# Generated response streams

Candidate ISB-06, Node target only. Authority effect: none.
[Authored inference stream and evidence](../alchlang-extensions/inference-router-v1/stream/README.md).

`response-stream-v1` lowers to the sibling DomainSpec
`domainspec.stream-lifecycle/v1-candidate` contract. The compiler validates the
complete seven-transition lifecycle: start opens a created stream, delta keeps
it open, and complete/fail/cancel lead to distinct terminal states. Created
streams may also fail or cancel. Missing, duplicate, reopening and cross-terminal
transitions reject. State names and public/provider event names are authored data.

Four pure local modules produce started, delta, completed and failed frames.
Their interfaces share a required scalar identity and a required output value.
Provider event inputs and failure code inputs are typed. Identity is checked
against the pinned values before frame output. The existing declarative compiler
owns schema validation and mapping behavior; transitive effectful modules reject.

```sh
alchlang check provider-stream.alch
alchlang build provider-stream.alch --out /absolute/new/bundle
```

The generated `app/stream/index.mjs` exports `createSession(session)`, its checked
contract and compiled modules. A session receives a typed HTTP exchange,
`cancelTransport`, pinned identity, cancellation signal, abort callback, optional
terminal observer and an optional lower total byte bound. Its response is SSE;
`finished` means local stream work ended. HTTP settlement remains the invocation
owner's independent responsibility. A hung cancellation acknowledgment cannot
turn local completion into proof of resource settlement or authorize a retry.

## Native responsibilities and races

`sse-adapter.ts` owns UTF-8 decoding, SSE lines, total/event byte limits and
capacity. It handles split multibyte characters, CRLF and bare CR, and rejects
incomplete or oversized events. It does not select provider events, project
product payloads or decide lifecycle transitions.

The response adapter queues at most one bounded frame. The producer may hold one
additional decoded/mapped event while waiting for capacity; it cannot read an
unbounded sequence ahead of a slow consumer. Parsing may retain the remaining
bytes of the current bounded input chunk. Native Node socket piping retains its
existing backpressure behavior.

A frame's accepted callback runs synchronously with enqueueing. The lifecycle
can therefore commit completion before a later cancellation claims a competing
terminal state. Cancellation before acceptance aborts the pending write and
suppresses late success. Error state is claimed before asynchronous failure
mapping; a concurrent downstream cancel closes output without recording a second
terminal outcome. Observer exceptions cannot affect lifecycle state.

A deadline interrupts input reads, normal mappings and writes waiting for capacity.
The failure frame may wait for downstream capacity; consumer cancellation releases
that wait. Error policy runs without the already-aborted provider signal so it can
serialize the terminal error, but downstream cancellation still interrupts it.
Parent request cancellation enters the cancelled state; a provider deadline enters
the failed state and uses the error policy. No additional frame is emitted to a cancelled consumer. Exactly one local terminal
observation does not mean delivery acknowledgment or remote execution termination.

## Open Questions

Request custody generation is ISB-07. Full independent service migration/reuse is
ISB-08; tenant authentication and authorization remain last, ISB-09. Operator
providers, durable storage, deployment and Rust service parity are separate work.
