[Documentation home](../../README.md)

# fulfills-request

<a id="rel-relation-fulfills-request"></a>

[Reference catalog](../relation-kinds.md#catalog-relations) / Exact record

# fulfills-request

The question this connection answers

Which request is this immutable output intended to fulfill?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **fulfills-request** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** fulfillment_role

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** currentness, source-authority, context-mutation

## Read one permitted pattern

[context-view](endpoint-context-view.md#endpoint-context-view) **fulfills-request**Required: fulfillment_role [context-request](endpoint-context-request.md#endpoint-context-request)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| context-view | context-request |

### Exact meaning axis, effect and qualifier contract

relation.fulfills-request

**Meaning axis:** `axis.request-fulfillment` — the distinct semantic question this rule owns.

Records request fulfillment without implying that included sources or Context remain current.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "fulfillment_role": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "fulfillment_role"
  ]
}
````

**Acceptance record**

Complete Lab definition model admission

**Original contract**

[Read the relation contract](../../../../authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/fulfills-request.json)

### Contract content fingerprint

9ec53ca0ef109e7e199e53e352e21d64aceb5d4c1ef736779eea09571cbbc4dc

SHA-256 identifies the captured contents, not truth or permission.

[Return to this catalog](../relation-kinds.md#catalog-relations)
