[Documentation home](../../README.md)

# Principal reference · v1

<a id="type-cal-artifact-type-principal-reference-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Principal reference · v1

# Principal reference · v1

This contract specifies requirements for records of kind `principal-reference`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Principal Reference](def-cal-definition-principal-reference.md#def-cal-definition-principal-reference)

<a id="type-cal-artifact-type-principal-reference-v1-section-1"></a>

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

**Declared endpoint kinds for this exact carrier:** [principal-reference](endpoint-principal-reference.md#endpoint-principal-reference)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, node_id, kind, name, lifecycle_state, authority_effect, owner_ref, scope_ref, evidence_refs, challenge_route, successor_refs, relation_refs, payload, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.principal-reference/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-principal-reference/v1"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/principal-reference/v1/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/principal-reference/v1/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

eb428ca6aaa41f53d088d95f9e7e817da41ad5eff6c7dbacb290a8db0930a2c4

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
