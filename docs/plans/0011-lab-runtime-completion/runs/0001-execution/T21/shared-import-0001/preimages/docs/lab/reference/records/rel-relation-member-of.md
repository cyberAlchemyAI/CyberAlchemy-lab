[Documentation home](../../README.md)

# member-of

<a id="rel-relation-member-of"></a>

[Reference catalog](../relation-kinds.md#catalog-relations) / Exact record

# member-of

The question this connection answers

Which governed container or scope is this member part of?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **member-of** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** membership_role

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** contribution, assignment, authority, identity-equivalence

## Read one permitted pattern

[agent-action](endpoint-agent-action.md#endpoint-agent-action) **member-of**Required: membership_role [agent-session](endpoint-agent-session.md#endpoint-agent-session)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| agent-action | agent-session |
| agent-assignment | project |
| agent-instance | agent-session |
| capability-realization-binding | project |
| classification-value | classification-scheme |
| context | product |
| context | project |
| decision | decision-bundle |
| evidence-set | project |
| experiment-design | project |
| experiment-run | project |
| failure-occurrence | incident |
| goal | project |
| ontology-node | ontology |
| person-reference | team |
| product | product |
| product-capability | product |
| product-thesis | product |
| project-state | project |
| research-inquiry | project |
| research-run | project |
| responsibility | role |
| typed-relation | ontology |
| work | project |

### Exact meaning axis, effect and qualifier contract

relation.member-of

**Meaning axis:** `axis.membership` — the distinct semantic question this rule owns.

Records scoped membership or composition in member-to-container direction without transferring identity or authority.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "membership_role": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "membership_role"
  ]
}
````

**Acceptance record**

Governance relation contracts admission

**Original contract**

[Read the relation contract](../../../../authority/relation-kinds/candidates/0007-governance-transaction-extension/instances/relation-kinds/member-of.json)

### Contract content fingerprint

ac3103da70adbc8d2a62c34503056f38b0ea2d9726627a045abe8956f778706f

SHA-256 identifies the captured contents, not truth or permission.

[Return to this catalog](../relation-kinds.md#catalog-relations)
