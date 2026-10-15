[Documentation home](../../README.md)

# realizes

<a id="rel-relation-realizes"></a>

[Reference](../README.md#reference) / [Connection rules](../relation-kinds.md#catalog-relations) / realizes

# realizes

The question this connection answers

Which declared design or capability is concretely instantiated by this subject?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **realizes** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** realization_role, exact_target_version_ref

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** conformance, effectiveness, adoption, support

<a id="rel-relation-realizes-section-1"></a>

## Read one permitted pattern

[experiment-run](endpoint-experiment-run.md#endpoint-experiment-run) **realizes**Required: realization_role, exact_target_version_ref [experiment-design](endpoint-experiment-design.md#endpoint-experiment-design)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| experiment-run | experiment-design |
| implementation | product-capability |

### Exact meaning axis, effect and qualifier contract

relation.realizes

**Meaning axis:** `axis.realization` — the distinct semantic question this rule owns.

Records realization or execution without implying conformance, effectiveness, adoption, or evidence acceptance.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "exact_target_version_ref": {
      "minLength": 1,
      "type": "string"
    },
    "realization_role": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "realization_role",
    "exact_target_version_ref"
  ]
}
````

**Acceptance record**

Complete Lab definition model admission

**Original contract**

[Read the relation contract](../../../../authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/realizes.json)

### Contract content fingerprint

affd03d8d00c136c70fa379e5aaf389b11cc8fd5856336790ce228277fcc16e3

SHA-256 identifies the captured contents, not truth or permission.

[Return to Connection rules](../relation-kinds.md#catalog-relations)
