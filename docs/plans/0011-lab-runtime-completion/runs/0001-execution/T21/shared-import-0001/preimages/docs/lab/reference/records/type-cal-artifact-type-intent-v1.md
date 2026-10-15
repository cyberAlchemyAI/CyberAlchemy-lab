[Documentation home](../../README.md)

# Intent · v1

<a id="type-cal-artifact-type-intent-v1"></a>

[Reference catalog](../artifact-types.md#catalog-types) / Exact record

# Intent · v1

This contract specifies requirements for records of kind `intent`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Intent](def-cal-definition-intent.md#def-cal-definition-intent)

## Prepare a record

- `attributed_to`
- `authority_effect`
- `constraints`
- `direction`
- `kind`
- `motivation`
- `node_id`
- `owner_ref`
- `review_route`
- `scope_ref`
- `status`
- `intent_state`
- `target_pressure`
- `current_output_hypothesis`
- `satisfaction_refs`
- `successor_refs`
- `revision_route`
- `revision_history`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**[Content example from the incident:](../../tutorials/incident-walkthrough.md)** Customers need complete eligible data; this need frames the investigation and possible responses. This describes the subject; a complete record must satisfy the full contract.

**Declared endpoint kinds for this exact carrier:** [intent](endpoint-intent.md#endpoint-intent)

### Required fields and schema rules

**Fields required at the selected level:** attributed_to, authority_effect, constraints, direction, kind, motivation, node_id, owner_ref, review_route, scope_ref, status, intent_state, target_pressure, current_output_hypothesis, satisfaction_refs, successor_refs, revision_route, revision_history

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.intent/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/kind",
  "value": "intent"
}
````

**Acceptance record**

Intent contract admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/intent/v1/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/intent/v1/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

71c19ffb4b45431acb02e6e05cee625acd0c8bc6f4f34ef64a51823f277ddf72

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to this catalog](../artifact-types.md#catalog-types)
