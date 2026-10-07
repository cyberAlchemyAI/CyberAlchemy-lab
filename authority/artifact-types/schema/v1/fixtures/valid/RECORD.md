<!-- GENERATED FILE: canonical data is record.json. -->

# Schema fixture

- Identity: `schema:example-001`
- Kind: `schema`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "conformance_profile_ref": "evaluation-profile:json-schema",
  "content_digest": "sha256:fedcba9876543210",
  "dialect": "https://json-schema.org/draft/2020-12/schema",
  "schema_ref": "schema:implementation/v1",
  "subject_kind_ref": "implementation"
}
```

## Declared relation roles

- `target` on `relation.binds-implementation` with `implementation` `implementation:example-001`

## Claim ceiling

Example Schema fixture for schema and relation-role validation only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
