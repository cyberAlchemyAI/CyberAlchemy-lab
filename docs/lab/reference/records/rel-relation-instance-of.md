[Documentation home](../../README.md)

# instance-of

<a id="rel-relation-instance-of"></a>

[Reference](../README.md#reference) / [Connection rules](../relation-kinds.md#catalog-relations) / instance-of

# instance-of

The question this connection answers

Under which exact parent model is this subject classified?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **instance-of** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** parent_version_ref, binding_ref

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** conformance, realization, ownership-transfer

<a id="rel-relation-instance-of-section-1"></a>

## Read one permitted pattern

[agent-action](endpoint-agent-action.md#endpoint-agent-action) **instance-of**Required: parent_version_ref, binding_ref [classification-value](endpoint-classification-value.md#endpoint-classification-value)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| agent-action | classification-value |
| agent-instance | classification-value |
| capability-instance | governed-model |
| capability-instance | product-capability |
| failure-mode | classification-value |
| failure-occurrence | classification-value |
| failure-occurrence | failure-mode |
| implementation | governed-model |
| implementation | product-capability |
| improvement-target | classification-value |
| operational-lesson | classification-value |
| product-capability | product |

### Exact meaning axis, effect and qualifier contract

relation.instance-of

**Meaning axis:** `axis.classification` — the distinct semantic question this rule owns.

Records classification without implying conformance, ownership transfer, or realization.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "binding_ref": {
      "minLength": 1,
      "type": "string"
    },
    "parent_version_ref": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "parent_version_ref",
    "binding_ref"
  ]
}
````

**Acceptance record**

Complete Lab definition model admission

**Original contract**

[Read the relation contract](../../../../authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/instance-of.json)

### Contract content fingerprint

02af44a7bb4693b04148dc168cd336749b711da4001dbaf2ea4bcc6047747cf4

SHA-256 identifies the captured contents, not truth or permission.

[Return to Connection rules](../relation-kinds.md#catalog-relations)
