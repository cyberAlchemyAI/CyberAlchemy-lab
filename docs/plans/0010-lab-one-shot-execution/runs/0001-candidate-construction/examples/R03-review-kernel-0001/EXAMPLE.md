# Actual candidate example: two targets, one pending checkpoint

Historical isolated raw-source preview. **20 tests and 94 independent audit checks passed.** Both fixture hosts and their keys were removed. This example has no admission or current authority.

## Proposed change

| Member | Carrier | Separate Decision | Proposed effect |
|---|---|---|---|
| 1 | `cal.artifact-type.work/v1` | `decision:R03-candidate-admit` | admit one exact Work revision after final owner authorization |
| 2 | `cal.artifact-type.user-decision-preference/v1` | `decision:R03-proposed-one-checkpoint-preference` | Admit only this exact preference for the recognized owner under the current single checkpoint profile after final owner authorization |

The first target is a Work artifact for preparing inspection evidence. The second is an explicit proposed User Decision Preference for `principal:repository-owner`; it has its own target and core. The old preference names `principal:lab-owner`, which has no matching current Principal in this source. The kernel refuses to alias the identities.

## Single checkpoint and separate voices

- One pending final-review Checkpoint for both members; all-or-nothing atomicity.
- Each member retains its own Decision identity, exact target bytes, core and proposed effect.
- Each member has two independently selected routing voices in this fixture: `role:repository-owner` and `role:definition-owner`. All four responses are pending.
- Role declarations support routing metadata. Coverage of every governing role and current owner authority is **not** verified by this preview.
- The protocol workflow reference is configuration, not a Workflow Run artifact.
- Every original semantic and operational gap is retained.

## Exact original targets

### Member 1

Original byte SHA-256: `b4657a354e037eef773cab3441cea307ee48f97f6ae2e5afb43f0db9c59b4513`

```json
{
  "authority_effect": "none",
  "challenge_route": "challenge-contract:cyberalchemy-lab-operational-foundation",
  "claim_ceiling": "Candidate Work record for building and validating the review package; completion establishes no admission or runtime activation.",
  "evidence_refs": [
    "docs/decisions/0072-project-state-bootstrap-admission/decision.json"
  ],
  "kind": "work",
  "lifecycle_state": "candidate",
  "name": "Inspect a complete candidate before its final owner decision",
  "node_id": "work:R03-exact-candidate-example",
  "owner_ref": "role:repository-owner",
  "payload": {
    "completion_state": "candidate-prepared",
    "goal_refs": [
      "goal:first-governed-agent-context"
    ],
    "input_refs": [
      "project-state:cyberalchemy-v2-to-lab-migration:decision-0071",
      "context-request:first-governed-agent-episode"
    ],
    "output_refs": [
      "candidate:first-governed-agent-context/v1",
      "receipt:first-governed-agent-context-validation"
    ],
    "project_ref": "project:cyberalchemy-v2-to-lab-migration",
    "work_statement": "Prepare exact target/core/schema evidence and inspect unresolved references before the final owner checkpoint."
  },
  "relation_refs": [
    {
      "counterpart_kind": "project",
      "counterpart_ref": "project:cyberalchemy-v2-to-lab-migration",
      "direction": "source",
      "relation_kind_ref": "relation.member-of"
    }
  ],
  "schema_version": "cyberalchemy-lab-work/v1",
  "scope_ref": "project:cyberalchemy-v2-to-lab-migration",
  "successor_refs": []
}
```

Stable Decision core:

```json
{
  "category": "artifact-instance",
  "decision_ref": "decision:R03-candidate-admit",
  "operation": "admit",
  "target_digest": "6fdcfdd39bd9d80064ac81093b6e86d9961d6d100ba5759a7f5cc822ee89c561",
  "version_ref": "work:R03-exact-candidate-example@R03-preparation-1"
}
```

### Member 2

Original byte SHA-256: `8641c04df9622938ef1397f8b96e6ec5c954f9a73571131af40b2da23af947e9`

```json
{
  "authority_effect": "none",
  "challenge_route": "route:artifact-type-challenge",
  "claim_ceiling": "Records the final-review interaction preference and supplies no admission authority by itself.",
  "evidence_refs": [],
  "kind": "user-decision-preference",
  "lifecycle_state": "candidate",
  "name": "One exact final owner checkpoint for this proposed change",
  "node_id": "user-decision-preference:R03-one-final-checkpoint",
  "owner_ref": "principal:repository-owner",
  "payload": {
    "invalidation_conditions": [
      "profile-no-longer-allows-final-review",
      "owner-withdrawal"
    ],
    "preferred_checkpoint_kind": "final-review",
    "profile_ref": "workflow-decision-profile:lab-governance-single-checkpoint",
    "scope_kind": "workflow-type",
    "scope_ref": "workflow-type:governed-repository-change",
    "status": "active",
    "user_ref": "principal:repository-owner"
  },
  "relation_refs": [
    {
      "counterpart_kind": "policy",
      "counterpart_ref": "policy:cyberalchemy-lab-operational-foundation",
      "direction": "source",
      "relation_kind_ref": "relation.governed-by"
    }
  ],
  "schema_version": "cyberalchemy-lab-user-decision-preference/v1",
  "scope_ref": "project:cyberalchemy-v2-to-lab-migration",
  "successor_refs": []
}
```

Stable Decision core:

```json
{
  "category": "artifact-instance",
  "decision_ref": "decision:R03-proposed-one-checkpoint-preference",
  "operation": "admit",
  "target_digest": "fe1ed412726faca802bc2cacdda363c23f9767a26c9f057096ea5919edac37e0",
  "version_ref": "user-decision-preference:R03-one-final-checkpoint@review.candidate.1"
}
```

## Generated carriers

### cal.artifact-type.decision-bundle/v1

Original byte SHA-256: `35514b5a6a627e856dde580caa5aabb01d40556910bc7e69699eb38164a92c99`

```json
{
  "authority_effect": "none",
  "challenge_route": "challenge-contract:cyberalchemy-lab-operational-foundation",
  "claim_ceiling": "Candidate review bytes only. Every target, gap and required owner voice is retained; no owner authorization, admission, WorkflowRun, activation or public API completion.",
  "evidence_refs": [
    "workspace-object:R03-c0516c3e22c44b11b0faf7abae1076c8:917dff5f29a077ab77fb896cf0ac54aa587d7f95f1827275f7210e316efddf36",
    "workspace-object:R03-c0516c3e22c44b11b0faf7abae1076c8:82b2dca13b131434804feee94b2f56ab31fa9b206f3be2ea463a4bcb7dfca0db",
    "candidate:work-core",
    "candidate:review-preference-core"
  ],
  "kind": "decision-bundle",
  "lifecycle_state": "candidate",
  "name": "Exact pending decision-bundle",
  "node_id": "decision-bundle:R03-exact-review:8c9e7eea4206b080fba848f701b9394a8fc5c5100476b05f2f514e68e8bf5771",
  "owner_ref": "principal:repository-owner",
  "payload": {
    "all_targets_materialized": true,
    "atomicity_requirement": "all-or-nothing",
    "bundle_digest": "50bafe70ec5134ff9b7202d9414a7cca69f271b69422c3b1c1e10abb99867611",
    "checkpoint_ref": "decision-checkpoint:R03-exact-review:8c9e7eea4206b080fba848f701b9394a8fc5c5100476b05f2f514e68e8bf5771",
    "invalidation_conditions": [
      "unmaterialized-target",
      "authority-owner-change",
      "new-external-effect",
      "profile-no-longer-allows-final-review",
      "owner-withdrawal",
      "any-target-original-byte-change",
      "source-cut-or-profile-change",
      "owner-routing-or-current-authority-change",
      "validation-or-example-change",
      "new-runtime-or-external-effect"
    ],
    "ordered_decisions": [
      {
        "decision_core_sha256": "3d04bd082e7442a1f56d4072339ec51472e18a31434b2a4aec59aba0f5967b06",
        "decision_ref": "decision:R03-candidate-admit",
        "effect_kind": "artifact-instance:admit",
        "owner_ref": "principal:repository-owner",
        "scope_ref": "project:cyberalchemy-v2-to-lab-migration",
        "selected_outcome": null,
        "target_digests": [
          {
            "sha256": "b4657a354e037eef773cab3441cea307ee48f97f6ae2e5afb43f0db9c59b4513",
            "target_ref": "work:R03-exact-candidate-example@R03-preparation-1"
          }
        ],
        "target_refs": [
          "work:R03-exact-candidate-example@R03-preparation-1"
        ]
      },
      {
        "decision_core_sha256": "f5fb36aebb27af905341c22fdba7ed66955ed91e7f41a3b3a286cd128c7624a1",
        "decision_ref": "decision:R03-proposed-one-checkpoint-preference",
        "effect_kind": "artifact-instance:admit",
        "owner_ref": "principal:repository-owner",
        "scope_ref": "project:cyberalchemy-v2-to-lab-migration",
        "selected_outcome": null,
        "target_digests": [
          {
            "sha256": "8641c04df9622938ef1397f8b96e6ec5c954f9a73571131af40b2da23af947e9",
            "target_ref": "user-decision-preference:R03-one-final-checkpoint@review.candidate.1"
          }
        ],
        "target_refs": [
          "user-decision-preference:R03-one-final-checkpoint@review.candidate.1"
        ]
      }
    ]
  },
  "relation_refs": [
    {
      "counterpart_kind": "policy",
      "counterpart_ref": "policy:cyberalchemy-lab-operational-foundation",
      "direction": "source",
      "relation_kind_ref": "relation.governed-by"
    }
  ],
  "schema_version": "cyberalchemy-lab-decision-bundle/v1",
  "scope_ref": "project:cyberalchemy-v2-to-lab-migration",
  "successor_refs": []
}
```

### cal.artifact-type.decision-checkpoint/v1

Original byte SHA-256: `de17a0a86aa5a4c58f7574f25377941f14e62f1ffbb1131a183ebd36a5c9ce7a`

```json
{
  "authority_effect": "none",
  "challenge_route": "challenge-contract:cyberalchemy-lab-operational-foundation",
  "claim_ceiling": "Candidate review bytes only. Every target, gap and required owner voice is retained; no owner authorization, admission, WorkflowRun, activation or public API completion.",
  "evidence_refs": [
    "workspace-object:R03-c0516c3e22c44b11b0faf7abae1076c8:917dff5f29a077ab77fb896cf0ac54aa587d7f95f1827275f7210e316efddf36",
    "workspace-object:R03-c0516c3e22c44b11b0faf7abae1076c8:82b2dca13b131434804feee94b2f56ab31fa9b206f3be2ea463a4bcb7dfca0db",
    "candidate:work-core",
    "candidate:review-preference-core"
  ],
  "kind": "decision-checkpoint",
  "lifecycle_state": "candidate",
  "name": "Exact pending decision-checkpoint",
  "node_id": "decision-checkpoint:R03-exact-review:8c9e7eea4206b080fba848f701b9394a8fc5c5100476b05f2f514e68e8bf5771",
  "owner_ref": "principal:repository-owner",
  "payload": {
    "checkpoint_kind": "final-review",
    "closed_at": null,
    "decision_bundle_ref": "decision-bundle:R03-exact-review:8c9e7eea4206b080fba848f701b9394a8fc5c5100476b05f2f514e68e8bf5771",
    "opened_at": "2026-10-10T00:15:02.452327+00:00",
    "presentation_state": "pending",
    "resolved_preference_ref": "user-decision-preference:R03-one-final-checkpoint@review.candidate.1",
    "workflow_instance_ref": "protocol:R03-review-workflow:62ed63f19e674eef9a1c865dedfa0db3",
    "workflow_profile_ref": "workflow-decision-profile:lab-governance-single-checkpoint@transaction.0074"
  },
  "relation_refs": [
    {
      "counterpart_kind": "policy",
      "counterpart_ref": "policy:cyberalchemy-lab-operational-foundation",
      "direction": "source",
      "relation_kind_ref": "relation.governed-by"
    }
  ],
  "schema_version": "cyberalchemy-lab-decision-checkpoint/v1",
  "scope_ref": "project:cyberalchemy-v2-to-lab-migration",
  "successor_refs": []
}
```

## Retained gaps

```json
[
  {
    "blocking_use": "candidate-semantic-use",
    "gap_ref": "gap:R03-api:a9749b5dfd9abe06",
    "owner_route": "R03/S02/R08",
    "reason": "Work Goal/input/output closure is incomplete in this exact selected cut. The missing references require selected material or a declared resolver before semantic use.",
    "subject_ref": "work:R03-exact-candidate-example@R03-preparation-1"
  },
  {
    "blocking_use": "candidate-semantic-use",
    "gap_ref": "gap:R03-api:13836d18dd84d420",
    "owner_route": "R03/S02/R08",
    "reason": "Exact schema/core checks do not close every carrier-specific domain reference obligation; semantic use remains blocked.",
    "subject_ref": "user-decision-preference:R03-one-final-checkpoint@review.candidate.1"
  },
  {
    "blocking_use": "admission",
    "gap_ref": "gap:R03-api:b1aaebc09529a1cd",
    "owner_route": "R03/S02/R08",
    "reason": "Construction evidence is staged. Final owner/operational review closure belongs to S02/R08; proposal.review is not implemented here.",
    "subject_ref": "proposal:R03-exact-work-candidate"
  }
]
```

This is a review-construction example. Public `proposal.review`, the complete S02 package, genuine pilot evidence and the actual final R08 owner response remain required.

[Exact original-byte preview](/home/vlad_/projects/CyberAlchemy-lab/docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/examples/R03-review-kernel-0001/actual-original-byte-preview.json)

[Frozen proof](/home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/interface/review-package-v2/receipts/independent-proof-0001.json)
