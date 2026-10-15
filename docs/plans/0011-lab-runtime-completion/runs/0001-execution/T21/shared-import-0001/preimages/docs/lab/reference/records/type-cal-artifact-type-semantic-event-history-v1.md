[Documentation home](../../README.md)

# Semantic event history · v1

<a id="type-cal-artifact-type-semantic-event-history-v1"></a>

[Reference catalog](../artifact-types.md#catalog-types) / Exact record

# Semantic event history · v1

This contract specifies requirements for records of kind `semantic-event-history`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Semantic Event History](def-cal-definition-semantic-event-history.md#def-cal-definition-semantic-event-history)

## Prepare a record

- `schema_version`
- `node_id`
- `kind`
- `name`
- `record_state`
- `authority_effect`
- `owner_ref`
- `scope_ref`
- `evidence_refs`
- `challenge_route`
- `successor_refs`
- `payload`
- `claim_ceiling`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**Declared endpoint kinds for this exact carrier:** [semantic-event-history](endpoint-semantic-event-history.md#endpoint-semantic-event-history)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, node_id, kind, name, record_state, authority_effect, owner_ref, scope_ref, evidence_refs, challenge_route, successor_refs, payload, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.semantic-event-history/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-semantic-event-history/v1"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/semantic-event-history/v1/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/semantic-event-history/v1/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

f81cd811a4c15c25ea5459cca9d7ee6ed8ebe112e0bf38c81fda487b452311bd

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to this catalog](../artifact-types.md#catalog-types)
