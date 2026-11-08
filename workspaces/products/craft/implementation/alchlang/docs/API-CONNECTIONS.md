# Connect generated contracts to inbound and outbound HTTP

A generated **Interface** gives your application an exact public request and
result contract. In the manual-adapter example below, your host supplies the
transport and service implementation. You can attach those contracts to an
existing HTTP framework and use them to validate requests to another service.
For selected application profiles, see [profile generation](PROFILE-GENERATION.md)
for generated process-local HTTP wiring. A hosted listener remains outside this
preview.

For a generated protected API with persistent state, use the bundled
`examples/generic-http` project and its [installed commands](GENERIC-APPLICATIONS.md#continue-with-a-protected-api-and-sqlite).
It generates GET/POST handlers from Entries and profiles, then checks authorization,
an atomic SQLite update and command replay. Its driver supplies isolated Auth
fixtures and Request objects; the business implementation is generated. The
example starts no listener and keeps production authentication integration explicit.

Start with the installed `quote-business` profile example when you want both a
generated public POST handler and a checked outbound inventory GET. It binds
an authored public intent to a route, validates the provider response and
computes the quote; you still supply the provider destination and credentials.
The manual adapter below is for an Interface contract that you connect to
your own host. The source-backed Commerce candidate demonstrates selected
persistence, Event and Workflow wiring, but its protected Entries do not yet
have a public installed credential-to-actor adapter.

The worked example in [api-connections](../examples/api-connections/README.md)
uses actual generated TypeScript exports: `endpointValues.find`,
`acceptsVersion`, two `calculateTotal` functions, and `mappingSummary`. Its
handwritten HTTP handler and fetch client connect in memory. The test opens no
listener and makes no remote calls.

## What belongs to each part

| Part | Responsibility |
| --- | --- |
| `Interface` | Public members, request/result types, named public contracts and version policy |
| Generated `endpointValues` | Normalize and own exact request/result values; UInt64 becomes bigint |
| `Mapping` | Explicit request or result projection between declared types |
| `Operation` | Declared action and its explicitly bound effects |
| `Query` | Declared read; its data/provider binding remains explicit |
| `inbound-endpoint` | Declared method/path and request → Operation → response binding |
| `outbound-call` | Declared external API and typed request/response mappings with an explicit adapter |
| Your host/client adapter | Routing, body decoding, authorization, network transport, status handling and deadlines |

Generating an Interface does not supply an implementation for its members. It
also does not execute domain invariants, perform database lookups, or turn an
Event intent into a delivery. The generated descriptor states
`transport_execution: "not-performed"` and
`invariant_execution: "not-performed"`.

The current declarative `inbound-endpoint` lowerer requires a declared
**Operation**. A public Interface may expose a Query, as the `commerce:api`
example does, but a direct Query target in `inbound-endpoint` is not accepted by
this source successor. Bind the Interface's read member to your supplied service
adapter when attaching it to your own host; keep the adapter's lookup/read policy
explicit. The worked example does that and supplies a finite fixture value.

## Run a complete example

Use an installed Craft package and exact consumer tools. The all-meta-type
example generates current native modules without hosting:

```sh
npm install --save-exact typescript@6.0.3 @types/node@26.4.0
node node_modules/@domainspec-v2/cli/examples/reconciled-commerce/test-meta-types.mjs \
  --output /tmp/domainspec-api-example
```

The output directory must be absent. Then run the new adapters against those
actual generated modules:

```sh
node node_modules/@cyberalchemy/alchlang/examples/api-connections/connections.test.mjs \
  --generated-root /tmp/domainspec-api-example/generated-1-js \
  --example-root node_modules/@domainspec-v2/cli/examples/reconciled-commerce
```

The local request body is `"1"`: a JSON decimal string, because this exact
Interface's request is UInt64. The successful wire response is:

```json
{"id":"1","net":"93","fee":"5"}
```

The native result is `{id: 1n, net: 93n, fee: 5n}`. The supplied service computes
`net` through the generated `commerce:total` Calculation, computes `fee` through
`billing:total`, and calls generated `mappingSummary` to produce the Interface
response. These feature-qualified Calculation identities remain distinct despite
both exporting `calculateTotal` in their own modules.

The runner also exercises unsupported versions, invalid request/result shapes,
nonmatching routes, a missing service value, remote HTTP errors, wrong content
type, response byte limits, transport cancellation, and an identity above
JavaScript's safe Number range. Invalid requests reach neither the service nor
fetch. All transport responses are supplied in memory.

## Attach it to your own host

Import your selected generated Interface and the provided handwritten helper.
Instantiate `createFindHttpHandler({api, service})`, where `service.find` is your
implementation of the Interface's member. The handler accepts this framework
independent object:

```js
const response = await handle({
  method: request.method,
  path: request.path,
  headers: {"x-interface-version": requestedVersion},
  body: rawUtf8JsonBody,
});
// Copy response.status, response.headers and response.body to your host response.
```

Here `request` and the response writer belong to your existing host. Apply your
host's authentication/authorization and bounded body reader before calling this
handler. This guide does not instantiate a server. The example's `POST
/orders/find` route is a deliberate choice in the handwritten transport adapter;
it is not inferred from the M09 Interface or a claimed generated endpoint.

The handler checks version eligibility, parses the body and normalizes it with
`api.endpointValues.find.request.normalize`. It invokes `service.find` only
with the normalized request. It validates the returned value with
`api.endpointValues.find.result.normalize`, then encodes bigint as decimal
strings. Unsupported versions return 409; invalid requests return 400; malformed
service results return 502. Your host can choose a different documented error
mapping when you attach it.

Use strings for UInt64 on the wire. Passing `9007199254740993` as a JavaScript
Number has already lost precision; pass `"9007199254740993"` and let the
normalizer construct the exact bigint.

## Call an external API

`createFindHttpClient` is a handwritten adapter implementing the same generated
Interface contract over a supplied fetch function. Its inputs include an explicit
endpoint, deadline and version:

```js
import * as api from "./generated/application/interfaces/api.js";
import {createFindHttpClient} from "./examples/api-connections/connections.mjs";

const remote = createFindHttpClient({
  api,
  baseUrl: process.env.ORDER_API_BASE_URL,
  fetchImpl: fetch,
  version: "1.0.0",
  timeoutMs: 5000,
});
// Calling remote.find("1") performs transport through the supplied fetch.
```

The example runner supplies an in-memory fetch adapter instead of the platform
`fetch`. Selecting an environment reference does not discover an endpoint or
provide credentials. Bind those through your own approved configuration and
authentication adapter; credentials are not placed in source examples.

The client normalizes the request before fetch, encodes UInt64 exactly, sends the
explicit method/path and Interface version, checks HTTP status and JSON content
type, enforces a declared response byte limit, and validates the result through
the generated Interface normalizer. It uses an AbortController deadline; the
supplied transport must honor that signal. An HTTP failure, aborted transport or
malformed result remains an error. The helper does not retry requests or infer
idempotency.

This client's JSON body reader rejects an oversized result after reading the
text. If your host requires a memory bound while streaming, supply a bounded
streaming transport/body reader as a separate adapter obligation.

## Declare inbound and outbound intent in AlchLang

The installed `examples/application-v1/typescript/commerce.alch` contains the
following real declaration shapes. These are selected excerpts; copy its
complete source and companion directory to retain its Rule meanings, typed
mappings, evidence references and runtime selection.

```alchlang
interface OrderApi:
  kind external
  version 1.0.0
  compatibility exact
  contract SubmitRequest:
    id UInt64
    accepted Bool
  contract Summary:
    id UInt64
    accepted Bool
  exposes SubmitOrder:
    request SubmitRequest
    result Summary

mapping RequestToOrder:
  input payload OrderApi.SubmitRequest
  target Order
  total true
  field id <- payload.id
  field accepted <- payload.accepted
mapping OrderToSummary:
  input result Order
  target OrderApi.Summary
  total true
  field id <- result.id
  field accepted <- result.accepted

mapping ProviderRequest:
  input request OrderApi.SubmitRequest
  target OrderApi.SubmitRequest
  total true
  field id <- request.id
  field accepted <- request.accepted
mapping ProviderResponse:
  input result OrderApi.Summary
  target OrderApi.Summary
  total true
  field id <- result.id
  field accepted <- result.accepted

inbound-endpoint SubmitHttp:
  HTTP POST "/orders"
    -> request OrderApi.SubmitRequest
    -> operation SubmitOrder
    -> response OrderApi.Summary
outbound-call ProviderCall:
  operation SubmitOrder
    -> request OrderApi.SubmitRequest
    -> external-api PaymentGateway
    -> response OrderApi.Summary
```

The external API companion explicitly resolves `PaymentGateway` to its domain
Interface and backend contract, selects both mappers, the integration kernel,
provider realization, authentication references where declared, and failure
translation. Source declarations alone do not establish those bindings. The
lowerer checks exact authored coverage, operation/type identity, mapping
identity and totality, and kernel/provider agreement. Missing, stale or mismatched
companions reject.

Use the actual public CLI and helper when you check a copied complete example:

```sh
alchlang check /absolute/path/commerce.alch \
  --application-bindings commerce.alch.application.json
alchlang build /absolute/path/commerce.alch --out /absolute/path/new-generated \
  --application-bindings commerce.alch.application.json
alchlang verify /absolute/path/commerce.alch --out /absolute/path/new-generated \
  --application-bindings commerce.alch.application.json
```

```js
import {checkApplicationFile} from "@cyberalchemy/alchlang";
const report = await checkApplicationFile("/absolute/path/commerce.alch", {
  companion: "commerce.alch.application.json",
});
```

The companion option is relative to the source directory. This commerce example
selects the larger PostgreSQL/NATS/HTTP provider pack and its explicit runtime
bindings. Check/build form and verify current artifacts; their
`runtime_guarantees_observed: false` result is not a provider execution receipt.
That pack is a separately scoped application runtime choice. The small
HTTP-shaped adapter example above needs no database, messaging service or
listener.

## Open Questions

Root qualification owns the exact newly installed package and freshly generated
native witnesses. Own-host authorization, production transport error policy,
streaming body bounds, provider credentials, persistence and real external API
behavior require explicitly selected bindings and their own tests. This guide
contains no live provider, hosting, TDE or EVF claim.
