[Documentation home](../../README.md)

# Project state · v2

<a id="type-cal-artifact-type-project-state-v2"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Project state · v2

# Project state · v2

This contract specifies requirements for records of kind `project-state`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Project State](def-cal-definition-project-state.md#def-cal-definition-project-state)

<a id="type-cal-artifact-type-project-state-v2-section-1"></a>

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

**[Content example from the incident:](../../tutorials/incident-walkthrough.md)** Persist permitted observations, evidence, proposals and decisions with their exact standing. This describes the subject; a complete record must satisfy the full contract.

**Declared endpoint kinds for this exact carrier:** [project-state](endpoint-project-state.md#endpoint-project-state)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, node_id, kind, name, lifecycle_state, authority_effect, owner_ref, scope_ref, evidence_refs, challenge_route, successor_refs, relation_refs, payload, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.project-state/v2

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-project-state/v2"
}
````

**Acceptance record**

Governance record types admission

**Contract**

[Read the type contract](../../assets/ed6b7fcd97c5-artifact.json)

**Schema**

[Read the schema](../../assets/a8d565464111-schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

a8d565464111eaa9c2e829d8f01277b009b7fe4dffae70efd1167c95450f7e28

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
