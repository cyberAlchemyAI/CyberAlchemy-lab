[Documentation home](../../README.md)

# responds-to

<a id="rel-relation-responds-to"></a>

[Reference](../README.md#reference) / [Connection rules](../relation-kinds.md#catalog-relations) / responds-to

# responds-to

The question this connection answers

Which Failure Occurrence or Incident is this Agent Action intended to address?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **responds-to** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** response_role, intended_outcome

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** recovery-success, cause, closure, authority

<a id="rel-relation-responds-to-section-1"></a>

## Read one permitted pattern

[agent-action](endpoint-agent-action.md#endpoint-agent-action) **responds-to**Required: response_role, intended_outcome [failure-occurrence](endpoint-failure-occurrence.md#endpoint-failure-occurrence)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| agent-action | failure-occurrence |
| agent-action | incident |

### Exact meaning axis, effect and qualifier contract

relation.responds-to

**Meaning axis:** `axis.operational-response` — the distinct semantic question this rule owns.

Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "intended_outcome": {
      "minLength": 1,
      "type": "string"
    },
    "response_role": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "response_role",
    "intended_outcome"
  ]
}
````

**Acceptance record**

Complete Lab definition model admission

**Original contract**

[Read the relation contract](../../../../authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/responds-to.json)

### Contract content fingerprint

56f28bbcbc3b490064d486b213ee30baaa00c8fdba566d7bb6051eccb638ba25

SHA-256 identifies the captured contents, not truth or permission.

[Return to Connection rules](../relation-kinds.md#catalog-relations)
