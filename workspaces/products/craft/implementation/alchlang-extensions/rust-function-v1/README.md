# Native Rust pricing candidate

The complete pricing module now compiles to a Rust library and native executable. [quantity-price.alch](quantity-price.alch) retains the business declarations from the Node example and changes only its deployment target/runtime clauses to `rust-http` / `rust>=1.94`.

See [the Rust guide](../../alchlang/docs/RUST-FUNCTIONS.md) for commands, architecture and target limits. The tested executable is [evidence/bundle/alch-function](/home/vlad_/projects/cyberAlchemy-v2/language/capabilities/alchlang/plans/general-compiler-v1/extensions/rust-function-v1/evidence/bundle/alch-function); its generated library is [src/lib.rs](/home/vlad_/projects/cyberAlchemy-v2/language/capabilities/alchlang/plans/general-compiler-v1/extensions/rust-function-v1/evidence/bundle/rust/compositions/function/src/lib.rs). The bundle contains no JavaScript files. Cargo dependencies are pinned and locked, and the Linux x86_64 binary was compiled with Rust 1.94.0.

## Validation

111 Alch tests and 46 focused DomainSpec tests passed. Native tests execute all 20 pricing fixtures, compare ordinary and traced results, reverse input row order, check arithmetic overflow and invalid data, exercise authenticated loopback HTTP responses and size limits, verify manifest hashes, and reject overwriting an existing bundle. JSON integer spellings such as 15 and 15e0 agree.

The final [product test](/home/vlad_/projects/cyberAlchemy-v2/language/capabilities/alchlang/plans/general-compiler-v1/extensions/rust-function-v1/evidence/product-test.json) records standard DomainSpec Rust artifact verification and all 20 native result/trace comparisons. [The native trace](/home/vlad_/projects/cyberAlchemy-v2/language/capabilities/alchlang/plans/general-compiler-v1/extensions/rust-function-v1/evidence/quoted-trace.json) records tier10 at USD 8.00 and subtotal USD 120.00 for quantity 15. Public CLI check/trace receipts are also in `evidence/`. No remote provider or Medusa oracle was contacted.

`validate.mjs` creates evidence with exclusive writes and requires a fresh destination. `candidate.json` binds the selected source, generated compiler, tests, docs and evidence bytes. Earlier candidates are retained unchanged.

## Construction and operational support

Product construction reached a tested local Rust candidate. Product approval and ontology admission are not recorded. Publication, cross-platform release and provider deployment are deferred operational support owned by the release/deployment owner; none blocks this local prototype stage.

## Open Questions

The current binary is specific to its build host. RFC 3339 timestamp handling and the bounded common regex subset are explicit Rust target limits. Native traces use their own schema and exact JSON integers, requiring lossless parsing for full UInt64 events. Live provider interoperability, cross-compilation, whole-function formal proof, signed runtime evidence and deployment remain future work. See [PLAN.md](PLAN.md).
