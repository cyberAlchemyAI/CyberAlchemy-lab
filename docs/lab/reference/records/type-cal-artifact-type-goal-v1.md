[Documentation home](../../README.md)

# Goal · v1

<a id="type-cal-artifact-type-goal-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Goal · v1

# Goal · v1

This contract specifies requirements for records of kind `goal`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Goal](def-cav2-d59.md#def-cav2-d59) · [Identity Carrier](def-cal-definition-identity-carrier.md#def-cal-definition-identity-carrier)

<a id="type-cal-artifact-type-goal-v1-section-1"></a>

## Prepare a record

- `schema_version`
- `goal_id`
- `version`
- `name`
- `status`
- `authority_effect`
- `semantic_definition_refs`
- `outcome`
- `rationale`
- `success_conditions`
- `evidence_requirements`
- `accountable_owner_ref`
- `challenge_route`
- `claim_ceiling`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**[Content example from the incident:](../../tutorials/incident-walkthrough.md)** Declare the scoped repair outcome, criteria, required evidence and responsible owner. This describes the subject; a complete record must satisfy the full contract.

**Declared endpoint kinds for this exact carrier:** [goal](endpoint-goal.md#endpoint-goal)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, goal_id, version, name, status, authority_effect, semantic_definition_refs, outcome, rationale, success_conditions, evidence_requirements, accountable_owner_ref, challenge_route, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.goal/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-goal/v1"
}
````

**Acceptance record**

Identity artifact types admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/goal/v1/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/goal/v1/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

9c81c21cdebd0584aac4ec41424008a1882bc78271c3c540938ff9a65ef3aeb3

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
