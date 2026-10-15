[Documentation home](../../README.md)

# Role · v1

<a id="type-cal-artifact-type-role-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Role · v1

# Role · v1

This contract specifies requirements for records of kind `role`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Role](def-cal-definition-role.md#def-cal-definition-role)

<a id="type-cal-artifact-type-role-v1-section-1"></a>

## Prepare a record

- `authority_effect`
- `kind`
- `node_id`
- `owner_ref`
- `scope_ref`
- `status`
- `name`
- `purpose`
- `functions`
- `responsibility_refs`
- `eligible_authority_relation_kinds`
- `authority_boundary`
- `exclusions`
- `lifecycle_state`
- `successor_refs`
- `owner_route`
- `challenge_route`
- `claim_ceiling`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**Declared endpoint kinds for this exact carrier:** [role](endpoint-role.md#endpoint-role)

### Required fields and schema rules

**Fields required at the selected level:** authority_effect, kind, node_id, owner_ref, scope_ref, status, name, purpose, functions, responsibility_refs, eligible_authority_relation_kinds, authority_boundary, exclusions, lifecycle_state, successor_refs, owner_route, challenge_route, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.role/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/kind",
  "value": "role"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/role/v1/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/role/v1/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

4705f341530d0a20e98655e93febead21a4dfc24cef1c3dcac7d792a649bb2b4

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
