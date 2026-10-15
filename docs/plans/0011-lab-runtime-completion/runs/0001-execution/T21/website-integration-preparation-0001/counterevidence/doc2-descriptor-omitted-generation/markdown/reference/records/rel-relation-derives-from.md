[Documentation home](../../README.md)

# derives-from

<a id="rel-relation-derives-from"></a>

[Reference](../README.md#reference) / [Connection rules](../relation-kinds.md#catalog-relations) / derives-from

# derives-from

The question this connection answers

From which material or governed source was this artifact derived?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **derives-from** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** derivation_role

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** identity-equality, source-authority-transfer, admission

<a id="rel-relation-derives-from-section-1"></a>

## Read one permitted pattern

[agent-reflection](endpoint-agent-reflection.md#endpoint-agent-reflection) **derives-from**Required: derivation_role [agent-action](endpoint-agent-action.md#endpoint-agent-action)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| agent-reflection | agent-action |
| agent-reflection | agent-session |
| agent-reflection | evidence-set |
| agent-reflection | failure-assessment |
| agent-reflection | feedback-record |
| agent-reflection | finding |
| agent-reflection | observation |
| agent-reflection | operational-observation |
| agent-reflection | work-outcome-assessment |
| classification-assignment | evidence-set |
| classification-assignment | feedback-record |
| classification-assignment | finding |
| classification-assignment | measurement-result |
| classification-assignment | observation |
| classification-assignment | operational-observation |
| classification-assignment | source |
| context-view | context |
| evidence-set | experiment-run |
| evidence-set | research-run |
| finding | evidence-set |
| finding | research-run |
| generated-output | source |
| improvement-signal | drift-assessment |
| improvement-signal | failure-assessment |
| improvement-signal | operational-observation |
| improvement-signal | work-outcome-assessment |
| improvement-target | improvement-signal |
| improvement-target | lesson-outcome-assessment |
| improvement-target | operational-lesson |
| measurement-result | experiment-run |
| measurement-result | research-run |
| observation | experiment-run |
| observation | research-run |
| operational-lesson | agent-reflection |
| operational-lesson | evidence-set |
| operational-lesson | failure-assessment |
| operational-lesson | feedback-record |
| operational-lesson | finding |
| operational-lesson | lesson-outcome-assessment |
| product-capability | product-thesis |

### Exact meaning axis, effect and qualifier contract

relation.derives-from

**Meaning axis:** `axis.derivation` — the distinct semantic question this rule owns.

Records derivation, compilation, or projection while preserving source and derived identities.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "derivation_role": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "derivation_role"
  ]
}
````

**Acceptance record**

Complete Lab definition model admission

**Original contract**

[Read the relation contract](../../assets/63a0ce68e91d-derives-from.json)

### Contract content fingerprint

63a0ce68e91df2b5a194738e6534dc5da2c10436ea847752fbdf4d8a45d8c891

SHA-256 identifies the captured contents, not truth or permission.

[Return to Connection rules](../relation-kinds.md#catalog-relations)
