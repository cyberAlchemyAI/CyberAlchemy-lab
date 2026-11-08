# Independent review: T35 phase ledger 0001

**Verdict: HOLD as a qualifying T35 lifetime/strictest-lease ledger; bounded PASS as a local timing and output-digest experiment.**

`python3 -B implementation/lab-runtime/local-host/phase-ledger-0001/test_record_phase.py` and the same command with `-O` each passed **3/3**. The ledger captures real UTC and monotonic start/end, subprocess exit, output lengths and SHA-256 digests without copying stdout/stderr into the receipt. It reserves a `0600` exclusive receipt before launching the child, so an existing receipt prevents another command from running. The test demonstrates expiry refusal before a command and selection of a stricter caller-supplied deadline. The source file and test create no authority effect.

## Blocking findings for T35 use

1. **Timeout or launch failure strands an empty receipt.** `record()` reserves the exclusive file, then `subprocess.run(... timeout=3600)` may raise `TimeoutExpired` or `OSError`. The exception handler closes the descriptor but writes no terminal observation. I reproduced a timeout by injecting `TimeoutExpired`: the receipt existed at size zero, and retry with the same path failed `FileExistsError`. Capture a bounded uncertain/timeout receipt with start/end and child status, or provide a separately safe reconciliation rule. Never turn an unknown child effect into a fresh blind retry.
2. **The receipt does not prove the actual strictest lease.** `selection()` accepts any JSON file with an `expires_at` string and hashes those bytes; it does not cold-verify a signed current source or bind a selected Reader/Context/Session grant. `--deadline` rows are optional even for `reader`, `context` and `session` phases. I ran a `session` phase with no Session deadline and received `ended_before_strictest_deadline: true` based on the source time alone. Require phase-appropriate deadlines from pinned, verified inputs, or label the result explicitly caller-supplied and ineligible for T35 qualification.

Additional limits: the one-hour subprocess timeout is not the source/reader/Session deadline; a child may continue after a lease expires and the recorder only detects this after return. This tool can measure violation but cannot enforce runtime expiry. The test imports `record_phase` as a top-level module, so `python -m unittest` from the repository root fails import while direct script invocation passes; document or fix the test command. Output is spooled to temporary files without a size cap, so this is not yet a bounded-output host harness. No protected family or original-role phase was run in this review.

No candidate code, original task state, Docker resource or authority record was changed by this review.
