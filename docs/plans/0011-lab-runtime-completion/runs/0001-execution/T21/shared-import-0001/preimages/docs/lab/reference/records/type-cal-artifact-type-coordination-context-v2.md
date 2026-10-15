[Documentation home](../../README.md)

# Coordination context · v2

<a id="type-cal-artifact-type-coordination-context-v2"></a>

[Reference catalog](../artifact-types.md#catalog-types) / Exact record

# Coordination context · v2

This contract specifies requirements for records of kind `coordination-context`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Coordination Context](def-cal-definition-coordination-context.md#def-cal-definition-coordination-context)

## Prepare a record

- `schema_version`
- `coordination_context_id`
- `version`
- `status`
- `authority_effect`
- `classification`
- `product_ref`
- `project_ref`
- `goal_ref`
- `purpose`
- `consumer_refs`
- `intended_uses`
- `subject_scope`
- `source_policy_refs`
- `bounded_context_refs`
- `owner_ref`
- `owner_route`
- `lifecycle_state`
- `predecessor_ref`
- `revision_history`
- `challenge_route`
- `evidence_refs`
- `residue_refs`
- `source_direction`
- `claim_ceiling`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**Declared endpoint kinds for this exact carrier:** None in this selected catalog.

### Required fields and schema rules

**Fields required at the selected level:** schema_version, coordination_context_id, version, status, authority_effect, classification, product_ref, project_ref, goal_ref, purpose, consumer_refs, intended_uses, subject_scope, source_policy_refs, bounded_context_refs, owner_ref, owner_route, lifecycle_state, predecessor_ref, revision_history, challenge_route, evidence_refs, residue_refs, source_direction, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.coordination-context/v2

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-coordination-context/v2"
}
````

**Acceptance record**

Coordination Context successor admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/coordination-context/v2/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/coordination-context/v2/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

6b13f5afed37dbd8d7134c877d6ff484cc9b2ad259fbd8c7b7a5bbc57a8ea7b9

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to this catalog](../artifact-types.md#catalog-types)
