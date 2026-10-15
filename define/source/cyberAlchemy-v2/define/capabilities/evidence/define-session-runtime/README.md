# Define Session Runtime Evidence

Status: private candidate evidence contract
Execution mode: dry-run only
Runtime evidence: not evaluable

This package maps all 23 Define Shared Meaning obligations to the current
Define Session Runtime system model. It keeps three questions separate:

1. Does the model contain a place for the obligation?
2. Does a dry-run fixture have the required evidence shape?
3. Has an implemented runtime produced valid evidence?

Only the first two are evaluated here. The system ontology declares the
runtime `not-implemented`, so this package cannot mark any obligation
satisfied or issue a behavioral-conformance verdict.

The first experiment is `EXP-DEFINE-OBL-011-CLI-CHAT-CONTINUITY`. It models
one exact vertical: create a session through CLI, preserve an open question in
a confirmed saved revision, restart the process, and resume through chat with
the same session identity, revision, digest, current question, and open gaps.
The fixtures are synthetic protocol examples, not runtime observations.

Validate with:

```bash
python3 cyberAlchemy-v2/define/capabilities/evidence/define-session-runtime/scripts/validate.py
python3 cyberAlchemy-v2/define/capabilities/evidence/define-session-runtime/tests/test_negative_mutations.py
```
