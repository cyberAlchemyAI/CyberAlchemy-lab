[Documentation home](../../README.md)

# violates

<a id="rel-relation-violates"></a>

[Reference catalog](../relation-kinds.md#catalog-relations) / Exact record

# violates

The question this connection answers

Which exact expected boundary does evidence indicate was not satisfied?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **violates** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** boundary_version_ref, evidence_posture

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** cause, severity, authority, automatic-failure-confirmation

## Read one permitted pattern

[failure-occurrence](endpoint-failure-occurrence.md#endpoint-failure-occurrence) **violates**Required: boundary_version_ref, evidence_posture [challenge-contract](endpoint-challenge-contract.md#endpoint-challenge-contract)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| failure-occurrence | challenge-contract |
| failure-occurrence | contract |
| failure-occurrence | policy |
| failure-occurrence | schema |

### Exact meaning axis, effect and qualifier contract

relation.violates

**Meaning axis:** `axis.boundary-violation` — the distinct semantic question this rule owns.

Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "boundary_version_ref": {
      "minLength": 1,
      "type": "string"
    },
    "evidence_posture": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "boundary_version_ref",
    "evidence_posture"
  ]
}
````

**Acceptance record**

Complete Lab definition model admission

**Original contract**

[Read the relation contract](../../../../authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/violates.json)

### Contract content fingerprint

7ada5e225d79db87376b8cf34c6afc5734a11c1298979e7b05ceb86db6102dfc

SHA-256 identifies the captured contents, not truth or permission.

[Return to this catalog](../relation-kinds.md#catalog-relations)
