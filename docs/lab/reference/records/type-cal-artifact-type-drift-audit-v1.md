[Documentation home](../../README.md)

# Drift audit · v1

<a id="type-cal-artifact-type-drift-audit-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Drift audit · v1

# Drift audit · v1

This contract specifies requirements for records of kind `drift-audit`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:**

<a id="type-cal-artifact-type-drift-audit-v1-section-1"></a>

## Prepare a record

No required fields are declared directly at the selected schema level.

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**Declared endpoint kinds for this exact carrier:** None in this selected catalog.

### Required fields and schema rules

**Fields required at the selected level:** No required fields are declared directly at this level. Other schema sections or referenced rules may still require them.

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.drift-audit/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-definition-drift-audit/v1"
}
````

**Acceptance record**

Foundational model admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/artifact-type/v1/artifact.json)

**Schema**

[Read the schema](../../../../authority/foundation/v1/schema.json) · selected section `#/$defs/driftAudit` (this contract uses that part of a shared schema)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

b09e0dbac01d29e7877b7131cf931334e89a87b9defa24e60a1a0bec59c100f9

[Return to Record formats](../artifact-types.md#catalog-types)
