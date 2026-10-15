[Documentation home](../../README.md)

# Responsibility · v1

<a id="type-cal-artifact-type-responsibility-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Responsibility · v1

# Responsibility · v1

This contract specifies requirements for records of kind `responsibility`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Responsibility](def-cal-definition-responsibility.md#def-cal-definition-responsibility)

<a id="type-cal-artifact-type-responsibility-v1-section-1"></a>

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

**Declared endpoint kinds for this exact carrier:** [responsibility](endpoint-responsibility.md#endpoint-responsibility)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, node_id, kind, name, lifecycle_state, authority_effect, owner_ref, scope_ref, evidence_refs, challenge_route, successor_refs, relation_refs, payload, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.responsibility/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-responsibility/v1"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../assets/3a3b2c0abb03-artifact.json)

**Schema**

[Read the schema](../../assets/46d975988229-schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

46d975988229d2eea2e8f72ab4ebb928a67751020499d14369b6bcc733c7ed72

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
