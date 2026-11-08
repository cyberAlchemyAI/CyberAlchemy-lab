# Portable Node and Rust functions

Add a portability declaration to a declarative function:

```alch
profile declarative-function-v1
portability node-rust-v1
```

The same source can be checked for either target. A Node-authored endpoint can generate both bundles; the target override changes deployment metadata, while the business source remains identical.

```sh
node dist/cli.js check ../extensions/portable-conformance-v1/shipping-options.alch --target rust-http
node dist/cli.js conformance ../extensions/portable-conformance-v1/shipping-options.alch \
  --fixtures ../extensions/portable-conformance-v1/shipping-options.fixtures.json \
  --out /tmp/new-shipping-conformance
```

The output contains `node/`, `rust/` and `report.json`. Each bundle retains its DomainSpec project, generated behavior, ontology scaffold and hashed manifest. The runner requires a fresh output directory, builds both targets, executes every fixture and exits nonzero if an output, expected error, request or decision differs. Cargo builds offline. Fixture environments are explicit synthetic values; ambient credentials are never loaded and transport calls receive controlled responses.

A fixture contains `name`, `input` and a complete `expected` outcome, plus optional `env` and `responses`. A successful outcome is `{"status":"succeeded","result":{...}}`; a failure is `{"status":"failed","code":"FUNCTION_PATTERN"}`. Responses supply `status` and `body`, or `raw` text for decoding tests, or an injected `FUNCTION_INTEGRATION_TIMEOUT` / `FUNCTION_INTEGRATION_FAILED` error. Unconsumed or missing responses fail conformance. Use fixture credentials: prepared request headers are recorded in the local report.

## Profile semantics

- Core arithmetic uses checked UInt64. Boundary integers must be within JavaScript's safe integer range. Decimal conversion uses a literal scale from 0 through 18 and rejects excess precision, signs, noncanonical leading zeroes, line terminators and overflow.
- JSON input uses Unicode scalar strings. String limits and ordering use UTF-16 code units. `lower` folds ASCII A–Z only; identifier emptiness ignores only ASCII space, tab, CR and LF.
- Missing optional fields remain absent. Explicit `null` requires `nullable`. `present` is false for both; `coalesce` selects its fallback for either. A mapper assigning an absent optional field omits that field from its output.
- Schema validation rejects unknown fields first, then checks declared fields in lexicographic order. Queries evaluate all filters before projections, preserving input order. `exists` / `forall` short-circuit; `exactly_one` evaluates all witnesses. Every result condition is evaluated, exactly one must match, and only its value is evaluated.
- Timestamps require `YYYY-MM-DDTHH:mm:ss`, optional 1–9 fractional digits, and `Z` or a signed `HH:mm` offset. Years are 0001–9999, calendar dates must exist, seconds are 00–59, and offsets have hours 00–23 and minutes 00–59. Lowercase separators and leap seconds are rejected.
- Patterns require a complete anchored match. The common grammar admits ASCII literal letters, digits, spaces, underscores and hyphens, ASCII character classes/ranges, alternation optionally wrapped in one group, and `?` / `{n}` / `{n,m}` repetitions bounded by 1000. Escapes, lookarounds, nested groups, `*`, `+` and open-ended bounds are rejected during checking with the source file, line and field.
- Integration requests use HTTPS GET, refuse URL credentials and redirects, require nonempty declared environment values, replace existing values for authored query keys, and retain unrelated query parameters. Status, byte limits, decoding and schema checks use declared error codes.

Without the portability declaration, existing target-specific behavior remains available. Rust still rejects unsupported pattern syntax at checking time. The profile is an implementation contract with finite test evidence, not a theorem covering every program or malformed JSON transport.

## Evidence and limits

Reports bind source bytes, fixture bytes and both complete bundle manifests. They compare full public outcomes against an independent expected result, and compare normalized request preparation and ordered decision events across targets. Decision events retain query acceptance, assertion phase/code/result, Rule booleans and result selection; large numeric intermediate payloads and target-specific source metadata are excluded. Truncated capture is `not_evaluable`, never a pass.

The native binary has a diagnostic `conform` command accepting `{input,env,responses}` on stdin. It exercises generated behavior and the real request-preparation/response-decoding helpers with a controlled transport. It never opens a provider connection. Normal `invoke`, local `trace` and HTTP execution remain separate entry points.

The suite does not test real network timing, TLS interoperability, provider credentials, cloud packaging or deployment. Native binaries target the build host. Product approval, ontology admission and operational authority are separate from this local report.
