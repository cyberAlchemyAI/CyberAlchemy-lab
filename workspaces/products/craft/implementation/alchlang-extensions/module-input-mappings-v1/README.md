# Checkout with typed module-input mappings

The [local checkout](checkout-quote.alch) and [HTTP checkout](checkout-quote-http.alch)
construct shipping input from pricing output and customer shipping preferences.
All bindings and mapping behavior are expressed in Alch.

```alch
integration ShippingPrice:
  transport module-local
  module Shipping
  input ShippingInput
  output Shipping.ShippingResponse
  timeout-ms 10000
  max-bytes 262144
```

`ShippingInput` combines a `ShippingRequest` Mapping with an optional snapshot.
`ShippingRequest.request_id` comes from `pricing.request_id`. Shipping's guard
skips both mappings when pricing cannot return a quote.

See [language documentation](../../alchlang/docs/MODULE-INPUT-MAPPINGS.md),
[specification](SPEC.md), [construction plan](PLAN.md), and [sample input](input.json).

Run `node validation/run.mjs <new-output-directory>` to build Node/Rust candidates
and check controlled scenarios, then `node validation/assert-inputs.mjs
<output-directory> <new-receipt.json>` to verify mapped bodies and skipped work.
`validation/http-smoke.mjs` checks the Node handler and native loopback endpoint.
Final evidence is recorded in candidate.json and validation receipts.

Open questions: [SPEC.md](SPEC.md#open-questions).
