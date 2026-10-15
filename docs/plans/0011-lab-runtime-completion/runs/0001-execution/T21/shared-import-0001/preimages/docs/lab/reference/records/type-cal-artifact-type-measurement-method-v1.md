[Documentation home](../../README.md)

# Measurement method · v1

<a id="type-cal-artifact-type-measurement-method-v1"></a>

[Reference catalog](../artifact-types.md#catalog-types) / Exact record

# Measurement method · v1

This contract specifies requirements for records of kind `measurement-method`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Measurement Method](def-cal-definition-measurement-method.md#def-cal-definition-measurement-method)

## Prepare a record

- `authority_effect`
- `kind`
- `node_id`
- `owner_ref`
- `scope_ref`
- `status`
- `name`
- `property`
- `entropy_register`
- `source_operation_ref`
- `residue_type_ref`
- `observable_kind`
- `mathematical_reading`
- `scope_kind`
- `procedure`
- `conditions`
- `unit`
- `uncertainty_rule`
- `claim_status`
- `authority_treatment`
- `interpretation`
- `owner_route`
- `challenge_route`
- `claim_ceiling`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

[Inspect a complete specimen and a one-field failure →](../record-examples.md#example-measurement-method)

**Declared endpoint kinds for this exact carrier:** [measurement-method](endpoint-measurement-method.md#endpoint-measurement-method)

### Required fields and schema rules

**Fields required at the selected level:** authority_effect, kind, node_id, owner_ref, scope_ref, status, name, property, entropy_register, source_operation_ref, residue_type_ref, observable_kind, mathematical_reading, scope_kind, procedure, conditions, unit, uncertainty_rule, claim_status, authority_treatment, interpretation, owner_route, challenge_route, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.measurement-method/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/kind",
  "value": "measurement-method"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/measurement-method/v1/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/measurement-method/v1/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

c7182a5ad0e48bfd417159a7e59eddadfc9ce9203af4976a6bf0765e932c76f0

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to this catalog](../artifact-types.md#catalog-types)
