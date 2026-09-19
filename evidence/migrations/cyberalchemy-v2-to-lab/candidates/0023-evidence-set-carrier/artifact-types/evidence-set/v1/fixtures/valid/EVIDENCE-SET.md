<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Evidence Set Fixture

- Identity: `EXAMPLE-RESIDUE-CHECKER-EVIDENCE-001`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

- **Artifact Type Ref**: `cal.artifact-type.evidence-set/v1`
- **Challenge Route**: `route:evidence-review-challenge`
- **Claim Ceiling**: `Exact evidence inventory and declared question coverage only; role assignments, truth, sufficiency and conclusions remain unproven.`
### Gaps

```json
[
  {
    "missing": "Independent semantic preservation evidence.",
    "next_step": "Define a semantic preservation test and obtain attributable run evidence before making a broader claim.",
    "owner_route": "route:representation-owner",
    "question_ref": "general-proof"
  }
]
```

### Members

```json
[
  {
    "binding": {
      "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0022-residue-carrier/receipts/validation.json",
      "sha256": "a3216c5c3694ebb712a42ef8fcd674ec7b444a417bba3f8767910c4aada0b94d"
    },
    "contributions": [
      {
        "question_ref": "local-checks",
        "rationale": "The bound local validation record reports PASS.",
        "role": "supporting"
      }
    ],
    "member_id": "validation"
  },
  {
    "binding": {
      "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0022-residue-carrier/README.md",
      "sha256": "9e9293595bee868af4c66b72c4786af758809c04932349875094efe5a1f46996"
    },
    "contributions": [
      {
        "question_ref": "general-proof",
        "rationale": "The documented limits explicitly exclude semantic equivalence and actual operation provenance.",
        "role": "counterevidence"
      }
    ],
    "member_id": "limitations"
  }
]
```

- **Owner Route**: `route:evidence-owner`
- **Profile**: `candidate:question-evidence-inventory/v1`
### Questions

```json
[
  {
    "question": "Does the candidate report passing its documented local validation?",
    "question_id": "local-checks"
  },
  {
    "question": "Does local validation establish general semantic preservation?",
    "question_id": "general-proof"
  }
]
```

- **Schema Version**: `cal-evidence-set-record/v1`
- **Scope Ref**: `scope:residue-checker-review`
### Source Direction

```json
{
  "canonical": "evidence-set-record.json",
  "human_projection": "EVIDENCE-SET.md",
  "projection_policy": "generated-only"
}
```


## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
