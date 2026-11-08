# One compilation boundary

AlchLang owns parsing, source diagnostics and lowering. DomainSpec owns typed
project validation, the compiled graph, composition generation and verification.
New composition builds adapt their derived ontology to
`domainspec.composition-ontology/v1` with `source_format: alchlang` using the
public compiler adapter. Explanations retain the original source evidence.
An old DomainSpec build without that adapter rejects with
`DOMAINSPEC_COMPOSITION_ONTOLOGY_BUILD_REQUIRED`; rebuild the compiler first.

## Backend selection

```sh
# Supported core profile and its source-bound .domainspec.json sidecar:
alchlang check examples/domainspec-order.alch
alchlang build examples/domainspec-order.alch --out /tmp/new-order

# Explicit compatibility for the previous, broader local carrier compiler:
alchlang check examples/backend-types.alch --backend local-compat
alchlang build examples/backend-types.alch --backend local-compat --out /tmp/local-types
```

`--backend domainspec` is equivalent to the default. Missing bindings, unsupported
constructs or a failed compiler reject without emitting a completed output.
Only explicit local compatibility accepts its historical `--force` behavior.
Function, event and host source profiles retain their existing specific dispatch;
this change does not migrate their operational runtimes or grant execution rights.

The core lowering profiles cover their declared records, rules, calculations,
mappings, policies and (exact UInt64 profile) queries. They do not silently lower
all local actions, events, states, transitions, workflows or interfaces. Those
remain explicit compatibility scope or separately implemented specialized profiles.

## Checkout binding and tests

`ALCHLANG_DOMAINSPEC_PACKAGE_ROOT` is the exact override. Without it, the adapter
selects `craft/projects/domainspec-v2/impl/cli` in this checkout. It does not
search for a sibling `domainspec-core` checkout. A missing Craft package rejects;
package and built API version checks still apply.

The focused reconciliation/parity tests accept `ALCHLANG_TEST_TSX` and
`ALCHLANG_TEST_TYPESCRIPT` for isolated host tools. These are test-only overrides;
they do not change compiler selection or claim pinned-container acceptance.

Direct JSON and AlchLang composition tests compare executable artifacts and
dependencies while requiring distinct source-bound certificates. Mutations of
ontology dependencies and meanings reject. DomainSpec snapshot tests remove
source files after compilation and require identical generation from the graph.

## Open Questions

- Which remaining local-carrier constructs should migrate next?
- When can the explicit compatibility backend and legacy ontology schema retire?
- Pinned-container acceptance remains separate from the recorded host tests.
