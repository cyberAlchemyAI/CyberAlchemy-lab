[Documentation home](../../README.md)

# Research inquiry · v1

<a id="type-cal-artifact-type-research-inquiry-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Research inquiry · v1

# Research inquiry · v1

This contract specifies requirements for records of kind `research-inquiry`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Research Inquiry](def-cal-definition-research-inquiry.md#def-cal-definition-research-inquiry)

<a id="type-cal-artifact-type-research-inquiry-v1-section-1"></a>

## Prepare a record

- `authority_effect`
- `exclusions`
- `inclusions`
- `kind`
- `method_ref`
- `node_id`
- `owner_ref`
- `project_ref`
- `question`
- `scope_ref`
- `status`
- `stop_conditions`
- `goal_refs`
- `source_policy`
- `source_refs`
- `evidence_aggregate_refs`
- `counterevidence_refs`
- `finding_refs`
- `limitations`
- `created_at`
- `last_updated_at`
- `owner_route`
- `challenge_route`
- `claim_ceiling`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**Declared endpoint kinds for this exact carrier:** [research-inquiry](endpoint-research-inquiry.md#endpoint-research-inquiry)

### Required fields and schema rules

**Fields required at the selected level:** authority_effect, exclusions, inclusions, kind, method_ref, node_id, owner_ref, project_ref, question, scope_ref, status, stop_conditions, goal_refs, source_policy, source_refs, evidence_aggregate_refs, counterevidence_refs, finding_refs, limitations, created_at, last_updated_at, owner_route, challenge_route, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.research-inquiry/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/kind",
  "value": "research-inquiry"
}
````

**Acceptance record**

Research Inquiry contract admission

**Contract**

[Read the type contract](../../assets/a30eb33d7012-artifact.json)

**Schema**

[Read the schema](../../assets/7d7a951f3307-schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

7d7a951f330785bcdd05d76a629496b2edc1233e4e0c3ded3382811d14750330

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
