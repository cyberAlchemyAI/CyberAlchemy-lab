[Documentation home](../../README.md)

# Ontology · v1

<a id="type-cal-artifact-type-ontology-v1"></a>

[Reference catalog](../artifact-types.md#catalog-types) / Exact record

# Ontology · v1

This contract specifies requirements for records of kind `ontology`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Ontology](def-cal-definition-ontology.md#def-cal-definition-ontology)

## Prepare a record

- `authority_effect`
- `kind`
- `node_id`
- `owner_ref`
- `scope_ref`
- `status`
- `name`
- `ontology_version`
- `purpose`
- `boundaries`
- `node_refs`
- `relation_refs`
- `branch_refs`
- `role_assignment_refs`
- `provenance_refs`
- `confidence_policy_ref`
- `promotion_state`
- `governance_rules`
- `owner_route`
- `challenge_route`
- `successor_refs`
- `claim_ceiling`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**[Content example from the incident:](../../tutorials/incident-walkthrough.md)** Organize typed meanings, subjects, connections and evidence so the investigation can recover their context. This describes the subject; a complete record must satisfy the full contract.

**Declared endpoint kinds for this exact carrier:** [ontology](endpoint-ontology.md#endpoint-ontology)

### Required fields and schema rules

**Fields required at the selected level:** authority_effect, kind, node_id, owner_ref, scope_ref, status, name, ontology_version, purpose, boundaries, node_refs, relation_refs, branch_refs, role_assignment_refs, provenance_refs, confidence_policy_ref, promotion_state, governance_rules, owner_route, challenge_route, successor_refs, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.ontology/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/kind",
  "value": "ontology"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/ontology/v1/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/ontology/v1/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

89f831b26155857e7e9f9d1a467f2c5f950e05526d72d65832338db7a58ef6d1

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to this catalog](../artifact-types.md#catalog-types)
