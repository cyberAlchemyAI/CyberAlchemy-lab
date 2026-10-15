[Documentation home](../../README.md)

# addresses-improvement-target

<a id="rel-relation-addresses-improvement-target"></a>

[Reference](../README.md#reference) / [Connection rules](../relation-kinds.md#catalog-relations) / addresses-improvement-target

# addresses-improvement-target

The question this connection answers

Which Improvement Target is this Research Inquiry intended to address?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **addresses-improvement-target** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** target_version_ref, addressing_role

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** resolution, improvement, priority, authority

<a id="rel-relation-addresses-improvement-target-section-1"></a>

## Read one permitted pattern

[research-inquiry](endpoint-research-inquiry.md#endpoint-research-inquiry) **addresses-improvement-target**Required: target_version_ref, addressing_role [improvement-target](endpoint-improvement-target.md#endpoint-improvement-target)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| research-inquiry | improvement-target |

### Exact meaning axis, effect and qualifier contract

relation.addresses-improvement-target

**Meaning axis:** `axis.improvement-target-addressing` — the distinct semantic question this rule owns.

Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "addressing_role": {
      "minLength": 1,
      "type": "string"
    },
    "target_version_ref": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "target_version_ref",
    "addressing_role"
  ]
}
````

**Acceptance record**

Complete Lab definition model admission

**Original contract**

[Read the relation contract](../../../../authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/addresses-improvement-target.json)

### Contract content fingerprint

85bb6746337f42e9be2a2ee93b9971e775692592151857e542cb9e965f10228a

SHA-256 identifies the captured contents, not truth or permission.

[Return to Connection rules](../relation-kinds.md#catalog-relations)
