# Independent T35 explicit-boundary candidate review

**Verdict: bounded PASS as a disjoint observation helper; T35 remains open.**
Reviewed `phase-ledger-0003/observe.py` SHA-256
`29bed81a37ba58efd1a1f74be5c975b7af51aa0183d26f996b3989e25814f79e`,
`test_observe.py` SHA-256
`bf7335abfb727d70338f8d363ee2836574aba0520b33adea5d91ac12689248fe`,
and the 15-row selected-boundaries JSON SHA-256
`eb7ef625460202a579dfa24381443881dbfbe218cd0d41b2f158e92b1f9eb915`.
Eleven tests pass under normal and optimized Python.

The selector checks the independent release digest, selected API33 source
manifest digest, source-manifest membership for API paths, exact file bytes and
closed boundary names. The ledger now accepts only the identical selected row
object from a closed `VerifiedBoundaries` mapping; synthetic test callbacks
are explicitly `fixture-only`. This closes the prior arbitrary-Selection
counting gap. Before invoking a callback it also recompiles selected source
and compares a deep live code signature, checks module-member origin for
non-fixture rows, and preserves the same callable object. A same-object
`__code__` substitution now refuses; I had independently reproduced that
substitution passing under the earlier implementation.

The actual-clock tests cover entry/exit counts, expiry before invocation,
expiry after execution, original exceptions and scope cleanup. A late
exception retains its original class while an independent
`expired_at_completion` flag records expiry. The receipt's claim ceiling
correctly states that post-work expiry does not roll back an effect and that
Source/lease deadlines remain caller supplied rather than issuer
authenticated.

This candidate has **not** been routed through the frozen seventh API33 test
run or an actual selected Reader/Context/Session callback. Thus the current
T35 phase ledger must retain `null` callback and pure-scope counts. A later
selected successor needs real per-case callback/scope invocation, issued
lease-origin binding, exact recorder/selector byte pins and cold replay before
reporting observed counts or a full lifetime verdict. The helper counts only
explicitly routed boundaries; nested callbacks remain unmeasured.
