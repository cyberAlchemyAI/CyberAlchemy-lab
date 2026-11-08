# Atomic checkpoint process-interruption experiment

- `PROFILE_ID`: `cal-checkpoint-crash-consistency/v1`
- `LIFECYCLE_OWNER`: CyberAlchemy ontology-product prototype construction
- `ARTIFACT_TYPE`: checkpoint maintenance failure-injection experiment
- `CONTRACT_PATH`: `requirements.json`
- `PROMPT_SET`: frozen W7 canonical event-file epoch
- `REGIME_SET`: `w7-process-interruption`
- `PROFILE_VALIDATION`: performed by `validate.py`

## Quality bar

- Build the locked release binary outside the measured sequences.
- Run two independent sequences in separate temporary directories.
- Create cursor 15 through a synced same-directory stage, atomic rename, and parent-directory sync.
- Terminate the writer with exit 75 after cursor 23 staging sync; require the cursor 15 target to remain byte-identical and exactly recoverable to cursor 47.
- Replace cursor 15 with cursor 23 normally and require a synced success receipt.
- Terminate the writer with exit 75 after renaming cursor 35 but before parent-directory sync; require the target visible to the running system to be a valid cursor 35 checkpoint that exactly recovers to cursor 47.
- Require retrying the exact cursor 35 bytes to be idempotent without another stage or rename.
- Reject regressing and incomparable cursor pairs without changing target bytes.
- Reject an invalid existing target without changing its bytes.
- Reject a symbolic-link target without touching its referent.
- Reject a concurrent writer while preserving target bytes.
- Require deterministic normalized state evidence across both attempts.
- Preserve raw logs and timestamped reports, then remove temporary test state.

## Claim ceiling

This experiment proves local process-interruption behavior at two explicit
checkpoint write boundaries. It does not simulate sudden power loss, storage
controller behavior, filesystem corruption, or cross-platform rename semantics,
and it establishes no durability, production, approval, admission, activation,
publication, or cutover claim.
