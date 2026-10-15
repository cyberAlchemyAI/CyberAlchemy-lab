[Documentation home](../../README.md)

# Failure occurrence · v1

<a id="type-cal-artifact-type-failure-occurrence-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Failure occurrence · v1

# Failure occurrence · v1

This contract specifies requirements for records of kind `failure-occurrence`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Failure Occurrence](def-cal-definition-failure-occurrence.md#def-cal-definition-failure-occurrence)

<a id="type-cal-artifact-type-failure-occurrence-v1-section-1"></a>

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

[Inspect a complete specimen and a one-field failure →](../record-examples.md#example-failure-occurrence)

**Declared endpoint kinds for this exact carrier:** [failure-occurrence](endpoint-failure-occurrence.md#endpoint-failure-occurrence)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, node_id, kind, name, lifecycle_state, authority_effect, owner_ref, scope_ref, evidence_refs, challenge_route, successor_refs, relation_refs, payload, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.failure-occurrence/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-failure-occurrence/v1"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/failure-occurrence/v1/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/failure-occurrence/v1/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

2c1eb7d10cfa1a4450d8cb7982150d78ff74c5c4039fd2a4d59b8b4a4d40e288

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
