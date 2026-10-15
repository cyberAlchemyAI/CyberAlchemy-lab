[Documentation home](../../README.md)

# Admission transaction · v1

<a id="type-cal-artifact-type-admission-transaction-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Admission transaction · v1

# Admission transaction · v1

This contract specifies requirements for records of kind `admission-transaction`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Admission Transaction](def-cal-definition-admission-transaction.md#def-cal-definition-admission-transaction)

<a id="type-cal-artifact-type-admission-transaction-v1-section-1"></a>

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

**Declared endpoint kinds for this exact carrier:** [admission-transaction](endpoint-admission-transaction.md#endpoint-admission-transaction)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, node_id, kind, name, lifecycle_state, authority_effect, owner_ref, scope_ref, evidence_refs, challenge_route, successor_refs, relation_refs, payload, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.admission-transaction/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-admission-transaction/v1"
}
````

**Acceptance record**

Governance record types admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/admission-transaction/v1/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/admission-transaction/v1/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

29388897b29e980e02142497132497b12835b4dbdae3ec5d61fde1398c22215f

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
