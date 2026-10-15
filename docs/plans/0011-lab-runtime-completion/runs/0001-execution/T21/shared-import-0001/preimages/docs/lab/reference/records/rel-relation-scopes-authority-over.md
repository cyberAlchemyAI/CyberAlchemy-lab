[Documentation home](../../README.md)

# scopes-authority-over

<a id="rel-relation-scopes-authority-over"></a>

[Reference catalog](../relation-kinds.md#catalog-relations) / Exact record

# scopes-authority-over

The question this connection answers

What governed scope is bounded by this explicit Authority Claim or Authority Boundary?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **scopes-authority-over** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** authority_role, scope_ref

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** permission-grant, claim-authentication, effect-execution

## Read one permitted pattern

[authority-boundary](endpoint-authority-boundary.md#endpoint-authority-boundary) **scopes-authority-over**Required: authority_role, scope_ref [decision-scope](endpoint-decision-scope.md#endpoint-decision-scope)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| authority-boundary | decision-scope |
| authority-claim | decision-scope |
| authority-claim | role-assignment |

### Exact meaning axis, effect and qualifier contract

relation.scopes-authority-over

**Meaning axis:** `axis.authority-scope` — the distinct semantic question this rule owns.

Records an explicit authority subject's bounded scope without granting permission, authenticating the subject, or executing an effect.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "authority_role": {
      "minLength": 1,
      "type": "string"
    },
    "scope_ref": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "authority_role",
    "scope_ref"
  ]
}
````

**Acceptance record**

Governance relation contracts admission

**Original contract**

[Read the relation contract](../../../../authority/relation-kinds/candidates/0007-governance-transaction-extension/instances/relation-kinds/scopes-authority-over.json)

### Contract content fingerprint

d1b444063b414b3573b7da829303cde5b884bfafa57086ac1818ce0cdffd59f9

SHA-256 identifies the captured contents, not truth or permission.

[Return to this catalog](../relation-kinds.md#catalog-relations)
