[Documentation home](../../README.md)

# Evidence set · v1

<a id="type-cal-artifact-type-evidence-set-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Evidence set · v1

# Evidence set · v1

This contract specifies requirements for records of kind `evidence-set`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Evidence Set](def-cal-definition-evidence-set.md#def-cal-definition-evidence-set)

<a id="type-cal-artifact-type-evidence-set-v1-section-1"></a>

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

**[Content example from the incident:](../../tutorials/incident-walkthrough.md)** Group the selected inputs, method and result that bear on the omission assessment. This describes the subject; a complete record must satisfy the full contract.

[Inspect a complete specimen and a one-field failure →](../record-examples.md#example-evidence-set)

**Declared endpoint kinds for this exact carrier:** [evidence-set](endpoint-evidence-set.md#endpoint-evidence-set)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, node_id, kind, name, lifecycle_state, authority_effect, owner_ref, scope_ref, evidence_refs, challenge_route, successor_refs, relation_refs, payload, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.evidence-set/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-evidence-set/v1"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../assets/1ab42ade4cea-artifact.json)

**Schema**

[Read the schema](../../assets/cdd6acb7d154-schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

cdd6acb7d1546ae5e709c042d75cd656335297aac8111e8d0e2e631abf325ae9

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
