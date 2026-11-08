# T31 operational-learning producer and consumer prerequisite

A fresh original W06 episode completed in isolated historical source
`run-0007/`. It signed a candidate Lesson in a disposable branch, invalidated
the first Agent, reconstructed the exact Lesson in a new Agent's Project State,
ran one controlled later application, assessed its bounded outcome, and made
an unapplied improvement proposal. Independent cold replay passed with 57
original records, 15 typed connections and no private key restoration.

`verify_outputs.py` checks the exact original bytes and carrier schemas for the
three selected operational-learning output sets: Operational Lesson, Lesson
Application, and Lesson Outcome Assessment plus Improvement Signal. It checks
the actual later Lesson → Application → Outcome → Improvement references, the
signed export hash, 57 record and 21 blob hashes, 29 current original-source
pins, and the no-effect claim. Five focused positive/negative tests pass.

This producer does **not** emit an original WorkflowRun transition event.
Consequently it supplies three output-carrier/consumer prerequisites, **zero
additional T31 transition applications**, and the previous local candidate
count remains **4/28 with 24 original transition identities open**. The bounded
outcome says only `supported-for-this-controlled-case`; the corrected builder
had succeeded before this Lesson, so this run cannot establish its causal or
general benefit.

The primary checkout's `authority/project-state-transitions/current.json` has
changed since W06's selected `d75` source. The original producer refused that
source. For this historical reconstruction only, an isolated sparse HEAD
worktree used the selected `HEAD^` `.gitignore` bytes and one ignored W05
`.pyc` whose bytes matched the original W05 receipt. The original native
executable was rebuilt at its historical path with SHA-256
`62f4244cfe23b8f0252e99b3778ed9a78807a2e67657f069882c823ed97e7f59`;
the producer's reader required a real, nonsymlink executable path. No primary
source or authority file was changed. The observed cold result is in
`COLD-READBACK-0001.json`, and `RESULT.json` is the machine carrier/consumer
verification. The independent review of the preceding four-ref slice is
[`REVIEW.md`](../working/t31-independent-review-0001/REVIEW.md).

```bash
python3 -B implementation/lab-runtime/local-host/t31-workflow-stream-0003/verify_outputs.py
python3 -B -m unittest discover -s implementation/lab-runtime/local-host/t31-workflow-stream-0003 -p 'test_*.py' -v
```
