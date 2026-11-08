# Observed current-family phase ledger

`reconcile.py` is a disjoint, read-only verifier for the selected local native Source/Reader/Mapper/Context family and the API33 whole-class run. It rehashes the five native phase results and their selected source/package bindings, confirms the 24-hour Source period and two cold replays, then attributes each API test's actual UTC and monotonic duration to the *observed* public Reader, Context delivery, and Session expiries. The old Context construction delivery expiry remains a separate historical field; API33 creates new deliveries at request time.

The ledger contains no raw policy, response body, key, or subprocess output. `callback_count` and `pure_scope_boundary_count` remain `null` because the current API runner does not instrument those events. A missing per-case lease appears as a missing lease kind, never as a synthetic current lease. This ledger is bounded T35 evidence and does not alone qualify the original protected Source8 runtime or full T35 callback requirements.

When the API33 runner has produced `working/whole-classes-result.json`, run:

```bash
python3.14 -I -B implementation/lab-runtime/local-host/phase-ledger-0002/reconcile.py
python3.14 -I -B -m unittest discover -s implementation/lab-runtime/local-host/phase-ledger-0002 -p 'test_*.py' -q
```

The output file is created once at mode 0600. Use a new versioned `--output` path for a later API rerun; old observations remain intact.
