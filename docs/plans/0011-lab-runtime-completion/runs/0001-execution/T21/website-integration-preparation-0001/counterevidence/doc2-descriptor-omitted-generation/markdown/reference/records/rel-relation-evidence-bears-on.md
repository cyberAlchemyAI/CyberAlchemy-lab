[Documentation home](../../README.md)

# evidence-bears-on

<a id="rel-relation-evidence-bears-on"></a>

[Reference](../README.md#reference) / [Connection rules](../relation-kinds.md#catalog-relations) / evidence-bears-on

# evidence-bears-on

The question this connection answers

What evidential polarity does this evidence have toward this claim?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **evidence-bears-on** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** polarity

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** claim-acceptance, decision, admission, truth

<a id="rel-relation-evidence-bears-on-section-1"></a>

## Read one permitted pattern

[evidence-set](endpoint-evidence-set.md#endpoint-evidence-set) **evidence-bears-on**Required: polarity [authority-claim](endpoint-authority-claim.md#endpoint-authority-claim)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| evidence-set | authority-claim |
| evidence-set | challenge-event |
| evidence-set | classification-assignment |
| evidence-set | drift-assessment |
| evidence-set | failure-assessment |
| evidence-set | failure-occurrence |
| evidence-set | finding |
| evidence-set | hypothesis |
| evidence-set | identity-claim |
| evidence-set | improvement-signal |
| evidence-set | lesson-outcome-assessment |
| evidence-set | operational-lesson |
| evidence-set | preference-application-assessment |
| evidence-set | work-outcome-assessment |
| feedback-record | challenge-event |
| feedback-record | classification-assignment |
| feedback-record | drift-assessment |
| feedback-record | failure-assessment |
| feedback-record | failure-occurrence |
| feedback-record | improvement-signal |
| feedback-record | lesson-outcome-assessment |
| feedback-record | operational-lesson |
| feedback-record | preference-application-assessment |
| feedback-record | work-outcome-assessment |
| finding | challenge-event |
| finding | classification-assignment |
| finding | drift-assessment |
| finding | failure-assessment |
| finding | failure-occurrence |
| finding | improvement-signal |
| finding | lesson-outcome-assessment |
| finding | operational-lesson |
| finding | preference-application-assessment |
| finding | work-outcome-assessment |
| measurement-result | authority-claim |
| measurement-result | challenge-event |
| measurement-result | classification-assignment |
| measurement-result | drift-assessment |
| measurement-result | failure-assessment |
| measurement-result | failure-occurrence |
| measurement-result | finding |
| measurement-result | hypothesis |
| measurement-result | identity-claim |
| measurement-result | improvement-signal |
| measurement-result | lesson-outcome-assessment |
| measurement-result | operational-lesson |
| measurement-result | preference-application-assessment |
| measurement-result | work-outcome-assessment |
| observation | authority-claim |
| observation | challenge-event |
| observation | classification-assignment |
| observation | drift-assessment |
| observation | failure-assessment |
| observation | failure-occurrence |
| observation | finding |
| observation | hypothesis |
| observation | identity-claim |
| observation | improvement-signal |
| observation | lesson-outcome-assessment |
| observation | operational-lesson |
| observation | preference-application-assessment |
| observation | work-outcome-assessment |
| operational-observation | challenge-event |
| operational-observation | classification-assignment |
| operational-observation | drift-assessment |
| operational-observation | failure-assessment |
| operational-observation | failure-occurrence |
| operational-observation | improvement-signal |
| operational-observation | lesson-outcome-assessment |
| operational-observation | operational-lesson |
| operational-observation | preference-application-assessment |
| operational-observation | work-outcome-assessment |

### Exact meaning axis, effect and qualifier contract

relation.evidence-bears-on

**Meaning axis:** `axis.evidence-polarity` — the distinct semantic question this rule owns.

Records supporting or contradicting evidence without accepting, rejecting, or deciding the claim.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "polarity": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "polarity"
  ]
}
````

**Acceptance record**

Complete Lab definition model admission

**Original contract**

[Read the relation contract](../../assets/f6b0cda804c0-evidence-bears-on.json)

### Contract content fingerprint

f6b0cda804c0130d47c09b900ffb19cadfde8c371ee001df66d0d0c73c0d5253

SHA-256 identifies the captured contents, not truth or permission.

[Return to Connection rules](../relation-kinds.md#catalog-relations)
