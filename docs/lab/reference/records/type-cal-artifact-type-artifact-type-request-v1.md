[Documentation home](../../README.md)

# Artifact type request · v1

<a id="type-cal-artifact-type-artifact-type-request-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Artifact type request · v1

# Artifact type request · v1

This contract specifies requirements for records of kind `artifact-type-request`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Artifact Type](def-cal-definition-artifact-type.md#def-cal-definition-artifact-type) · [Artifact Type Request](def-cal-definition-artifact-type-request.md#def-cal-definition-artifact-type-request) · [Artifact Type Resolution](def-cal-definition-artifact-type-resolution.md#def-cal-definition-artifact-type-resolution)

<a id="type-cal-artifact-type-artifact-type-request-v1-section-1"></a>

## Prepare a record

- `schema_version`
- `request_id`
- `version`
- `status`
- `authority_effect`
- `owner_ref`
- `proposed_semantic_kind`
- `proposed_package_home_ref`
- `resolution_evidence`
- `compatibility_analysis`
- `semantic_definition_refs`
- `representation_proposal`
- `validation_purpose`
- `consumed_as_subject`
- `expiry`
- `source_direction`
- `claim_ceiling`
- `proposed_discriminator`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**[Content example from the incident:](../../tutorials/incident-walkthrough.md)** The Work contract specifies how investigation records identify their kind and carry the required information. This describes the subject; a complete record must satisfy the full contract.

**Declared endpoint kinds for this exact carrier:** [artifact-type-request](endpoint-artifact-type-request.md#endpoint-artifact-type-request)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, request_id, version, status, authority_effect, owner_ref, proposed_semantic_kind, proposed_package_home_ref, resolution_evidence, compatibility_analysis, semantic_definition_refs, representation_proposal, validation_purpose, consumed_as_subject, expiry, source_direction, claim_ceiling, proposed_discriminator

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.artifact-type-request/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-artifact-type-request/v1"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/artifact-type-request/v1/candidates/0002-executable-surface/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/artifact-type-request/v1/candidates/0002-executable-surface/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

e119550e3cc3fce1b87966b20f9c1216976f956e9c750a23dd556727067a95f5

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
