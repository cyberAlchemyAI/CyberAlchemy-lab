<!-- GENERATED FILE: canonical data is record.json. -->

# Generated Output fixture

- Identity: `generated-output:example-001`
- Kind: `generated-output`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "generator_ref": "generator:endpoint-carrier/v1",
  "input_refs": [
    "artifact:implementation/v1"
  ],
  "output_digest": "sha256:0123456789abcdef",
  "reproducibility_receipt_ref": "receipt:projection-parity"
}
```

## Declared relation roles

- `source` on `relation.derives-from` with `source` `source:example-001`

## Claim ceiling

Example Generated Output fixture for schema and relation-role validation only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
