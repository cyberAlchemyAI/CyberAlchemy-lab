[Documentation home](../../README.md)

# binds-implementation

<a id="rel-relation-binds-implementation"></a>

[Reference](../README.md#reference) / [Connection rules](../relation-kinds.md#catalog-relations) / binds-implementation

# binds-implementation

The question this connection answers

Which Ontology or Schema does this implementation bind?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **binds-implementation** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** binding_role

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** conformance, runtime-effectiveness, admission

<a id="rel-relation-binds-implementation-section-1"></a>

## Read one permitted pattern

[implementation](endpoint-implementation.md#endpoint-implementation) **binds-implementation**Required: binding_role [ontology](endpoint-ontology.md#endpoint-ontology)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| implementation | ontology |
| implementation | schema |

### Exact meaning axis, effect and qualifier contract

relation.binds-implementation

**Meaning axis:** `axis.implementation-binding` — the distinct semantic question this rule owns.

Records an implementation-model binding without proving conformance or runtime behavior.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "binding_role": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "binding_role"
  ]
}
````

**Acceptance record**

Complete Lab definition model admission

**Original contract**

[Read the relation contract](../../../../authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/binds-implementation.json)

### Contract content fingerprint

eece4ecf3e801ca5e53b8675dcda4ed024d93f766fbb1cc09167ffcb59292b2d

SHA-256 identifies the captured contents, not truth or permission.

[Return to Connection rules](../relation-kinds.md#catalog-relations)
