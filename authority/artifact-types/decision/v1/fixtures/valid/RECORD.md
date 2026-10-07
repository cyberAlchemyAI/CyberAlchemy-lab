<!-- GENERATED FILE: canonical data is record.json. -->

# Decision fixture

- Identity: `decision:example-001`
- Kind: `decision`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "decision_maker_ref": "person-reference:owner",
  "declared_effect_refs": [
    "effect:registry-v2-admitted-current"
  ],
  "evidence_basis_refs": [
    "receipt:registry-v2-validation"
  ],
  "selected_outcome": "admit exact reviewed bytes",
  "subject_refs": [
    "artifact-type:registry/v2"
  ]
}
```

## Declared relation roles

- `source` on `relation.declares-effect-on` with `artifact-type` `artifact-type:example-001`

## Claim ceiling

Example Decision fixture for schema and relation-role validation only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
