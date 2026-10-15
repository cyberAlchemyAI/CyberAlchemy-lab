[Documentation home](../../README.md)

# Workflow decision profile · v1

<a id="type-cal-artifact-type-workflow-decision-profile-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Workflow decision profile · v1

# Workflow decision profile · v1

This contract specifies requirements for records of kind `workflow-decision-profile`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Workflow Decision Profile · Lab workflow](def-cal-definition-workflow-decision-profile.md#def-cal-definition-workflow-decision-profile)

<a id="type-cal-artifact-type-workflow-decision-profile-v1-section-1"></a>

## Prepare a record

- `schema_version`
- `node_id`
- `kind`
- `name`
- `lifecycle_state`
- `authority_effect`
- `owner_ref`
- `scope_ref`
- `evidence_refs`
- `challenge_route`
- `successor_refs`
- `relation_refs`
- `payload`
- `claim_ceiling`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**Declared endpoint kinds for this exact carrier:** [workflow-decision-profile](endpoint-workflow-decision-profile.md#endpoint-workflow-decision-profile)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, node_id, kind, name, lifecycle_state, authority_effect, owner_ref, scope_ref, evidence_refs, challenge_route, successor_refs, relation_refs, payload, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.workflow-decision-profile/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-workflow-decision-profile/v1"
}
````

**Acceptance record**

Governance record types admission

**Contract**

[Read the type contract](../../assets/566ea9062d39-artifact.json)

**Schema**

[Read the schema](../../assets/91f9f0bd51c5-schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

91f9f0bd51c5d65c8aacce4e6abe4c92d7a6338bcd01569a67f4368f8bd74471

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
