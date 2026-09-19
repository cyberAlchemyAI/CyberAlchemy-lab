# Gate carrier

Proposed effect -> exact input and evidence -> required checks -> proposed verdict -> owner record.

A Gate defines an effect boundary, required checks and decision route. It names its owner, scope, input, criteria, verdict vocabulary, evidence requirements, unresolved-issue route, record location and downstream effect. This candidate preserves the D5 Promotion Gate and D37 Gate source meanings.

The four verdicts are pass, flag, block and defer. All checks matching produces pass. A failed criterion produces its declared block, flag or defer verdict. Missing evidence or fields always defer. Block takes precedence over defer, then flag, then pass. Scope or requested-effect mismatch blocks.

A flag must carry a risk description, named risk owner and follow-up. Flag risks remain visible even if another criterion blocks or defers the aggregate result. A flag is never silently counted as a pass. The record also requires distinct declared source and destination states.

Observations bind the exact Gate record and input by content hash; each criterion's supplied evidence is hash-bound. Changed files, duplicate or unknown criterion evidence and input mismatches are rejected. Primitive JSON values compare without coercion.

The example proposes recording review readiness for the prior Responsibility candidate. Synthetic failing and risk evidence are labeled fixture-only. Passing verifies only the selected fields in supplied files, not evidence truth, relevance or their relationship to the input. The profile does not inspect actual current state, authenticate owners, verify broader lifecycle transitions or perform downstream effects.

The checker reports a proposed verdict. It never records an authoritative owner verdict or grants or executes an effect. The record location and routes are declared destinations; the checker does not write to them. An owner must separately assess the evidence and record any governing decision.

Run from the Lab root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/candidates/0018-gate-carrier/validate.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/candidates/0018-gate-carrier/check.py evidence/migrations/cyberalchemy-v2-to-lab/candidates/0018-gate-carrier/artifact-types/gate/v1/fixtures/valid/gate-record.json evidence/migrations/cyberalchemy-v2-to-lab/candidates/0018-gate-carrier/examples/supported.json
```

CLI status 0 means proposed pass, 1 means flag, block or defer, and 2 means invalid input. Status 0 grants no permission.

Validation passes 20 behavioral tests and 8 invalid contract fixtures. It verifies the Gate Definition and both D5/D37 source sections. The selected dependency closure has no source-lineage residues; the inherited predecessor chain and existing D53 overlay remain preserved. Generated files reproduce and the predecessor snapshot remains unchanged.

The 195-target ledger now has 13 admitted targets, 92 constructed candidates and 90 remaining scaffolds. Next: `type.typed-relation`.

The user's `next` authorizes construction and testing. A later Gate adoption would approve its exact effect boundary, required checks, risk handling and owner decision route. A particular transition still needs its own governing record; this candidate does not approve it.
