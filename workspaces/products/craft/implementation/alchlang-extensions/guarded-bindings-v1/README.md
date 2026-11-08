# Guarded checkout module candidate

Checkout calls Shipping only when Pricing returns `quoted`. The complete
[local example](checkout-quote.alch) and [HTTP example](checkout-quote-http.alch)
include imports, schemas, integrations, rules, mappings, exact-money calculation,
result and endpoint declarations. No TypeScript is embedded in the Alch files.

```alch
  bind pricing from ItemPrice
  bind shipping from ShippingPrice when HasPrice
```

See [semantics](SPEC.md), [construction plan](PLAN.md), and
[language documentation](../../alchlang/docs/GUARDED-BINDINGS.md).

Run `node validation/run.mjs <new-output-directory>` with Node 26.8.1 and the
local DomainSpec 1.0.0 compiler installed. It builds both targets and checks guarded
checkout plus existing standalone pricing/shipping regressions.
`validation/assert-skips.mjs` verifies the zero-call requirements in its reports.
`validation/http-smoke.mjs` tests the generated Node handler and native loopback
HTTP endpoint using provided inputs.

Status and byte-bound test evidence are recorded in candidate.json after tests.
Product approval and deployment remain separate; no provider connection is needed.

Open questions: [SPEC.md](SPEC.md#open-questions).
