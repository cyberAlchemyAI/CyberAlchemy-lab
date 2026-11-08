# Validation strategy

> Generated from [PLAN-SOURCE.json](../PLAN-SOURCE.json).
> Standalone candidate. 33/35 tasks accepted with hash-bound evidence; see task receipts for review scope. No formal Invoke admission is claimed.

## Planning checks performed now

The compiler checks source identity, unique tasks/SWUs, acyclicity, final gate reachability, complete layer gate ancestry, formalization-first ordering, disjoint scopes, evidence coverage and status consistency. Accepted F0 tasks require current hash-bound outputs, criteria and dependency evidence. Thirteen hostile mutations must be rejected, including unbound acceptance and attempts to start decoding or baseline capture before formalization review. All views, cards, working units and waves are derived from one source.

```bash
python3 docs/plans/relational-theorem-checker/compile_plan.py check
```

This verifies deterministic regeneration and bound source hashes. It does not run the future checker, prove Lean theorems, execute the pilot or admit a Plan.

## Future execution validation

| Layer | Required evidence | Principal failure class |
|---|---|---|
| L0 | Independent predicates, general soundness, statement/axiom audit, bound demo and hostile controls | Circular correctness or weakened theorem |
| L1 | Exact registry projection, ordered pairs, reference resolution, coverage and replay | Omission, pair widening or stale evidence |
| L2 | Required obligations, data compatibility, preservation and model evidence | Vacuity or unsupported conservativity |
| L3 | Derivation soundness, least-fixed-point adequacy, protected lineage and checked witnesses | Indirect authority leakage or incomplete closure |
| L4 | Isolated proof replay, complete aggregation, application freshness and pilot | Substituted proof, missing obligation or source drift |

## Claim ceilings

Planning checks establish consistency and fidelity to captured sources. Semantic acceptance requires task evidence. A DAG is not a proved relational model; theorem acceptance does not establish parser, hash or compiled-runtime correctness.

## Rebuilding

Build refuses to overwrite an existing package. Preserve the current source and package when preparing a successor version. The custom compiler is fixed to this package target and does not implement the formal Invoke compiler or admission contract.
