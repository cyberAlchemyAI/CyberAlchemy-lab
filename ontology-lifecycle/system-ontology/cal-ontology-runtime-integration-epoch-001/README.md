# D65-S5 deterministic system-ontology candidate

This package composes the DomainSpec v2 minted-project compiler with the
DomainSpec Event Sourcing Contract compiler for the exact source admitted by
`CAL-D65SRC-0019`.

The generated graph remains a semantic read model. The generated system
ontology adds no independently authored product meaning: it contains the same
nodes and edges, the compiled event contract, and mechanically resolved
subject/projection inputs. Per-subject ordered complete-resulting-state event
histories are canonical. Latest snapshots, governed projections, the compiled
graph, and this system ontology are rebuildable evidence.

Run candidate compilation and validation with the WSL-native Node/TSX runtime:

```text
TMPDIR=/tmp /home/vrondelli/.nvm/versions/node/v26.8.1/bin/node \
  /home/vrondelli/projects/domainspec-core/implementation/domainspec/backend/node_modules/tsx/dist/cli.mjs \
  compiler.ts
python3 validate.py
python3 hostile-checks.py
```

A passing compile or validator result is candidate evidence only. The package
remains blocked at `G-D65-COMPILE` until the system-ontology owner selects an
exact disposition. It contains no exact implementation binding and grants no
Rust mutation, context-adapter implementation, migration, publication,
deployment, or external effect.
