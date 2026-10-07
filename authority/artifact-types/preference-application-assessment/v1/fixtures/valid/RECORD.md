<!-- GENERATED FILE: canonical data is record.json. -->

# Preference Application Assessment fixture

- Identity: `preference-application-assessment:example-001`
- Kind: `preference-application-assessment`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "applicability": "applies",
  "conflict_refs": [],
  "feasibility": "feasible",
  "output_ref": "response:candidate-review",
  "override_refs": [],
  "preference_revision_ref": "communication-preference:show-revised-example@1",
  "request_ref": "request:review-next-artifact",
  "required_response_change": "Include one complete realistic fixture before asking for admission."
}
```

## Declared relation roles

- `target` on `relation.challenges` with `challenge-event` `challenge-event:example-001`

## Claim ceiling

Realistic Preference Application Assessment example for candidate review only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
