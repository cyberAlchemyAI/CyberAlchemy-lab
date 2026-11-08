# Event-file parity resource experiment profile

- `PROFILE_ID`: `cal-ontology-event-file-parity/v1`
- `LIFECYCLE_OWNER`: CyberAlchemy ontology-product prototype construction
- `ARTIFACT_TYPE`: implementation recovery and resource experiment
- `CONTRACT_PATH`: `resource-requirements.json`
- `PROMPT_SET`: deterministic 250,000-subject synthetic canonical-format event files
- `REGIME_SET`: `parity`
- `PROFILE_VALIDATION`: performed by `validate.py`

## Quality bar

- Fail before generation when declared RAM, disk, or inode headroom is absent.
- Enforce a hard virtual-memory limit on generator and recovery processes.
- Generate 250,000 semantic and 250,000 exact governance event files.
- Derive the expected source envelope and graph index independently in memory.
- Record logical bytes, allocated filesystem bytes, file count, wall time, and peak RSS.
- Start two independent recovery processes against the unchanged fixture.
- Match the source envelope and graph index exactly in both processes.
- Stay inside every declared time, memory, and filesystem bound.
- Reject a byte-valid but non-canonical event file.
- Remove the temporary fixture after durable evidence is written.

## Claim ceiling

This is local synthetic 250,000-subject event-file parity evidence. It does not
establish production capacity, sustained ingestion, persistence, checkpoint
validity, crash consistency, durability, approval, admission, or activation.
