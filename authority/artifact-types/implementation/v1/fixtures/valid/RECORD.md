<!-- GENERATED FILE: canonical data is record.json. -->

# Implementation fixture

- Identity: `implementation:example-001`
- Kind: `implementation`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "conforms_to_schema_refs": [
    "schema:artifact-type-registry/v2"
  ],
  "environment_contract_ref": "contract:python-runtime",
  "execution_entrypoint_ref": "python:validate.py",
  "implementation_kind": "validator",
  "realizes_capability_refs": [
    "product-capability:effective-state-resolution"
  ]
}
```

## Declared relation roles

- `source` on `relation.binds-implementation` with `ontology` `ontology:example-001`

## Claim ceiling

Example Implementation fixture for schema and relation-role validation only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
