[Documentation home](../../README.md)

# Authority boundary · v1

<a id="type-cal-artifact-type-authority-boundary-v1"></a>

[Reference catalog](../artifact-types.md#catalog-types) / Exact record

# Authority boundary · v1

This contract specifies requirements for records of kind `authority-boundary`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Authority Boundary](def-cal-definition-authority-boundary.md#def-cal-definition-authority-boundary)

## Prepare a record

- `schema_version`
- `node_id`
- `kind`
- `name`
- `lifecycle_state`
- `authority_effect`
- `owner_ref`
- `scope_ref`
- `evidence_refs`
- `challenge_route`
- `successor_refs`
- `relation_refs`
- `payload`
- `claim_ceiling`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**Declared endpoint kinds for this exact carrier:** [authority-boundary](endpoint-authority-boundary.md#endpoint-authority-boundary)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, node_id, kind, name, lifecycle_state, authority_effect, owner_ref, scope_ref, evidence_refs, challenge_route, successor_refs, relation_refs, payload, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.authority-boundary/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-authority-boundary/v1"
}
````

**Acceptance record**

Governance record types admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/authority-boundary/v1/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/authority-boundary/v1/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

c4a3c525e2bd062a0dade7611e0f5fad4d37e233dd02d93f1251f97881bc06f8

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to this catalog](../artifact-types.md#catalog-types)
