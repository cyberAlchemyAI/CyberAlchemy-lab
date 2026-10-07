<!-- GENERATED FILE: canonical data is record.json. -->

# Review fixture

- Identity: `review:example-001`
- Kind: `review`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "disposition": "ready-for-decision",
  "finding_refs": [
    "finding:no-collapse-pass"
  ],
  "review_profile_ref": "review-profile:artifact-type",
  "reviewer_refs": [
    "person-reference:owner"
  ],
  "subject_ref": "artifact-type:implementation/v1"
}
```

## Declared relation roles

- `target` on `relation.frames` with `context` `context:example-001`

## Claim ceiling

Example Review fixture for schema and relation-role validation only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
