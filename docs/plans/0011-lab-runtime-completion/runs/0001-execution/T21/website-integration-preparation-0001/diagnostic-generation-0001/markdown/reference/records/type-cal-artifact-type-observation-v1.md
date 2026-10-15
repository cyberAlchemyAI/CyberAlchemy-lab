[Documentation home](../../README.md)

# Observation · v1

<a id="type-cal-artifact-type-observation-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Observation · v1

# Observation · v1

This contract specifies requirements for records of kind `observation`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Observation](def-cal-definition-observation.md#def-cal-definition-observation)

<a id="type-cal-artifact-type-observation-v1-section-1"></a>

## Prepare a record

- `authority_effect`
- `kind`
- `node_id`
- `owner_ref`
- `scope_ref`
- `status`
- `run_ref`
- `subject_ref`
- `statement`
- `method_ref`
- `conditions`
- `observed_at`
- `observer_ref`
- `provenance_refs`
- `uncertainty`
- `evidence_ref`
- `limitations`
- `owner_route`
- `challenge_route`
- `claim_ceiling`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**Declared endpoint kinds for this exact carrier:** [observation](endpoint-observation.md#endpoint-observation)

### Required fields and schema rules

**Fields required at the selected level:** authority_effect, kind, node_id, owner_ref, scope_ref, status, run_ref, subject_ref, statement, method_ref, conditions, observed_at, observer_ref, provenance_refs, uncertainty, evidence_ref, limitations, owner_route, challenge_route, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.observation/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/kind",
  "value": "observation"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../assets/9c52f8b4395f-artifact.json)

**Schema**

[Read the schema](../../assets/8b12ad86681b-schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

8b12ad86681b9fcc51d539a070f491db7cecbe694457cb64637d2bde26a9d1b3

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
