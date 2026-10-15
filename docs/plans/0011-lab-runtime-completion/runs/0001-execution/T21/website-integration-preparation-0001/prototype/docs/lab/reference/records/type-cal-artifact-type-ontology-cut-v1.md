[Documentation home](../../README.md)

# Ontology cut · v1

<a id="type-cal-artifact-type-ontology-cut-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Ontology cut · v1

# Ontology cut · v1

This contract specifies requirements for records of kind `ontology-cut`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Ontology Cut](def-cal-definition-ontology-cut.md#def-cal-definition-ontology-cut)

<a id="type-cal-artifact-type-ontology-cut-v1-section-1"></a>

## Prepare a record

- `schema_version`
- `node_id`
- `kind`
- `name`
- `record_state`
- `authority_effect`
- `owner_ref`
- `scope_ref`
- `evidence_refs`
- `challenge_route`
- `successor_refs`
- `payload`
- `claim_ceiling`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**Declared endpoint kinds for this exact carrier:** [ontology-cut](endpoint-ontology-cut.md#endpoint-ontology-cut)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, node_id, kind, name, record_state, authority_effect, owner_ref, scope_ref, evidence_refs, challenge_route, successor_refs, payload, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.ontology-cut/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-ontology-cut/v1"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../assets/8660dcb0173e-artifact.json)

**Schema**

[Read the schema](../../assets/ae5f8e23cb0d-schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

ae5f8e23cb0d5b34b1e55d6816a03ee4618b884c51262d86c46af4260c025471

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
