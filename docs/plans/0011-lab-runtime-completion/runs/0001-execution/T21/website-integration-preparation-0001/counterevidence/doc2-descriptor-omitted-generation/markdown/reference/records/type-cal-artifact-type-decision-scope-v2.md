[Documentation home](../../README.md)

# Decision scope · v2

<a id="type-cal-artifact-type-decision-scope-v2"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Decision scope · v2

# Decision scope · v2

This contract specifies requirements for records of kind `decision-scope`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Decision Scope](def-cal-definition-decision-scope.md#def-cal-definition-decision-scope)

<a id="type-cal-artifact-type-decision-scope-v2-section-1"></a>

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

**Declared endpoint kinds for this exact carrier:** [decision-scope](endpoint-decision-scope.md#endpoint-decision-scope)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, node_id, kind, name, lifecycle_state, authority_effect, owner_ref, scope_ref, evidence_refs, challenge_route, successor_refs, relation_refs, payload, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.decision-scope/v2

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-decision-scope/v2"
}
````

**Acceptance record**

Governance record types admission

**Contract**

[Read the type contract](../../assets/9c1100a0f2bc-artifact.json)

**Schema**

[Read the schema](../../assets/d8e6c90cea70-schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

d8e6c90cea70e37c376ab36c92323459c65f7e08f1bd47e40e290a1f5a05e53c

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
