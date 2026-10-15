[Documentation home](../../README.md)

# Canonical package manifest · v1

<a id="type-cal-artifact-type-canonical-package-manifest-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Canonical package manifest · v1

# Canonical package manifest · v1

This contract specifies requirements for records of kind `canonical-package-manifest`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Artifact Type](def-cal-definition-artifact-type.md#def-cal-definition-artifact-type) · [Canonical Package Home](def-cal-definition-canonical-package-home.md#def-cal-definition-canonical-package-home) · [Canonical Package Manifest](def-cal-definition-canonical-package-manifest.md#def-cal-definition-canonical-package-manifest) · [Artifact Surface Classification](def-cal-definition-artifact-surface-classification.md#def-cal-definition-artifact-surface-classification)

<a id="type-cal-artifact-type-canonical-package-manifest-v1-section-1"></a>

## Prepare a record

- `schema_version`
- `package_id`
- `version`
- `status`
- `authority_effect`
- `aggregate_ref`
- `package_root`
- `lifecycle_owner_ref`
- `unit_of_change`
- `surface_entries`
- `nested_packages`
- `source_direction`
- `claim_ceiling`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**[Content example from the incident:](../../tutorials/incident-walkthrough.md)** The Work contract specifies how investigation records identify their kind and carry the required information. This describes the subject; a complete record must satisfy the full contract.

**Declared endpoint kinds for this exact carrier:** [canonical-package-manifest](endpoint-canonical-package-manifest.md#endpoint-canonical-package-manifest)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, package_id, version, status, authority_effect, aggregate_ref, package_root, lifecycle_owner_ref, unit_of_change, surface_entries, nested_packages, source_direction, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.canonical-package-manifest/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-canonical-package-manifest/v1"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/canonical-package-manifest/v1/candidates/0002-executable-surface/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/canonical-package-manifest/v1/candidates/0002-executable-surface/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

33cf444c265d306d6e6eb75338a4b4cccc609ccf7c736f2f39e2af06d109b930

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
