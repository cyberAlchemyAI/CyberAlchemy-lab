# Typed checkout module composition

`checkout-quote.alch` imports pricing and shipping contracts, invokes their generated implementations locally, and combines exact amounts. `checkout-quote-http.alch` selects authenticated HTTP calls through its bindings. The example input produces a 120.00 USD item subtotal plus 3.50 USD shipping: **123.50 USD**.

Read [SPEC.md](SPEC.md) for definitions and ontology scaffolds, [PLAN.md](PLAN.md) for construction scope, and [the language guide](../../alchlang/docs/MODULE-COMPOSITION.md) for syntax and limits.

After building DomainSpec and Alch with the pinned Node toolchain, run from this extension:

```sh
node validation/run.mjs /tmp/new-module-conformance
node validation/http-smoke.mjs /tmp/new-module-conformance/checkout-quote /tmp/new-module-http.json
node validation/verify.mjs
```

The runner builds both targets for the local and HTTP checkout variants and reruns the standalone portable fixtures. HTTP responses and credentials are synthetic fixtures; no provider connection is made. `validation/report.json` records the tested run, and `candidate.json` binds the selected sources and evidence. Generated executable bundles are local build outputs; retained artifact manifests identify their tested bytes.

## Open Questions

See the [language guide](../../alchlang/docs/MODULE-COMPOSITION.md#open-questions). This candidate does not grant product approval, ontology admission, release, publication or deployment authority.
