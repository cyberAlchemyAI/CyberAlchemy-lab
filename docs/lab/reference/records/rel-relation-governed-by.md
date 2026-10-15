[Documentation home](../../README.md)

# governed-by

<a id="rel-relation-governed-by"></a>

[Reference](../README.md#reference) / [Connection rules](../relation-kinds.md#catalog-relations) / governed-by

# governed-by

The question this connection answers

Which Policy or Constitution governs this subject?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **governed-by** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** governance_role

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** conformance, authorization, admission

<a id="rel-relation-governed-by-section-1"></a>

## Read one permitted pattern

[admission-transaction](endpoint-admission-transaction.md#endpoint-admission-transaction) **governed-by**Required: governance_role [policy](endpoint-policy.md#endpoint-policy)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| admission-transaction | policy |
| agent-action | policy |
| agent-instance | policy |
| agent-profile | policy |
| agent-session | policy |
| artifact-type | constitution |
| authority-boundary | policy |
| challenge-contract | policy |
| challenge-event | challenge-contract |
| classification-assignment | classification-scheme |
| classification-assignment | policy |
| communication-preference | policy |
| context | policy |
| decision-bundle | policy |
| decision-checkpoint | policy |
| definition | constitution |
| failure-assessment | policy |
| failure-control-binding | policy |
| failure-mode | policy |
| failure-occurrence | policy |
| feedback-record | policy |
| incident | policy |
| ontology | policy |
| ontology-edge | policy |
| ontology-node | policy |
| operational-lesson | policy |
| relation-kind | constitution |
| user-decision-preference | policy |
| workflow-decision-profile | policy |

### Exact meaning axis, effect and qualifier contract

relation.governed-by

**Meaning axis:** `axis.governance-applicability` — the distinct semantic question this rule owns.

Records applicable governance without proving compliance or authorization.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "governance_role": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "governance_role"
  ]
}
````

**Acceptance record**

Governance relation contracts admission

**Original contract**

[Read the relation contract](../../../../authority/relation-kinds/candidates/0007-governance-transaction-extension/instances/relation-kinds/governed-by.json)

### Contract content fingerprint

2e63e56783a856d2eaa7f755dc67cb7a02188656c1b410daf8aa54e50bcd37f7

SHA-256 identifies the captured contents, not truth or permission.

[Return to Connection rules](../relation-kinds.md#catalog-relations)
