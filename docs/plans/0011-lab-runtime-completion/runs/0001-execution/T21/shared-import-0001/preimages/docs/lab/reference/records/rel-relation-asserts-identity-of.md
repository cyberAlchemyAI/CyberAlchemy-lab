[Documentation home](../../README.md)

# asserts-identity-of

<a id="rel-relation-asserts-identity-of"></a>

[Reference catalog](../relation-kinds.md#catalog-relations) / Exact record

# asserts-identity-of

The question this connection answers

What bounded identity correspondence is being asserted between these endpoints?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **asserts-identity-of** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** assertion_kind, claim_scope

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** identity-merge, authority-transfer, private-attribute-inference

## Read one permitted pattern

[identity-claim](endpoint-identity-claim.md#endpoint-identity-claim) **asserts-identity-of**Required: assertion_kind, claim_scope [person-reference](endpoint-person-reference.md#endpoint-person-reference)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| identity-claim | person-reference |
| person-reference | person |
| person-reference | person-reference |
| principal-reference | principal |

### Exact meaning axis, effect and qualifier contract

relation.asserts-identity-of

**Meaning axis:** `axis.identity-assertion` — the distinct semantic question this rule owns.

Records representation, identity linking, or identifier claims without merging identities or authority.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "assertion_kind": {
      "minLength": 1,
      "type": "string"
    },
    "claim_scope": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "assertion_kind",
    "claim_scope"
  ]
}
````

**Acceptance record**

Complete Lab definition model admission

**Original contract**

[Read the relation contract](../../../../authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/asserts-identity-of.json)

### Contract content fingerprint

8aac274b24af42de5dd6848292b1ee4e96f25d11224279ebb7b3f20efbd943e9

SHA-256 identifies the captured contents, not truth or permission.

[Return to this catalog](../relation-kinds.md#catalog-relations)
