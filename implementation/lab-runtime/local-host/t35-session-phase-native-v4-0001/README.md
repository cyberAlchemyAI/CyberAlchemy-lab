# T35 d95 Session phase run

From the repository root, run `python3 -B implementation/lab-runtime/local-host/t35-session-phase-native-v4-0001/run.py`. The runner cold-pins the signed d95 Source period and frozen API source/profile, verifies the 15 selected callback definitions, and exercises an authenticated Context delivery plus a native Session open, guard, and close in a disposable private workspace. It records actual UTC timestamps and monotonic callback durations, checks lease ordering, refuses a past-deadline opening before a live resource or journal entry appears, and checks memory disposal and workspace cleanup.

The retained predecessor one-call receipt is only a pinned diagnostic dependency; current phase observations use the native-v4 API selection. This is local fixture evidence, with no owner/admission effect or claim about the original protected Source8 run.

`verify.py` cold-checks the selected manifests, run code, lease order, four API reply records, and six callback timestamps. Four mutation tests run normally and with optimized Python. The past-deadline refusal in this first run compares journal file names; it does not compare existing journal file bytes. Only explicitly routed callbacks are counted.
