# Ontology Product event-runtime realization layering

Status: construction model  
Authority effect: none

## L0 — Minimum event-calculated vertical

After this layer, we know whether the exact admitted navigation graph can become
canonical D65 node and relation event histories and rebuild the same 14-node,
15-relation topology.

- Minimum working unit: translate 29 subjects, seal 29 semantic and 29 exact-
  reference governance events, bind one integration epoch, load the event store,
  and calculate latest snapshots plus a Context projection.
- Deferred: mutation after the initial cut, checkpoint recovery, packaging, scale.
- Exit evidence: Rust tests for exact counts, source digests, relation closure,
  child-state preservation, and authority effect `none`.

## L1 — Evolution and per-subject latest state

After this layer, we know whether a later event on one subject replaces only
that subject's calculated snapshot without mutating source packages.

- Included: expected-stream-version append, semantic/governance pair, exact
  reference join, latest root snapshot at the new cursor.
- Non-regression: L0 topology and all child authority states remain intact.
- Exit evidence: append and latest-snapshot tests.

## L2 — Recovery and hostile integrity

After this layer, we know whether the same graph survives restart and checkpoint
recovery and refuses incomplete or corrupted source history.

- Included: two independent materializations, checkpoint-plus-tail equality,
  missing epoch/event rejection, digest failure, nonempty-target refusal,
  DomainSpec collision preservation, and authority-inflation rejection.
- Deferred: production storage, multi-writer coordination, power-loss proof.
- Exit evidence: deterministic equality and hostile tests.

## L3 — Exact testable Product candidate

After this layer, we know whether one immutable source and implementation set is
eligible for Product approval review.

- Included: exact source registry, implementation binding, frozen candidate,
  two passing test runs, schema validation, and product-test receipt.
- Operational residue: admission, runtime adoption, activation, migration,
  cutover, publication, release, deployment, credentials, and source retirement.
- Promotion decision: request Product approval only after all evidence is current.

Boundary heuristic: each layer unlocks a distinct decision—basic realization,
event evolution, recovery integrity, then Product review—without mixing later
operational effects into construction.
