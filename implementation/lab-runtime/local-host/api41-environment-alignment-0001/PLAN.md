# API41 current guarded-read successor

Status: revised design; no API41 runtime or inherited-test PASS yet. API33 v4, API40, the historical Source5 chain, T06 SDK and the selected current Source8 family remain unchanged.

## Causal boundary

The inherited API40 `GuardedReads.setUpClass` calls `source.replay_source('custody-participation')`. That selects `current-participation-v5` and `current-source-adapter-v2-action-0148`; both require jsonschema 4.23.0. Their episode contract expired on 2026-10-13. API40, its T06 SDK/Action overlay route, and the selected current Source8 family require jsonschema 4.19.2. A system-Python probe refused during class setup and executed zero methods. No single current in-process environment can make those immutable historical and current selections simultaneously valid.

The current native reader also constructs a guarded `SignedSources.sources` ExactSources and attaches `custody_signed_sources` to its actual view. The selected API40 `participation_snapshot` may therefore be reusable, but only after the current reader/Context origin and borrowed-scope checks pass dynamically. Its old Source5 setup and period cannot be reused.

## Smallest coherent successor

1. Keep API40's selected 4.19.2 environment, SDK, Action, governance and current Source8 chain. Create a disjoint API41 source/test package binding the same current family and exact API40 predecessor bytes; do not reissue or relabel expired Source5. Existing API40 tests remain historical evidence with zero current result for the failed probe.
2. Reuse the selected `participation_snapshot` only if it accepts the actual current reader's attached `custody_signed_sources` and current Context producer. It must preserve actual original bytes, current view/source-cut identity, and guards at entry and exit. If dynamic replay exposes a real contract difference, build a versioned helper with the same invariants; do not cast or alias a foreign object to bypass checks.
3. Add a disjoint current test class using `source.replay_source(source.CURRENT_SOURCE8_NAME)` or the exact current legacy alias where the contract requires it. First target the inherited snapshot-header mutation body against the actual current source, requiring one real test and expected refusal. Then run the current guarded-read method inventory and relevant API40 source/model tests under jsonschema 4.19.2, retaining original method bodies/names only when their assertions and semantics remain valid. Record new IDs for genuinely new tests.
4. Cold-bind API41 source/profile/test/helper bytes and the selected native Source→Reader→Mapper→Context manifests. Enforce exact start/end row hashes, expected test ID inventory, wrong-origin and wrong-source mutation negatives, and actual lease clocks. Do not infer currentness from the 24-hour Source period alone.
5. Run a bounded T06/Action smoke and independently review the new selected cut before claiming T16/T18. The API33 v4 99-method result remains separate evidence.

This route avoids a new Source8 family or a misleading revival of the expired Source5 period. It is implementation work, not a qualification claim.
