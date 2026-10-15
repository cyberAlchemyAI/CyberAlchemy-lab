[Documentation home](../../README.md)

# Method binding · v1

<a id="type-cal-artifact-type-method-binding-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Method binding · v1

# Method binding · v1

This contract specifies requirements for records of kind `method-binding`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Craft Method](def-cav2-d20.md#def-cav2-d20) · [Identity Relation](def-cal-definition-identity-relation.md#def-cal-definition-identity-relation)

<a id="type-cal-artifact-type-method-binding-v1-section-1"></a>

## Prepare a record

- `schema_version`
- `binding_id`
- `version`
- `name`
- `status`
- `authority_effect`
- `semantic_definition_refs`
- `method_ref`
- `subject_ref`
- `subject_kind`
- `application_scope`
- `binding_owner_ref`
- `evidence_refs`
- `challenge_route`
- `claim_ceiling`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**Declared endpoint kinds for this exact carrier:** [method](endpoint-method.md#endpoint-method)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, binding_id, version, name, status, authority_effect, semantic_definition_refs, method_ref, subject_ref, subject_kind, application_scope, binding_owner_ref, evidence_refs, challenge_route, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.method-binding/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-method-binding/v1"
}
````

**Acceptance record**

Identity artifact types admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/method-binding/v1/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/method-binding/v1/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

790565f10324a47ef32c3702695c34cdd367d474501a1f1090c83eae4969d8ac

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
