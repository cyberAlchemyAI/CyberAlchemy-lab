<!-- GENERATED FILE: canonical data is record.json. -->

# Constitution fixture

- Identity: `constitution:example-001`
- Kind: `constitution`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "amendment_policy_ref": "policy:constitution-amendment",
  "governed_scope_ref": "scope:lab-semantic-governance",
  "invariant_refs": [
    "invariant:no-implicit-authority"
  ],
  "rule_refs": [
    "rule:typed-coupling"
  ]
}
```

## Declared relation roles

- `target` on `relation.governed-by` with `artifact-type` `artifact-type:example-001`

## Claim ceiling

Example Constitution fixture for schema and relation-role validation only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
