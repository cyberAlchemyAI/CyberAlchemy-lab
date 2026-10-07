<!-- GENERATED FILE: canonical data is record.json. -->

# Contract fixture

- Identity: `contract:example-001`
- Kind: `contract`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "breach_route": "route:contract-challenge",
  "obligation_refs": [
    "obligation:preserve-exact-bytes"
  ],
  "party_refs": [
    "role:artifact-type-owner"
  ],
  "permission_refs": [
    "permission:validate-candidate"
  ],
  "prohibition_refs": [
    "prohibition:implicit-admission"
  ],
  "subject_refs": [
    "artifact-type:registry/v2"
  ]
}
```

## Declared relation roles

- `target` on `relation.conforms-to` with `capability-instance` `capability-instance:example-001`

## Claim ceiling

Example Contract fixture for schema and relation-role validation only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
