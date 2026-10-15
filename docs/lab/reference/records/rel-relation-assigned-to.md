[Documentation home](../../README.md)

# assigned-to

<a id="rel-relation-assigned-to"></a>

[Reference](../README.md#reference) / [Connection rules](../relation-kinds.md#catalog-relations) / assigned-to

# assigned-to

The question this connection answers

Which Role or Responsibility is explicitly assigned to this assignee?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **assigned-to** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** assignment_kind, relation_record_ref

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** team-membership, authority, permission, identity

<a id="rel-relation-assigned-to-section-1"></a>

## Read one permitted pattern

[agent-instance](endpoint-agent-instance.md#endpoint-agent-instance) **assigned-to**Required: assignment_kind, relation_record_ref [responsibility](endpoint-responsibility.md#endpoint-responsibility)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| agent-instance | responsibility |
| agent-instance | role |
| person-reference | responsibility |
| person-reference | role |
| team | responsibility |
| team | role |

### Exact meaning axis, effect and qualifier contract

relation.assigned-to

**Meaning axis:** `axis.assignment` — the distinct semantic question this rule owns.

Records an assignment through its lifecycle-bearing record without implying Team membership or authority.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "assignment_kind": {
      "minLength": 1,
      "type": "string"
    },
    "relation_record_ref": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "assignment_kind",
    "relation_record_ref"
  ]
}
````

**Acceptance record**

Complete Lab definition model admission

**Original contract**

[Read the relation contract](../../../../authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/assigned-to.json)

### Contract content fingerprint

b772abbe7ed9af4649b8ed39cac281045f36610ba347b15fbd1596c41fb5f610

SHA-256 identifies the captured contents, not truth or permission.

[Return to Connection rules](../relation-kinds.md#catalog-relations)
