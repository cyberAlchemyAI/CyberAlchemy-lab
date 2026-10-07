<!-- GENERATED FILE: canonical data is record.json. -->

# Operational Lesson fixture

- Identity: `operational-lesson:example-001`
- Kind: `operational-lesson`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "applicability": "Complete model or admission reviews",
  "classification_assignment_refs": [
    "classification:lesson/procedural"
  ],
  "counterevidence_refs": [],
  "evidence_refs": [
    "audit:definition-carrier-coverage"
  ],
  "exclusions": [
    "Narrow single-type review"
  ],
  "expires_at": "owner-defined",
  "falsifier": "A comparable review uses the audit and still misses an admitted Definition.",
  "lesson_statement": "Run Definition-to-carrier coverage before calling the Artifact Type model complete.",
  "predicted_benefit": "Fewer omitted carrier families",
  "retention_policy_ref": "policy:project-learning",
  "scope_refs": [
    "project:lab-semantic-governance"
  ],
  "status": "candidate"
}
```

## Declared relation roles

- `target` on `relation.applies-lesson` with `lesson-application` `lesson-application:example-001`

## Claim ceiling

Realistic Operational Lesson example for candidate review only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
