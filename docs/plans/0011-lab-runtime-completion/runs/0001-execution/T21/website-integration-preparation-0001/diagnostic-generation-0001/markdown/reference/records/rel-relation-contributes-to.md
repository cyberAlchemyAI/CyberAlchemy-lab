[Documentation home](../../README.md)

# contributes-to

<a id="rel-relation-contributes-to"></a>

[Reference](../README.md#reference) / [Connection rules](../relation-kinds.md#catalog-relations) / contributes-to

# contributes-to

The question this connection answers

Which Product or Goal is this activity intended to advance?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **contributes-to** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** contribution_role, contribution_scope

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** membership, realization, evaluation-result, product-value

<a id="rel-relation-contributes-to-section-1"></a>

## Read one permitted pattern

[agent-action](endpoint-agent-action.md#endpoint-agent-action) **contributes-to**Required: contribution_role, contribution_scope [goal](endpoint-goal.md#endpoint-goal)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| agent-action | goal |
| agent-action | product |
| experiment-design | goal |
| experiment-run | goal |
| project | goal |
| project | product |
| research-inquiry | goal |
| research-run | goal |

### Exact meaning axis, effect and qualifier contract

relation.contributes-to

**Meaning axis:** `axis.contribution` — the distinct semantic question this rule owns.

Records intended contribution without proving success, realization, or value.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "contribution_role": {
      "minLength": 1,
      "type": "string"
    },
    "contribution_scope": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "contribution_role",
    "contribution_scope"
  ]
}
````

**Acceptance record**

Complete Lab definition model admission

**Original contract**

[Read the relation contract](../../assets/a162c2943fe7-contributes-to.json)

### Contract content fingerprint

a162c2943fe792186572b280c04b8f4b9fc919cba6ced30decc3da17c006fd52

SHA-256 identifies the captured contents, not truth or permission.

[Return to Connection rules](../relation-kinds.md#catalog-relations)
