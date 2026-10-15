[Documentation home](../../README.md)

# uses-method

<a id="rel-relation-uses-method"></a>

[Reference](../README.md#reference) / [Connection rules](../relation-kinds.md#catalog-relations) / uses-method

# uses-method

The question this connection answers

Which Method does this subject depend on or employ?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **uses-method** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** usage_role

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** conformance, realization, validation, achievement

<a id="rel-relation-uses-method-section-1"></a>

## Read one permitted pattern

[agent-action](endpoint-agent-action.md#endpoint-agent-action) **uses-method**Required: usage_role [method](endpoint-method.md#endpoint-method)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| agent-action | method |
| experiment-run | method |
| measurement-result | method |
| observation | method |
| product | method |
| project | method |
| research-run | method |

### Exact meaning axis, effect and qualifier contract

relation.uses-method

**Meaning axis:** `axis.method-dependency` — the distinct semantic question this rule owns.

Records Method dependency without implying conformance, realization, or success.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "usage_role": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "usage_role"
  ]
}
````

**Acceptance record**

Complete Lab definition model admission

**Original contract**

[Read the relation contract](../../assets/6e6d0bec81cf-uses-method.json)

### Contract content fingerprint

6e6d0bec81cfd4a9179d97a109d0f904ef0855c1f9420be7cc71f2b1f2dd0ee6

SHA-256 identifies the captured contents, not truth or permission.

[Return to Connection rules](../relation-kinds.md#catalog-relations)
