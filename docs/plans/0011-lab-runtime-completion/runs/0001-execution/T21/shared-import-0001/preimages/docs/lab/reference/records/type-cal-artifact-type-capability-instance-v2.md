[Documentation home](../../README.md)

# Capability instance · v2

<a id="type-cal-artifact-type-capability-instance-v2"></a>

[Reference catalog](../artifact-types.md#catalog-types) / Exact record

# Capability instance · v2

This contract specifies requirements for records of kind `capability-instance`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Capability Instance](def-cal-definition-capability-instance.md#def-cal-definition-capability-instance)

## Prepare a record

No required fields are declared directly at the selected schema level.

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**Declared endpoint kinds for this exact carrier:** [capability-instance](endpoint-capability-instance.md#endpoint-capability-instance)

### Required fields and schema rules

**Fields required at the selected level:** No required fields are declared directly at this level. Other schema sections or referenced rules may still require them.

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.capability-instance/v2

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-capability-instance/v2"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/capability-instance/v2/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/capability-instance/v2/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

af2c05dd637f6a32427020a4c54d85c8324f87302f98a67edf803918ff74ee01

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to this catalog](../artifact-types.md#catalog-types)
