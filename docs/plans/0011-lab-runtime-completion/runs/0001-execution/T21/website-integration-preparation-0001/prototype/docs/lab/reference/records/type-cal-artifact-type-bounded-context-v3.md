[Documentation home](../../README.md)

# Bounded context · v3

<a id="type-cal-artifact-type-bounded-context-v3"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Bounded context · v3

# Bounded context · v3

This contract specifies requirements for records of kind `bounded-context`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Bounded Context](def-cal-definition-bounded-context.md#def-cal-definition-bounded-context)

<a id="type-cal-artifact-type-bounded-context-v3-section-1"></a>

## Prepare a record

No required fields are declared directly at the selected schema level.

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**Declared endpoint kinds for this exact carrier:** [bounded-context](endpoint-bounded-context.md#endpoint-bounded-context)

### Required fields and schema rules

**Fields required at the selected level:** No required fields are declared directly at this level. Other schema sections or referenced rules may still require them.

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.bounded-context/v3

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-bounded-context/v3"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../assets/3bea2dc969e6-artifact.json)

**Schema**

[Read the schema](../../assets/fa9944d659ac-schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

fa9944d659ac26d0587f9c8e97102bc81d736df685681b945aad401c2851c9c4

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
