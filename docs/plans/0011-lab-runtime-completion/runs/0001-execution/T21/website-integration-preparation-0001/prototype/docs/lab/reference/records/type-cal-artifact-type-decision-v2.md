[Documentation home](../../README.md)

# Decision · v2

<a id="type-cal-artifact-type-decision-v2"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Decision · v2

# Decision · v2

This contract specifies requirements for records of kind `decision`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Decision](def-cal-definition-decision.md#def-cal-definition-decision)

<a id="type-cal-artifact-type-decision-v2-section-1"></a>

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

**Declared endpoint kinds for this exact carrier:** [decision](endpoint-decision.md#endpoint-decision)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, node_id, kind, name, lifecycle_state, authority_effect, owner_ref, scope_ref, evidence_refs, challenge_route, successor_refs, relation_refs, payload, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.decision/v2

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-decision/v2"
}
````

**Acceptance record**

Governance record types admission

**Contract**

[Read the type contract](../../assets/662a72c6c30d-artifact.json)

**Schema**

[Read the schema](../../assets/d8858de94810-schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

d8858de9481049e23cd22b367b600dbeb3dc643b2d247ed91b8a6e57aff41dc9

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
