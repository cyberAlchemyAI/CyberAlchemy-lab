[Documentation home](../../README.md)

# Artifact type registry · v2

<a id="type-cal-artifact-type-artifact-type-registry-v2"></a>

[Reference catalog](../artifact-types.md#catalog-types) / Exact record

# Artifact type registry · v2

This contract specifies requirements for records of kind `artifact-type-registry`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Artifact Type Registry](def-cal-definition-artifact-type-registry.md#def-cal-definition-artifact-type-registry) · [Artifact Type Resolution](def-cal-definition-artifact-type-resolution.md#def-cal-definition-artifact-type-resolution) · [Generated Output](def-cal-definition-generated-output.md#def-cal-definition-generated-output)

## Prepare a record

- `schema_version`
- `registry_id`
- `version`
- `status`
- `authority_effect`
- `owner_ref`
- `inventory`
- `descriptors`
- `admitted_contracts`
- `current_by_identity`
- `duplicate_resolutions`
- `candidate_lineage`
- `overlay_sources`
- `resolution_rule`
- `source_direction`
- `claim_ceiling`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**Declared endpoint kinds for this exact carrier:** None in this selected catalog.

### Required fields and schema rules

**Fields required at the selected level:** schema_version, registry_id, version, status, authority_effect, owner_ref, inventory, descriptors, admitted_contracts, current_by_identity, duplicate_resolutions, candidate_lineage, overlay_sources, resolution_rule, source_direction, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.artifact-type-registry/v2

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-artifact-type-effective-state-registry/v2"
}
````

**Acceptance record**

Artifact type registry admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/candidates/0006-effective-state-registry/artifact-type-candidate.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/candidates/0006-effective-state-registry/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

5140e341541582fec1711e3645d86c1545872f953ff4d2366e0efb18f7fed707

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to this catalog](../artifact-types.md#catalog-types)
