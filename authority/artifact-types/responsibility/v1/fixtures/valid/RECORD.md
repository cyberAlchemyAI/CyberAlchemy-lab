<!-- GENERATED FILE: canonical data is record.json. -->

# Responsibility fixture

- Identity: `responsibility:example-001`
- Kind: `responsibility`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "accountable_role_refs": [
    "role:artifact-type-owner"
  ],
  "completion_evidence_refs": [
    "decision:artifact-type-admission"
  ],
  "responsibility_statement": "Review and admit exact Artifact Type postimages",
  "scope_ref": "scope:artifact-type-governance"
}
```

## Declared relation roles

- `target` on `relation.assigned-to` with `person-reference` `person-reference:example-001`

## Claim ceiling

Example Responsibility fixture for schema and relation-role validation only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
