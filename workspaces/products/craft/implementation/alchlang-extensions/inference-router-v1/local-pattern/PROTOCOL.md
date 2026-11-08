# Local text inference protocol v1

Identifier: `alch-local-text/v1`. Candidate contract, authority effect: none.
Open questions: README.md#open-questions.

This names the existing Alch request, response and stream mappings as a reusable
local protocol. It claims no compatibility with another engine's API. The source
schemas and transitions are preserved in the generated invocation and stream
bundles; this document is explanatory, not a second schema authority.

The operator binds a numeric loopback URL. The engine receives one JSON POST:

```json
{"messages":[{"role":"user","content":"Hello"}],"model":"configured-engine-model","max_tokens":256,"stream":false}
```

Messages retain order and text. Roles are system/user/assistant; at least one user
message is required. The internal mapper status field is not sent. In JSON mode,
the engine returns status 200, application/json, and:

```json
{"answer":"Hello","stop_reason":"stop","prompt_tokens":1,"completion_tokens":1}
```

Token counts are optional/nullable; missing counts remain unavailable rather than
zero. Finish reasons are stop, length, content_filter or unknown. No additional
fields are accepted by the mapped schema.

With stream true, return status 200 and text/event-stream. Send named SSE frames
with JSON objects, for example:

```text
event: delta
data: {"text":"Hello"}

event: completed
data: {"stop_reason":"stop","prompt_tokens":1,"completion_tokens":1}

```

An engine `error` event terminates with a sanitized public error. The service
emits its own started event with its request ID and public model alias. Completed
does not repeat generated text. EOF without completion is failure. This protocol
does not accept NDJSON, unnamed data-only token events or a `[DONE]` sentinel.

The reference composition permits 64 KiB requests/responses/total upstream stream,
16 KiB upstream events, 64 KiB public frames, two active invocations, one attempt,
and an operator-selected deadline up to the authored 30 seconds. The opt-in
DomainSpec outbound v2 contract permits authored deadlines up to 300 seconds;
legacy v1 remains capped at five seconds. Host overrides can only tighten bounds.

ContextBound is an operator assertion covering every valid prompt and engine in
the catalog; inputTokens plus requested output must fit the selected offering.
The example fixture's 65536-input-token bound is valid for its byte-counting
fixture protocol. A real engine requires an independently justified bound/version.
This is neither exact usage metering nor a universal tokenizer assumption.

No retries after uncertain execution, stream resumption or remote completion proof
are promised. Cancellation releases local resources when transport cleanup settles;
it does not prove model computation stopped. Memory custody is lost on restart.
