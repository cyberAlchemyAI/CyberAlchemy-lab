# Portable language conformance prototype

Product construction frontier: one explicit node-rust-v1 semantic profile and a reproducible differential report. Runnable locally with the existing compilers and offline Rust toolchain.

Definitions: portable means the same accepted source and well-formed JSON input have the same output, first error, integration request and normalized decision trace in both targets, within the declared profile. Differential evidence is finite test evidence, not a proof for every possible program.

D65 stages: define portable value, optionality, ordering, timestamp, pattern and transport semantics; retain generated ontology scaffolds; product prototype is two complete deployable modules; business prototypes are base-price quotation and shipping-option eligibility; DomainSpec contracts carry the portability profile; compiled graphs bind both targets; implementations supply controlled local transports; an exact tested candidate contains results, source rejections, traces and source/build hashes.

Mutation scope: Alch src/declarative-profile.ts, function-runtime.ts (model type only), boundary-runtime.ts, function-builder.ts, rust-function-builder.ts, cli.ts, new conformance.ts and tests; DomainSpec src/typed-backend/declarative-function.ts, portable-function.ts, src/input/project-composition.ts, src/generation/rust-composition.ts, rust-function-runtime.ts and focused tests; generated dist, docs and this extension. No historical candidate is refreshed.

Operational support: deployment/publication remain deferred, owned by the deployment/release owner, and affect no current prototype stage. Controlled transport fixtures do not access remote services. Factory automation remains future development.

## Open Questions

The portable profile deliberately narrows patterns and timestamps. Transport parity tests observe prepared outbound requests and controlled responses; they do not prove live provider interoperability. Formal proof, product approval and operational authority remain separate.

## Tested frontier

Completed: shared profile and generated contract binding; derived shipping ontology scaffolds; two complete module sources; check-time target rejection; controlled transport comparison; current finite product-test evidence. The conformance report passes 73 cases. The regression evidence records 115 Alch tests, a subsequent five-test focused run, and 49 focused DomainSpec tests.

Exact additional implementation files: `implementation/src/invocation-trace.ts` shares calculation failure normalization; `projects/domainspec-v2/impl/cli/package.json` includes the new portable test in its existing test command; this extension's `validation/run.mjs` reproduces the two-module report.

No causal construction blocker remains for this candidate. Operational residue remains deferred to the release/deployment owner: provider integration, platform packaging, publication and deployment. Automatic meta-type factory fallback is future construction. Product approval is not recorded.
