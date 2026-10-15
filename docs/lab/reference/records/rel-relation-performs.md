[Documentation home](../../README.md)

# performs

<a id="rel-relation-performs"></a>

[Reference](../README.md#reference) / [Connection rules](../relation-kinds.md#catalog-relations) / performs

# performs

The question this connection answers

Which attributable activity is performed or attempted by this Agent Instance?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **performs** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** session_ref, participation_role, action_posture

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** ownership, approval, admission, successful-effect

<a id="rel-relation-performs-section-1"></a>

## Read one permitted pattern

[agent-instance](endpoint-agent-instance.md#endpoint-agent-instance) **performs**Required: session_ref, participation_role, action_posture [agent-action](endpoint-agent-action.md#endpoint-agent-action)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| agent-instance | agent-action |
| agent-instance | experiment-run |
| agent-instance | research-run |
| agent-instance | review |
| agent-instance | work |

### Exact meaning axis, effect and qualifier contract

relation.performs

**Meaning axis:** `axis.agent-performance-attribution` — the distinct semantic question this rule owns.

Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "action_posture": {
      "minLength": 1,
      "type": "string"
    },
    "participation_role": {
      "minLength": 1,
      "type": "string"
    },
    "session_ref": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "session_ref",
    "participation_role",
    "action_posture"
  ]
}
````

**Acceptance record**

Complete Lab definition model admission

**Original contract**

[Read the relation contract](../../../../authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/performs.json)

### Contract content fingerprint

eed979c4a84b0ba04655a371805464a9d8c1b0e3edc1e630f843475721dfd5da

SHA-256 identifies the captured contents, not truth or permission.

[Return to Connection rules](../relation-kinds.md#catalog-relations)
