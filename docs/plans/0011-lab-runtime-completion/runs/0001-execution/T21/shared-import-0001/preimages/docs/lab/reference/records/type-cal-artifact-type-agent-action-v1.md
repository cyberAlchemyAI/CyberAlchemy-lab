[Documentation home](../../README.md)

# Agent action · v1

<a id="type-cal-artifact-type-agent-action-v1"></a>

[Reference catalog](../artifact-types.md#catalog-types) / Exact record

# Agent action · v1

This contract specifies requirements for records of kind `agent-action`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Agent Action](def-cal-definition-agent-action.md#def-cal-definition-agent-action)

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

**Declared endpoint kinds for this exact carrier:** [agent-action](endpoint-agent-action.md#endpoint-agent-action)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, node_id, kind, name, lifecycle_state, authority_effect, owner_ref, scope_ref, evidence_refs, challenge_route, successor_refs, relation_refs, payload, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.agent-action/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-agent-action/v1"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/agent-action/v1/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/agent-action/v1/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

16ba34e853afd2feee61b0d64fd81dce778725c6b9a788b7d81daaded9f7b508

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to this catalog](../artifact-types.md#catalog-types)
