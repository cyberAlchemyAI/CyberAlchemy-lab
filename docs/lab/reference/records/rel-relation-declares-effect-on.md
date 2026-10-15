[Documentation home](../../README.md)

# declares-effect-on

<a id="rel-relation-declares-effect-on"></a>

[Reference](../README.md#reference) / [Connection rules](../relation-kinds.md#catalog-relations) / declares-effect-on

# declares-effect-on

The question this connection answers

Which exact governance effect does this Decision declare?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **declares-effect-on** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** effect_kind, exact_target_version_ref

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** effect-execution, cross-effect-inference, runtime-success

<a id="rel-relation-declares-effect-on-section-1"></a>

## Read one permitted pattern

[decision](endpoint-decision.md#endpoint-decision) **declares-effect-on**Required: effect_kind, exact_target_version_ref [agent-capability](endpoint-agent-capability.md#endpoint-agent-capability)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| decision | agent-capability |
| decision | agent-profile |
| decision | artifact-type |
| decision | capability-realization-binding |
| decision | challenge-event |
| decision | classification-assignment |
| decision | communication-preference |
| decision | definition |
| decision | delegation |
| decision | effect |
| decision | failure-assessment |
| decision | failure-control-binding |
| decision | failure-mode |
| decision | failure-occurrence |
| decision | governed-model |
| decision | improvement-target |
| decision | incident |
| decision | intent-resolution |
| decision | operational-lesson |
| decision | product-capability |
| decision | relation-kind |

### Exact meaning axis, effect and qualifier contract

relation.declares-effect-on

**Meaning axis:** `axis.decision-effect` — the distinct semantic question this rule owns.

Records admission, adoption, or authorization as separate effect values and executes none of them.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "effect_kind": {
      "minLength": 1,
      "type": "string"
    },
    "exact_target_version_ref": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "effect_kind",
    "exact_target_version_ref"
  ]
}
````

**Acceptance record**

Complete Lab definition model admission

**Original contract**

[Read the relation contract](../../../../authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/declares-effect-on.json)

### Contract content fingerprint

bd16d779231c9d29a052fc9fc1217d5d6ff9edc52785cf012fb202a2cc6bdb9c

SHA-256 identifies the captured contents, not truth or permission.

[Return to Connection rules](../relation-kinds.md#catalog-relations)
