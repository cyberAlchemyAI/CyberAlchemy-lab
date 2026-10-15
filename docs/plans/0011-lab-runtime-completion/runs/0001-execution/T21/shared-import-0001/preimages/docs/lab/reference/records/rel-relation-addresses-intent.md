[Documentation home](../../README.md)

# addresses-intent

<a id="rel-relation-addresses-intent"></a>

[Reference catalog](../relation-kinds.md#catalog-relations) / Exact record

# addresses-intent

The question this connection answers

Which exact Intent is this governed subject intended to address?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **addresses-intent** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** intent_resolution_ref, addressing_role

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** satisfaction, completion, authority, membership

## Read one permitted pattern

[agent-assignment](endpoint-agent-assignment.md#endpoint-agent-assignment) **addresses-intent**Required: intent_resolution_ref, addressing_role [intent](endpoint-intent.md#endpoint-intent)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| agent-assignment | intent |
| goal | intent |
| product | intent |
| product-capability | intent |
| project | intent |
| research-inquiry | intent |

### Exact meaning axis, effect and qualifier contract

relation.addresses-intent

**Meaning axis:** `axis.intent-addressing` — the distinct semantic question this rule owns.

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
    "intent_resolution_ref": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "intent_resolution_ref",
    "addressing_role"
  ]
}
````

**Acceptance record**

Complete Lab definition model admission

**Original contract**

[Read the relation contract](../../../../authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/addresses-intent.json)

### Contract content fingerprint

387bc793dd5199d280e5002916b2721af238d0e6f9991d426d8fa7233017ae85

SHA-256 identifies the captured contents, not truth or permission.

[Return to this catalog](../relation-kinds.md#catalog-relations)
