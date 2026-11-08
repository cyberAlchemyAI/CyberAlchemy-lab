# Typed module composition prototype

Product construction frontier: extend the tested portable functions with imported boundary types and explicit local/HTTP function invocation, then exercise one checkout quote on Node and Rust. Runnable now: definitions, linker, typed validation, generated runtime composition and controlled product tests. No operational prerequisite blocks this work.

Definitions: a module import binds one relative Alch source and its checked interface; a module binding selects local generated invocation or HTTP POST using that interface; a checkout quote combines one quantity-price subtotal and one selected eligible shipping fee with exact UInt64 addition. Imports form a finite acyclic graph. Errors stop binding evaluation in source order; business unavailability is a typed successful result. Modules do not share mutable invocation state.

D65 construction: these definitions -> derived module/interface ontology scaffolds -> pricing and shipping business prototypes -> imported DomainSpec boundary contracts and separately checked child compositions -> generated Node/Rust bundles -> checkout fixture and transport evidence -> one exact candidate. Product approval and all operational authority remain separate.

Exact implementation scope: Alch implementation/src/module-types.ts and module-source.ts (new), declarative-profile.ts, function-profile.ts, function-runtime.ts (model type), boundary-runtime.ts, function-builder.ts, rust-function-builder.ts, derived-ontology.ts, invocation-trace.ts, conformance.ts, trace-command.ts if needed; corresponding dist and tests; DomainSpec CLI src/input/project-composition.ts and src/generation/rust-composition.ts/rust-function-runtime.ts, focused tests; language docs and this extension. Preserve existing portable example sources and historical candidate records.

Operational support: release/deployment owner owns cloud packaging, provider credentials, live provider interoperability, publication and deployment. Affected current prototype stage: none. All are deferred residue. No remote provider requests are part of this implementation. Automatic meta-type factory fallback remains future construction.

## Open Questions

This bounded version imports boundary schemas and callable endpoints; general reusable behavior declarations, conditional invocation, live remote implementation identity, cross-project package registries and stateful effects remain future work. Import closure must be packaged and hashed, not silently resolved at runtime.

Additional compiler scope: `projects/domainspec-v2/impl/cli/src/typed-backend/declarative-function.ts` evaluates calculation arguments before emitting the invocation-start event, matching Rust call-by-value observation order; its existing portable test file covers invalid arguments. Imported source closure and child manifest hashes are included in conformance.

## Tested construction frontier

Completed: import/schema linking, source-closed module packaging, local and HTTP invocation, checkout and selected-shipping prototypes, derived caller/child scaffolds, namespaced traces and product-test evidence. The final report passes 106 cross-target cases (33 checkout, 73 standalone regressions); the loopback HTTP/trace check passes 15 cases. Regression evidence records 120 Alch tests, a subsequent five-test module run, and 50 focused DomainSpec tests.

No causal construction blocker remains for this local candidate. Release/deployment-owned operational support remains deferred and affects no current prototype stage. Product approval and operational authority are not recorded.
