<!-- GENERATED FILE: canonical data is record.json. -->

# Decision Scope fixture

- Identity: `decision-scope:example-001`
- Kind: `decision-scope`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "excluded_effects": [
    "activate-consumer",
    "admit-instance"
  ],
  "permitted_effects": [
    "admit"
  ],
  "subject_kind_refs": [
    "artifact-type"
  ],
  "subject_refs": [
    "artifact-type:registry/v2"
  ]
}
```

## Declared relation roles

- `target` on `relation.scopes-authority-over` with `authority-claim` `authority-claim:example-001`

## Claim ceiling

Example Decision Scope fixture for schema and relation-role validation only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
