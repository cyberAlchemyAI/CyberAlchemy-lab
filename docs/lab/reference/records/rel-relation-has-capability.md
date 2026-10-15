[Documentation home](../../README.md)

# has-capability

<a id="rel-relation-has-capability"></a>

[Reference](../README.md#reference) / [Connection rules](../relation-kinds.md#catalog-relations) / has-capability

# has-capability

The question this connection answers

Which Agent Capability is declared for this Agent Profile or Agent Instance?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **has-capability** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** capability_version_ref, declaration_basis

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** authority, successful-performance, product-value

<a id="rel-relation-has-capability-section-1"></a>

## Read one permitted pattern

[agent-instance](endpoint-agent-instance.md#endpoint-agent-instance) **has-capability**Required: capability_version_ref, declaration_basis [agent-capability](endpoint-agent-capability.md#endpoint-agent-capability)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| agent-instance | agent-capability |
| agent-profile | agent-capability |

### Exact meaning axis, effect and qualifier contract

relation.has-capability

**Meaning axis:** `axis.agent-capability-declaration` — the distinct semantic question this rule owns.

Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "capability_version_ref": {
      "minLength": 1,
      "type": "string"
    },
    "declaration_basis": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "capability_version_ref",
    "declaration_basis"
  ]
}
````

**Acceptance record**

Complete Lab definition model admission

**Original contract**

[Read the relation contract](../../../../authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/has-capability.json)

### Contract content fingerprint

1ce58bfff967a3593a3b9fba9630cc304de5e21b46a1ae56d5aafeb6d98b121b

SHA-256 identifies the captured contents, not truth or permission.

[Return to Connection rules](../relation-kinds.md#catalog-relations)
