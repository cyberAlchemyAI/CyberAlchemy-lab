# Epoch-002 activation and cutover owner gate

This package freezes the exact inactive admission, `CAL-PLAN-0006`, disposable
shadow activation evidence, canonical-event migration fixture, cutover and
rollback proof, and the four structurally admissible options for
`G-D65-EPOCH-002-ACTIVATION-CUTOVER`.

`D65CUT-1` was subsequently selected in `decision.json`. The exact successor
activation, canonical-event migration, cutover, and tested rollback envelope is
conditionally authorized. Execution remains not ready: the live target,
credential identity, maintenance boundary, live preimages and event cut,
fail-closed sequence, and independent envelope validation are still missing.
No runtime, event, data, credential, service, or external state was changed by
the decision.

The candidate is not a decision. `D65CUT-1` and `D65CUT-2` would authorize only
the preparation and later execution of separately bounded live envelopes.
Neither option performs an effect merely by appearing in this package.

Decision options:

- `D65CUT-1`: authorize a separate exact activation, migration, and cutover envelope.
- `D65CUT-2`: authorize a separate activation-only envelope.
- `D65CUT-3`: defer without changing state.
- `D65CUT-4`: reject this candidate and require amendment before a successor gate.
- `Explain / more context`: non-committal; expands the evidence and trade-offs.

Validate with:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 docs/decisions/0035-d65-epoch-002-activation-cutover/validate.py --write-receipt
PYTHONDONTWRITEBYTECODE=1 python3 docs/decisions/0035-d65-epoch-002-activation-cutover/validate-decision.py --write-receipt
```

Until one exact owner option is selected, runtime activation, migration,
cutover, publication, release, deployment, and external effects remain false.
