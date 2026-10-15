[Documentation home](../../README.md)

# Project identity · v1

<a id="type-cal-artifact-type-project-identity-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Project identity · v1

# Project identity · v1

This contract specifies requirements for records of kind `project-identity`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Project](def-cav2-d60.md#def-cav2-d60) · [Identity Carrier](def-cal-definition-identity-carrier.md#def-cal-definition-identity-carrier)

<a id="type-cal-artifact-type-project-identity-v1-section-1"></a>

## Prepare a record

- `schema_version`
- `project_id`
- `version`
- `name`
- `status`
- `authority_effect`
- `semantic_definition_refs`
- `purpose`
- `coordination_scope`
- `accountable_owner_ref`
- `evidence_refs`
- `challenge_route`
- `claim_ceiling`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**[Content example from the incident:](../../tutorials/incident-walkthrough.md)** The export-repair Project coordinates goals, decisions, evidence and work across sessions. This describes the subject; a complete record must satisfy the full contract.

**Declared endpoint kinds for this exact carrier:** [project](endpoint-project.md#endpoint-project)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, project_id, version, name, status, authority_effect, semantic_definition_refs, purpose, coordination_scope, accountable_owner_ref, evidence_refs, challenge_route, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.project-identity/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-project-identity/v1"
}
````

**Acceptance record**

Identity artifact types admission

**Contract**

[Read the type contract](../../assets/0bf6d42ec0ca-artifact.json)

**Schema**

[Read the schema](../../assets/1fbfeba8bfc7-schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

1fbfeba8bfc7157cf666d4c268ddcbd6c031b951acd2734817ef004eeb6145ef

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
