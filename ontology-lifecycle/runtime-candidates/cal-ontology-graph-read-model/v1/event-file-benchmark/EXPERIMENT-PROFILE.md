# Generated event-file recovery experiment profile

- `PROFILE_ID`: `cal-ontology-generated-event-file-recovery/v1`
- `LIFECYCLE_OWNER`: CyberAlchemy ontology-product prototype construction
- `ARTIFACT_TYPE`: implementation recovery experiment
- `CONTRACT_PATH`: `../recovery-requirements.json`
- `PROMPT_SET`: deterministic generated canonical-format semantic and governance events
- `REGIME_SET`: `medium`, `large`
- `PROFILE_VALIDATION`: performed by `validate.py`

## Quality bar

- Build the exact locked generator and recovery binary before timing.
- Generate one event pair per governed subject in a temporary directory.
- Derive the expected source envelope and graph index independently in memory.
- Start two independent recovery processes per profile.
- Measure event-store load and validation separately from calculation and graph rebuild.
- Match cursor, source-event-set digest, and rebuilt index digest exactly.
- Complete recovery inside the declared profile objective.
- Reject a byte-valid but non-canonical event file.
- Preserve attempt evidence, raw logs, and source-bound reports without preserving the temporary fixtures.

## Claim ceiling

The events are synthetic files that conform to the canonical event schema. They
are not canonical CyberAlchemy ontology records. Evidence applies only to the
declared 5,000- and 50,000-subject local profiles. It proves no 250,000-subject
event-file parity, RSS bound, persistence, checkpoint, crash consistency,
durability, approval, admission, or activation claim.
