[Documentation home](../../README.md)

# Intent resolution · v1

<a id="type-cal-artifact-type-intent-resolution-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Intent resolution · v1

# Intent resolution · v1

This contract specifies requirements for records of kind `intent-resolution`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Intent Resolution](def-cal-definition-intent-resolution.md#def-cal-definition-intent-resolution)

<a id="type-cal-artifact-type-intent-resolution-v1-section-1"></a>

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

**[Content example from the incident:](../../tutorials/incident-walkthrough.md)** Choose an investigation as the response to the reported need and declare how satisfaction will be assessed. This describes the subject; a complete record must satisfy the full contract.

**Declared endpoint kinds for this exact carrier:** [intent-resolution](endpoint-intent-resolution.md#endpoint-intent-resolution)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, node_id, kind, name, lifecycle_state, authority_effect, owner_ref, scope_ref, evidence_refs, challenge_route, successor_refs, relation_refs, payload, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.intent-resolution/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-intent-resolution/v1"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../assets/76053e704f74-artifact.json)

**Schema**

[Read the schema](../../assets/e82365ac90fd-schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

e82365ac90fd6c5963a23b40e98fe4e6a461ad16ee8ce402479e7cbf3d71e987

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
