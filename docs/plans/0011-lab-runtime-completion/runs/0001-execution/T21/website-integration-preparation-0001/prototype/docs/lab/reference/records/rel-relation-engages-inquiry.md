[Documentation home](../../README.md)

# engages-inquiry

<a id="rel-relation-engages-inquiry"></a>

[Reference](../README.md#reference) / [Connection rules](../relation-kinds.md#catalog-relations) / engages-inquiry

# engages-inquiry

The question this connection answers

How does this research carrier engage a Research Inquiry?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **engages-inquiry** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** inquiry_role

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** finding-acceptance, evidence-support, inquiry-completion

<a id="rel-relation-engages-inquiry-section-1"></a>

## Read one permitted pattern

[experiment-design](endpoint-experiment-design.md#endpoint-experiment-design) **engages-inquiry**Required: inquiry_role [research-inquiry](endpoint-research-inquiry.md#endpoint-research-inquiry)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| experiment-design | research-inquiry |
| experiment-run | research-inquiry |
| finding | research-inquiry |
| research-run | research-inquiry |

### Exact meaning axis, effect and qualifier contract

relation.engages-inquiry

**Meaning axis:** `axis.inquiry-engagement` — the distinct semantic question this rule owns.

Records whether an activity addresses or a Finding answers an Inquiry without converting either into the other.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "inquiry_role": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "inquiry_role"
  ]
}
````

**Acceptance record**

Complete Lab definition model admission

**Original contract**

[Read the relation contract](../../assets/080978c35ebd-engages-inquiry.json)

### Contract content fingerprint

080978c35ebdd242b3398d038db802d1031f10c1dedf3097161de7dc3910583a

SHA-256 identifies the captured contents, not truth or permission.

[Return to Connection rules](../relation-kinds.md#catalog-relations)
