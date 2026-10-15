[Documentation home](../../README.md)

# materializes-consequence

<a id="rel-relation-materializes-consequence"></a>

[Reference](../README.md#reference) / [Connection rules](../relation-kinds.md#catalog-relations) / materializes-consequence

# materializes-consequence

The question this connection answers

Which declared deterministic consequence did this Admission Transaction materialize?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **materializes-consequence** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** application_receipt_ref, consequence_role, output_digest

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** new-authorization, semantic-correctness, runtime-activation, external-effect

<a id="rel-relation-materializes-consequence-section-1"></a>

## Read one permitted pattern

[admission-transaction](endpoint-admission-transaction.md#endpoint-admission-transaction) **materializes-consequence**Required: application_receipt_ref, consequence_role, output_digest [generated-output](endpoint-generated-output.md#endpoint-generated-output)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| admission-transaction | generated-output |
| admission-transaction | project-governance-event-history |
| admission-transaction | project-semantic-event-history |
| admission-transaction | project-state |

### Exact meaning axis, effect and qualifier contract

relation.materializes-consequence

**Meaning axis:** `axis.transaction-consequence-materialization` — the distinct semantic question this rule owns.

Records a deterministic output created while atomically applying an already authorized Decision Bundle; it grants no additional authority and proves no semantic correctness.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "application_receipt_ref": {
      "minLength": 1,
      "type": "string"
    },
    "consequence_role": {
      "minLength": 1,
      "type": "string"
    },
    "output_digest": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "application_receipt_ref",
    "consequence_role",
    "output_digest"
  ]
}
````

**Acceptance record**

Governance relation contracts admission

**Original contract**

[Read the relation contract](../../../../authority/relation-kinds/candidates/0007-governance-transaction-extension/instances/relation-kinds/materializes-consequence.json)

### Contract content fingerprint

b47800d5e3d1270fea0e1a6493b8e894da13aa7ced5b986707befdaaad3e1b0c

SHA-256 identifies the captured contents, not truth or permission.

[Return to Connection rules](../relation-kinds.md#catalog-relations)
