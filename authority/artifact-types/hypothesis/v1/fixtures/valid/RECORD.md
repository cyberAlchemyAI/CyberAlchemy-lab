<!-- GENERATED FILE: canonical data is record.json. -->

# Hypothesis fixture

- Identity: `hypothesis:example-001`
- Kind: `hypothesis`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "disposition": "open",
  "falsification_conditions": [
    "Two builds from identical bytes produce different digests"
  ],
  "observation_targets": [
    "measurement-result:registry-digest"
  ],
  "proposition": "Registry generation is deterministic for identical inputs"
}
```

## Declared relation roles

- `target` on `relation.evidence-bears-on` with `evidence-set` `evidence-set:example-001`

## Claim ceiling

Example Hypothesis fixture for schema and relation-role validation only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
