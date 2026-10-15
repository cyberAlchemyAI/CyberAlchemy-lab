[Documentation home](../../README.md)

# Failure control binding · v1

<a id="type-cal-artifact-type-failure-control-binding-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Failure control binding · v1

# Failure control binding · v1

This contract specifies requirements for records of kind `failure-control-binding`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Failure Control Binding](def-cal-definition-failure-control-binding.md#def-cal-definition-failure-control-binding)

<a id="type-cal-artifact-type-failure-control-binding-v1-section-1"></a>

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

**Declared endpoint kinds for this exact carrier:** [failure-control-binding](endpoint-failure-control-binding.md#endpoint-failure-control-binding)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, node_id, kind, name, lifecycle_state, authority_effect, owner_ref, scope_ref, evidence_refs, challenge_route, successor_refs, relation_refs, payload, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.failure-control-binding/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-failure-control-binding/v1"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../assets/8a067c445702-artifact.json)

**Schema**

[Read the schema](../../assets/6f639e945252-schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

6f639e94525244173934cc9376259572e4a4320c81709016f447fad66e98f5b8

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
