# CAL-PLAN-0006 — Admitted Runtime Activation/Cutover Preparation

Status: candidate ready, unregistered  
Route: `CA2-ROUTE-PLAN`  
Authority effect: none

This package is the continuous post-admission plan for the exact inactive
epoch-002 implementation. It keeps prototype and evidence construction running
through one no-effect shadow activation, migration, cutover, and rollback
sequence. The sole owner gate is last.

```text
exact inactive admission
  -> AC-S1 activation and migration contract
  -> AC-S2 disposable shadow harness
  -> AC-S3 deterministic two-run comparison and mutation tournament
  -> AC-S4 disposable cutover and exact rollback rehearsal
  -> AC-S5 frozen tested decision candidate
  -> CUT-G1 owner decision
```

The ontology remains event-calculated: canonical events are the sole replay
source, while node and relation latest snapshots are disposable projections.
Context bindings and challenge contracts are preserved and tested as ontology
records. Candidate construction never uses a live target, production data,
credentials, or external effects.

The plan is intentionally not registered as admitted execution state. The
existing admission admits the implementation as inactive; it does not authorize
this plan, activation, migration, or cutover. Even a later `D65CUT-1` decision
must be executed by a separate exact effectful envelope.

Validate without writing:

```bash
python3 docs/plans/0006-d65-admitted-runtime-activation-cutover/validate.py
```

Materialize the deterministic validation receipt:

```bash
python3 docs/plans/0006-d65-admitted-runtime-activation-cutover/validate.py --write-receipt
```

## Claim ceiling

Validation proves only that the plan is structurally sound, binds the current
admission, keeps operational work separate, and defers the authority gate until
after complete shadow evidence. It does not run the plan or authorize any live
effect.
