# Public inference host and discovery

Current default: [ISB-09 protected host](security/IMPLEMENTATION.md). The anonymous
assembly described below is retained as historical ISB-08 fixture behavior.

Status: owner-directed local D8 candidate. Authority effect: none.
The owner explicitly deferred tenant authentication and authorization until last.
This supersedes the authentication prerequisite described in the historical
IDEMPOTENCY.md host frontier for this local prototype. All public calls currently
share one operator-configured scope, including idempotency keys.

## API

| Method and path | Behavior |
| --- | --- |
| GET /healthz | Process liveness; does not probe providers |
| GET /v1/models | Enabled public model aliases, task, limits and streaming support |
| GET /v1/capabilities | Configured routing strategies, task, streaming and replay support |
| POST /v1/inference | Normalized JSON or SSE inference through the compiled pipeline |

Example body:

```json
{"task":"text.generate","input":{"messages":[{"role":"user","content":"Hello"}]},"routing":{"strategy":"balanced"},"parameters":{"max_output_tokens":256},"stream":false}
```

`model` is optional. Defaults are balanced routing, 256 output tokens and
stream:false; routing and parameters may be omitted or empty objects. Unknown
fields are rejected at every schema level. Clients cannot supply tenant identity,
catalog, binding, destination, credentials, rank or token estimates. Only configured
strategies are accepted; unknown aliases return 404 and no eligible binding returns
503. `Content-Type: application/json` is required. Requests are bounded at 64 KiB
by default, with a lower configurable host limit. Invalid JSON/UTF-8 and invalid
contracts return 400; size overflow returns 413. Capacity failures return 429,
provider failures 502, and deadlines 504. Errors contain sanitized codes.

Optional `Idempotency-Key` uses the existing bounded in-memory store. Equivalent
explicit/default fields replay the original JSON result and request ID. Changed
model, messages, parameters or routing strategy conflicts with a retained key.
Catalog versions remain pinned by the first execution. Stream requests cannot be
replayed. See IDEMPOTENCY.md for retention and ambiguous-execution semantics.

The [compiled discovery definitions](discovery/README.md) project enabled operator catalog rows into public fields only. Limits
are conservative minima across bindings of an alias; streaming means at least one
configured binding supports it. Eligibility still depends on the chosen strategy
and request. Discovery does not expose binding IDs, remote model names, URLs or
secrets, and is not a provider health assertion. Configuration is snapshotted at
host creation; updates require a new host instance.

The [ISB-04 service definition](service/README.md) now owns public routing and
HTTP boundaries; provider execution remains the explicit native binding.

## Running

Use the Node/compiler setup in PROTOTYPE.md and compiler-binding.json:

```sh
node run.mjs test
node run.mjs serve /absolute/operator-config.mjs 3000
```

The launcher verifies the sibling DomainSpec build through run.mjs, compiles all
the inference handlers and [generated discovery/error policy](discovery/README.md) into a temporary bundle, listens on 127.0.0.1, and removes the
bundle on shutdown. Port 0 selects an ephemeral port. No deployment is performed.
An empty discovery-only operator configuration is:

```js
export default {
  token: 'local-internal-handler-token',
  bindings: [],
  catalogs: {balanced: {policy_version: 'balanced-v1', providers: []}},
  estimateContext: ({max_output_tokens}) => max_output_tokens
};
```

For inference, add trusted bindings and catalog rows using the shapes documented
in DISPATCH.md and provider-selection.alch. Supply provider secrets from operator
configuration/environment. Catalog keys can be balanced, cost and latency; each
has its own version and ranks. Balanced is required. Enabled rows must resolve to
a configured binding. The host sets the internal scope to public and makes all
operator-enabled rows available; tenant checks remain deferred.

`estimateContext({messages, model, max_output_tokens})` is a synchronous trusted
callback returning a conservative total context requirement, including reserved
output, across candidate providers. The discovery-only example is not a real
message tokenizer. A live configuration needs an appropriate provider/tokenizer
estimate. Invalid estimates fail before dispatch. `store` accepts existing
idempotency limits; dispatcher limits remain configurable as described in
DISPATCH.md. No automatic fallback or paid provider has been configured.

Embedding APIs are `createPublicHandler(config)` for Fetch Request/Response and
`createPublicServer(config)` for Node HTTP. Supply compiled selector, requestMapper,
responseMapper, deltaMapper, policy and publicMapper handlers plus operator config.
The Node adapter honors response backpressure and propagates client disconnects
to upstream cancellation. Existing bounded SSE buffering remains as documented in
STREAMING.md.

## Construction and verification

D65 dependencies: define/cli-result.json -> business-ontology.json and
product-capability.json -> public-request.alch plus the existing five authored
Alch functions -> compiler-binding.json sibling compiler -> generated handlers ->
host.mjs and serve.mjs -> dispatch.test.mjs local HTTP fixtures. No additional
ontology-runtime record or selector dependency is introduced. Route availability
is not governance admission. Prior receipts remain historical; host-evidence.json
owns this epoch and links its exact tested sources.

The tests cover discovery redaction, generated request defaults and strict nested
validation, JSON/SSE, replay/conflicts, catalog snapshots, error/size boundaries,
client cancellation, and launcher compilation/shutdown. The existing selector,
transport and custody regressions remain included.

## Open Questions

- Which two live providers, public aliases and conservative tokenizer estimates
  should be configured next?
- Which storage backend and retention/recovery rules should survive restart and
  support multiple hosts? Existing memory storage has no cross-host guarantee.
- Which production limits and provider-specific non-execution evidence should
  govern safe fallback?
- Tenant authentication, authorization and per-tenant discovery/key scoping are
  explicitly deferred until last, including authorization checks before replay.
- Durable Define-session continuity remains owned by define/CLI-RESULT.md.

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
