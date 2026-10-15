[Documentation home](../../README.md)

# Finding · v1

<a id="type-cal-artifact-type-finding-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Finding · v1

# Finding · v1

This contract specifies requirements for records of kind `finding`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Finding](def-cal-definition-finding.md#def-cal-definition-finding)

<a id="type-cal-artifact-type-finding-v1-section-1"></a>

## Prepare a record

- `authority_effect`
- `counterevidence_refs`
- `kind`
- `limitations`
- `node_id`
- `owner_ref`
- `scope_ref`
- `statement`
- `status`
- `inquiry_ref`
- `question`
- `research_run_refs`
- `evidence_set_refs`
- `evidence_refs`
- `support_assessment`
- `finding_state`
- `created_at`
- `last_updated_at`
- `owner_route`
- `challenge_route`
- `successor_refs`
- `revision_history`
- `claim_ceiling`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**Declared endpoint kinds for this exact carrier:** [finding](endpoint-finding.md#endpoint-finding)

### Required fields and schema rules

**Fields required at the selected level:** authority_effect, counterevidence_refs, kind, limitations, node_id, owner_ref, scope_ref, statement, status, inquiry_ref, question, research_run_refs, evidence_set_refs, evidence_refs, support_assessment, finding_state, created_at, last_updated_at, owner_route, challenge_route, successor_refs, revision_history, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.finding/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/kind",
  "value": "finding"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/finding/v1/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/finding/v1/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

b0e2d44bee4819881a8e38369dc89646e967297028cd6b28959b9e43ab01d023

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
