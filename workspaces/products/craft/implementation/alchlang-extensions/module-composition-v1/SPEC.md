# Checkout composition definitions and ontology prototype

A **module import** names a relative Alch source and exposes its boundary types under one alias. A **module invocation binding** relates a caller input selector to that imported endpoint's exact input/output types and selects local generated execution or HTTPS POST. An **import closure** is the finite acyclic source graph captured and packaged by the build. These are prototype language definitions, not admitted global ontology terms.

The product prototype lets an author compose independently deployable Alch functions without handwritten orchestration. Its business prototype quotes one item quantity and one selected eligible shipping method in USD, then adds the amounts exactly. It is not a complete cart, tax, inventory reservation or checkout payment engine.

## Product and business scaffolds

| Definition | Meaning and relation |
| --- | --- |
| Pricing import | Owns quantity-price input/output constraints and generated pricing behavior |
| Shipping import | Owns selected-option eligibility and exact shipping fee quotation |
| Envelope | Uses imported input types rather than locally duplicated schemas |
| ItemPrice / ShippingPrice | Bind caller input records to local or HTTP module invocation |
| CheckoutAmounts / CheckoutTotal | Define exact subtotal/fee operands and checked addition |
| NoPrice / AmbiguousPrice / ShippingUnavailable / Quoted | Define the four business result cases |
| QuoteCheckout | Checks identities and completeness, then selects exactly one result |
| Checkout endpoint | Exposes the composed quote through authenticated HTTP |
| modules.json / parent manifest | Bind imported source and executable artifact closure |

The caller's derived ontology contains imported boundary schema scaffolds, invocation bindings and behavior references. `module_imports` records child source hashes and interfaces; child bundles retain their own full derived ontologies. Imported schema locations point to the caller's import declaration, while child definitions remain available in the child scaffold. These records remain agent navigation scaffolds, not registry admission or formal proof.

## Testable candidate

Sources are `checkout-quote.alch`, `checkout-quote-http.alch`, `quantity-price.alch` and `shipping-quote.alch`. The two checkout sources differ in invocation bindings; pricing and selected-option shipping remain independently buildable. All mappings and calculations pass through DomainSpec's existing typed compiler/generators.

The test surface compares Node and native Rust using complete expected outcomes, controlled integration responses, prepared requests and module-qualified decision events. Cases include exact totals/overflow, absent prices, ambiguity, unavailable selected shipping, duplicate options, malformed provider data, request/response identity mismatches, typed invocation rejection and early failure. The standalone portable fixtures remain a regression surface.

Construction stages: prototype definitions and derived scaffolds -> module business/API/source prototypes -> checked DomainSpec caller/child contracts -> packaged target realizations -> current product-test evidence -> one exact candidate. Product approval is not implied by a passing report.

## Construction and operational residue

Product construction is runnable locally with the existing Node and offline Rust toolchains. No operational task blocks this candidate. The release/deployment owner owns live provider testing, cloud packaging, credential provisioning, publication and deployment; these affect no current prototype stage and remain deferred. Automatic meta-type factory fallback remains future construction.

## Open Questions

The complete language semantics, boundaries and unresolved work are recorded in [Module composition](../../alchlang/docs/MODULE-COMPOSITION.md). In particular, remote implementation identity and conditional invocation are not solved by this prototype.
