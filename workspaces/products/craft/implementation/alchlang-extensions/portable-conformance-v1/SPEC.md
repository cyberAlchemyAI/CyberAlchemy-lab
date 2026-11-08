# Portable function definitions and product prototype

A **portable function** is one declarative Alch source whose checked DomainSpec composition selects the `node-rust-v1` semantic profile. Node and Rust are realizations of the same typed behavior. A **conformance case** is an input, a controlled provider scenario and an independently stated complete outcome. A **conformance report** binds source, cases and generated bundles to finite observations; it grants no approval or deployment authority.

The product prototype answers: can an author keep schemas, business rules, quantified selection, mappers and integration bindings in one Alch file and obtain equivalent behavior on both supported targets? Its testable surface is checking plus two generated HTTP function bundles and a differential report. The business prototypes are base-price quotation and shipping-option eligibility. They are bounded examples, not a complete commerce pricing or shipping engine.

## Product and business ontology scaffolds

The product prototype combines the source module, a portability-bearing typed composition, target manifests, and derived integration/endpoint definitions with their dependencies. DomainSpec owns typed validation and generated mappers; Alch derives the navigation ontology from those authored definitions. Checked project/v2 compositions bind core selectors, boundary schemas and declarative contracts together. These generated records remain scaffolds, not registered or admitted ontology records.

The shipping business scaffold consists of:

| Definition | Meaning |
| --- | --- |
| ShippingChoice | Eligible method identity and exact minor-unit fee |
| Option / ShippingSnapshot | Provider facts, timestamp and bounded option list |
| Request | Country, weight, tracking requirement and optional customer note |
| Eligible | Enabled options satisfying country, inclusive weight and tracking predicates |
| Choice / Choices | DomainSpec mapping from eligible provider rows to typed domain choices |
| Available | An eligible choice exists |
| AllTracked | Every eligible option provides tracking, including vacuous truth for an empty set |
| SelectShipping | Identity/uniqueness/range constraints and exactly one response case |
| ShippingOptions | Supplied snapshot or bounded authenticated HTTPS GET binding |
| ShippingEligibility | Authenticated POST endpoint and response/error status mapping |

The source defines these relationships through typed references. `alchlang ontology` emits their derived graph; `alchlang explain ... Eligible` returns the relevant authored meaning and dependencies. No new meta type or mapper interpreter is introduced. Automatic meta-type factory fallback remains future development.

The normative profile and runner interface are in `../../implementation/docs/PORTABLE-CONFORMANCE.md`. Complete sources are `quantity-price.alch` and `shipping-options.alch`. Fixtures include exact maximum UInt64, overflow, tie preservation, boundary weights, empty quantifiers, missing/null fields, Unicode ordering, malformed dates/decimals/pattern inputs and controlled integration failures.

## Construction versus operations

Current product-construction work is prototype checking, target generation and reproducible product-test evidence. Its selected dependencies are the two source files, their derived ontology scaffolds and core selector bindings, the DomainSpec composition/generators, and the Alch boundary/build tooling. No ambient ontology registry or epoch is a prerequisite.

Operational support is deferred: release/deployment owner owns packaging, credential provisioning and provider testing; no current construction stage depends on those tasks. Product approval remains an owner decision for an exact tested candidate, and does not authorize deployment.
