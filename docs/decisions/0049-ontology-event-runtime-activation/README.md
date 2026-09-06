# Local runtime activation candidate 0049

This prepares a persistent local CLI instance of adopted binding v2. It does not
start a server. Each command runs, calculates its result, prints JSON, and exits.

## What you will see

The approved navigation graph becomes 29 semantic events, 29 governance events,
29 latest subject snapshots, and a Context projection covering 14 nodes and
15 relations. Event history remains the replay source. Source ontology residue
and all Product 0006 limitations remain unchanged.

```text
approved navigation --materialize--> canonical event files
canonical event files --replay--> latest snapshots
latest snapshots --calculate--> ontology cut and Context projection
runtime directory --observe--> JSON observation
```

## Proposed activation envelope

Owner selection `EVRT-ACT-1` would authorize one initial materialization into
`/home/vrondelli/projects/CyberAlchemy-lab/.local/ontology-event-runtime-0049`,
followed by observation and an execution receipt. The directory must not exist,
and no ancestor may be a symlink. Recheck that immediately before execution.
The exact candidate and current adoption evidence must also pass validation.

Proposed commands, **not yet authorized or executed on this target**:

```bash
cd /home/vrondelli/projects/CyberAlchemy-lab
cargo run --offline --locked --quiet --manifest-path implementation/bindings/ontology-product-event-runtime/v2/Cargo.toml -- materialize product/products/ontology/v1/navigation/cohesive-lab-system/navigation.json .local/ontology-event-runtime-0049
cargo run --offline --locked --quiet --manifest-path implementation/bindings/ontology-product-event-runtime/v2/Cargo.toml -- observe .local/ontology-event-runtime-0049
```

Execute sequentially and stop on the first failure. Preserve partial output for
inspection; never retry initial materialization into an existing directory.
There is no service to stop. Retain the event files; removal needs separate scope.

No network listener, repository enforcement, legacy import, child-ontology
admission, migration, cutover, publication or deployment is included. Cargo's
existing build cache may be used; source and lockfile bytes must stay unchanged.

## Validation and work lanes

```bash
PYTHONDONTWRITEBYTECODE=1 python3 docs/decisions/0049-ontology-event-runtime-activation/validate.py
```

Validation checks the adoption chain and current Product tests, then rehearses
the exact offline/locked commands in temporary storage. It checks restart
equality, read-only observation and refusal to overwrite a populated target.
Temporary test files are removed by the test harness; the proposed persistent
target is never created.

Product construction remains at approved Product 0006, with no new Product bytes
or causal construction blocker. This package is operational support owned by
the runtime owner. Persistent activation awaits exact owner selection; legacy
migration remains with source ontology owners and publication with the repository
owner. These do not block independent prototype construction.

This envelope is ready for review only when its current preacceptance is PASS.
No activation decision is recorded by this package.
