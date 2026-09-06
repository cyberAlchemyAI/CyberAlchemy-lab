# D65 export and cutover candidate plan

This package constructs the successor to the admitted D65-S8 integration epoch.
It preserves every admitted byte, makes the missing v2 Context Map the first
bounded implementation layer, and requires a new CAV2-D65 chain before a
separately versioned Rust candidate may export the Context adapters.

Revision 5 uses two lanes. Dependency-ready prototype construction continues
without a plan-approval gate; operational review and future authority work stay
visible as deferred residue. Product approval becomes eligible only after one
exact testable candidate passes its product tests. Cutover remains a separate
owner decision.

`CTXMAP2-S1` and `D65-S1` through `D65-S7` are tested local prototypes.
`D65-S8` froze and tested one exact product candidate. The current frontier is
the single end product-approval gate; no product approval has been requested,
and no admission or cutover authority exists.

Validate without writing evidence:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 validate.py
```

Write the planning validation receipt explicitly:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 validate.py --write-receipt
```
