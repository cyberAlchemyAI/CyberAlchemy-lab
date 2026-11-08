# API41 current Source8 Machine replay

This disjoint runner keeps the frozen API33 99-case Session/Custody evidence intact. It requires the independent reviewer to supply the terminal v4 result's exact SHA-256, checks the original runner/timer bytes and all 99 ordered inherited method IDs and per-case results, and accepts a combined v4 `FAIL` only when the one appended current Source8 Machine case has the known `CurrentFixtureReader` selector error. It then tests the current native Source8 reader under API41 and executes the inherited seven-read-operation Machine case with a fresh host policy, Context delivery, and Session. Wrong reader class and wrong module origin are explicit refusals. The old source is bound by three fixed hashes and its period is checked expired; the native Reader must refuse its exact old source/package pins for the expected predicate.

Cold evidence-selection tests:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B implementation/lab-runtime/local-host/api41-current-machine-replay-0001/test_run_machine.py
PYTHONDONTWRITEBYTECODE=1 python3 -B -O implementation/lab-runtime/local-host/api41-current-machine-replay-0001/test_run_machine.py
```

Run after the v4 whole-case result is terminal:

```sh
env -u PYTHONPATH PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 python3 -B -u implementation/lab-runtime/local-host/api41-current-machine-replay-0001/run_machine.py --v4-result-sha256 '<independently reviewed terminal SHA-256>' > implementation/lab-runtime/local-host/api41-current-machine-replay-0001/working/current-source8-machine-run-0001.log 2>&1
```

The runner verifies all 207 selected API41 source rows before importing package code and again after the test, then writes `working/current-source8-machine-result-0001.json` once. A cold test pass does not qualify the live Machine path. The API41 source/profile remain a current Source8 guarded-read successor only; this route makes no admission, contest-outcome, publication, historical Source5, or completed-T02 claim until the actual receipt is independently reviewed.
