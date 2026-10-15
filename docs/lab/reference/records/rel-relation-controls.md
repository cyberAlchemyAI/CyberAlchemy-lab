[Documentation home](../../README.md)

# controls

<a id="rel-relation-controls"></a>

[Reference](../README.md#reference) / [Connection rules](../relation-kinds.md#catalog-relations) / controls

# controls

The question this connection answers

Which Failure Mode is this Failure Control Binding intended to control?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **controls** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** control_role, control_version_ref, installation_posture

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** installation, execution, effectiveness, authority

<a id="rel-relation-controls-section-1"></a>

## Read one permitted pattern

[failure-control-binding](endpoint-failure-control-binding.md#endpoint-failure-control-binding) **controls**Required: control_role, control_version_ref, installation_posture [failure-mode](endpoint-failure-mode.md#endpoint-failure-mode)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| failure-control-binding | failure-mode |

### Exact meaning axis, effect and qualifier contract

relation.controls

**Meaning axis:** `axis.failure-control` — the distinct semantic question this rule owns.

Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "control_role": {
      "minLength": 1,
      "type": "string"
    },
    "control_version_ref": {
      "minLength": 1,
      "type": "string"
    },
    "installation_posture": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "control_role",
    "control_version_ref",
    "installation_posture"
  ]
}
````

**Acceptance record**

Complete Lab definition model admission

**Original contract**

[Read the relation contract](../../../../authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/controls.json)

### Contract content fingerprint

e087b196af984506249ea52fb44872117a2c79b90e19cc82715157ec9507e0bf

SHA-256 identifies the captured contents, not truth or permission.

[Return to Connection rules](../relation-kinds.md#catalog-relations)
