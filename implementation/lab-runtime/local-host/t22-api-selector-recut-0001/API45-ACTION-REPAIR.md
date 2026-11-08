# API45 Action profile repair

The API44 same-child composite attempt is retained as a refusal in
`RUN-API44-PAIRS-0001.json`. Its first Action call returned
`integrity-failed` before a counter effect. The selected Action v7 dependency
guard accepts the installed jsonschema overlay only when the integration
profile path is the historical API40 profile. The API44 composite correctly
supplied its own profile, so the guard refused.

The disjoint `api-action-integration-v8-current-t17-0001` changes only that
exact accepted profile origin to API45. `api-integration-v45-r03-0005-coverage-0001`
selects Action v8, its exact package rows, and a matching disjoint SDK and
branch driver. The API45 source, profile, Action, SDK, and branch pins are in
`API45-REBIND-RECEIPT.json`. The captured live runner and launcher are selected
by `API45-HARNESS-SELECTION-0001.json`.

Cold verification: the API45 source guard passes 207 selected rows; the Action
v8 dependency guard accepts the exact API45 profile and installed overlay;
`test_api45_action_cold.py` passes four tests under both normal and optimized
Python. The tests include old-profile-origin and wrong-current-digest refusals.
The nine-row captured harness selection also passes, and a wrong harness
digest refuses. These are preparation checks only. No API45 same-child
operation pairs or complete Lab product claim exists until the live runner
produces and is reviewed against a terminal receipt.

Launch from the repository root after shared heavy jobs clear:

```sh
python3 -B implementation/lab-runtime/local-host/t22-api-selector-recut-0001/launch_api45_pairs.py \
  --selection-sha256 8beaf596ef64b1db55e75c5761f9a8844738a1a4f85ee9d99a9c13fa57048b50
```

This fixture has no authority effect. Its intended positive scope is 15
same-child calls across seven distinct Base, Action, and Governance
operations with paired denials. It does not prove all 34 operations, the
fresh Agent contest, or a governing decision.
