[Documentation home](../../README.md)

# Agent instance · v1

<a id="type-cal-artifact-type-agent-instance-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Agent instance · v1

# Agent instance · v1

This contract specifies requirements for records of kind `agent-instance`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Agent Instance](def-cal-definition-agent-instance.md#def-cal-definition-agent-instance)

<a id="type-cal-artifact-type-agent-instance-v1-section-1"></a>

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

**[Content example from the incident:](../../tutorials/incident-walkthrough.md)** One temporary machine-agent instance performs session 12; a later session uses a new instance. This describes the subject; a complete record must satisfy the full contract.

**Declared endpoint kinds for this exact carrier:** [agent-instance](endpoint-agent-instance.md#endpoint-agent-instance)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, node_id, kind, name, lifecycle_state, authority_effect, owner_ref, scope_ref, evidence_refs, challenge_route, successor_refs, relation_refs, payload, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.agent-instance/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-agent-instance/v1"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../assets/7b384e156cd3-artifact.json)

**Schema**

[Read the schema](../../assets/0dc09d05ec9c-schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

0dc09d05ec9c932a6073c1cab41e6a81e9ea3a85116e21b1789923ad6915bf30

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
