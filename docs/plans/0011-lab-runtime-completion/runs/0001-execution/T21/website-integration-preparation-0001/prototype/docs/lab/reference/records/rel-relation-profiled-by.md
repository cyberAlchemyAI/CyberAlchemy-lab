[Documentation home](../../README.md)

# profiled-by

<a id="rel-relation-profiled-by"></a>

[Reference](../README.md#reference) / [Connection rules](../relation-kinds.md#catalog-relations) / profiled-by

# profiled-by

The question this connection answers

Which exact Agent Profile revision configures this Agent Instance?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **profiled-by** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** profile_version_ref, binding_ref

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** conformance, capability, authority, identity-continuity

<a id="rel-relation-profiled-by-section-1"></a>

## Read one permitted pattern

[agent-instance](endpoint-agent-instance.md#endpoint-agent-instance) **profiled-by**Required: profile_version_ref, binding_ref [agent-profile](endpoint-agent-profile.md#endpoint-agent-profile)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| agent-instance | agent-profile |

### Exact meaning axis, effect and qualifier contract

relation.profiled-by

**Meaning axis:** `axis.agent-profile-binding` — the distinct semantic question this rule owns.

Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "binding_ref": {
      "minLength": 1,
      "type": "string"
    },
    "profile_version_ref": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "profile_version_ref",
    "binding_ref"
  ]
}
````

**Acceptance record**

Complete Lab definition model admission

**Original contract**

[Read the relation contract](../../assets/ba59dbd901e2-profiled-by.json)

### Contract content fingerprint

ba59dbd901e25e3a80270ba3569afeea18fddbaef646f1780919c21e6f2c2f0a

SHA-256 identifies the captured contents, not truth or permission.

[Return to Connection rules](../relation-kinds.md#catalog-relations)
