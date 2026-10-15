[Documentation home](../../README.md)

# frames

<a id="rel-relation-frames"></a>

[Reference](../README.md#reference) / [Connection rules](../relation-kinds.md#catalog-relations) / frames

# frames

The question this connection answers

Which subject does this Context frame for relevance and interpretation?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **frames** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** framing_role

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** source-authority, currentness, truth

<a id="rel-relation-frames-section-1"></a>

## Read one permitted pattern

[context](endpoint-context.md#endpoint-context) **frames**Required: framing_role [bounded-context](endpoint-bounded-context.md#endpoint-bounded-context)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| context | bounded-context |
| context | goal |
| context | product |
| context | project |
| context | review |

### Exact meaning axis, effect and qualifier contract

relation.frames

**Meaning axis:** `axis.context-framing` — the distinct semantic question this rule owns.

Records Context framing, including Bounded Context reference, without making the framed subject authoritative or current.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "framing_role": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "framing_role"
  ]
}
````

**Acceptance record**

Complete Lab definition model admission

**Original contract**

[Read the relation contract](../../assets/f1e3c1b7f3a1-frames.json)

### Contract content fingerprint

f1e3c1b7f3a1bcd3e90544963398c3e5b9f3d40b9824e66692efcbbe87f06885

SHA-256 identifies the captured contents, not truth or permission.

[Return to Connection rules](../relation-kinds.md#catalog-relations)
