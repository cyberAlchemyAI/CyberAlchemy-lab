[Documentation home](../../README.md)

# Feedback record · v1

<a id="type-cal-artifact-type-feedback-record-v1"></a>

[Reference catalog](../artifact-types.md#catalog-types) / Exact record

# Feedback record · v1

This contract specifies requirements for records of kind `feedback-record`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Feedback Record](def-cal-definition-feedback-record.md#def-cal-definition-feedback-record)

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

**Declared endpoint kinds for this exact carrier:** [feedback-record](endpoint-feedback-record.md#endpoint-feedback-record)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, node_id, kind, name, lifecycle_state, authority_effect, owner_ref, scope_ref, evidence_refs, challenge_route, successor_refs, relation_refs, payload, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.feedback-record/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-feedback-record/v1"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/feedback-record/v1/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/feedback-record/v1/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

302402898d3122409b5236b7db08fab64475a4f83b36dd7df25e54f618b850a4

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to this catalog](../artifact-types.md#catalog-types)
