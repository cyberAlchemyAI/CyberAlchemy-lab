# Native Rust functions

The same declarative business definitions can produce a native Rust library and executable. Set the endpoint's deployment clauses:

```alch
  target rust-http
  runtime rust>=1.94
```

Mappings, quantified queries, rules, result cases, schemas and integration bindings remain in the `.alch` file. Existing Node-target sources can also be built with an explicit `--target rust-http` override; that selected target is recorded in the compiled model and ontology.

```sh
node dist/cli.js check ../extensions/rust-function-v1/quantity-price.alch
node dist/cli.js build ../extensions/rust-function-v1/quantity-price.alch --out /tmp/new-rust-quote
/tmp/new-rust-quote/alch-function invoke < ../extensions/rust-function-v1/input.json
/tmp/new-rust-quote/alch-function trace < ../extensions/rust-function-v1/input.json
# Set QUOTE_API_TOKEN in the environment before starting the HTTP server.
/tmp/new-rust-quote/alch-function serve
```

`alchlang trace` also recognizes an authored Rust endpoint; it builds a temporary native bundle and runs its local trace command. Reusing a built binary avoids rebuilding for each trace.

## Compilation and artifacts

DomainSpec validates the same typed composition and core selectors, then emits native Rust functions. Quantifiers compile into loops with the declared short-circuit behavior. Queries filter before projecting, and zero-input declarations memoize per invocation. Calculation calls use DomainSpec's generated Rust modules and checked `u64` arithmetic. No JavaScript runtime or behavioral AST interpreter is deployed.

The standard Rust project build and verifier cover the Cargo manifest, generated source, boundary model, bindings and ontology. Alch retains that verified project under `domain/`, copies it into `rust/` for Cargo compilation, locks dependencies offline, and hashes the sources, lockfile, native binary and receipts in the portable manifest. Compile the retained Cargo package from `rust/compositions/function/Cargo.toml`; preserve its relative references to the generated core modules.

The library exports `invoke`, `trace` and an Axum HTTP handler. The executable supports JSON on stdin and an HTTP server. `HOST` defaults to loopback and `PORT` to 3000. HTTP authentication, provided snapshots, HTTPS GET integrations, redirect refusal, input/output validation, request limits and upstream timeout/size limits follow the declared model. Missing environment references fail explicitly. No provider was contacted during local validation.

Rust uses [checked integer arithmetic](https://doc.rust-lang.org/std/primitive.u64.html#method.checked_mul), with [Reqwest's client limits](https://docs.rs/reqwest/0.12.28/reqwest/struct.ClientBuilder.html) at the integration boundary.

## Traces

Native traces use `alchlang.rust-invocation-trace/v1`. They record declaration evaluation, query-row decisions, assertions, selected result cases, failures and source-linked definitions. Capture is bounded at 10,000 events / 2 MiB; completeness is distinct from success. Tracing accepts supplied snapshots only and does not read integration credentials or fetch missing data.

The receipt hashes the source, ontology, generated behavior, composition, input and complete bundle manifest. Internal UInt64 event values are exact JSON integers. Consumers must use a lossless JSON parser for values beyond JavaScript's safe integer range. Public money results remain decimal strings. These local receipts are not signed production attestations.

## Scope and Open Questions

One composition per project is supported. The current native binary targets the build host (Linux x86_64 in this candidate); cross-compilation and cloud packaging remain future work. Building requires Rust 1.94+ and the pinned Cargo dependencies already cached; builds run offline and report missing dependencies rather than installing silently.

For `portability node-rust-v1`, timestamps, patterns, optional values and text operations follow [the shared profile](PORTABLE-CONFORMANCE.md). `check --target rust-http` validates the target without a Cargo build. Without that portability declaration, timestamp fields use RFC 3339. Rust patterns admit a bounded common ASCII regex syntax: literals, anchors, character classes, groups, alternation and repetition, with numeric repetition bounds at most 1000. Escapes and lookarounds are rejected before generation. Full JavaScript regex/date compatibility is not claimed.

Local pricing parity does not establish live provider interoperability. Generic checked assurance interchange, whole-function formal proofs, product approval, ontology admission, release and deployment remain separate work.

## Typed module composition

Portable functions can import boundary types and call another generated function with `module-local` or `module-http` bindings. See [Module composition](MODULE-COMPOSITION.md) for the checkout example, import closure, trace scope and limits.
