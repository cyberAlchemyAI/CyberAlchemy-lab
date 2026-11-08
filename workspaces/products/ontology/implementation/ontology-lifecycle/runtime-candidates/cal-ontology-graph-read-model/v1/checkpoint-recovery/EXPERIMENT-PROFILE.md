# Disposable checkpoint and canonical-tail recovery experiment

- `PROFILE_ID`: `cal-checkpoint-tail-recovery/v1`
- `LIFECYCLE_OWNER`: CyberAlchemy ontology-product prototype construction
- `ARTIFACT_TYPE`: implementation recovery and resource experiment
- `CONTRACT_PATH`: `resource-requirements.json`
- `PROMPT_SET`: deterministic 50,000-subject synthetic canonical-format event files
- `REGIME_SET`: `large`
- `PROFILE_VALIDATION`: performed by `validate.py`

## Quality bar

- Fail before fixture construction when declared RAM, disk, or inode headroom is absent.
- Build locked release binaries outside every timed region.
- Generate 50,000 semantic and 50,000 exact governance event files.
- Create one self-digested disposable checkpoint at semantic and governance cursor 49,000.
- Run four full-replay recoveries and four checkpoint-plus-tail recoveries in balanced alternating order.
- Require all eight recoveries to produce the exact independently derived final source envelope and graph index digest.
- Require the checkpoint path to open exactly 1,000 semantic and 1,000 governance tail event files.
- Require deterministic normalized receipts within each strategy and a checkpoint median no more than 1.25 times the full-replay median.
- Classify a performance benefit as supported only when the checkpoint median is lower and checkpoint wins at least three of four attempt-number pairs; do not require or claim that benefit for this cache format.
- Enforce the declared elapsed-time, peak-RSS, fixture-size, and checkpoint-size limits.
- Reject a non-canonical checkpoint, a checkpoint with a stale body digest, and a non-canonical canonical-tail event.
- Remove the temporary fixture and checkpoint after durable evidence is written.

## Claim ceiling

This is local synthetic 50,000-subject disposable-checkpoint evidence. The
checkpoint is a derived cache, never a canonical event source. The experiment
does not establish production capacity, durability, crash consistency,
sustained ingestion, multi-writer ordering, approval, admission, or activation.
