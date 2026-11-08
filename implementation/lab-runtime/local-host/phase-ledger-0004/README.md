# Current-family lifetime ledger with deliberate expiry

This version reads the selected native five-phase chain and the versioned
API33 T02 whole-class receipt from `source8-api30-rebind-0004`. It preserves
the phase-ledger-0002 source/Reader/Mapper/Context hash checks, two cold
replays, actual UTC and monotonic case times, and each observed public lease
expiry. It requires the exact versioned Session timer successor pin, all 99
ordered unique selected test IDs, and the separately identified current
Source8 Machine case. Every selected path component under the repository must
be a real directory or file, not a symlink.

The two Session timer tests and Machine transport expiry test deliberately
finish after their issued Session expiry. The ledger requires an observed
expired Session for each passing one and reports it separately. Other cases
ending after an observed lease appear under
`unexpected_expired_observed_lease_cases`; no missing lease is synthesized.
The Source period must still cover every case. Callback and pure-scope counts
remain unknown for the frozen API33 execution.

After the v4 whole-class result is terminal, create a private, exclusive
receipt with:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B implementation/lab-runtime/local-host/phase-ledger-0004/reconcile.py
```

Ten cold verifier tests pass in normal and optimized Python. A PASS ledger
does not by itself make the original protected Source8 run or T35 complete.
