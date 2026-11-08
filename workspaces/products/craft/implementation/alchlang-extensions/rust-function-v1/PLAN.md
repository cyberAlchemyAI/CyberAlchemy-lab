# Native Rust function prototype

Product construction frontier: compile the existing declarative composition and typed core bindings into native Rust through the DomainSpec project build. Runnable locally with Rust 1.94 and cached Cargo dependencies.

D65 stages: retain existing language definitions and ontology scaffolds; product prototype is the same complete pricing function; business prototype retains inclusive USD base-price quotation; DomainSpec prototype selects rust-http/rust>=1.94; compiled prototype binds native artifacts in its project graph; implementation is a Cargo library, HTTP executable and local trace command; test an exact candidate against all 20 pricing fixtures and rejection cases. No new meta-type or operational admission is proposed.

Implementation files: DomainSpec src/generation/rust-composition.ts and rust-function-runtime.ts, src/input/project-composition.ts, src/generation/project-build.ts, focused tests; Alch src/rust-function-builder.ts, domainspec-project-writer.ts, function-profile.ts, function-builder.ts, cli.ts, focused tests; corresponding dist files, documentation, and this extension's evidence. Historical candidates are unchanged.

Operational support: publication and provider deployment are deferred, owned by the release/deployment owner, and affect no current prototype stage. Local Cargo builds and loopback HTTP tests are validation prerequisites. No remote business service is required.

## Open Questions

Rust trace event representation, portable binary compatibility and provider packaging require explicit scope. Checked assurance interchange remains unsupported for compositions. Local tests do not imply product approval, ontology admission or deployment authority.
