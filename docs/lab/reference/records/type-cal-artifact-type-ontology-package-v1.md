[Documentation home](../../README.md)

# Ontology package · v1

<a id="type-cal-artifact-type-ontology-package-v1"></a>

[Reference](../README.md#reference) / [Record formats](../artifact-types.md#catalog-types) / Ontology package · v1

# Ontology package · v1

This contract specifies requirements for records of kind `ontology-package`. Its linked definitions explain their meaning; its schema specifies structure and constraints.

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Definitions this format uses:** [Ontology](def-cal-definition-ontology.md#def-cal-definition-ontology) · [Generated Output](def-cal-definition-generated-output.md#def-cal-definition-generated-output)

<a id="type-cal-artifact-type-ontology-package-v1-section-1"></a>

## Prepare a record

- `schema_version`
- `package_id`
- `version`
- `status`
- `authority_effect`
- `domain`
- `product_ref`
- `product_output_ref`
- `source_binding`
- `nodes`
- `relations`
- `residue`
- `query_contract`
- `source_direction`
- `claim_ceiling`

These are the required keys at the selected schema level. Read the full schema for nested fields, alternatives and referenced rules before judging a complete record.

**[Content example from the incident:](../../tutorials/incident-walkthrough.md)** Organize typed meanings, subjects, connections and evidence so the investigation can recover their context. This describes the subject; a complete record must satisfy the full contract.

**Declared endpoint kinds for this exact carrier:** [ontology-package](endpoint-ontology-package.md#endpoint-ontology-package)

### Required fields and schema rules

**Fields required at the selected level:** schema_version, package_id, version, status, authority_effect, domain, product_ref, product_output_ref, source_binding, nodes, relations, residue, query_contract, source_direction, claim_ceiling

Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.

Top level of the selected schema; follow the exact schema and its references for full constraints.

### Exact type reference and how a record identifies its type

cal.artifact-type.ontology-package/v1

A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.

````json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-ontology-package/v1"
}
````

**Acceptance record**

Complete Lab definition model admission

**Contract**

[Read the type contract](../../../../authority/artifact-types/ontology-package/v1/artifact.json)

**Schema**

[Read the schema](../../../../authority/artifact-types/ontology-package/v1/schema.json)

### Schema content fingerprint and descriptor status

**Schema fingerprint · SHA-256**

331f3535aab9460c159168cd4ed0697a8b77332a28fb9b7e9ebb7dd5ad85cc07

Descriptor status codes: admitted-current. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.

[Return to Record formats](../artifact-types.md#catalog-types)
