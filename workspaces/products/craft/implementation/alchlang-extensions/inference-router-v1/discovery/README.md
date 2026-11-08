# Generated discovery and public error policy

Status: ISB-03 local implementation candidate. Authority effect: none.
D65 chain: [Define pack and candidate contracts](../service-contracts-v1/README.md)
-> [business/product scaffolds](../service-contracts-v1/scaffolds.json)
-> [selected service contract](../service-contracts-v1/service.example.json)
-> authored functions below -> compiler/runtime realization ->
[evidence](evidence.json) and generated bundle receipt (referenced result or source binding is not imported). This records construction and verification, not admission
or deployment. Tenant authentication and authorization remain ISB-09, last.

| Authored source | Generated behavior |
| --- | --- |
| [aliases.alch](aliases.alch) | Filter enabled rows, deduplicate aliases, sort using portable lexical order |
| [summary-input.alch](summary-input.alch) | Bind one alias to the original catalog snapshot |
| [model-summary.alch](model-summary.alch) | Group enabled rows, independently minimize context/output limits, OR streaming, project public fields |
| [models.alch](models.alch) | Bound pure iteration and assemble `{models: [...]}` |
| [capabilities.alch](capabilities.alch) | Configured strategies, enabled streaming, task and current memory/public-scope policy |
| [public-error.alch](public-error.alch) | HTTP error codes/statuses, request identity, sanitized unknown fallback, including 404/405 route failures |
| [stream-error.alch](stream-error.alch) | Recognized public SSE error codes and sanitized stream fallback |

The [generic compiler profile](../../../alchlang/QUERY-ITERATION.md) supplies
the missing bounded iteration. Every query/mapping is compiled by the sibling
DomainSpec compiler. No aggregate primitive, correlated query or new DomainSpec
meta-type was needed. The generated iteration manifest resolves the candidate
Catalog, Alias, SummaryInput and Model types to actual schema constraints. Intermediate
`status`/`value` fields are internal typed function envelopes; authored field selections
unwrap them. The service example remains a design contract, not executable multi-route
service syntax. Route-level type binding and health/inference assembly are ISB-04 onward.

[host.mjs](../host.mjs) now calls the compiled model, capability and error functions.
The stream adapter also uses the compiled SSE error mapping; its transitions remain
ISB-06 work.
Its remaining discovery adaptation flattens the three possible catalog containers;
it does not filter rows, group aliases, calculate limits or project public fields.
Configuration and discovery are snapshotted per host; projection initializes lazily
and is shared between requests. Unknown-model validation consults generated discovery.
The host still owns route dispatch, media/body handling, estimator binding and native
execution composition, assigned to later units. If even the error mapper fails at
the socket boundary, the adapter closes with an empty HTTP 500.

Up to 300 schema-valid provider rows (100 per strategy) feed discovery. Disabled rows
remain part of input validation but never appear publicly. Up to 100 distinct enabled
aliases and 65,536 output bytes are permitted; overflow rejects the whole projection.
Input is bounded at 262,144 bytes. Alias order now uses the portable compiler's lexical
comparison rather than locale-dependent sorting. Response field shapes are preserved.
Capabilities describe configured strategies even when no provider is enabled.

The [build adapter](../build-public-policy.mjs) is shared by tests and the public
launcher. Run `node run.mjs test` from the parent directory using its documented
Node/compiler binding. It runs the original 47 regressions plus 12 ISB-03 witnesses:
seven generic runtime/compiler tests and five generated public-policy tests. These
cover independent minima, duplicate aliases across strategies, disabled/empty
catalogs, secret redaction, every existing error status, unknown faults, bounds,
cancellation, deadline checks, type mismatch, dependency purity and path rejection.

The sibling had existing changes for shared composition ontology and validated
project snapshots. [Binding update](compiler-binding-update.json) records the old/new
hashes; the active compiler binding was refreshed and 10 selected composition tests passed. Its separate Rust execution witness could
not run: Cargo is installed, but the C linker `cc` is unavailable. No Rust
execution parity is claimed.
ISB-03 did not edit DomainSpec compiler sources. Earlier audit/contract/host receipts
remain historical and are not rewritten as fresh evidence.

## Open Questions

- ISB-04 must select and compile the service route assembly, including anonymous GET,
  multi-route validation and passing client cancellation to generated entrypoints.
- Pure iteration is Node-only and cooperative; no Rust parity, effectful iteration
  or preemptive CPU scheduling is claimed.
- HTTP attempt settlement, stream transitions and request custody remain ISB-05..07.
- Live providers/tokenizers, durable storage and production hosting remain deferred
  choices. Tenant identity and authorization are explicitly last, in ISB-09.
