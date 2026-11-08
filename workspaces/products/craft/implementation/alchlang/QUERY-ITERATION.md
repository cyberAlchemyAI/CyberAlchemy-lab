# Bounded pure query iteration

Status: owner-directed ISB-03 compiler candidate; authority effect: none.
Contract: [ISB-02 Pure Query Iteration](../alchlang-extensions/inference-router-v1/service-contracts-v1/README.md).
This Alch composition reuses DomainSpec Query and Mapping; it introduces no DomainSpec
meta-type and does not change the frozen catalog.

`query-iteration-v1` compiles three declarative functions: a source query, an input
mapping and an item query. The mapping takes exactly `{context, item}`, where context
is the original source input. Selected fields unwrap its typed argument and the
item query's public value. The result is one named list. See the complete
[models source](../alchlang-extensions/inference-router-v1/discovery/models.alch).

All declarations in that source are required. Only `node-http` constituent functions,
`concurrency 1`, `order input` and `partial-result reject` are supported. Maximum
bounds are 100 items, 65,536 output bytes, 262,144 input bytes and 5,000 milliseconds.
Smaller positive bounds are accepted. Unknown or duplicate declarations, unsupported
policies, unsafe fields, path traversal and symlink escapes reject before building.
The output directory must not exist.

The compiler resolves structural types, including nested constraints, across the
source item, mapping context/item, mapping output and query input. Selected fields
must be required and non-nullable. Recursive iteration interface types are rejected.
Every constituent import is checked for purity: local module composition is allowed;
provided data integrations, HTTP modules and other integrations are rejected,
including dependencies in unused imported modules. Normal DomainSpec compilation
validates each function's internal mappings and result types.

The generic runtime clones the input, iterates in source order and checks input,
item count and cumulative UTF-8 output bounds. It returns a complete list or rejects
on the first failure. It yields between items and checks cancellation and a monotonic
deadline before and after constituent calls. These are cooperative checks around
bounded, compiled pure work; they do not preempt a synchronous JavaScript computation.
The runtime does not expose fetch, operator environment or injected callables through
an authored definition. Its exported factory is compiler plumbing, not an untrusted
plugin execution interface.

Build/check through the Alch CLI:

```sh
node dist/cli.js check path/models.alch
node dist/cli.js build path/models.alch --out /absolute/new/bundle
```

The bundle exports `app/function/index.mjs#invoke(input, env?, {signal}?)`; it is a
pure callable, not an HTTP service. Its manifest contains the source digest,
normalized bounds and field selections, resolved interfaces, child source digests,
and an inventory binding the generated child bundles. Child provenance carries
DomainSpec contracts, source locations and composition traces. Publication reserves
the destination and creates the completion manifest last.

Implementation: [compiler](src/query-iteration.ts),
[runtime](src/query-iteration-runtime.ts),
[negative and runtime tests](../alchlang-extensions/inference-router-v1/discovery/discovery.test.mjs).

## Open Questions

- Route assembly and binding these pure callables to HTTP is ISB-04.
- Rust execution parity, effectful loops, partial results and concurrent iteration
  are outside this candidate. They need separate contracts and evidence if requested.
- Shared service/product questions are owned by the
  [service plan](../alchlang-extensions/inference-router-v1/SERVICE-PLAN.md#open-questions).
