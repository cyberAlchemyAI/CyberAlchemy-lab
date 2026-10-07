<!-- GENERATED FILE: canonical data is record.json. -->

# Evidence Set fixture

- Identity: `evidence-set:example-001`
- Kind: `evidence-set`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "coverage_statement": "Exact candidate schema and hostile cases",
  "item_refs": [
    "receipt:carrier-validation"
  ],
  "limitations": [
    "No runtime behavior evaluated"
  ],
  "source_refs": [
    "source:validator-run"
  ]
}
```

## Declared relation roles

- `source` on `relation.derives-from` with `experiment-run` `experiment-run:example-001`

## Claim ceiling

Example Evidence Set fixture for schema and relation-role validation only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
