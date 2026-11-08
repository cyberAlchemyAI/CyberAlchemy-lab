# Declarative quantity-price candidate

This prototype replaces application flow steps with DomainSpec-generated Mapping, Query and Rule behavior. Existing exact Calculation generation supplies the subtotal. The complete authored input is `quantity-price.alch`, including shapes, ontology meanings, integration and endpoint bindings. No application adapter or authored TypeScript is required.

The query keeps every eligible price for which no cheaper eligible price exists. Exactly one witness yields a quote, no witnesses yields no_price, and multiple witnesses yield ambiguous_price with sorted identities. Money uses UInt64 minor units; zero, large values and overflow retain the predecessor's semantics. Supported scope remains explicit USD base pricing with bounded quantity, no price lists or pricing rules, and a validated snapshot of at most 1000 prices.

See [the implementation plan and construction boundary](PLAN.md) and [the language guide](../../alchlang/docs/DECLARATIVE-FUNCTIONS.md). The deferred Meta-Type Factory proposal remains in ../current-meta-type-fit-v1/FUTURE-DEVELOPMENT.md.

## Validation

`evidence/alch-tests.log` records the full Alch regression run. The new tests exercise all 20 prior pricing fixtures through invoke and HTTP, reversed input order, exact values, duplicate/range/provider identity failures, malformed amounts, generated behavior changes, compile-time diagnostics, output-case ambiguity, integration failures, authentication, time/size limits and a real loopback Node launcher.

`evidence/domainspec-tests.log` records focused DomainSpec checks, including the new generator tests and existing exact arithmetic, typed closure, Rust lowering and system-integration tests. These are local product tests. The historical 120-case Medusa repository/PostgreSQL oracle was not rerun for this candidate, and no live provider or cloud deployment was exercised.

`candidate.json` binds the selected source/dependency bytes, generated bundle and test logs. These are candidate product receipts, not product approval or operational authority. Prior frozen extension evidence is not refreshed.

## Open questions

Composition currently has a separate DomainSpec contract and trace. Full project-graph certification of this extension, other language targets, broader Medusa pricing features and hosting deployment remain future work. No new meta-type is justified by the implemented slice. Product approval is pending owner review of this candidate.
