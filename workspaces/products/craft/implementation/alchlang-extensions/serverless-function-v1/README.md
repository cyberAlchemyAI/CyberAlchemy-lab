# One AlchLang file, one HTTP function

[quantity-price.alch](quantity-price.alch) is the complete authored function unit.
It owns records, query/calculation logic, ontology meanings, boundary schemas,
conversions, guards, outcome branches, snapshot integration, HTTP statuses,
authentication references, runtime target, and limits. It requires no authored
adapter JavaScript or DomainSpec JSON sidecar. Those artifacts are generated.

## Build and run

From the AlchLang implementation directory:

```sh
npm run build
node dist/cli.js check ../extensions/serverless-function-v1/quantity-price.alch
node dist/cli.js build ../extensions/serverless-function-v1/quantity-price.alch --out /tmp/quantity-price-function-new
```

Build requires the existing DomainSpec 1.0.0 exact UInt64 realization and TypeScript
toolchain. Output must be a new directory with an existing parent. No force option
is supported. `manifest.json` is written last; an interrupted/incomplete output
without that completion marker must not be treated as a completed bundle.

The resulting bundle runs without installing npm dependencies:

```sh
# Supply QUOTE_API_TOKEN through your runtime environment or secret manager.
node /tmp/quantity-price-function-new/server.mjs
```

`HOST` defaults to `127.0.0.1`; `PORT` defaults to `3000`. The generated module also
exports `handler(request, env)` and `invoke(input, env)`. The HTTP handler enforces
authentication; direct `invoke` is a trusted in-process API. The first target is
Node >=26.8.1 using the Web Request/Response API and a Node HTTP launcher. Runtime
API references: [Node globals](https://nodejs.org/api/globals.html#class-request)
and [Node HTTP](https://nodejs.org/api/http.html#serverrequesttimeout).

For a request body, use `{ "request": <quote request>, "snapshot": <price snapshot> }`
from the predecessor [fixtures](../medusa-quantity-price-v1/fixtures.json). Send it
to `POST /quote` with `Content-Type: application/json` and bearer authentication.
Quantity 15 selects the $8.00 tier and returns an exact $120.00 subtotal.

## Everything application-owned is in source

| Declaration | Meaning |
| --- | --- |
| `profile function-v1` | Selects the complete-function compiler |
| `entity`, `query`, `calculation` | Existing domain semantics lowered through DomainSpec |
| `ontology` | Inline meaning, identity and property selectors; generates the sidecar |
| `schema` | Closed input, integration-result and output structures with constraints |
| `integration` | Provided/HTTP transport, output schema, selectors, environment references and bounds |
| `flow` | Named values, integration reads, guards, branching and generated query/calculation calls |
| `endpoint` | Target/runtime, HTTP entry, bearer-secret reference, limits and result/error statuses |

For this module the integration uses `input.snapshot` when supplied. Otherwise it
performs an HTTPS GET to `PRICE_SNAPSHOT_URL`, adds the declared `variant_id` query
parameter, and uses `PRICE_SNAPSHOT_TOKEN` as a bearer secret. The response must
match `PriceSnapshot`; the flow checks the requested variant and price-set
consistency. This is an explicit snapshot-provider contract, not a claim that
Medusa has a native endpoint with this response. A live provider has not been
connected. To require remote data exclusively, declare `http-get` and remove the
`provided` clause. Transport selection and its effect boundary are visible in source.

Secret values and endpoint environment values are injected at invocation time.
The build never reads them or embeds them. HTTP uses GET, refuses redirects, and
bounds response bytes and timeout. The endpoint bounds request bytes and time to
read the body. Output is validated against the declared schema before serialization.

The exact-integer query and calculation remain generated DomainSpec code. General
runtime primitives implement decimal conversion, collection transformations and
branch evaluation. There is no application-specific adapter selected by a hidden
Medusa opcode. Changing the source currency changes behavior, as a regression test
proves.

## Evidence and construction state

The four function tests cover all 20 predecessor pricing fixtures through both
invoke and HTTP, a real loopback call to the generated launcher, source-directed
currency changes, auth, malformed input, overflow, provided-vs-remote selection,
upstream failures, schema mismatch, query parameters, secrets, body limits,
timeouts, source diagnostics and refusal to overwrite an output directory.

The earlier 120-case Medusa repository run remains predecessor evidence. This
successor tests behavior against its 20 named fixtures; it does not claim to have
rerun Medusa's database suite or connected a live service.

[DESIGN.md](DESIGN.md) owns the prototype definitions and product/business
scaffolds. Selected ontology dependencies are the `ontology` declaration and
property selectors inside `quantity-price.alch`; they remain local scaffolds.
The tested compiler source, generated bundle and evidence are bound in
`candidate.json`. Product approval is not recorded.

Product construction frontier: locally tested function profile and complete
pricing function. Operational support: toolchain/tests are local to this task;
cloud provisioning, live snapshot integration, secrets and publication belong to
future environment/product owners and are deferred. They do not block this local
construction result. Earlier candidate snapshots are historical; their digests
are not rewritten when the compiler changes.

## Open questions and limits

The target packages a Node HTTP function; no Lambda/Workers/provider-specific
provisioner or deployment has been implemented or invoked. The bounded v1 profile
supports one POST endpoint, read-only snapshot integrations and no retries or
write-side effects. Schemas validate at runtime; name/operator/integration
references validate at build time. Full expression type inference, arbitrary
JavaScript, recursive user functions, provider SDKs, fractional quantities, taxes,
price lists and other currencies in this particular pricing contract are outside
this candidate.
