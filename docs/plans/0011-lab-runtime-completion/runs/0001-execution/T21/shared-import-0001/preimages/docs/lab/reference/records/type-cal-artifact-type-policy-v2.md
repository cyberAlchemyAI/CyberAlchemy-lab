[Documentation home](../../README.md)

# Policy · v2

<a id="type-cal-artifact-type-policy-v2"></a>

[Reference catalog](../artifact-types.md#catalog-types) / Exact record

# Policy · v2

This contract specifies requirements for records of kind `policy`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Policy](def-cal-definition-policy.md#def-cal-definition-policy)

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

**Declared endpoint kinds for this exact carrier:** [policy](endpoint-policy.md#endpoint-policy)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, node_id, kind, name, lifecycle_state, authority_effect, owner_ref, scope_ref, evidence_refs, challenge_route, successor_refs, relation_refs, payload, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.policy/v2

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-policy/v2"
}
````

**Acceptance record**

Governance record types admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/candidates/0013-governance-transaction-surface/impacted-carrier-successors/policy/v2/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/candidates/0013-governance-transaction-surface/impacted-carrier-successors/policy/v2/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

acebd41016dcbe7a68fde3603fa3f41e4dd891be6186e4194f8faa53e9ca9fb4

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to this catalog](../artifact-types.md#catalog-types)
