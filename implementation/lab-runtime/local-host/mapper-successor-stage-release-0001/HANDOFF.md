# Mapper successor stage one-shot release 0001 — not dispatched

Status: **effect-capable wrapper frozen for an independent static review;
actual private stage effect not run**. This disjoint wrapper pins the corrected
stage 0002 freeze SHA-256
`c214e06c122186124a11f16e456257a1f800cfea8b05361da9d18247ece60311`
and its bounded independent static PASS review SHA-256
`fad287769926dafe0a662ce9007d28b4bd90ba4523364b51a3ecd6a30974633f`.
It checks all fourteen frozen member bytes, the effect-disabled predecessor,
991-file/931-source-directory/933-target-directory closure, 37 private input
rows, and exact stage/copy/verifier plan digests. The reviewed `stage.py`,
`held_stage.py` and `anchored_copy.py` are compiled from those checked bytes;
neither unchecked rereads nor bytecode cache supply the executed stage code.

Read-only `--preflight` passes against the current retained Reader stage and
absent Mapper attempt. It dynamically reselects the actual Reader effect and
current Source period, checks source inventory and public hashes while the
private inventory rows stay metadata-only, verifies the public native ELF,
and checks finite capacity. The reviewed selector reads selected private
metadata JSON; no `branch.snapshot` body is opened by preflight.

Only `--execute-reviewed-one-shot` temporarily enables this exact loaded
stage module, calls preflight, invokes its consumed-once effect, and resets
the in-memory flag on success or failure. Its intended effect claims the
exclusive owner-only Mapper attempt, fsyncs a consumed marker before private
copy, uses held nofollow target/source custody and identity checks, stages the
991 files and public native ELF, verifies closure, and writes a stage-only
terminal. It never launches Mapper Docker or the native executable. The
attempt must never be retried after an ambiguous or failed claim/effect.

Normal and optimized wrapper suites pass **4/4**. The tests check real
selection/preflight, exact checked-byte module loading, temporary enable and
reset, and failure propagation after a simulated terminal write/final-close
error. The actual effect route has **not** been invoked. The existing Mapper
attempt remains absent.

An independent static reviewer must assess this wrapper and its exact freeze,
including module-name restoration, review binding, preflight-to-effect
recheck, one-shot semantics, and failure propagation. After a PASS review,
the operator must run a current same-state predispatch check and exactly one
external invocation, retaining OS exit, stdout and stderr independently.
Terminal presence or `OBSERVED_STAGE_ONLY` never suffices: use the result
only after **external OS exit zero AND independent stage effect review** of
the consumed marker, terminal, absence of UNKNOWN, exact staged inventory,
file hashes/modes/identities, native attachment and retained Reader stage.
A final-close failure can leave a terminal without a zero external exit; that
case must not be accepted or retried. A subsequent Mapper Docker release and
output verifier require their own separate review and observed effect.
