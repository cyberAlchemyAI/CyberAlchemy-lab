[Documentation home](../../README.md)

# Failure assessment · v1

<a id="type-cal-artifact-type-failure-assessment-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Failure assessment · v1

# Failure assessment · v1

This contract specifies requirements for records of kind `failure-assessment`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Failure Assessment](def-cal-definition-failure-assessment.md#def-cal-definition-failure-assessment)

<a id="type-cal-artifact-type-failure-assessment-v1-section-1"></a>

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

**[Content example from the incident:](../../tutorials/incident-walkthrough.md)** Establish omission in E12 while leaving cause, wider impact and recovery unresolved. This describes the subject; a complete record must satisfy the full contract.

[Inspect a complete specimen and a one-field failure →](../record-examples.md#example-failure-assessment)

**Declared endpoint kinds for this exact carrier:** [failure-assessment](endpoint-failure-assessment.md#endpoint-failure-assessment)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, node_id, kind, name, lifecycle_state, authority_effect, owner_ref, scope_ref, evidence_refs, challenge_route, successor_refs, relation_refs, payload, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.failure-assessment/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-failure-assessment/v1"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/failure-assessment/v1/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/failure-assessment/v1/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

379afebf48710eae88bfa9c43c9eee63ce0db80a6416de45ad1016f11ee4f521

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
