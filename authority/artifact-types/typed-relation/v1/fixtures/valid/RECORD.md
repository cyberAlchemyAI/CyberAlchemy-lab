<!-- GENERATED FILE: canonical data is record.json. -->

# Typed Relation fixture

- Identity: `typed-relation:example-001`
- Kind: `typed-relation`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "qualifiers": [
    {
      "axis": "realization-role",
      "value": "validator"
    }
  ],
  "relation_evidence_refs": [
    "receipt:validator-pass"
  ],
  "relation_kind_ref": "relation.realizes",
  "relation_lifecycle_state": "candidate",
  "source_ref": "implementation:registry-validator",
  "target_ref": "product-capability:effective-state-resolution"
}
```

## Declared relation roles

- `source` on `relation.member-of` with `ontology` `ontology:example-001`

## Claim ceiling

Example Typed Relation fixture for schema and relation-role validation only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
