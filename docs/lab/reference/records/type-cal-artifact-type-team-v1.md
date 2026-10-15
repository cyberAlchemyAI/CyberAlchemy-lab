[Documentation home](../../README.md)

# Team · v1

<a id="type-cal-artifact-type-team-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Team · v1

# Team · v1

This contract specifies requirements for records of kind `team`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Team](def-cal-definition-team.md#def-cal-definition-team)

<a id="type-cal-artifact-type-team-v1-section-1"></a>

## Prepare a record

- `authority_effect`
- `kind`
- `node_id`
- `owner_ref`
- `scope_ref`
- `status`
- `name`
- `purpose`
- `identity_boundary`
- `owner_route`
- `lifecycle_state`
- `membership_refs`
- `responsibility_refs`
- `role_assignment_refs`
- `authority_claim_refs`
- `revision_history`
- `successor_refs`
- `challenge_route`
- `claim_ceiling`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**Declared endpoint kinds for this exact carrier:** [team](endpoint-team.md#endpoint-team)

### Required fields and schema rules

**Fields required at the selected level:** authority_effect, kind, node_id, owner_ref, scope_ref, status, name, purpose, identity_boundary, owner_route, lifecycle_state, membership_refs, responsibility_refs, role_assignment_refs, authority_claim_refs, revision_history, successor_refs, challenge_route, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.team/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/kind",
  "value": "team"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/team/v1/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/team/v1/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

87eeaa4fa82bcaf3963e0ab4cb41b3b2ad8c5fde58c19b3612e6caf044a188a1

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
