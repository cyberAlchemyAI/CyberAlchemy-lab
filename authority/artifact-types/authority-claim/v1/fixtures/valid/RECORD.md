<!-- GENERATED FILE: canonical data is record.json. -->

# Authority Claim fixture

- Identity: `authority-claim:example-001`
- Kind: `authority-claim`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "authority_basis_refs": [
    "decision:0068"
  ],
  "claimant_ref": "role:artifact-type-owner",
  "claimed_permissions": [
    "admit-exact-reviewed-artifact-type"
  ],
  "decision_scope_ref": "decision-scope:artifact-type-registry",
  "limitations": [
    "no consumer activation"
  ]
}
```

## Declared relation roles

- `target` on `relation.evidence-bears-on` with `evidence-set` `evidence-set:example-001`

## Claim ceiling

Example Authority Claim fixture for schema and relation-role validation only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
