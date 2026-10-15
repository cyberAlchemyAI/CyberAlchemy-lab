[Documentation home](../../README.md)

# Identity graph · v1

<a id="type-cal-artifact-type-identity-graph-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Identity graph · v1

# Identity graph · v1

This contract specifies requirements for records of kind `identity-graph`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Identity Relation](def-cal-definition-identity-relation.md#def-cal-definition-identity-relation)

<a id="type-cal-artifact-type-identity-graph-v1-section-1"></a>

## Prepare a record

- `schema_version`
- `graph_id`
- `version`
- `name`
- `status`
- `authority_effect`
- `semantic_definition_refs`
- `nodes`
- `relations`
- `graph_owner_ref`
- `evidence_refs`
- `challenge_route`
- `claim_ceiling`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**Declared endpoint kinds for this exact carrier:** None in this selected catalog.

### Required fields and schema rules

**Fields required at the selected level:** schema_version, graph_id, version, name, status, authority_effect, semantic_definition_refs, nodes, relations, graph_owner_ref, evidence_refs, challenge_route, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.identity-graph/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-identity-graph/v1"
}
````

**Acceptance record**

Identity artifact types admission

**Contract**

[Read the type contract](../../assets/9c8c4ea4ddf8-artifact.json)

**Schema**

[Read the schema](../../assets/33863efed380-schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

33863efed380ffe586439de4a36b79c44b4b2eac065da5a3de6a68b0bb430190

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
