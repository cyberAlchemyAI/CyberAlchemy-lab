# Epoch-002 shadow activation and cutover rehearsal

This package executes `AC-S1` through `AC-S4` from `CAL-PLAN-0006` entirely in
disposable local state. It starts from the exact seven-event rehearsal cut,
appends four canonical events that project the admitted inactive state, and
calculates the target ontology from the resulting eleven-event cut.

The target contains the latest state of two nodes, one directed relation, the
v2 Context Map binding, and the challenge contract for the final owner gate.
Snapshots are calculated accelerators and are never replay sources.

The runner performs two deterministic migrations, two Rust public-contract
runs, a disposable cutover sequence, exact rollback to the seven-event
preimage, ten hostile mutation probes, and protected-byte comparison.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 ontology-lifecycle/activation/cal-d65-epoch-002/validate.py
```

Passing evidence does not activate or cut over any live runtime. It only makes
the separately frozen `CUT-G1` decision candidate eligible for owner review.
