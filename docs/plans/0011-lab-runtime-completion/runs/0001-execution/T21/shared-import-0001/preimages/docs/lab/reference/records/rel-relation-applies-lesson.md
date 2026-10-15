[Documentation home](../../README.md)

# applies-lesson

<a id="rel-relation-applies-lesson"></a>

[Reference catalog](../relation-kinds.md#catalog-relations) / Exact record

# applies-lesson

The question this connection answers

Which exact Operational Lesson revision was used or deliberately not used by this Lesson Application?

**Acceptance status:** Accepted · selected current `(admitted-current)`.

**Read in this direction:** source → **applies-lesson** → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.

**Required extra details · qualifiers:** lesson_revision_ref, application_posture, applicability_assessment_ref, instruction_precedence

Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.

**Conclusions this link does not justify:** compliance, benefit, authority, method-use

## Read one permitted pattern

[lesson-application](endpoint-lesson-application.md#endpoint-lesson-application) **applies-lesson**Required: lesson_revision_ref, application_posture, applicability_assessment_ref, instruction_precedence [operational-lesson](endpoint-operational-lesson.md#endpoint-operational-lesson)

This is one declared ordered pair. An actual connection needs exact endpoints and the full contract, including qualifiers. The other permitted pairs are listed below.

| Source kind | Target kind |
| --- | --- |
| lesson-application | operational-lesson |

### Exact meaning axis, effect and qualifier contract

relation.applies-lesson

**Meaning axis:** `axis.lesson-application` — the distinct semantic question this rule owns.

Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.

````json
{
  "closed": true,
  "properties": {
    "applicability_assessment_ref": {
      "minLength": 1,
      "type": "string"
    },
    "application_posture": {
      "minLength": 1,
      "type": "string"
    },
    "instruction_precedence": {
      "minLength": 1,
      "type": "string"
    },
    "lesson_revision_ref": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required_axes": [
    "lesson_revision_ref",
    "application_posture",
    "applicability_assessment_ref",
    "instruction_precedence"
  ]
}
````

**Acceptance record**

Complete Lab definition model admission

**Original contract**

[Read the relation contract](../../../../authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/applies-lesson.json)

### Contract content fingerprint

c0bf14d9aeae6fecea8ea32eeae07d7b885b28d0fd9ef85d2db6112ff2990738

SHA-256 identifies the captured contents, not truth or permission.

[Return to this catalog](../relation-kinds.md#catalog-relations)
