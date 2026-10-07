<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Role Assignment Fixture

- Identity: `role-assignment:reviewer:artifact-type-reviewer`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

- **Assignee Kind**: `person-reference`
- **Assignee Ref**: `person-reference:repository-reviewer`
- **Assignment Basis Ref**: `decision:assign-artifact-type-reviewer`
- **Assignment State**: `active`
### Authority Claim Refs

```json
[
  "authority-claim:may-recommend-artifact-type-admission"
]
```

- **Challenge Route**: `route:role-assignment-challenge`
- **Claim Ceiling**: `This assignment binds an assignee to a Role in scope and time. It does not create Team Membership or authority beyond separately admitted claims.`
- **Kind**: `role-assignment`
- **Owner Ref**: `role:artifact-type-owner`
- **Owner Route**: `role:role-assignment-owner`
### Period

```json
{
  "end": null,
  "start": "2026-10-05T00:00:00Z"
}
```

### Responsibility Refs

```json
[
  "responsibility:artifact-type-review-quality"
]
```

- **Role Ref**: `role:artifact-type-reviewer`
- **Scope Ref**: `scope:cyberalchemy-lab-model-review`
### Successor Refs

```json
[]
```


## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
