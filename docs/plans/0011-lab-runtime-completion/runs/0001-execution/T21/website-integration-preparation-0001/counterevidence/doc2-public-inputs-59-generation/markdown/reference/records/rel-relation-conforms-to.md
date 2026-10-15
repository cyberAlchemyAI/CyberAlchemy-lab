[Documentation home](../../README.md)

# conforms-to

<a id="rel-relation-conforms-to"></a>

[Reference](../README.md#reference) / [Connection rules](../relation-kinds.md#catalog-relations) / conforms-to

# conforms-to

The question this connection answers

Which exact contract does this subject demonstrably conform to, and under which evidence?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **conforms-to** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** conformance_scope, exact_version_ref, conformance_evidence_refs

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** admission, runtime-conformance, effectiveness, authority

<a id="rel-relation-conforms-to-section-1"></a>

## Read one permitted pattern

[capability-instance](endpoint-capability-instance.md#endpoint-capability-instance) **conforms-to**Required: conformance_scope, exact_version_ref, conformance_evidence_refs [contract](endpoint-contract.md#endpoint-contract)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| capability-instance | contract |
| capability-instance | governed-model |
| context | context-profile |

### Exact meaning axis, effect and qualifier contract

relation.conforms-to

**Meaning axis:** `axis.conformance` — the distinct semantic question this rule owns.

Records scoped conformance only; it does not imply admission, implementation conformance outside scope, or runtime conformance.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "conformance_evidence_refs": {
      "minLength": 1,
      "type": "string"
    },
    "conformance_scope": {
      "minLength": 1,
      "type": "string"
    },
    "exact_version_ref": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "conformance_scope",
    "exact_version_ref",
    "conformance_evidence_refs"
  ]
}
````

**Acceptance record**

Complete Lab definition model admission

**Original contract**

[Read the relation contract](../../assets/f8da5ba839d1-conforms-to.json)

### Contract content fingerprint

f8da5ba839d1e262817d1b1bcdde5a1ee1463a52d15ce14c426c1ec707970608

SHA-256 identifies the captured contents, not truth or permission.

[Return to Connection rules](../relation-kinds.md#catalog-relations)
