# AlchLang function profile v1

An `.alch` compilation unit can now describe a complete HTTP function. Add
`profile function-v1`, keep ordinary entity/query/calculation declarations, and
add the sections below. The compiler produces a dependency-free Node HTTP bundle
through the DomainSpec 1.0.0 exact UInt64 realization.

See the complete [quantity-price source](../../alchlang-extensions/serverless-function-v1/quantity-price.alch)
and its [runnable guide](../../alchlang-extensions/serverless-function-v1/README.md).

## Source grammar

New sections use a named header (`schema Request:`) and flat two-space-indented
clauses. Flow expressions can continue on lines indented by four spaces. Unknown or duplicate clauses fail.
One endpoint is required. Existing non-function profiles remain available.

`ontology Name` accepts `id "SELECTOR"`, `meaning "text"`, optional `identity field`,
and `property field "SELECTOR#field" "meaning"`. The generated sidecar binds the
lowered domain portion to its source digest; the bundle separately binds the full
function source. Every lowered declaration must have its required bindings.

`schema Name` fields use `field: Type` followed by optional constraints:
`optional`, `nullable`, `min N`, `max N`, `const <JSON scalar>`, `pattern "regex"`.
Types are string, identifier, timestamp, integer (safe integer Number), boolean,
a named schema, or `Name[]` / `string[]` / `identifier[]`. Lists require a maximum
length. `min` applies to integers; `max` applies to numbers, string length or list
length. Records are closed: unknown properties and accessors are rejected.

`integration Name` accepts:

```alch
integration Prices:
  transport provided-or-http
  provided input.snapshot
  output PriceSnapshot
  url-env PRICE_SNAPSHOT_URL
  secret-env PRICE_SNAPSHOT_TOKEN
  query variant_id input.request.variant_id
  timeout-ms 3000
  max-bytes 262144
```

Transports are `provided`, `http-get`, or `provided-or-http`. Provided-only bindings
omit URL, secret and query clauses. HTTP-only bindings omit `provided`. The provided
selector must have the output schema type; query selectors must be scalar fields
of the endpoint input. HTTP environment references are uppercase variable names.
`secret-env` is optional. URLs must be HTTPS without embedded credentials, and
redirects are rejected. Limits are required; timeout is 1–30000 ms and body size
is 1–1048576 bytes. HTTP integration is invoked only when the flow reaches `bind`.

`flow Name` supports ordered clauses:

```alch
flow QuotePrice:
  bind snapshot from Prices
  let currency = lower(input.request.currency_code)
  require eq(currency, "usd") else "UNSUPPORTED_CURRENCY"
  return {status: "ready", currency: currency}
```

This grammar example needs corresponding domain, schemas and endpoint to build.
`when <condition> return <expression>` provides a conditional early return; a
final unconditional return is still required. Names resolve in preceding clauses; lambdas have local bindings. Expressions
support literals, dotted references, object/array literals and these operators:

- Boolean/selection: `eq`, `ne`, `lte`, `gte`, `gt`, `not`, `and`, `or`, `present`, `if`.
  `if`, `and`, and `or` evaluate lazily; predicates require Boolean results.
- Exact scalar conversion: `lower`, `uint64`, `decimalToUInt64(value, scale)`,
  `formatDecimal(value, scale)`, `string`. Decimal conversion rejects excess
  fractional digits, malformed values and UInt64 overflow without rounding.
- Collections: `count`, `first`, `map`, `filter`, `every`, `distinct`, `sort`.
  Collection callbacks use `row => expression`; `sort` sorts strings.
- Construction: `merge(object, object)`.
- Generated behavior: `query("DeclaredQuery", rows, parameters)` and
  `calculate("DeclaredCalculation", inputs)`. Target names resolve during build.

There is no general JavaScript evaluation. Expression symbols/operators are checked
at build time; schema and primitive value checks occur at runtime. Missing dotted
properties produce an absent value, which can be tested with `present`.

`endpoint Name` requires target `node-http`, runtime `node>=26.8.1`, method `POST`,
path, input and output schema, flow, `auth-env`, `max-bytes`, `timeout-ms`, and
`error-status`. Repeated `status <result.status> <HTTP code>` and
`error <fault code> <HTTP code>` clauses map results. The timeout bounds request-body
reading; each integration has its own timeout. The runtime also handles routing,
authentication, JSON media type/parse errors, and unexpected failures. Public
handler calls require the declared bearer secret. Direct invocation is trusted.

## Build

```sh
node dist/cli.js check path/to/function.alch
node dist/cli.js build path/to/function.alch --out /tmp/new-function-bundle
```

Output includes `source.alch`, generated domain source and bindings, DomainSpec
project and receipts, compiled domain runtime, `function.json`, `runtime.mjs`,
`index.mjs`, `server.mjs`, `package.json`, `deployment.json`, and a final hash
manifest. `deployment.json` declares environment references and limits; it does
not provision or deploy anything. Existing output directories are refused.

## Open questions

The [function guide](../../alchlang-extensions/serverless-function-v1/README.md#open-questions-and-limits)
owns current target limits, product questions and evidence scope.
