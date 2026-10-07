<!-- GENERATED FILE: canonical data is record.json. -->

# Relation Kind fixture

- Identity: `relation-kind:example-001`
- Kind: `relation-kind`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "allowed_endpoint_pairs": [
    {
      "source_kind": "work",
      "target_kind": "project"
    }
  ],
  "axis_id": "axis.membership",
  "inverse_ref": "none",
  "predicate": "member-of",
  "qualifier_schema_ref": "schema:membership-qualifiers/v1"
}
```

## Declared relation roles

- `target` on `relation.declares-effect-on` with `decision` `decision:example-001`

## Claim ceiling

Example Relation Kind fixture for schema and relation-role validation only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
