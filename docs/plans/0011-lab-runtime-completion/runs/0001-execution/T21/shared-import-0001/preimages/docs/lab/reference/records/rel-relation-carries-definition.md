[Documentation home](../../README.md)

# carries-definition

<a id="rel-relation-carries-definition"></a>

[Reference catalog](../relation-kinds.md#catalog-relations) / Exact record

# carries-definition

The question this connection answers

Which exact Definition version supplies this Artifact Type's governed meaning?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **carries-definition** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** definition_version_ref, definition_sha256

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** admission, authority-transfer, endpoint-identity-collapse

## Read one permitted pattern

[artifact-type](endpoint-artifact-type.md#endpoint-artifact-type) **carries-definition**Required: definition_version_ref, definition_sha256 [definition](endpoint-definition.md#endpoint-definition)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| artifact-type | definition |

### Exact meaning axis, effect and qualifier contract

relation.carries-definition

**Meaning axis:** `axis.semantic-contract` — the distinct semantic question this rule owns.

Records the semantic contract without admitting either endpoint or transferring Definition authority.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "definition_sha256": {
      "minLength": 1,
      "type": "string"
    },
    "definition_version_ref": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "definition_version_ref",
    "definition_sha256"
  ]
}
````

**Acceptance record**

Complete Lab definition model admission

**Original contract**

[Read the relation contract](../../../../authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/carries-definition.json)

### Contract content fingerprint

8dff2439e99a86deed5ef3284d787082aa53f5bba51c8bd7c289b8a3bdd0cbd5

SHA-256 identifies the captured contents, not truth or permission.

[Return to this catalog](../relation-kinds.md#catalog-relations)
