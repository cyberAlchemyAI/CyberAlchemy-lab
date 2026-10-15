[Documentation home](../../README.md)

# Project governance event history · v2

<a id="type-cal-artifact-type-project-governance-event-history-v2"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Project governance event history · v2

# Project governance event history · v2

This contract specifies requirements for records of kind `project-governance-event-history`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Project Governance Event History](def-cal-definition-project-governance-event-history.md#def-cal-definition-project-governance-event-history)

<a id="type-cal-artifact-type-project-governance-event-history-v2-section-1"></a>

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

**Declared endpoint kinds for this exact carrier:** [project-governance-event-history](endpoint-project-governance-event-history.md#endpoint-project-governance-event-history)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, node_id, kind, name, lifecycle_state, authority_effect, owner_ref, scope_ref, evidence_refs, challenge_route, successor_refs, relation_refs, payload, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.project-governance-event-history/v2

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-project-governance-event-history/v2"
}
````

**Acceptance record**

Governance record types admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/candidates/0013-governance-transaction-surface/impacted-carrier-successors/project-governance-event-history/v2/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/candidates/0013-governance-transaction-surface/impacted-carrier-successors/project-governance-event-history/v2/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

c4c39e3d171e17b3ea6e5902cb3542bc63af33c3b88dc34c02a7d930d6ce3987

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
