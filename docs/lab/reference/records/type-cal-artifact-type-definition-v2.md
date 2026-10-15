[Documentation home](../../README.md)

# Definition · v2

<a id="type-cal-artifact-type-definition-v2"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Definition · v2

# Definition · v2

This contract specifies requirements for records of kind `definition`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Definition](def-cal-definition-definition.md#def-cal-definition-definition)

<a id="type-cal-artifact-type-definition-v2-section-1"></a>

## Prepare a record

- `schema_version`
- `definition_id`
- `version`
- `term`
- `aliases`
- `classification`
- `semantic_owner_ref`
- `scope`
- `voices`
- `boundaries`
- `source_refs`
- `primary_consumer_refs`
- `index_entry`
- `drift_route`
- `source_direction`
- `schema_ref`
- `schema_digest`
- `evidence_refs`
- `residue_refs`
- `typed_relations`
- `claim_ceiling`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**[Content example from the incident:](../../tutorials/incident-walkthrough.md)** The owner-accepted completeness criterion governs identifier coverage for Northstar, the declared filters and S1. This describes the subject; a complete record must satisfy the full contract.

[Inspect a complete specimen and a one-field failure →](../record-examples.md#example-definition)

**Declared endpoint kinds for this exact carrier:** [definition](endpoint-definition.md#endpoint-definition)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, definition_id, version, term, aliases, classification, semantic_owner_ref, scope, voices, boundaries, source_refs, primary_consumer_refs, index_entry, drift_route, source_direction, schema_ref, schema_digest, evidence_refs, residue_refs, typed_relations, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.definition/v2

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-definition/v2"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/definition/v2/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/definition/v2/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

269591e7f0dd7c1c077579dd874599ba08fa8e17df10fa262d936f8ad5519181

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
