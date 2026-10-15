[Documentation home](../../README.md)

# requests-resolution-of

<a id="rel-relation-requests-resolution-of"></a>

[Reference](../README.md#reference) / [Connection rules](../relation-kinds.md#catalog-relations) / requests-resolution-of

# requests-resolution-of

The question this connection answers

Which exact Context version does this Context Request ask to resolve?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **requests-resolution-of** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** context_version_ref

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** resolution, context-mutation, source-authority

<a id="rel-relation-requests-resolution-of-section-1"></a>

## Read one permitted pattern

[context-request](endpoint-context-request.md#endpoint-context-request) **requests-resolution-of**Required: context_version_ref [context](endpoint-context.md#endpoint-context)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| context-request | context |

### Exact meaning axis, effect and qualifier contract

relation.requests-resolution-of

**Meaning axis:** `axis.context-resolution-request` — the distinct semantic question this rule owns.

Records a resolution request without performing resolution or mutating Context.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "context_version_ref": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "context_version_ref"
  ]
}
````

**Acceptance record**

Complete Lab definition model admission

**Original contract**

[Read the relation contract](../../assets/e59b4da66971-requests-resolution-of.json)

### Contract content fingerprint

e59b4da66971a08fa757f1a0022e8b5ed9a1972b9b2bdabf9b70843ea0c34772

SHA-256 identifies the captured contents, not truth or permission.

[Return to Connection rules](../relation-kinds.md#catalog-relations)
