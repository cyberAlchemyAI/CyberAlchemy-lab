# AlchLang function profile v1

Product construction: one authored .alch compilation unit owns domain semantics,
inline ontology bindings, boundary schemas, orchestration, integration selection,
HTTP exposure and deployment requirements. The compiler supplies general runtime
primitives and packages the generated DomainSpec calculation/query implementation.
No application-specific JavaScript or authored JSON sidecar is required.

Prototype definitions: a Function Unit is one source and its transitive compiler
runtime; an Integration is a named typed external/provided input contract; a
Binding selects a transport and environment references; an Entry Point defines
HTTP method, path, authentication, limits, and result mapping. A Portable HTTP
Bundle exposes a Web Request/Response handler and a Node HTTP launcher. Deployable
means packaged and locally executable; it does not mean provisioned or deployed.

Product scaffold: Function Unit declares Schemas, Integration, Flow and Endpoint;
Flow invokes generated DomainSpec Queries/Calculations; Endpoint exposes Flow;
Bundle realizes Unit. Business scaffold: Merchant configures Offers, Caller requests
Quote, Quote reports unique price / missing price / ambiguous price, and does not
commit a sale. These local scaffolds are prototypes, not ontology admission.

Implementation contract: opt-in `profile function-v1`; existing domain sections
retain existing syntax. `ontology` sections replace the authored binding sidecar.
`schema`, `integration`, `flow`, and `endpoint` are new strict sections. Expressions
use literals, references, object/array literals, named primitives, and collection
lambdas; arbitrary JavaScript, dynamic imports, eval, and filesystem calls are not
source constructs. Query/calculation calls resolve statically. Runtime schemas and
primitive checks enforce value contracts; this is not a full static type checker.

Current construction frontier: generic compiler/runtime and migrated pricing flow
are locally tested. Generated handlers, integration failures, source diagnostics,
secret exclusion, limits and predecessor fixture parity pass; the complete AlchLang
suite passes 94 tests. Runnable work in the bounded v1 scope is complete. Product approval is
not recorded. Existing compiler snapshots remain historical after compiler changes.

Operational support: local toolchain and tests are owned by this task and affect
product-test stage only. Cloud provisioning, secret provisioning, live endpoint
selection, publication and deployment belong to environment/product owners and
are deferred; they do not block local construction. No cloud provider is selected.

## Open questions

Provider-specific packaging (Lambda, Workers, etc.) and live Medusa snapshot
extraction need separate targets/contracts. The HTTP integration here consumes the
explicit snapshot schema, not an invented native Medusa API endpoint. See README.md
for actual supported syntax, checks and remaining limits.
