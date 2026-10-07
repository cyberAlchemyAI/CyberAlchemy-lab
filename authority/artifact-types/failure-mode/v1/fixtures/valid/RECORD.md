<!-- GENERATED FILE: canonical data is record.json. -->

# Failure Mode fixture

- Identity: `failure-mode:example-001`
- Kind: `failure-mode`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "control_binding_refs": [
    "failure-control-binding:coverage-audit"
  ],
  "detection_method_refs": [
    "checklist:complete-lab-model-layers@1"
  ],
  "exclusions": [
    "A deliberately narrow review"
  ],
  "expected_boundary_ref": "contract:complete-lab-model-coverage@1",
  "manifestation": "A review presented as complete omits a required lifecycle layer.",
  "recovery_expectation": "Revise the model and preserve residue.",
  "signal_refs": [
    "feedback:owner-correction"
  ],
  "subject_kind_ref": "complete-system-model-review"
}
```

## Declared relation roles

- `target` on `relation.challenges` with `challenge-event` `challenge-event:example-001`

## Claim ceiling

Realistic Failure Mode example for candidate review only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
