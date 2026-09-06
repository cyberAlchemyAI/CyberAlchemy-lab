# D65 L5 local active runtime product approval

This package freezes and validates the exact L5 process-local active ontology
runtime candidate. The runtime has already been compiled and tested. It stays
active across stdin commands, exposes the event-calculated 47-subject
projection, and tears down exactly on `stop` or EOF.

The owner selected `L5PAPP-1`, approving the exact candidate digest as a
product. The decision creates no governed runtime activation, live readiness,
migration, cutover, publication, deployment, or external-effect authority.

Validate the candidate packet:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 validate-decision.py --write-receipt
```
