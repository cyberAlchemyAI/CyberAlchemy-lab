# Typed function modules

A portable Alch function can import another function's boundary schemas and invoke its endpoint through an explicit integration binding. Mappers, rules, calculations and result selection remain declarative. Each child still compiles through DomainSpec and can be built as its own function.

```alch
import Pricing from "./quantity-price.alch"

schema Envelope:
  pricing: Pricing.Envelope

integration ItemPrice:
  transport module-local
  module Pricing
  input input.pricing
  output Pricing.Quote
  timeout-ms 10000
  max-bytes 262144
```

A result binds its typed output with `bind pricing from ItemPrice`. `Pricing.Envelope` and `Pricing.Quote` are imported types, not copies maintained by the author. The linker derives namespaced schemas, retaining optionality, nullability, constants, patterns and limits. Imported core/behavior declarations are not exposed as arbitrary source-level functions in this version.

For HTTP invocation, change the binding to:

```alch
integration ItemPrice:
  transport module-http
  module Pricing
  input input.pricing
  output Pricing.Quote
  url-env PRICING_MODULE_URL
  secret-env PRICING_MODULE_TOKEN
  timeout-ms 10000
  max-bytes 262144
```

This sends an authenticated HTTPS POST with the selected input record as JSON. Redirects and URL credentials are refused. The response must satisfy the imported output schema, and its HTTP status must match the imported endpoint's declared business status. A declared business result can use HTTP 404 or 409; transport failures remain errors. An unexpected status produces `FUNCTION_INTEGRATION_STATUS`; invalid output produces `FUNCTION_INTEGRATION_SCHEMA`.

## Checkout example

`../extensions/module-composition-v1/checkout-quote.alch` imports quantity pricing and a selected-option shipping quote. The caller supplies each module's input record. Checkout verifies request/response identities, preserves no-price, ambiguity and shipping-unavailable outcomes, and adds subtotal and shipping fee with checked UInt64 arithmetic. Its completion guard requires monetary fields before calculating; missing amounts cannot become a zero-priced quote.

For the supplied example, pricing returns a subtotal of 12000 cents and shipping returns 350 cents. Checkout returns 12350 cents (`123.50` USD). The shipping quote is a separate module derived from the earlier eligibility example; the historical shipping-options source remains unchanged.

```sh
node dist/cli.js check ../extensions/module-composition-v1/checkout-quote.alch --target rust-http
node dist/cli.js build ../extensions/module-composition-v1/checkout-quote.alch --out /tmp/new-checkout-node
node dist/cli.js build ../extensions/module-composition-v1/checkout-quote.alch --target rust-http --out /tmp/new-checkout-rust
node dist/cli.js ontology ../extensions/module-composition-v1/checkout-quote.alch
node dist/cli.js trace ../extensions/module-composition-v1/checkout-quote.alch --input ../extensions/module-composition-v1/input.json
```

The matching `checkout-quote-http.alch` keeps the business rules and chooses HTTP for both imported calls. Conformance uses controlled responses and does not contact a provider.

## Compiler and package boundaries

Imports resolve at build/check time relative to their importing file. All source files must remain inside the entry file's directory after resolving symlinks. Cycles, duplicate aliases, declaration/alias conflicts, missing types and schema-incompatible invocation bindings fail checking. Imports require `node-rust-v1`; the graph is bounded to depth 8, 32 visits, 1 MiB per source and 4 MiB in total. There are no network imports or runtime filesystem resolution.

Alch checks every child composition using DomainSpec and derives the caller's imported schemas from those child models. DomainSpec validates the caller's invocation input/output bindings and imported constraints. Each module retains its own DomainSpec project/certificate; this is not one newly admitted multi-composition DomainSpec project. Alch owns assembling and hashing the executable module closure.

Bundles contain `modules/<Alias>/` for imported generated artifacts and a `modules.json` lock containing child source and manifest hashes. The parent manifest covers those files recursively and is written last. Native Rust links child generated libraries into the parent executable; it does not spawn child processes or embed JavaScript. Node imports the packaged child modules. Copied child launchers remain independently runnable, but local parent calls use their libraries.

Local calls use child schema validation and generated behavior without crossing the child's HTTP authentication boundary. The parent endpoint supplies the public authentication boundary. Deployment metadata lists the parent auth reference plus environment references reachable through local calls. HTTP module bindings require their own declared URL/token references and do not require the remote module's provider credentials.

## Invocation and evidence

Bindings run sequentially in authored order. A raised error stops later bindings. An unguarded binding still runs after a typed unavailable result. Use `bind shipping from ShippingPrice when HasPrice` to skip it explicitly. The parent evaluates its business result cases after the bindings complete. Compensation remains future work.

Local bindings bound serialized input/output sizes and asynchronous waiting. Neither runtime preempts synchronous computation; existing schema and collection limits bound the supported computation. Local deadline failures use `FUNCTION_MODULE_TIMEOUT`, and their trace capture is marked incomplete because cancellation can omit child observations. HTTP timing and cancellation under live network conditions are outside the controlled conformance claim.

Traces name child paths such as `Pricing` and `Shipping`; nested paths are qualified. Root selection and root declaration summaries exclude child events with colliding names. Child source definitions remain associated with their own events. Conformance compares ordered module events, decisions, requests, outputs and expected errors, and verifies that both bundles contain the captured import sources. Truncated/incomplete capture cannot pass.

## Open Questions

Remote schema/status checking does not prove that a deployed service runs the imported implementation or satisfies its relational business postconditions. Remote implementation identity, cross-project package registries, general behavior imports, stateful effects, cloud packaging and whole-program proofs remain future work. Product approval, ontology admission, publication and deployment are separate decisions.

## Conditional invocation

`bind shipping from ShippingPrice when HasPrice` invokes a module only when its
Boolean guard holds. DomainSpec checks output availability and generates both Node
and Rust behavior. See [guarded bindings](GUARDED-BINDINGS.md) for the complete contract and examples.

## Module input mappings

`input ShippingInput` selects a typed Mapping that constructs an imported module
argument from the request and earlier binding outputs. See [module input mappings](MODULE-INPUT-MAPPINGS.md)
for typing, guarded availability, runtime validation and open questions.
