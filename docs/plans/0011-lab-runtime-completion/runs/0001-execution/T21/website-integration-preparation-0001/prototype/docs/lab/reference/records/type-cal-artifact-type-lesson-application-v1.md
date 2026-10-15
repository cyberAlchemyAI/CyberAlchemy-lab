[Documentation home](../../README.md)

# Lesson application · v1

<a id="type-cal-artifact-type-lesson-application-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Lesson application · v1

# Lesson application · v1

This contract specifies requirements for records of kind `lesson-application`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Lesson Application](def-cal-definition-lesson-application.md#def-cal-definition-lesson-application)

<a id="type-cal-artifact-type-lesson-application-v1-section-1"></a>

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

**[Content example from the incident:](../../tutorials/incident-walkthrough.md)** A later export investigation records the exact lesson it actually uses. This describes the subject; a complete record must satisfy the full contract.

**Declared endpoint kinds for this exact carrier:** [lesson-application](endpoint-lesson-application.md#endpoint-lesson-application)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, node_id, kind, name, lifecycle_state, authority_effect, owner_ref, scope_ref, evidence_refs, challenge_route, successor_refs, relation_refs, payload, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.lesson-application/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-lesson-application/v1"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../assets/b9d052c2e4f1-artifact.json)

**Schema**

[Read the schema](../../assets/c5c7e8fc7ba4-schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

c5c7e8fc7ba4b2a1adda2a2c1800e392a97fce9d2ad956f76e73286ca4da69a7

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
