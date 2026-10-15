[Documentation home](../../README.md)

# Role assignment · v1

<a id="type-cal-artifact-type-role-assignment-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Role assignment · v1

# Role assignment · v1

This contract specifies requirements for records of kind `role-assignment`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Role Assignment](def-cal-definition-role-assignment.md#def-cal-definition-role-assignment)

<a id="type-cal-artifact-type-role-assignment-v1-section-1"></a>

## Prepare a record

- `authority_effect`
- `kind`
- `node_id`
- `owner_ref`
- `scope_ref`
- `status`
- `assignee_kind`
- `assignee_ref`
- `role_ref`
- `assignment_basis_ref`
- `assignment_state`
- `period`
- `responsibility_refs`
- `authority_claim_refs`
- `owner_route`
- `challenge_route`
- `successor_refs`
- `claim_ceiling`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**Declared endpoint kinds for this exact carrier:** [role-assignment](endpoint-role-assignment.md#endpoint-role-assignment)

### Required fields and schema rules

**Fields required at the selected level:** authority_effect, kind, node_id, owner_ref, scope_ref, status, assignee_kind, assignee_ref, role_ref, assignment_basis_ref, assignment_state, period, responsibility_refs, authority_claim_refs, owner_route, challenge_route, successor_refs, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.role-assignment/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/kind",
  "value": "role-assignment"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../assets/6006dd6a6bdb-artifact.json)

**Schema**

[Read the schema](../../assets/bb5dfb9d3eec-schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

bb5dfb9d3eecf2cd86b84310a1f1a60c770ea7c109a5995401f58eb64347327c

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
