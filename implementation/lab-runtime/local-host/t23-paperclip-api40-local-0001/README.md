# T23 disposable Paperclip process to API40 Base journey

`RUN-0007.json` records one **local technical PASS** on this WSL host. A real cached Paperclip `2026.1005.0` process adapter spawned one isolated Python reader. The reader authenticated to the current local legacy fixture through API40, obtained `lab.status` and `catalog.get` results, then sent a `lab.status` call with `scope:outside` in the same connection and received `error/unauthorized`. All three replies passed their selected schema, request, handler, profile, and trusted-context bindings. The API40 child and Paperclip process exited 0.

The run created a fresh private `/tmp` fixture policy/key/workspace and removed it afterward. No Lab mutation was requested; the workspace had zero objects and zero effect-journal entries before and after. API40's current-legacy Session host created one owned, empty, mode-0600 `.session-custody.lock` in the workspace journal at service startup; the reader checks that exact distinction. Neither a Paperclip server nor a persistent Paperclip service or database was started, and the existing private Paperclip pilot state was not used.

The fixture policy has `workspace.max_actions=1` and API40's required broad `LEGACY_SUPPORTED` operation list; the schema rejects a zero-action candidate grant. The actual `read-plan.json` and executed calls were read-only status/catalog plus the wrong-scope refusal. This is an isolated current **legacy fixture**, not the original protected Source8 Session. The result is not evidence of human usefulness, a Paperclip server/API integration, original reader/mapper/Context issuer grants, or whole API40 qualification. The cached Paperclip `execute.js` path is hashed before and after use, but Node reopens it during import; its transitive dependencies are not byte-backed attestations either. The API fixture helper is selected by preflight/guard and imported by path, not compiled from immutable verified bytes. The task's own Node and Python entrypoints use verified-byte bootstraps. This run establishes a technical journey under the observed local state, not adversarial module-origin safety.

Earlier `RUN-0001.json` through `RUN-0006.json` are retained refusal diagnostics. They led to the explicit Node selection, the API40 one-action schema minimum, the current-legacy fixture selection, and the Session custody-lock distinction. They are not positive product receipts.

From the repository root, run the fast controls with:

```sh
python3 -B -m unittest discover -s implementation/lab-runtime/local-host/t23-paperclip-api40-local-0001 -p test_run.py -q
python3 -O -B -m unittest discover -s implementation/lab-runtime/local-host/t23-paperclip-api40-local-0001 -p test_run.py -q
```

A fresh live run creates a new `RUN-*.json` receipt and takes several minutes because API40 verifies its full selected source/profile on entry and exit:

```sh
python3 -B implementation/lab-runtime/local-host/t23-paperclip-api40-local-0001/run.py --receipt RUN-0008.json
```
