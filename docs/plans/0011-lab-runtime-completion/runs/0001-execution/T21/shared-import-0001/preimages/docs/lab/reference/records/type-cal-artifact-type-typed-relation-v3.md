[Documentation home](../../README.md)

# Typed relation · v3

<a id="type-cal-artifact-type-typed-relation-v3"></a>

[Reference catalog](../artifact-types.md#catalog-types) / Exact record

# Typed relation · v3

This contract specifies requirements for records of kind `typed-relation`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Typed Relation](def-cal-definition-typed-relation.md#def-cal-definition-typed-relation)

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

**[Content example from the incident:](../../tutorials/incident-walkthrough.md)** A source-bound observation can originate from a Source under a declared ordered pair and qualifier contract. This describes the subject; a complete record must satisfy the full contract.

**Declared endpoint kinds for this exact carrier:** [typed-relation](endpoint-typed-relation.md#endpoint-typed-relation)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, node_id, kind, name, lifecycle_state, authority_effect, owner_ref, scope_ref, evidence_refs, challenge_route, successor_refs, relation_refs, payload, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.typed-relation/v3

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-typed-relation/v3"
}
````

**Acceptance record**

Governance record types admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/candidates/0013-governance-transaction-surface/impacted-carrier-successors/typed-relation/v3/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/candidates/0013-governance-transaction-surface/impacted-carrier-successors/typed-relation/v3/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

7d5fb3dafdf7411c6186d35bd92cfa1c10bfa1c8580b22f880245ec7c601f28b

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to this catalog](../artifact-types.md#catalog-types)
