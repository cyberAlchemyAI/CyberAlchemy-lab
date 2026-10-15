[Documentation home](../../README.md)

# Experiment design · v1

<a id="type-cal-artifact-type-experiment-design-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Experiment design · v1

# Experiment design · v1

This contract specifies requirements for records of kind `experiment-design`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Experiment Design](def-cal-definition-experiment-design.md#def-cal-definition-experiment-design)

<a id="type-cal-artifact-type-experiment-design-v1-section-1"></a>

## Prepare a record

- `authority_effect`
- `kind`
- `node_id`
- `owner_ref`
- `scope_ref`
- `status`
- `project_ref`
- `goal_refs`
- `research_refs`
- `product_evaluation_context`
- `question_or_hypothesis`
- `subject_ref`
- `protocol_ref`
- `conditions`
- `variables_or_interventions`
- `measure_refs`
- `environment`
- `prerequisites`
- `stop_rules`
- `run_refs`
- `evidence_refs`
- `finding_refs`
- `limitations`
- `design_state`
- `created_at`
- `last_updated_at`
- `owner_route`
- `challenge_route`
- `claim_ceiling`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**Declared endpoint kinds for this exact carrier:** [experiment-design](endpoint-experiment-design.md#endpoint-experiment-design)

### Required fields and schema rules

**Fields required at the selected level:** authority_effect, kind, node_id, owner_ref, scope_ref, status, project_ref, goal_refs, research_refs, product_evaluation_context, question_or_hypothesis, subject_ref, protocol_ref, conditions, variables_or_interventions, measure_refs, environment, prerequisites, stop_rules, run_refs, evidence_refs, finding_refs, limitations, design_state, created_at, last_updated_at, owner_route, challenge_route, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.experiment-design/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/kind",
  "value": "experiment-design"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../assets/abc7e7d4e0e7-artifact.json)

**Schema**

[Read the schema](../../assets/b06e1aaf0577-schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

b06e1aaf05777ce8f901c6c856db64f9569c9dcbaa49e225baee18f1b28928b6

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
