# T17 current-cut coverage inventory

This is a **static source inventory, not T17 qualification**. `INVENTORY-0003.json`
pins API38 source manifest `71f5ba4008ce1955265e949bb5250a5af6d9cc5da046d40c8fa7c6a765f774a7`,
profile `32e43cbdaf65a81ccd29033d7351f1685e28ca54c640d595e894322749f82869`,
the exact 34-operation protocol, selected Action-v5 and Governance-v5 source
manifests, and each cited test file SHA, class, method, and line. API39 was
being re-pinned while this inventory was built; no API39 hash is selected here.
`build_inventory.py` checks twelve frozen top-level hashes, including the API38
branch manifest and historical caller/selection, before reading candidates and
again before producing an inventory. It refuses a changed operation set,
missing test method, or test row absent from its selected API/Action source
manifest. `INVENTORY.json` and `INVENTORY-0002.json` are earlier retained
candidates; the latest version corrects negative-test claim labels and adds
the branch pin. The
builder executes no service call and cannot overwrite either inventory.

Of 34 operations, 23 have an API38 or selected Action-v5 positive source
candidate and 19 have a selected-cut negative source candidate. Three more
positives are **external component** examples: empty `lesson.select`,
`package.import`, and `workflow.transition`. Eight operations have no cited
positive method (`typed.extension.prepare`, `lesson.assess`, `lesson.apply`,
`challenge.resolve`, `ontology.project`, and all three Governance operations).
Twelve have no cited negative method. Even where both methods exist, their
presence does not prove schema-valid positive and causal negative calls on one
maintained common dispatcher. Some negatives are only other-grant refusals;
their `claim` field says so. T06's branch driver explicitly records zero
dispatched operations at startup. T17 remains open.

After T06's actual API39 startup and independent source/profile review pass:

1. Freeze one exact API39 source, profile, integration-members, Action,
   Governance, launcher, and dependency selection. Rebuild this inventory
   against those final hashes; do not transfer API38 rows by filename alone.
2. Version the historical `common-all34-0277/caller.py` and
   `common-all34-selection-0278/selection-plan.json` into a new task-local
   caller/plan. Replace stale API/source/profile/fixture origins, retain its
   untrusted external-caller boundary and 23 disjoint unit outline, and verify
   the 34-operation union exactly once before dispatch. The historical caller
   itself is pinned here as a design source, not executable current evidence.
3. Use a fresh same-family Source8 period and a private owned test root. Run
   the 23 units serially through the maintained `IntegrationService` launcher,
   with one exact positive and one schema-valid causal Actor/Agent negative per
   operation. The seven-operation `member:Source8-lifecycle` unit must stay in
   one actual permitted lifetime; do not replace its expiry or restore RAM.
   Record UTC/monotonic call times and actual issued Reader, Context, and
   Session expiries. Stop on the first failed unit and retain its receipt.
4. For every call, retain raw request-byte hash, selected source/profile/cut,
   request and domain-reply schema results, allowed error code, and before/after
   owned effect-state hash for refusals. `release.prepare` counts as a positive
   conformance result only when it returns the correct **blocked** posture;
   it does not approve a release.
5. Aggregate exact 34 positive and 34 negative terminal rows, all seven
   lifetime rows, fresh source guards at entry and exit, owned-root cleanup,
   and zero missing operations. Independently replay the resulting receipt
   before calling T17 complete.

Verify the retained versioned inventory without writing or running a service:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B implementation/lab-runtime/local-host/t17-coverage-inventory-0001/build_inventory.py --verify implementation/lab-runtime/local-host/t17-coverage-inventory-0001/INVENTORY-0003.json
```

For a different reviewed cut, create a new versioned builder and use its
explicit `--output .../INVENTORY-NNNN.json` path; output creation refuses an
existing file. The cold provenance tests are `test_inventory.py` (4/4 normal
and optimized Python).
