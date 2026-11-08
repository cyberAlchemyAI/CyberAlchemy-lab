# Source-linked invocation evidence

The pricing source retains the preceding derived-ontology example unchanged. The compiler now emits optional observations, and a local invocation can explain actual query decisions, Rule results, assertion failures, calculations and result-case selection.

Run the command in [the guide](../../alchlang/docs/INVOCATION-TRACES.md), or inspect `evidence/quoted-trace.json`. `input.json` supplies the same request and price snapshot as the quantity_15 fixture. Evidence for no-price, ties and overflow is also recorded under evidence after validation.

## Validation

Current checks: 109 Alch tests, 26 focused DomainSpec tests, typecheck/builds, and 20 final-bundle fixture comparisons passed.

The new tests compare traced and ordinary results across all 20 pricing fixtures, bind traces to source and generated artifacts, exercise failures and skipped calculations, isolate concurrent invocations, verify capture limits, reject accessor input without invoking it, and prove the CLI does not obtain missing snapshots from environment credentials. DomainSpec generator tests additionally prove that observers cannot mutate computation values or change results by throwing.

`evidence/alch-tests.log` and `evidence/domainspec-tests.log` are the fresh test receipts. `candidate.json` records the selected source, compiler and evidence hashes. No historical candidate is refreshed.

## Open questions

See [PLAN.md](PLAN.md). Composite predicate results are observed; individual quantified witnesses remain outside this slice. Capture completeness is distinct from execution success. These are local receipts rather than signed production attestations. Remote tracing, retention/access policy, registration, publication and deployment remain deferred.
