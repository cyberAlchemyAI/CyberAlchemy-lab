# Customer Credit Release imported as a reference candidate

Approved state -> known risk provenance -> required human confirmation and bounded authority -> released, denied or blocked.

This is an AlchLang reference example. Real lending decisions and fund transfers are explicitly excluded. The source action is bounded to an in-memory adapter invocation.

Four action-linked domain rules supply the missing acceptance conditions: approved state, known risk provenance, human confirmation when the example risk score is at or below 472, and current bounded credit authority. The threshold belongs to this reference model only. Exact descriptions are retained without turning predicate names into executable logic.

Capability and ontology references, declared owner, action-to-rule links, effect boundary and failure continuation are validated. Inline input/output descriptions remain in the source record; no separate contract identities are invented.

[Result and mappings](result.json). [Current inventory](inventory.json). **33 imported candidates / 11 blocked / 1 excluded.** Store: `.local/capability-inventory-import-0021/imports.json`.

[Verification](verification.json) checks replay, wrong capability binding, missing rules, unsafe effect/failure changes, queue isolation, prior imports and combined graph validity. Run `PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/executions/0021-customer-credit-release-import/verify.py` from the Lab root.

The capability description is imported. Source runtime tests and the example were not rerun. No operational authority is granted.

## Open questions

Next blocked declaration: CA2-REF-CAP-INVENTORY-RESERVATION. Runtime conformance remains separate from this description import.
