# T35 explicit boundary observation candidate

`observe.py` is a disjoint driver helper for a later selected API successor. It
routes an **already selected** callback or context-manager factory through the
same object, checks its exact source file and object identity, and records
actual UTC and monotonic entry/exit. It refuses an already expired Source or
observed lease before invoking a callback; if expiry arrives during a callback
or pure scope, the original callback or scope exit runs, then the result is
refused. Original exceptions pass through. It records only callback type,
times, status, and observed deadline, never request/reply bodies or keys.

`selected-boundaries.json` names 15 selected API33 boundary candidates:
Service and Machine calls, Reader and Session guards, Context delivery,
the native fact read scope, API fact-copy scopes, and Vault and journal locks.
The ledger accepts only the exact selected row object returned by a closed
selection; test functions use an explicitly `fixture-only` selection. The
selection requires an independently supplied release digest, the exact
API33 source-manifest digest, source-manifest membership for API files, and
fresh hashes for every selected file. These are exact byte references for
later integration, **not** evidence that the running API33 suite uses this helper.
The current `phase-ledger-0002` must keep callback and pure-scope counts null
for the live seventh run. A future disjoint API runner must route each selected
boundary explicitly, bind the selector and recorder bytes, and attach its
per-case receipt before a successor ledger can report observed counts. Hidden
nested callbacks remain unknown even then; no profiler or monitoring hook is
installed by this candidate.

The eleven cold tests use real clocks. They cover successful callback and scope
entry/exit counts, wrong origin/identity, expiry before and after work, and
exception/cleanup preservation in normal and optimized Python. They also
refuse a same-object callback whose `__code__` was replaced while its selected
source file stayed unchanged. A late original
exception stays original and carries an independent expiry flag. They do not
qualify a protected runtime or prove full T35 lifecycle completion. The caller
supplies the observed lease deadline; this candidate does not authenticate the
lease origin. A later integration must bind each deadline to its actual issued
Reader/Context/Session permission before a lease-margin claim is valid.
Expiry after a callback or scope refuses its returned result; it does not
roll back work already done inside that call.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B implementation/lab-runtime/local-host/phase-ledger-0003/test_observe.py
PYTHONDONTWRITEBYTECODE=1 python3 -B -O implementation/lab-runtime/local-host/phase-ledger-0003/test_observe.py
```
