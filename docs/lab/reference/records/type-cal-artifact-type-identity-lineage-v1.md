[Documentation home](../../README.md)

# Identity lineage · v1

<a id="type-cal-artifact-type-identity-lineage-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Identity lineage · v1

# Identity lineage · v1

This contract specifies requirements for records of kind `identity-lineage`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Identity Lineage](def-cal-definition-identity-lineage.md#def-cal-definition-identity-lineage)

<a id="type-cal-artifact-type-identity-lineage-v1-section-1"></a>

## Prepare a record

- `schema_version`
- `lineage_id`
- `version`
- `name`
- `status`
- `authority_effect`
- `semantic_definition_refs`
- `lineage_kind`
- `subject_kind`
- `predecessor_ref`
- `predecessor_name`
- `successor_ref`
- `successor_name`
- `preserved_identity_assertions`
- `changed_attributes`
- `evidence_refs`
- `lineage_owner_ref`
- `challenge_route`
- `claim_ceiling`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**Declared endpoint kinds for this exact carrier:** None in this selected catalog.

### Required fields and schema rules

**Fields required at the selected level:** schema_version, lineage_id, version, name, status, authority_effect, semantic_definition_refs, lineage_kind, subject_kind, predecessor_ref, predecessor_name, successor_ref, successor_name, preserved_identity_assertions, changed_attributes, evidence_refs, lineage_owner_ref, challenge_route, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.identity-lineage/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-identity-lineage/v1"
}
````

**Acceptance record**

Identity artifact types admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/identity-lineage/v1/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/identity-lineage/v1/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

21ff54dbb21be075d4adba9b0d093b7eb08f685aead92b58180ff0690c497bb6

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
