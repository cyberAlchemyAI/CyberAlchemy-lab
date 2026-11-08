# Public route assembly

Status: ISB-04 local compiler candidate. Authority effect: none.
The existing [multi-entry service format](docs/MULTI-ENTRY-SERVICES.md) remains
supported. `profile service-v1` plus `assembly public-routes-v1` selects the
additional public route assembly described here. No DomainSpec meta-type or
frozen definition is changed.

See the complete [authored inference service](../alchlang-extensions/inference-router-v1/public-service.alch)
and its [construction plan](../alchlang-extensions/inference-router-v1/service/PLAN.md).

## Authored contract

A service declares a domain, the assembly mode, `node-http` target, explicit
`deferred` authentication/authorization, `shared-public` scope, byte/read limits,
local function imports, one error-policy function, operations and routes.
These fields are closed: unknown or repeated clauses reject. Paths are relative
to the service source root; traversal and symlink escapes reject. Imported
functions must be declarative functions or bounded pure query iterations.
Transitive effectful integrations reject; native effects require a named
operation binding. Existing per-function source/type checks still apply.

Each route declares method, path, function, input source, output selection,
response mode and success status. GET accepts `unit` or `context <name>`;
POST accepts JSON. `unit` uses the explicit internal carrier `{unit:true}` because
the function profile requires a nonempty record schema. It is not public input.
`output all` returns the complete function result; a named output field must be
required and non-nullable. Bodyless success statuses 204/205 are unsupported.

An operation declares `input <Function>.output`, `output <ResultFunction>.input`
and `response json|json-or-sse`. Its route must select a result function and the
same response mode. Nested structural types and constraints must agree. JSON
results pass through the compiled result function before public serialization.
The generated service requires exactly the declared operation callables and
context slots at construction. Context values are snapshotted and validated by
the compiled function when used. Runtime validation cannot prove a native
callable implements its contract for every possible input.

Default maxima are 32 routes, 16 imports, 16 operations, 65,536 request bytes,
65,536 JSON response bytes and 30,000 ms body-read time. The inference definition
selects a 5,000 ms read deadline. An operator may lower request/read limits, but
cannot raise them above the source. The response bound includes encoded UTF-8
bytes. The error policy maps boundary faults into the public body/status; a
failure in that policy closes with an empty 500.

## Generated interface

```sh
node dist/cli.js check path/public-service.alch
node dist/cli.js build path/public-service.alch --out /absolute/new/bundle
```

`app/service/index.mjs` exports `createHandler`, `createServer`, `functions` and
`plan`. Construct with `{contexts, operations, maxRequestBytes?, readTimeoutMs?}`.
An operation has `(normalizedJson, env, {signal, headers})` arguments. Its JSON
input is copied through serialization to preserve the previous HTTP boundary's
plain-data representation. It returns JSON data or, only for `json-or-sse`, a
Response with the declared success status and `text/event-stream` media type.
A JSON Response cannot bypass the compiled output validation. Unsupported
Responses are cancelled and rejected. Event payloads remain the stream binding's
responsibility until ISB-06.

Routing is generated from the source. The runtime owns bounded JSON/body handling,
context supply, compiled invocation, response validation and serialization. It
forwards client cancellation and suppresses late JSON success; the supplied native
operation still owns attempt deadlines and transport settlement. A cancellation
check is also added to the existing generated function boundary, and its HTTP
handler combines the client and explicitly supplied signals for invocation.

The generic Node adapter owns incoming byte streams, socket disconnects and
response pipeline backpressure. It preserves structured errors for chunked
request overflow. It contains no inference paths, model rules or error-code map.

`routes.json` contains the sorted route manifest, required context/operation
types, source lines and function digests. `evidence/service/assembly-trace.json`
links authored routes and typed bindings to child manifests; each child carries
its DomainSpec compilation/ontology/Craft evidence. The completion manifest binds
all generated files and is published last into an exclusively created directory.
A source change during compilation rejects before publication.

Implementation: [compiler](src/service-routes.ts),
[boundary](src/service-runtime.ts), [socket adapter](src/node-service-host.ts).
Tests: [service witnesses](../alchlang-extensions/inference-router-v1/service/service.test.mjs)
and [existing multi-entry regressions](test/service-profile.test.ts).

## Open Questions

- Native provider execution, stream lifecycle and custody remain ISB-05..07.
  This assembly does not make their current implementation generated policy.
- Rust service assembly, authenticated routes, other HTTP methods, effectful
  imported functions and additional response modes need separate contracts.
- The service's product questions are owned by the
  [shared plan](../alchlang-extensions/inference-router-v1/SERVICE-PLAN.md#open-questions).
