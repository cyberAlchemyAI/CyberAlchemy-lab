[Documentation home](../../README.md)

# inherits-contract

<a id="rel-relation-inherits-contract"></a>

[Reference](../README.md#reference) / [Connection rules](../relation-kinds.md#catalog-relations) / inherits-contract

# inherits-contract

The question this connection answers

Which exact contract obligations are inherited by this instance?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **inherits-contract** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** binding_ref, contract_version_ref

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** ownership-transfer, conformance, adoption

<a id="rel-relation-inherits-contract-section-1"></a>

## Read one permitted pattern

[capability-instance](endpoint-capability-instance.md#endpoint-capability-instance) **inherits-contract**Required: binding_ref, contract_version_ref [contract](endpoint-contract.md#endpoint-contract)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| capability-instance | contract |

### Exact meaning axis, effect and qualifier contract

relation.inherits-contract

**Meaning axis:** `axis.contract-inheritance` — the distinct semantic question this rule owns.

Records inherited obligations without transferring parent ownership or proving conformance.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "binding_ref": {
      "minLength": 1,
      "type": "string"
    },
    "contract_version_ref": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "binding_ref",
    "contract_version_ref"
  ]
}
````

**Acceptance record**

Complete Lab definition model admission

**Original contract**

[Read the relation contract](../../assets/bfa1c4ca9dbf-inherits-contract.json)

### Contract content fingerprint

bfa1c4ca9dbf8ebaea6cd1f9859a454268915b47b20bee067faed7c88e5312ee

SHA-256 identifies the captured contents, not truth or permission.

[Return to Connection rules](../relation-kinds.md#catalog-relations)
