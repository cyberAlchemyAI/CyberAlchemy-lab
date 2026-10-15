[Documentation home](../../README.md)

# Operational lesson · v1

<a id="type-cal-artifact-type-operational-lesson-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Operational lesson · v1

# Operational lesson · v1

This contract specifies requirements for records of kind `operational-lesson`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Operational Lesson](def-cal-definition-operational-lesson.md#def-cal-definition-operational-lesson)

<a id="type-cal-artifact-type-operational-lesson-v1-section-1"></a>

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

**[Content example from the incident:](../../tutorials/incident-walkthrough.md)** Propose checking export boundaries, with evidence, applicability, exclusions, predicted benefit and a falsifier. This describes the subject; a complete record must satisfy the full contract.

**Declared endpoint kinds for this exact carrier:** [operational-lesson](endpoint-operational-lesson.md#endpoint-operational-lesson)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, node_id, kind, name, lifecycle_state, authority_effect, owner_ref, scope_ref, evidence_refs, challenge_route, successor_refs, relation_refs, payload, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.operational-lesson/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-operational-lesson/v1"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../assets/c54ada8c16ae-artifact.json)

**Schema**

[Read the schema](../../assets/ed31d5bb0e5c-schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

ed31d5bb0e5c38f68a26d2682800f4e4246446317e2169a55f0ec96933f2180a

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
