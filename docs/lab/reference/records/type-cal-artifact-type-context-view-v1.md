[Documentation home](../../README.md)

# Context view · v1

<a id="type-cal-artifact-type-context-view-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Context view · v1

# Context view · v1

This contract specifies requirements for records of kind `context-view`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Context View](def-cal-definition-context-view.md#def-cal-definition-context-view)

<a id="type-cal-artifact-type-context-view-v1-section-1"></a>

## Prepare a record

- `authority_effect`
- `kind`
- `node_id`
- `owner_ref`
- `scope_ref`
- `status`
- `request_ref`
- `context_ref`
- `context_version_ref`
- `source_epoch`
- `generated_at`
- `expires_at`
- `included_material`
- `excluded_material`
- `lineage_refs`
- `limitations`
- `selection_basis`
- `owner_route`
- `challenge_route`
- `claim_ceiling`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**[Content example from the incident:](../../tutorials/incident-walkthrough.md)** Prepare a frozen answer to the session’s task-information request, with selected source versions and limits. This describes the subject; a complete record must satisfy the full contract.

[Inspect a complete specimen and a one-field failure →](../record-examples.md#example-context-view)

**Declared endpoint kinds for this exact carrier:** [context-view](endpoint-context-view.md#endpoint-context-view)

### Required fields and schema rules

**Fields required at the selected level:** authority_effect, kind, node_id, owner_ref, scope_ref, status, request_ref, context_ref, context_version_ref, source_epoch, generated_at, expires_at, included_material, excluded_material, lineage_refs, limitations, selection_basis, owner_route, challenge_route, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.context-view/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/kind",
  "value": "context-view"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/context-view/v1/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/context-view/v1/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

08b7e0667bc43b45bc125c06c18bc21b91fc72d0f9c2d7c1dade2b7e6b7668c2

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
