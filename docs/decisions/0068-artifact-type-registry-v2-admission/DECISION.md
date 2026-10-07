<!-- GENERATED FILE: canonical data is decision.json. -->

# Artifact Type Registry/v2 and initial registry admission

- Decision: `CAL-DECISION-0068-ARTIFACT-TYPE-REGISTRY-V2-ADMISSION`
- Status: `owner-admitted`
- Artifact Type: `cal.artifact-type.artifact-type-registry/v2` — `admitted-current`
- Initial registry: `CAL-ARTIFACT-TYPE-EFFECTIVE-STATE-REGISTRY-0001` — `admitted-current`
- Descriptor snapshot: `56`
- Admitted-contract snapshot: `33`
- Other Artifact Types admitted: `0`
- Consumer activations: `0`

## Bootstrap rule

Decision 0068 enters a later registry refresh. The admitted initial snapshot remains byte-for-byte unchanged.

## Claim ceiling

This overlay admits the exact Artifact Type Registry/v2 candidate.2 contract and the exact initial effective-state registry instance. It does not admit any other Artifact Type or instance, change any state represented inside the snapshot, perform a semantic rebind, admit a relation, or activate a consumer or runtime.
