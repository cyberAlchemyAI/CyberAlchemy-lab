# T24 local acceptance matrix

`matrix.py` cold-reads the pinned Product acceptance text, original 46-task DAG,
63-unit manifest, all 36 local task contracts, the local engineering state,
and every evidence path referenced there. It emits one row for each AC01–AC13
with its exact clause digest, mapped tasks and current evidence-byte digests.
The T19 managed-file proof is explicitly added to AC07 because its original
task header omits that mapping. State statuses are reported as source data,
not independently verified task completions. All original
acceptance rows remain `PENDING`; no fixture run, status label or result
envelope is promoted to Product acceptance. In particular, AC12 has no
observed human owner pilot, and protected Source8, admission and release
remain unqualified.

From the repository root, run:

`python3 -B implementation/lab-runtime/local-host/t24-acceptance-matrix-0001/matrix.py`

The checked-in `MATRIX.json` is a current-state snapshot. Rebuild it after
engineering-state changes. Seven focused tests run normally and with `-O` and
include missing-clause, changed-mapping, changed-evidence, absolute-path and
unsupported-status negatives.

The local stream's matrix-generation check is complete: all 13 clauses map to
current evidence or an explicit unfulfilled original clause, and the independent
review passed. The original T24 acceptance audit remains open while technical
criteria and human observations remain unfulfilled. This component has no
authority effect.
