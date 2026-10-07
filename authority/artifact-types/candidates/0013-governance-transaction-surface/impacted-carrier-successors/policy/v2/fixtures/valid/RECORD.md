<!-- GENERATED FILE: canonical data is record.json. -->

# Policy fixture

- Identity: `policy:example-001`
- Kind: `policy`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "effective_period": "until superseded",
  "exception_route": "route:policy-exception",
  "governed_scope_ref": "scope:artifact-type-admission",
  "issuer_ref": "role:governance-owner",
  "rule_refs": [
    "rule:exact-byte-admission"
  ]
}
```

## Declared relation roles

- `target` on `relation.governed-by` with `admission-transaction` `admission-transaction:governance-transaction-example`

## Claim ceiling

Example Policy fixture for schema and relation-role validation only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
