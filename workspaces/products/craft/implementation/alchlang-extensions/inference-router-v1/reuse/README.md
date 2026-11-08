# Generated service reuse and migration

ISB-08 completed local candidate.

Validation: **106 service tests**, **14 DomainSpec contract tests**, and
**three existing service compatibility tests** pass. The independent standalone
bundle also passes four pricing boundary requests. [Construction plan](PLAN.md), [evidence](evidence.json),
[native inventory](native-inventory.json), [independent fixture](quote-service/README.md).

The independent parcel quote service uses existing Alch service and function
profiles plus DomainSpec compilation. Its generated Node server exposes health
and a typed CalculateQuote operation. Changing an authored price changes the
response without changing adapter code. Negative witnesses cover request and
output schemas, absent operation bindings, cancellation and diagnostic redaction.

The inference host now calls [compiled admission](../admission.alch) for strategy
availability and known aliases. Error precedence remains strategy first, then
model. Provider selection, public projections/errors, stream transitions and
custody/replay policy were migrated in the preceding units.

The native inventory records exact hashes, line counts, complete line coverage,
responsibility and owner for every active service wiring/runtime source. Native
code still validates operator configuration, snapshots catalogs, supplies context
estimates, wires dependencies, performs socket/byte/clock/storage work and executes
normalized contracts. Operator strategy vocabulary and estimator sanity are an
explicit inference host contract. Generic adapters contain no inference ranking,
model aliases, public endpoint declarations or replay decision table.

The fixture establishes independent Node service assembly and function/operation
reuse. Outbound HTTP, SSE and custody retain their separate conformance and
inference witnesses. This is not a production or cross-target parity claim.

Build the runnable fixture from the repository root:

```sh
ALCHLANG_TYPESCRIPT_COMPILER=/tmp/ca2-ds-toolchain/node_modules/typescript/bin/tsc6 \
  tools/toolchain/run node language/capabilities/alchlang/plans/general-compiler-v1/extensions/inference-router-v1/reuse/build.mjs /absolute/new/quote-bundle
```

Import `createServer` from the resulting `index.mjs`, then call
`server.listen(0, '127.0.0.1')`. The bundle manifest binds the entry and both
compiled modules. All service regressions run through the existing `run.mjs test`.

## Open Questions

ISB-09 is now the remaining planned construction unit: tenant authentication and
authorization, including checking current access before replay. Its identity
source and authorization rules still need an explicit owner decision. No choice
is inferred here. Durable multi-host storage and deployment remain separate
operational decisions, not prerequisites for these local candidate fixtures.
