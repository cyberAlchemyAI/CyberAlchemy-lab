[Documentation home](../../README.md)

# Artifact type · v3

<a id="type-cal-artifact-type-artifact-type-v3"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Artifact type · v3

# Artifact type · v3

This contract specifies requirements for records of kind `artifact-type`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Artifact Type](def-cal-definition-artifact-type.md#def-cal-definition-artifact-type)

<a id="type-cal-artifact-type-artifact-type-v3-section-1"></a>

## Prepare a record

- `schema_version`
- `artifact_type_id`
- `artifact_type_ref`
- `version`
- `name`
- `status`
- `authority_effect`
- `classification`
- `semantic_owner_ref`
- `semantic_definition_refs`
- `semantic_definition_bindings`
- `schema_ref`
- `schema_digest`
- `predecessor_contract`
- `instance_contract`
- `distinct_validation_purpose`
- `allowed_relation_kinds`
- `relation_roles`
- `orthogonality_rules`
- `registration_policy`
- `self_application`
- `registered_types`
- `source_direction`
- `four_facets`
- `validation_contract`
- `typed_residue`
- `claim_ceiling`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**[Content example from the incident:](../../tutorials/incident-walkthrough.md)** The Work contract specifies how investigation records identify their kind and carry the required information. This describes the subject; a complete record must satisfy the full contract.

**Declared endpoint kinds for this exact carrier:** None in this selected catalog.

### Required fields and schema rules

**Fields required at the selected level:** schema_version, artifact_type_id, artifact_type_ref, version, name, status, authority_effect, classification, semantic_owner_ref, semantic_definition_refs, semantic_definition_bindings, schema_ref, schema_digest, predecessor_contract, instance_contract, distinct_validation_purpose, allowed_relation_kinds, relation_roles, orthogonality_rules, registration_policy, self_application, registered_types, source_direction, four_facets, validation_contract, typed_residue, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.artifact-type/v3

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-artifact-type/v3"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/artifact-type/v3/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/artifact-type/v3/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

ca24f3f56ed63cd08ae03843694a4d0a34cd0be7ad37a6c8a4f01e9256f6c938

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
