<!-- GENERATED FILE: canonical data is record.json. -->

# Effect fixture

- Identity: `effect:example-001`
- Kind: `effect`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "effect_kind": "lifecycle-transition",
  "effective_when": "decision postimage is valid",
  "intended_state": "admitted-current",
  "subject_ref": "artifact-type:registry/v2",
  "verification_refs": [
    "registry:snapshot-0002"
  ]
}
```

## Declared relation roles

- `target` on `relation.declares-effect-on` with `decision` `decision:example-001`

## Claim ceiling

Example Effect fixture for schema and relation-role validation only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
