# Recovery modeling records

The [rule source](rule-source.json) defines 20 candidate failure-specific Recovery Rules. The [index](index.json) points to one generated, source-digested [rule record](rules/rr-01.json) per ID. The [session recovery protocol](../../software/RECOVERY-PROTOCOL.md) explains their state and fairness consequences.

The [Recovery Rule](../carriers/recovery-rule/v1/request.json), [Recovery Decision](../carriers/recovery-decision/v1/request.json) and [Upload Attempt](../carriers/upload-attempt/v1/request.json) Artifact Type Requests have local descriptors and closed candidate schemas. Only the rules are authored concrete domain instances. The [synthetic fixtures](synthetic/) demonstrate a recovery decision and an incomplete upload shape; they are not participant, failure or media records.

Rebuild after editing the source with `python3 tools/build_recovery_records.py`, then run `python3 tools/validate_recovery_records.py` and refresh the [coverage index](../carriers/coverage.json). These checks establish source parity and schema shape only. The Administration Policy, compatible released replacement forms, timed browser evidence and owner approvals remain open.
