[Documentation home](../../README.md)

# Foundation manifest · v1

<a id="type-cal-artifact-type-foundation-manifest-v1"></a>

[Reference catalog](../artifact-types.md#catalog-types) / Exact record

# Foundation manifest · v1

This contract specifies requirements for records of kind `foundation-manifest`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:**

## Prepare a record

- `schema_version`
- `record_id`
- `artifact_type_ref`
- `status`
- `authority_effect`
- `owner_ref`
- `source_direction`
- `claim_ceiling`
- `principal_id`
- `materials`
- `d65_boundary`
- `admission_posture`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**Declared endpoint kinds for this exact carrier:** None in this selected catalog.

### Required fields and schema rules

**Fields required at the selected level:** schema_version, record_id, artifact_type_ref, status, authority_effect, owner_ref, source_direction, claim_ceiling, principal_id, materials, d65_boundary, admission_posture

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.foundation-manifest/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-foundation-manifest/v1"
}
````

**Acceptance record**

Foundational model admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/artifact-type/v1/artifact.json)

**Schema**

[Read the schema](../../../../authority/foundation/v1/schema.json) · selected section `#/$defs/manifest` (this contract uses that part of a shared schema)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

b09e0dbac01d29e7877b7131cf931334e89a87b9defa24e60a1a0bec59c100f9

[Return to this catalog](../artifact-types.md#catalog-types)
