# Ontology Product event-runtime binding v2

This successor translates the exact admitted cohesive navigation graph into
canonical D65 node and relation events, then uses the existing Rust lifecycle
engine to calculate latest subject snapshots and Context projections.

It preserves the frozen L3 binding as historical evidence. This package binds
the current runtime source rather than refreshing the stale L3 digest.

```text
admitted navigation.json
  -> deterministic package translator
  -> 29 semantic events + 29 governance events
  -> integration epoch record
  -> D65 EventStore
  -> 29 latest subject snapshots
  -> 14-node / 15-relation Context projection
```

Only canonical event files are replay sources. The admitted root, package,
navigation projection, integration epoch, snapshots, Context projections, and
observations remain derived or authority-reference artifacts.

## Test

```bash
cargo test --manifest-path implementation/bindings/ontology-product-event-runtime/v2/Cargo.toml
```

## Run the prototype

From the repository root:

```bash
cargo run --quiet \
  --manifest-path implementation/bindings/ontology-product-event-runtime/v2/Cargo.toml \
  -- materialize \
  product/products/ontology/v1/navigation/cohesive-lab-system/navigation.json \
  /tmp/cal-ontology-product-runtime

cargo run --quiet \
  --manifest-path implementation/bindings/ontology-product-event-runtime/v2/Cargo.toml \
  -- observe /tmp/cal-ontology-product-runtime
```

The first command writes the canonical event histories and prints their
calculated observation. The second reloads those histories and must print the
same observation. Use an absent or empty output directory: the prototype
refuses to overwrite a nonempty target.

The implementation is a Product construction candidate. It does not admit the
binding, adopt or activate the runtime, admit a child ontology, resolve the
DomainSpec collision, migrate sources, publish, release, or deploy anything.
