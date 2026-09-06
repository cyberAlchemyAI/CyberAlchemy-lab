# Disposable checkpoint and canonical-tail recovery protocol

The harness builds the locked candidate binaries, performs a resource
preflight, and generates a temporary canonical-format event-file fixture. It
creates a checkpoint at cursor 49,000 from the validated event store, then
measures full replay and checkpoint-plus-tail recovery in separate processes.
Checkpoint construction is recorded but excluded from recovery timing because
it is a prior cache-maintenance operation.

Every recovery remains bound to the final expectation produced independently
by the fixture generator. The checkpoint strategy must validate its own body,
validate the prefix boundary carried by the checkpoint, validate each canonical
tail event, and produce the same source-set and graph-index digests as full
replay. The performance comparison uses four attempts per strategy in balanced
alternating order. It compares process elapsed medians and enforces a maximum
1.25 checkpoint-to-full median ratio. A performance benefit is reported only
when the checkpoint median is lower and checkpoint wins at least three of four
attempt-number pairs; correctness does not manufacture a speed claim.

Three controls run after the measured attempts: leading whitespace in the
checkpoint must be rejected as `CHECKPOINT_NON_CANONICAL_JSON`; a changed checkpoint body
with its old digest must be rejected as `CHECKPOINT_BODY_DIGEST_MISMATCH`; and
leading whitespace in the first semantic tail event must be rejected as
`NON_CANONICAL_JSON`.

All evidence is local and non-authoritative. No result selects a database,
persistence design, checkpoint admission, operational activation, or cutover.
