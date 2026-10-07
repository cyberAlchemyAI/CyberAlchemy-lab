<!-- GENERATED FILE: canonical data is registry.json. -->

# Artifact Type effective-state registry — Snapshot 0002

- Registry: `CAL-ARTIFACT-TYPE-EFFECTIVE-STATE-REGISTRY-0002`
- Version: `2.0.0-candidate.2`
- Status: `candidate-postimage`
- Authority effect: `none`
- Predecessor: `CAL-ARTIFACT-TYPE-EFFECTIVE-STATE-REGISTRY-0001`
- Exact delta: Registry/v2 descriptor, admitted contract, current identity mapping, and Decision 0068 overlay

## Inventory

- Admitted Contract Count: `34`
- Admitted Current Count: `29`
- Admitted Historical Count: `5`
- Descriptor Count: `57`
- Descriptor Declared Ref Count: `50`
- Descriptor Identity Count: `46`
- Descriptor Resolved Ref Count: `52`
- Duplicate Resolution Count: `2`
- Semantic Binding Counts: `{"admitted-successor-required": 1, "candidate-rebind-required": 4, "current-as-declared": 52}`
- State Counts: `{"admitted-current": 22, "admitted-historical": 5, "candidate-unadmitted": 28, "resolved-duplicate": 2}`

## Added current carrier

| Artifact Type ref | Effective state | Decision |
| --- | --- | --- |
| `cal.artifact-type.artifact-type-registry/v2` | `admitted-current` | `CAL-DECISION-0068-ARTIFACT-TYPE-REGISTRY-V2-ADMISSION` |

## Realistic example

A consumer asks which Artifact Type contract governs effective-state registry instances. Snapshot 0002 resolves the identity `cal.artifact-type.artifact-type-registry` to `cal.artifact-type.artifact-type-registry/v2`, and the exact instance discriminator remains `/schema_version = cyberalchemy-lab-artifact-type-effective-state-registry/v2`.

## Claim ceiling

This candidate snapshot resolves 57 visible Artifact Type descriptors and 34 admitted contract entries after ingesting Decision 0068. It does not admit this snapshot, alter Snapshot 0001, admit any remaining candidate Artifact Type or instance, perform a semantic rebind, admit a relation, or activate a consumer or runtime.
