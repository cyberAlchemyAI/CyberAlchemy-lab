# Local Project artifact pilot

`pilot.py` prepares one new `project-identity/v1` artifact, `project:lab-strattum-feature-gap-pilot`, for the selected installed API76 governance v5 branch. It verifies the installed member's exact source manifest and validates its literal 13-field record against the installed ProjectIdentity schema before using fresh synthetic qualification keys and a private disposable `/tmp` Store. A successful run would retain the signed local transaction and an in-process cold readback receipt under `.local/strattum-new-project-pilot/`; it would still be an artifact in the baseline Project's Store, not a separate Project State or durable runtime namespace.

The first installed run stopped before native review or commit. The v4 runtime profile pins `authority/project-state-transitions/current.json` to SHA-256 `8ba8ee25ccbf12721d800c693120a3452ddf1ec44...`, while the installed file is SHA-256 `12937950af2a00ef329deb1a922275250c61ad199b8f6216eab448e06bf49984`. The retained private refusal is `.local/strattum-new-project-pilot/run-0001/REFUSAL.json` (SHA-256 `d99e9739c743f6caaed856830e6ddbd706b78e579064765b2db9d1bf3677eae6`). No new Project was admitted.

The first fresh API76 build produced a real signed family, API76 package view, and archive. Its isolated installation then failed the installed cold API check: API76's guard rejected the governance v5 source rows that its package view deliberately selected. The entire failed installation remains private under `.local/strattum-new-project-pilot/api76-build-0001/`; no pilot Project call ran. The checkout guard was repaired and independently reviewed, then a fresh archive and installation were built. The failed installed bytes remain unchanged.

The repaired API76 build `api76-build-0003` passed fresh installed cold API qualification. Its governed pilot `run-0002` then received `integrity-failed` from `checkpoint.resolve` before any durable governance operation. The native Store remains at bootstrap sequence 0 and its private Store is retained under the reconciliation receipt. The installed governance v5 adapter assumes every native target record has `node_id`; ProjectIdentity/v1 instead has the selected `project_id` identity field. No governed Project admission occurred.

The isolated API76 `api76-build-0003` installation passed its cold API qualification (`INSTALLATION-RESULT.json` SHA-256 `5c14af8942cf5c93c630729768839350073c1c7dbab081c5c40c762f8aaef646`). A single independently reviewed `pilot_native.py` invocation then called the selected native `Store.apply` with a synthetic local approval. The Store committed sequence 1, but the pilot's postcommit receipt failed: it sent a 1,980,014-byte signed transaction through an API JSON parser limited to 1 MiB. `native-run-0001/REFUSAL.json` (SHA-256 `32a9287381153ed966030d4166c115b4370a64e37dce3608f9466e938588d61d`) and `RECONCILIATION-REQUIRED.json` (SHA-256 `bd2256ba8ca333ee5f48bce2597f9134e554a677ed572df5b754b242a2d36598`) remain intact. The native operation was **not retried**.

`reconcile_native.py` read the committed Store, verified its exact signed transaction, owner approval, current ProjectIdentity carrier, Project original, and cold replay, then copied the six Store files into a new owner-private 0700 directory and cold replayed that copy. Its separate `native-recovery-0001/RECOVERY-RESULT.json` is SHA-256 `d273d655983e45bbe766628b7bd451a270b6822810be28c1ca9419655956be3d`: `PASS-reconciled-local-ProjectIdentity-admission` for `project:lab-strattum-feature-gap-pilot`, native HEAD sequence 1. Both the original `/tmp` Store and failed run receipts were preserved. The recovered Store is under `/home/vlad_/.local/share/cyberalchemy-lab/strattum-new-project-pilot/native-recovery-0001/NATIVE-STORE`.

This establishes one **local native ProjectIdentity artifact** with `authority_effect:none`. It does not establish a successful governance API checkpoint/admission, canonical repository admission, independent Project State namespace, or separate Project runtime. `Project/v1` remains unadmitted in the selected baseline.

Read-only checks from the repository root:

```bash
python3 -m unittest implementation/lab-runtime/local-host/strattum-new-project-pilot-0001/test_native_pilot_boundary.py implementation/lab-runtime/local-host/strattum-new-project-pilot-0001/test_native_recovery_boundary.py -v
sha256sum /home/vlad_/.local/share/cyberalchemy-lab/strattum-new-project-pilot/native-recovery-0001/RECOVERY-RESULT.json
python3 - <<'PY'
from pathlib import Path
import hashlib, json, stat
p = Path('/home/vlad_/.local/share/cyberalchemy-lab/strattum-new-project-pilot/native-recovery-0001')
r = json.loads((p / 'RECOVERY-RESULT.json').read_bytes())
assert r['result'] == 'PASS-reconciled-local-ProjectIdentity-admission'
assert r['store_head']['sequence'] == 1 and r['separate_project_runtime'] is False
assert stat.S_IMODE(p.stat().st_mode) == stat.S_IMODE((p / 'NATIVE-STORE').stat().st_mode) == 0o700
assert all(hashlib.sha256((p / name).read_bytes()).hexdigest() == digest for name, digest in r['retained_originals'].items())
assert all(hashlib.sha256((p / 'NATIVE-STORE' / name).read_bytes()).hexdigest() == digest for name, digest in r['store_files'].items())
print('read-only receipt and retained-byte checks PASS')
PY
```

Never rewrite an installed lookup or failed installed cut to make a pin pass. Do not retry `checkpoint.resolve`, `admission.apply`, or `native-Store.apply` when a corresponding `RECONCILIATION-REQUIRED.json` exists; inspect the retained private Store first.
