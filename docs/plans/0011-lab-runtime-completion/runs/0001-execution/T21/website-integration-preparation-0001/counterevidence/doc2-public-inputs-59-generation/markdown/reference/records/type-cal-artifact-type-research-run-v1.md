[Documentation home](../../README.md)

# Research run · v1

<a id="type-cal-artifact-type-research-run-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Research run · v1

# Research run · v1

This contract specifies requirements for records of kind `research-run`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Research Run](def-cal-definition-research-run.md#def-cal-definition-research-run)

<a id="type-cal-artifact-type-research-run-v1-section-1"></a>

## Prepare a record

- `authority_effect`
- `inquiry_ref`
- `kind`
- `limitations`
- `node_id`
- `owner_ref`
- `period`
- `receipt_ref`
- `scope_ref`
- `status`
- `inquiry_version_ref`
- `project_ref`
- `goal_refs`
- `inspected_sources`
- `method_performed`
- `observation_refs`
- `counterevidence_refs`
- `evidence_set_ref`
- `run_state`
- `stop_reason`
- `owner_route`
- `challenge_route`
- `claim_ceiling`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**Declared endpoint kinds for this exact carrier:** [research-run](endpoint-research-run.md#endpoint-research-run)

### Required fields and schema rules

**Fields required at the selected level:** authority_effect, inquiry_ref, kind, limitations, node_id, owner_ref, period, receipt_ref, scope_ref, status, inquiry_version_ref, project_ref, goal_refs, inspected_sources, method_performed, observation_refs, counterevidence_refs, evidence_set_ref, run_state, stop_reason, owner_route, challenge_route, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.research-run/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/kind",
  "value": "research-run"
}
````

**Acceptance record**

Research Run contract admission

**Contract**

[Read the type contract](../../assets/7b1d40256113-artifact.json)

**Schema**

[Read the schema](../../assets/6c4e0abd972d-schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

6c4e0abd972db936fd55649561b7c5fa681fdf7c053973bd904f32078a262ed5

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
