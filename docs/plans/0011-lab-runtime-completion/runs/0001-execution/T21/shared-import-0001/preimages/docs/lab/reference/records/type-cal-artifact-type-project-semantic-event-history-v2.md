[Documentation home](../../README.md)

# Project semantic event history · v2

<a id="type-cal-artifact-type-project-semantic-event-history-v2"></a>

[Reference catalog](../artifact-types.md#catalog-types) / Exact record

# Project semantic event history · v2

This contract specifies requirements for records of kind `project-semantic-event-history`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Project Semantic Event History](def-cal-definition-project-semantic-event-history.md#def-cal-definition-project-semantic-event-history)

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

**Declared endpoint kinds for this exact carrier:** [project-semantic-event-history](endpoint-project-semantic-event-history.md#endpoint-project-semantic-event-history)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, node_id, kind, name, lifecycle_state, authority_effect, owner_ref, scope_ref, evidence_refs, challenge_route, successor_refs, relation_refs, payload, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.project-semantic-event-history/v2

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-project-semantic-event-history/v2"
}
````

**Acceptance record**

Governance record types admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/candidates/0013-governance-transaction-surface/impacted-carrier-successors/project-semantic-event-history/v2/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/candidates/0013-governance-transaction-surface/impacted-carrier-successors/project-semantic-event-history/v2/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

f1f005d1b13185921b3d2c002fd794f026c36d00f2e83ef4031bc3c45f8a80c2

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to this catalog](../artifact-types.md#catalog-types)
