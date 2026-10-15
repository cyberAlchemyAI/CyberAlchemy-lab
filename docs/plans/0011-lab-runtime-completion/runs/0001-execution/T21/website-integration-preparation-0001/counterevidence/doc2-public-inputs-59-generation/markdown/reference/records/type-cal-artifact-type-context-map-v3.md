[Documentation home](../../README.md)

# Context map · v3

<a id="type-cal-artifact-type-context-map-v3"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Context map · v3

# Context map · v3

This contract specifies requirements for records of kind `context-map`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Context Map](def-cal-definition-context-map.md#def-cal-definition-context-map)

<a id="type-cal-artifact-type-context-map-v3-section-1"></a>

## Prepare a record

No required fields are declared directly at the selected schema level.

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**Declared endpoint kinds for this exact carrier:** [context-map](endpoint-context-map.md#endpoint-context-map)

### Required fields and schema rules

**Fields required at the selected level:** No required fields are declared directly at this level. Other schema sections or referenced rules may still require them.

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.context-map/v3

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-context-map/v3"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../assets/0069e71aa6e2-artifact.json)

**Schema**

[Read the schema](../../assets/11e3ff003d7c-schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

11e3ff003d7cf132b6a33fd2f95644bd09e5932a8373989b014e6194ee99fb17

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
