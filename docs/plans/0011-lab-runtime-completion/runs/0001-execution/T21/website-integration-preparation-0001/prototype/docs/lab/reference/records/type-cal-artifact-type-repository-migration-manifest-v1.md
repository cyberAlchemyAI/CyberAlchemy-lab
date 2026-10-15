[Documentation home](../../README.md)

# Artifact type · v1

<a id="type-cal-artifact-type-repository-migration-manifest-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Artifact type · v1

# Artifact type · v1

This contract specifies requirements for records of kind `artifact-type`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Artifact Type](def-cal-definition-artifact-type.md#def-cal-definition-artifact-type) · [Repository Migration Manifest](def-cal-definition-repository-migration-manifest.md#def-cal-definition-repository-migration-manifest) · [Validation](def-cal-definition-validation.md#def-cal-definition-validation)

<a id="type-cal-artifact-type-repository-migration-manifest-v1-section-1"></a>

## Prepare a record

- `schema_version`
- `migration_manifest_id`
- `version`
- `status`
- `authority_effect`
- `source_repository`
- `target_repository`
- `architecture`
- `mapping_rules`
- `exclusion_inventory`
- `copy_allowlist`
- `expected_postimage`
- `rollback_ref`
- `copy_semantics`
- `execution_authority`
- `validation_obligations`
- `semantic_definition_refs`
- `source_direction`
- `claim_ceiling`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**[Content example from the incident:](../../tutorials/incident-walkthrough.md)** The Work contract specifies how investigation records identify their kind and carry the required information. This describes the subject; a complete record must satisfy the full contract.

**Declared endpoint kinds for this exact carrier:** [artifact-type](endpoint-artifact-type.md#endpoint-artifact-type)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, migration_manifest_id, version, status, authority_effect, source_repository, target_repository, architecture, mapping_rules, exclusion_inventory, copy_allowlist, expected_postimage, rollback_ref, copy_semantics, execution_authority, validation_obligations, semantic_definition_refs, source_direction, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.repository-migration-manifest/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-repository-migration-manifest/v1"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../assets/7be737ec03d5-artifact.json)

**Schema**

[Read the schema](../../assets/ccfbeea982c4-schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

ccfbeea982c405c09e454eb2bdec5081df6dbdeeeaccf6553148046481b5d084

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
