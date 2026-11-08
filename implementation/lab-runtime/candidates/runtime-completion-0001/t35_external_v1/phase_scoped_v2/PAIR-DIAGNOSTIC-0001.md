# Phase-scoped Source→Reader paired diagnostic, inactive candidate

`prefix_pair_diagnostic_0001.py` is a disjoint successor to the sealed
single-attempt prefix and diagnostic probes. It captures the 1,703 selected
repository input bytes once, creates one disposable episode and role control,
and uses those exact application bytes for at most two separate Source→Reader
attempts. Each attempt gets a fresh disposable family, signer, and private
store. The 27-template plan stays immutable; only the Source/Reader prefix is
materialized, and future Mapper/Context output paths remain absent.

The registered 900-second SIGALRM watchdog covers selected-input capture,
pure construction, and sandbox effects. Each child is capped at 180 seconds
and the remaining pair window. An inherited SIGALRM mask is refused before
selected-input capture. SIGALRM is blocked and the watchdog is
suspended around no-replace evidence write, fsync, and held-parent verification,
so 900 seconds is **not**
a strict total process wall-time bound. The result reports measured elapsed
wall time. The episode validity window must cover 900 seconds plus a 60-second
margin before either attempt starts. A timer or child timeout is a failure.

On the effect-capable entry point, `phase-pair-attempt-0001.json` is published
immediately after attempt 1, before attempt 2 begins. Attempt 2 gets
`phase-pair-attempt-0002.json`, including a skipped outcome if attempt 1 left
unclean scratch. `phase-pair-summary-0001.json` binds all completed attempt
receipts. These names are O_EXCL and never replaced. Interruption after
attempt 1 leaves its receipt available; an I/O failure may leave a partial
numbered leaf, which blocks reuse and must be audited rather than removed.
The publisher recursively admits closed counts, digests, booleans, stage and
failure codes. It drops argv shapes and never publishes stdout, stderr, raw
exception text, source bytes, signer keys, or scratch paths.

The pair has the same **selected application input vector** by construction.
The three derived selection digests (`plan_leaf`, `stage_control`, and
`source_manifest`) are compared only when both attempts successfully produce
all three. A refusal before that point yields unknown derived equality, not
a claim of difference. Wall clock, signer/store, `constructed_at`, duration,
and system Python/libraries can vary between attempts and are not fully
SHA-closed. Two PASS outcomes cannot explain the earlier ContractError; a
mixed outcome can localize a stage without proving intrinsic nondeterminism.

This is fixture-only work. It grants no LC-U02-05 acceptance, host/protected
Source8 qualification, installed same-UID isolation, real issuer/owner
authority, or activation. The historical failed replay remains part of the
record. No paired effect run is authorized by this design note or pure tests;
an exact-source independent static review must precede one bounded run.
