# Fresh native T31 supervision

Run these external scripts with the **new installed repository's**
`implementation/lab-runtime/local-host/t25-native-launcher-0001/selected-python`.
`make_control_plan.py` records its actual API Source/profile in a new private
plan. `supervise.py --plan ... --evidence ...` runs `control_probe.py` once in
a fresh directory and retains its original result or failure. Never replay a
pending/indeterminate claim or reuse an evidence directory.

The 28 original transition refs are selected from
`t31-native-challenge-0001/ORIGINAL-28-TRANSITION-INVENTORY-0002.json`.
`make_transition_plan.py` takes an ordered JSON list of objects shaped
`{"name":"unique-name","config_path":"/absolute/private/config.json"}`.
It binds each already prepared `run_current.py` config, the same-release
passing control result, and the original inventory. The first phase omits
`--prior-result`; subsequent phases pass the exact preceding phase
`RESULT.json`. This allows configs depending on prior native outputs to be
sealed after those outputs actually exist. Every phase adds fresh original
transition refs as the exact next slice of the original inventory. The next
phase recursively verifies every prior terminal and native child result before
extending the cumulative ledger. Only a successful ledger containing all 28 is
`PASS-all28`.

Each selected native config still has to satisfy `run_current.py`: genuine
retained API/typed originals, successful bound public reply, one durable
journal event per transition, exact retry, original output bytes, cold replay,
and final current Source and permission checks. The supervisor additionally
requires final installed Source/profile pins and an exact passing control,
records separate logs and terminal evidence for each child, and stops on the
first failed or timed-out child. A phase failure has no resumable token; inspect
the retained originals and prepare a fresh plan and fixtures.

Source and plan validation alone do not qualify any native transition. All
eight missing-family config groups and later dependent inputs must be supplied
from actual final-release producer receipts before `PASS-all28` is possible.
