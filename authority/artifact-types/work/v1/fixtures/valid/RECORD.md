<!-- GENERATED FILE: canonical data is record.json. -->

# Work fixture

- Identity: `work:example-001`
- Kind: `work`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "completion_state": "candidate-complete",
  "goal_refs": [
    "goal:complete-integrated-lab-model"
  ],
  "input_refs": [
    "plan:step5-carrier-closure"
  ],
  "output_refs": [
    "artifact-type:implementation/v1"
  ],
  "project_ref": "project:lab-semantic-governance",
  "work_statement": "Materialize missing endpoint carriers"
}
```

## Declared relation roles

- `source` on `relation.member-of` with `project` `project:example-001`

## Claim ceiling

Example Work fixture for schema and relation-role validation only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
