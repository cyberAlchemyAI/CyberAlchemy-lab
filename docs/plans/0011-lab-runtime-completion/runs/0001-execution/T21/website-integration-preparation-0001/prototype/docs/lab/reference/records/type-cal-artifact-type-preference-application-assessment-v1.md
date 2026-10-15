[Documentation home](../../README.md)

# Preference application assessment · v1

<a id="type-cal-artifact-type-preference-application-assessment-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Preference application assessment · v1

# Preference application assessment · v1

This contract specifies requirements for records of kind `preference-application-assessment`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Preference Application Assessment](def-cal-definition-preference-application-assessment.md#def-cal-definition-preference-application-assessment)

<a id="type-cal-artifact-type-preference-application-assessment-v1-section-1"></a>

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

**Declared endpoint kinds for this exact carrier:** [preference-application-assessment](endpoint-preference-application-assessment.md#endpoint-preference-application-assessment)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, node_id, kind, name, lifecycle_state, authority_effect, owner_ref, scope_ref, evidence_refs, challenge_route, successor_refs, relation_refs, payload, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.preference-application-assessment/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-preference-application-assessment/v1"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../assets/3e3b26e4d3fd-artifact.json)

**Schema**

[Read the schema](../../assets/397c4b7bf1cb-schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

397c4b7bf1cbe5a58d7bcc2c18354a2cbd9e9e3159905beee054a3f0aea20b01

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
