# One source, one project build

`declarative-function-v1` now produces an opt-in `domainspec.project/v2` project. Its declared `compositions/function.json` contains the typed mappings, queries, rules, assertions and result cases; core record/calculation selectors and field bindings; boundary schemas, integrations and endpoint; original source; and derived ontology.

```text
.alch declarations
  -> typed composition + core DomainSpec nodes
  -> project source manifest
  -> validated compiled graph and compilation certificate
  -> DomainSpec build / verify
  -> portable HTTP bundle + exact file manifest
  -> local invocation trace bound to that manifest
```

DomainSpec checks the complete composition when compiling the project. Calculation arguments resolve to typed UInt64 inputs and results. Record field bindings preserve property identities, types and meanings. All behavioral dependencies, endpoint types, integration selectors and ontology reference roles must close. Unknown clauses, missing sources and unsupported targets reject.

The normal TypeScript exact UInt64 project build emits `compositions/function/{behavior.mjs,composition.json,composition-trace.json,ontology.json,function.json,bindings.json,source.alch}`. Alch consumes those verified artifacts and supplies the transport and tracing runtimes, core API wrapper and Node launcher. The portable manifest hashes those runtimes together with the project certificate and build receipt. A local invocation trace binds to the complete manifest.

```sh
node dist/cli.js check ../extensions/unified-project-v1/quantity-price.alch
node dist/cli.js build ../extensions/unified-project-v1/quantity-price.alch --out /tmp/new-unified-quote
node dist/cli.js explain ../extensions/unified-project-v1/quantity-price.alch Cheapest
node dist/cli.js trace ../extensions/unified-project-v1/quantity-price.alch --input ../extensions/unified-project-v1/input.json
```

The source contains the integration configuration. Deployment credentials remain environment references. No handwritten application mapper, flow or adapter is needed. Existing project/v1 inputs retain their previous compilation format.

## Scope and Open Questions

This prototype supports one declarative composition per project. Targets are Node HTTP / TypeScript exact UInt64 and [native Rust HTTP](RUST-FUNCTIONS.md). Core meta-type obligation counts remain core counts; the certificate reports composition validation separately. Legacy whole-project instantiation and checked assurance interchange explicitly reject this extension until they cover its formalization scope.

The compilation certificate records typed dependency checks and exact artifacts. It does not prove business meaning or reparse Alch source independently; Alch owns source parsing and lowering. The ontology remains a generated scaffold. Product approval, ontology admission, signed runtime attestation, meta-type factory automation and provider deployment remain separate future work.
