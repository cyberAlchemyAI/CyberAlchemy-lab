<!-- GENERATED FILE: canonical data is record.json. -->

# Failure Occurrence fixture

- Identity: `failure-occurrence:example-001`
- Kind: `failure-occurrence`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "cause_posture": "unresolved",
  "detection_evidence_refs": [
    "feedback:owner-correction/implementation"
  ],
  "expected_boundary_ref": "contract:complete-lab-model-coverage@1",
  "impact_refs": [
    "project:lab-semantic-governance"
  ],
  "observed_manifestations": [
    "Implementation omitted",
    "Agent memory ownership omitted"
  ],
  "occurrence_posture": "supported",
  "recovery_posture": "recovered-with-residue",
  "residue_refs": [
    "residue:carrier-closure-pending"
  ],
  "response_action_refs": [
    "agent-action:revise-model"
  ],
  "subject_ref": "review:lab-complete-model-initial"
}
```

## Declared relation roles

- `source` on `relation.occurs-during` with `agent-action` `agent-action:example-001`

## Claim ceiling

Realistic Failure Occurrence example for candidate review only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
