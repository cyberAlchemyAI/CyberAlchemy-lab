[Documentation home](../../README.md)

# produces

<a id="rel-relation-produces"></a>

[Reference](../README.md#reference) / [Connection rules](../relation-kinds.md#catalog-relations) / produces

# produces

The question this connection answers

Which governed output was produced by this Agent Action?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **produces** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** action_receipt_ref, production_role, output_posture

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** acceptance, correctness, admission, authority-effect

<a id="rel-relation-produces-section-1"></a>

## Read one permitted pattern

[agent-action](endpoint-agent-action.md#endpoint-agent-action) **produces**Required: action_receipt_ref, production_role, output_posture [agent-reflection](endpoint-agent-reflection.md#endpoint-agent-reflection)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| agent-action | agent-reflection |
| agent-action | challenge-event |
| agent-action | classification-assignment |
| agent-action | definition |
| agent-action | drift-assessment |
| agent-action | evidence-set |
| agent-action | failure-assessment |
| agent-action | failure-occurrence |
| agent-action | feedback-record |
| agent-action | finding |
| agent-action | generated-output |
| agent-action | improvement-signal |
| agent-action | lesson-application |
| agent-action | measurement-result |
| agent-action | observation |
| agent-action | operational-lesson |
| agent-action | operational-observation |
| agent-action | typed-relation |
| agent-action | work-outcome-assessment |

### Exact meaning axis, effect and qualifier contract

relation.produces

**Meaning axis:** `axis.attributable-production` — the distinct semantic question this rule owns.

Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "action_receipt_ref": {
      "minLength": 1,
      "type": "string"
    },
    "output_posture": {
      "minLength": 1,
      "type": "string"
    },
    "production_role": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "action_receipt_ref",
    "production_role",
    "output_posture"
  ]
}
````

**Acceptance record**

Complete Lab definition model admission

**Original contract**

[Read the relation contract](../../assets/929d432a8ec4-produces.json)

### Contract content fingerprint

929d432a8ec4f16a17d6729816595fa732fe1375ce551a00700d05eca0fe6103

SHA-256 identifies the captured contents, not truth or permission.

[Return to Connection rules](../relation-kinds.md#catalog-relations)
