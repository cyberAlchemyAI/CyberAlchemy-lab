[Documentation home](../../README.md)

# acts-for

<a id="rel-relation-acts-for"></a>

[Reference](../README.md#reference) / [Connection rules](../relation-kinds.md#catalog-relations) / acts-for

# acts-for

The question this connection answers

Which Principal is this Agent Instance acting for under one exact Delegation?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **acts-for** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** delegation_ref, scope_ref, effective_period, revocation_state

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** identity-equivalence, ownership-transfer, unrestricted-authority

<a id="rel-relation-acts-for-section-1"></a>

## Read one permitted pattern

[agent-instance](endpoint-agent-instance.md#endpoint-agent-instance) **acts-for**Required: delegation_ref, scope_ref, effective_period, revocation_state [principal](endpoint-principal.md#endpoint-principal)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| agent-instance | principal |

### Exact meaning axis, effect and qualifier contract

relation.acts-for

**Meaning axis:** `axis.bounded-representation` — the distinct semantic question this rule owns.

Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "delegation_ref": {
      "minLength": 1,
      "type": "string"
    },
    "effective_period": {
      "minLength": 1,
      "type": "string"
    },
    "revocation_state": {
      "minLength": 1,
      "type": "string"
    },
    "scope_ref": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "delegation_ref",
    "scope_ref",
    "effective_period",
    "revocation_state"
  ]
}
````

**Acceptance record**

Complete Lab definition model admission

**Original contract**

[Read the relation contract](../../../../authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/acts-for.json)

### Contract content fingerprint

da08d8570d32664fe5045782b76c602ec5162afaeea4eb1cafcf1a09e66e46f3

SHA-256 identifies the captured contents, not truth or permission.

[Return to Connection rules](../relation-kinds.md#catalog-relations)
