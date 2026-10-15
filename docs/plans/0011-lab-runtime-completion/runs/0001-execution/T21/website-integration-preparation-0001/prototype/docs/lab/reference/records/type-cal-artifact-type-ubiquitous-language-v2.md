[Documentation home](../../README.md)

# Ubiquitous language · v2

<a id="type-cal-artifact-type-ubiquitous-language-v2"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Ubiquitous language · v2

# Ubiquitous language · v2

This contract specifies requirements for records of kind `ubiquitous-language`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Ubiquitous Language](def-cal-definition-ubiquitous-language.md#def-cal-definition-ubiquitous-language)

<a id="type-cal-artifact-type-ubiquitous-language-v2-section-1"></a>

## Prepare a record

No required fields are declared directly at the selected schema level.

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**Declared endpoint kinds for this exact carrier:** [ubiquitous-language](endpoint-ubiquitous-language.md#endpoint-ubiquitous-language)

### Required fields and schema rules

**Fields required at the selected level:** No required fields are declared directly at this level. Other schema sections or referenced rules may still require them.

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.ubiquitous-language/v2

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-ubiquitous-language/v2"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../assets/d52fdc3dcc39-artifact.json)

**Schema**

[Read the schema](../../assets/5d8ca6b41a63-schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

5d8ca6b41a63d0d120f60d23e1e5c1e01cea50529f52af603cd8a55e6e2c8c93

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
