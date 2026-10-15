[Documentation home](../../README.md)

# tests-hypothesis

<a id="rel-relation-tests-hypothesis"></a>

[Reference](../README.md#reference) / [Connection rules](../relation-kinds.md#catalog-relations) / tests-hypothesis

# tests-hypothesis

The question this connection answers

Which exact Hypothesis is this Experiment Design constructed to test?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **tests-hypothesis** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** hypothesis_version_ref, test_role

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** support, contradiction, truth, successful-execution

<a id="rel-relation-tests-hypothesis-section-1"></a>

## Read one permitted pattern

[experiment-design](endpoint-experiment-design.md#endpoint-experiment-design) **tests-hypothesis**Required: hypothesis_version_ref, test_role [hypothesis](endpoint-hypothesis.md#endpoint-hypothesis)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| experiment-design | hypothesis |

### Exact meaning axis, effect and qualifier contract

relation.tests-hypothesis

**Meaning axis:** `axis.hypothesis-testing` — the distinct semantic question this rule owns.

Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "hypothesis_version_ref": {
      "minLength": 1,
      "type": "string"
    },
    "test_role": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "hypothesis_version_ref",
    "test_role"
  ]
}
````

**Acceptance record**

Complete Lab definition model admission

**Original contract**

[Read the relation contract](../../assets/644268137f28-tests-hypothesis.json)

### Contract content fingerprint

644268137f28414c446968be09b53df39310c696f67b3ec5265d3bf9dac07d80

SHA-256 identifies the captured contents, not truth or permission.

[Return to Connection rules](../relation-kinds.md#catalog-relations)
