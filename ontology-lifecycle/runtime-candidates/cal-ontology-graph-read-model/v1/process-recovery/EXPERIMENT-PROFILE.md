# Process recovery experiment profile

- `PROFILE_ID`: `cal-ontology-event-file-process-recovery/v1`
- `LIFECYCLE_OWNER`: CyberAlchemy ontology-product prototype construction
- `ARTIFACT_TYPE`: implementation recovery experiment
- `CONTRACT_PATH`: `../recovery-requirements.json`
- `PROMPT_SET`: frozen W7 semantic and governance event directories
- `REGIME_SET`: `w7-event-files`
- `PROFILE_VALIDATION`: performed by `validate.py`

## Quality bar

- Build the exact locked candidate before timing.
- Start two independent child processes after the build completes.
- Load 47 semantic and 47 governance event files in each child.
- Match cursor, source-event-set digest, and rebuilt index digest exactly.
- Complete each child-process recovery within the declared local objective.
- Reject a missing event directory and a changed expected index digest.
- Preserve raw logs, attempt evidence, and one source-bound report.

## Claim ceiling

Evidence applies only to the frozen W7 event-file fixture on this local system.
It proves no large event-file scale, persistence, checkpoint, crash consistency,
durability, approval, admission, or activation claim.
