[Documentation home](../../README.md)

# affects

<a id="rel-relation-affects"></a>

[Reference](../README.md#reference) / [Connection rules](../relation-kinds.md#catalog-relations) / affects

# affects

The question this connection answers

Which exact subject was affected, under what declared scope?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **affects** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** impact_scope, evidence_posture

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** cause, severity, blame, ownership

<a id="rel-relation-affects-section-1"></a>

## Read one permitted pattern

[failure-occurrence](endpoint-failure-occurrence.md#endpoint-failure-occurrence) **affects**Required: impact_scope, evidence_posture [agent-capability](endpoint-agent-capability.md#endpoint-agent-capability)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| failure-occurrence | agent-capability |
| failure-occurrence | agent-session |
| failure-occurrence | artifact-type |
| failure-occurrence | generated-output |
| failure-occurrence | implementation |
| failure-occurrence | ontology |
| failure-occurrence | person-reference |
| failure-occurrence | product |
| failure-occurrence | product-capability |
| failure-occurrence | project |
| failure-occurrence | work |
| incident | agent-capability |
| incident | agent-session |
| incident | artifact-type |
| incident | generated-output |
| incident | implementation |
| incident | ontology |
| incident | person-reference |
| incident | product |
| incident | product-capability |
| incident | project |
| incident | work |

### Exact meaning axis, effect and qualifier contract

relation.affects

**Meaning axis:** `axis.scoped-impact` — the distinct semantic question this rule owns.

Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "evidence_posture": {
      "minLength": 1,
      "type": "string"
    },
    "impact_scope": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "impact_scope",
    "evidence_posture"
  ]
}
````

**Acceptance record**

Complete Lab definition model admission

**Original contract**

[Read the relation contract](../../assets/279f185d1d70-affects.json)

### Contract content fingerprint

279f185d1d70e04737747a26c3605c95a570d1cbda77049aa2c8c3a23b0c8850

SHA-256 identifies the captured contents, not truth or permission.

[Return to Connection rules](../relation-kinds.md#catalog-relations)
