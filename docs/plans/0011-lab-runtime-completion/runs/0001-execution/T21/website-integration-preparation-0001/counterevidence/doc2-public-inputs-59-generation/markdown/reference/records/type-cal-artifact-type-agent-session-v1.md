[Documentation home](../../README.md)

# Agent session · v1

<a id="type-cal-artifact-type-agent-session-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Agent session · v1

# Agent session · v1

This contract specifies requirements for records of kind `agent-session`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Agent Session](def-cal-definition-agent-session.md#def-cal-definition-agent-session)

<a id="type-cal-artifact-type-agent-session-v1-section-1"></a>

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

**[Content example from the incident:](../../tutorials/incident-walkthrough.md)** Bind the instance to its exact assignment, views, permissions, inputs, budgets and termination conditions. This describes the subject; a complete record must satisfy the full contract.

[Inspect a complete specimen and a one-field failure →](../record-examples.md#example-agent-session)

**Declared endpoint kinds for this exact carrier:** [agent-session](endpoint-agent-session.md#endpoint-agent-session)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, node_id, kind, name, lifecycle_state, authority_effect, owner_ref, scope_ref, evidence_refs, challenge_route, successor_refs, relation_refs, payload, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.agent-session/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-agent-session/v1"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../assets/d1c4be36dedc-artifact.json)

**Schema**

[Read the schema](../../assets/e05780ad1ee2-schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

e05780ad1ee2f87cc4bc288a05cca24c6e0ac35e97771ff689de0ec64d14aae8

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
