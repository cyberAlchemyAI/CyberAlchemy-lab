# L4 state-bearing sandbox adapter-admission packet

This package records the owner decision for the exact product-approved L4
state-bearing sandbox adapter. It contains the frozen admission candidate,
Decision Gate admissibility evidence, exact `L4AADM-1` decision, and
deterministic pre- and post-decision validators.

The candidate scope is bounded non-live sandbox activation observation followed
by explicit exact teardown. The existing ten-step execution engine still
refuses this binding. Migration, cutover, governed runtime activation, live
execution, credentials, network, production data, and external effects remain
forbidden.

Validate the undecided candidate from the CyberAlchemy-lab root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 docs/decisions/0040-d65-l4-state-bearing-sandbox-adapter-admission/validate.py --write-receipt
```

The pre-decision `validate.py` and `candidate-validation.json` remain immutable
candidate evidence. Use `validate-decision.py` for the current admitted-adapter
state.
