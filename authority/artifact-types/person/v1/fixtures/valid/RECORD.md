<!-- GENERATED FILE: canonical data is record.json. -->

# Person fixture

- Identity: `person:example-001`
- Kind: `person`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "display_name": "Repository owner",
  "identity_boundary": "Human identity remains separate from references, roles, sessions, and Agents",
  "identity_evidence_refs": [
    "identity-claim:local-owner"
  ],
  "privacy_classification": "restricted",
  "stable_identity_ref": "person:local-owner"
}
```

## Declared relation roles

- `target` on `relation.asserts-identity-of` with `person-reference` `person-reference:example-001`

## Claim ceiling

Example Person fixture for schema and relation-role validation only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
