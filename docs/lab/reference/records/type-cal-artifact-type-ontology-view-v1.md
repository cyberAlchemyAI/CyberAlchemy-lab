[Documentation home](../../README.md)

# Ontology view · v1

<a id="type-cal-artifact-type-ontology-view-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Ontology view · v1

# Ontology view · v1

This contract specifies requirements for records of kind `ontology-view`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Ontology View](def-cal-definition-ontology-view.md#def-cal-definition-ontology-view)

<a id="type-cal-artifact-type-ontology-view-v1-section-1"></a>

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

**[Content example from the incident:](../../tutorials/incident-walkthrough.md)** Select an exact consistent cut of subjects and connections for the investigation’s purpose and consumer. This describes the subject; a complete record must satisfy the full contract.

**Declared endpoint kinds for this exact carrier:** [ontology-view](endpoint-ontology-view.md#endpoint-ontology-view)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, node_id, kind, name, record_state, authority_effect, owner_ref, scope_ref, evidence_refs, challenge_route, successor_refs, payload, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.ontology-view/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-ontology-view/v1"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/ontology-view/v1/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/ontology-view/v1/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

32c12b7e917e8872b82174d963d4a17e2b2e5ff64d7c798774a72cfcdb497d4b

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
