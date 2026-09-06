# Local event runtime: activated

The user authorized activation with “activate it and migrate and show me running
so i can just do 1 approval”. [decision.json](decision.json) binds that activation
to candidate 0049. [Execution evidence](receipts/execution.json) records successful
materialization and restart observation against the persistent target.

## See it work

Run this from any terminal; it prints a fresh observation calculated by Rust
from the persisted event histories:

```bash
cd /home/vrondelli/projects/CyberAlchemy-lab
cargo run --offline --locked --quiet --manifest-path implementation/bindings/ontology-product-event-runtime/v2/Cargo.toml -- observe .local/ontology-event-runtime-0049
```

Verified result: 14 nodes, 15 relations, 29 semantic events, 29 governance events,
29 latest snapshots and a Context projection. There are 59 persisted files
(58 subject events and one integration event). Snapshots are calculated, not
the canonical stored source.

The command exits normally. The persistent instance is available on demand;
there is no daemon, HTTP endpoint or always-running Lab service. Do not rerun
initial materialization into this populated target.

## What migrated, and what did not

The exact approved navigation graph was copied into canonical event histories.
No source data was deleted or replaced. The underlying child ontologies'
records and typed properties have **not** been migrated.

[Migration coverage](migration-coverage.json) lists all 14 represented components.
The code in binding v2 rejects any different navigation digest and requires
exactly 14 components and 15 relations. A successor importer is needed before
a complete migration can be tested; approval alone cannot supply that capability.

Product construction can proceed with that importer independently of operational
administration. Its runnable work, causal blocker, owner and deferred cutover
are listed in the coverage record. No additional prototype approval is requested.
New migration Product acceptance remains for the end, after end-to-end tests.

## Evidence use after activation

The frozen README and preacceptance describe the pre-activation state and remain
unchanged. The initial validator now correctly fails its target-absent check;
do not alter that check or refresh the old receipt to disguise activation.

For current operation, use the read-only observe command above and compare its
full JSON output and event-file hashes to the execution receipt. Any changed
source, target or execution envelope requires explicit reassessment.
