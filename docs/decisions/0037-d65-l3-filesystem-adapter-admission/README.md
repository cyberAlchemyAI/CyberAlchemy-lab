# L3 filesystem adapter-admission packet

This package records one owner decision for the exact product-approved L3
filesystem adapter. It contains the frozen admission candidate, Decision Gate
admissibility evidence, the exact `L3AADM-1` decision, and deterministic
decision validation.

`L3AADM-1` admits only the exact adapter identity for governed non-live
disposable-filesystem rehearsal. It does not activate the runtime or authorize
live execution, migration, cutover, publication, deployment, credentials,
destructive action, or external effects.

Validate from the CyberAlchemy-lab root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 docs/decisions/0037-d65-l3-filesystem-adapter-admission/validate-decision.py --write-receipt
```

The pre-decision `validate.py` and `candidate-validation.json` remain immutable
candidate evidence. Once `decision.json` exists, its owner-selection-absent
check is expected to block if re-run; use `validate-decision.py` for the current
admitted state.
