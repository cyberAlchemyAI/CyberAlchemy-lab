[Documentation home](../../README.md)

# evaluates

<a id="rel-relation-evaluates"></a>

[Reference](../README.md#reference) / [Connection rules](../relation-kinds.md#catalog-relations) / evaluates

# evaluates

The question this connection answers

Which subject or proposition is being assessed?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **evaluates** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** evaluation_role, evaluation_purpose

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** support, contradiction, adoption, realization, product-value

<a id="rel-relation-evaluates-section-1"></a>

## Read one permitted pattern

[evaluation](endpoint-evaluation.md#endpoint-evaluation) **evaluates**Required: evaluation_role, evaluation_purpose [capability-realization-binding](endpoint-capability-realization-binding.md#endpoint-capability-realization-binding)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| evaluation | capability-realization-binding |
| evaluation | product-capability |
| evaluation | product-thesis |
| experiment-design | capability-realization-binding |
| experiment-design | product |
| experiment-design | product-capability |
| experiment-design | product-thesis |
| experiment-run | capability-realization-binding |
| experiment-run | product |
| experiment-run | product-capability |
| experiment-run | product-thesis |
| failure-assessment | failure-occurrence |
| lesson-outcome-assessment | lesson-application |
| preference-application-assessment | communication-preference |
| work-outcome-assessment | agent-action |
| work-outcome-assessment | work |

### Exact meaning axis, effect and qualifier contract

relation.evaluates

**Meaning axis:** `axis.evaluation` — the distinct semantic question this rule owns.

Records evaluation scope without deciding evidence polarity, adoption, realization, or value.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "evaluation_purpose": {
      "minLength": 1,
      "type": "string"
    },
    "evaluation_role": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "evaluation_role",
    "evaluation_purpose"
  ]
}
````

**Acceptance record**

Complete Lab definition model admission

**Original contract**

[Read the relation contract](../../../../authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/evaluates.json)

### Contract content fingerprint

508e41bd0dd8be28344c9ba4c6aa9d1fe0a469459c6de9883bc893094b4c84c9

SHA-256 identifies the captured contents, not truth or permission.

[Return to Connection rules](../relation-kinds.md#catalog-relations)
