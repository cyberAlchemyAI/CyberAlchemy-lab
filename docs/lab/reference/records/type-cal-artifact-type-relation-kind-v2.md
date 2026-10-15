[Documentation home](../../README.md)

# Relation kind · v2

<a id="type-cal-artifact-type-relation-kind-v2"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Relation kind · v2

# Relation kind · v2

This contract specifies requirements for records of kind `relation-kind`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Relation Kind](def-cal-definition-relation-kind.md#def-cal-definition-relation-kind)

<a id="type-cal-artifact-type-relation-kind-v2-section-1"></a>

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

**Declared endpoint kinds for this exact carrier:** [relation-kind](endpoint-relation-kind.md#endpoint-relation-kind)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, node_id, kind, name, lifecycle_state, authority_effect, owner_ref, scope_ref, evidence_refs, challenge_route, successor_refs, relation_refs, payload, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.relation-kind/v2

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-relation-kind/v2"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/relation-kind/v2/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/relation-kind/v2/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

e0b6c594b1b95dedaeddef93dd2fdc36c7ecc7a9e4235d63144ba6167023693c

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
