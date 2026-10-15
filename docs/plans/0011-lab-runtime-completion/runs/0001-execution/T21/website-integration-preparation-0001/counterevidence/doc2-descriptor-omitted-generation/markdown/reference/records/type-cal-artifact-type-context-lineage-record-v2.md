[Documentation home](../../README.md)

# Context lineage record · v2

<a id="type-cal-artifact-type-context-lineage-record-v2"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Context lineage record · v2

# Context lineage record · v2

This contract specifies requirements for records of kind `context-lineage-record`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Context Lineage Record](def-cal-definition-context-lineage-record.md#def-cal-definition-context-lineage-record)

<a id="type-cal-artifact-type-context-lineage-record-v2-section-1"></a>

## Prepare a record

No required fields are declared directly at the selected schema level.

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**Declared endpoint kinds for this exact carrier:** [context-lineage-record](endpoint-context-lineage-record.md#endpoint-context-lineage-record)

### Required fields and schema rules

**Fields required at the selected level:** No required fields are declared directly at this level. Other schema sections or referenced rules may still require them.

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.context-lineage-record/v2

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-context-lineage-record/v2"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../assets/ee0ce42f54d2-artifact.json)

**Schema**

[Read the schema](../../assets/d0d3eabd7bea-schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

d0d3eabd7beadfc5b0a70cb2409cb172d0d4b4e1a442393bee76c786cdbae637

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
