[Documentation home](../../README.md)

# Experiment run · v1

<a id="type-cal-artifact-type-experiment-run-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Experiment run · v1

# Experiment run · v1

This contract specifies requirements for records of kind `experiment-run`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Experiment Run](def-cal-definition-experiment-run.md#def-cal-definition-experiment-run)

<a id="type-cal-artifact-type-experiment-run-v1-section-1"></a>

## Prepare a record

- `authority_effect`
- `kind`
- `node_id`
- `owner_ref`
- `scope_ref`
- `status`
- `design_ref`
- `design_version_ref`
- `project_ref`
- `goal_refs`
- `research_refs`
- `product_evaluation_context`
- `environment`
- `input_refs`
- `interventions`
- `deviations`
- `observation_refs`
- `measurement_result_refs`
- `evidence_set_ref`
- `run_state`
- `stop_reason`
- `period`
- `owner_route`
- `challenge_route`
- `claim_ceiling`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**Declared endpoint kinds for this exact carrier:** [experiment-run](endpoint-experiment-run.md#endpoint-experiment-run)

### Required fields and schema rules

**Fields required at the selected level:** authority_effect, kind, node_id, owner_ref, scope_ref, status, design_ref, design_version_ref, project_ref, goal_refs, research_refs, product_evaluation_context, environment, input_refs, interventions, deviations, observation_refs, measurement_result_refs, evidence_set_ref, run_state, stop_reason, period, owner_route, challenge_route, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.experiment-run/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/kind",
  "value": "experiment-run"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/experiment-run/v1/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/experiment-run/v1/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

9dc27a20b2fe10070fb6f73d8d1a320a68946c5b88b72b354d9117153da9e4f9

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
