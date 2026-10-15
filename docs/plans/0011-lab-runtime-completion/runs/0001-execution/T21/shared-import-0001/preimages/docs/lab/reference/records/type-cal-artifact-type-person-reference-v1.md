[Documentation home](../../README.md)

# Person reference · v1

<a id="type-cal-artifact-type-person-reference-v1"></a>

[Reference catalog](../artifact-types.md#catalog-types) / Exact record

# Person reference · v1

This contract specifies requirements for records of kind `person-reference`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Person Reference](def-cal-definition-person-reference.md#def-cal-definition-person-reference)

## Prepare a record

- `authority_effect`
- `kind`
- `node_id`
- `owner_ref`
- `scope_ref`
- `status`
- `local_label`
- `reference_type`
- `reference_value`
- `purpose`
- `identity_scope`
- `minimization_basis`
- `permitted_uses`
- `prohibited_uses`
- `lifecycle_state`
- `successor_refs`
- `owner_route`
- `challenge_route`
- `claim_ceiling`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**Declared endpoint kinds for this exact carrier:** [person-reference](endpoint-person-reference.md#endpoint-person-reference)

### Required fields and schema rules

**Fields required at the selected level:** authority_effect, kind, node_id, owner_ref, scope_ref, status, local_label, reference_type, reference_value, purpose, identity_scope, minimization_basis, permitted_uses, prohibited_uses, lifecycle_state, successor_refs, owner_route, challenge_route, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.person-reference/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/kind",
  "value": "person-reference"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/person-reference/v1/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/person-reference/v1/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

41622d391d7e22cb3a875f612b5738956707d98933b24c6f73b86b7285cd382e

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to this catalog](../artifact-types.md#catalog-types)
