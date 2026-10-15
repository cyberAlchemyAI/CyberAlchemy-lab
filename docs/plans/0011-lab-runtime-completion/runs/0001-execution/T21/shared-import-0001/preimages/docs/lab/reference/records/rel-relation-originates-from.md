[Documentation home](../../README.md)

# originates-from

<a id="rel-relation-originates-from"></a>

[Reference catalog](../relation-kinds.md#catalog-relations) / Exact record

# originates-from

The question this connection answers

From which source did this identity or content originate?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **originates-from** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** origin_role

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** derivation, successor, authority-transfer

## Read one permitted pattern

[artifact-type](endpoint-artifact-type.md#endpoint-artifact-type) **originates-from**Required: origin_role [source](endpoint-source.md#endpoint-source)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| artifact-type | source |
| definition | source |
| drift-assessment | source |
| feedback-record | source |
| finding | source |
| operational-observation | source |
| relation-kind | source |

### Exact meaning axis, effect and qualifier contract

relation.originates-from

**Meaning axis:** `axis.origin-lineage` — the distinct semantic question this rule owns.

Records origin lineage without asserting transformation, succession, or authority transfer.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "origin_role": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "origin_role"
  ]
}
````

**Acceptance record**

Complete Lab definition model admission

**Original contract**

[Read the relation contract](../../../../authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/originates-from.json)

### Contract content fingerprint

1a53e04e5eac4d04c3ca1cac67292fa670ff72c7486f5fcc5f1975b741779e3b

SHA-256 identifies the captured contents, not truth or permission.

[Return to this catalog](../relation-kinds.md#catalog-relations)
