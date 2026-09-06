# L4 state-bearing sandbox product-approval packet

This package records the owner decision for the exact tested L4 state-bearing
local sandbox candidate. It contains the frozen manifest, original undecided
approval request, Decision Gate admissibility evidence, exact `L4PAPP-1`
decision, and deterministic validators.

The sandbox state survives the bounded activation observation and is then
restored and removed by explicit teardown. This is not governed runtime
activation, migration, cutover, live readiness, or an external-system effect.

Validate from the CyberAlchemy-lab root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 docs/decisions/0039-d65-l4-state-bearing-sandbox-product-approval/validate.py --write-receipt
```

The pre-decision `validate.py` and `receipts/validation.json` remain immutable
candidate evidence. Once `decision.json` exists, its owner-selection-absent
check is expected to block if re-run; use `validate-decision.py` for the
current approved-product state.

Product approval does not admit the adapter or authorize
governed runtime activation, live execution, migration, cutover, publication,
deployment, credentials, destructive action, or external effects.
