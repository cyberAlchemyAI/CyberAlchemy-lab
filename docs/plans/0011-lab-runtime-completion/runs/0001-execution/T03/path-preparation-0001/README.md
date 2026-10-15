# Pure invocation-local root path preparation candidate

The candidate retains defensive helper `9de43ed...` as an exact immutable preimage. Only `selected`, `verify_all` and `capture_one` differ: prepare the canonical root once per invocation, compose its parts with relative selector parts, and keep the original slice semantics. Direct selector callers remain compatible. No integrity check, callback, hash backend, row, external rule or attachment/cleanup check is removed.

Actual selected V2/0004 controls passed 37 cases, including 384 selector parity combinations and owned filesystem order/replacement/cleanup checks. A separate unprofiled process verified the original public 1,310-row table in six alternating samples with full 1,010 dependency guards. Candidate median was lower, but overlapping ranges and uncontrolled load prevent a general speedup or Session-margin claim.

The initial timing harness had a path-indexing typo and exited before measurement. Its source, execution selection and terminal are retained. The corrected harness has a distinct filename, selection and outputs; candidate helper bytes stayed unchanged.

This is an independently reviewable pure candidate. Shared helper/API/profiles/native families and original periods/grants remain unchanged. Future caller selection must independently select the candidate’s exact new origin and pin after review.
