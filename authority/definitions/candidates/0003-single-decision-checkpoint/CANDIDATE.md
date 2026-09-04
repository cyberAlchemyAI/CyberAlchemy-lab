<!-- GENERATED FILE: edit candidate.json and run render.py. -->

# Single Decision Checkpoint Definition Pack

> Generated from the machine-canonical candidate manifest; it has no authority effect.

- Candidate: `CAL-DEFINITION-CANDIDATE-SET-SINGLE-DECISION-CHECKPOINT-0003`
- Status: `candidate-authored-awaiting-validation-and-dependency-resolution`
- Authority effect: `none`

## Candidate Definitions

| ID | Version | Path | Digest |
| --- | --- | --- | --- |
| `cal.definition.authority-boundary` | `1.0.0-candidate.1` | `authority/definitions/candidates/0003-single-decision-checkpoint/definitions/authority-boundary/v1/definition.json` | `e6928339ebf6cbd41966e268da7eeee32d395da382522da086f98c3e2737896c` |
| `cal.definition.decision-bundle` | `1.0.0-candidate.1` | `authority/definitions/candidates/0003-single-decision-checkpoint/definitions/decision-bundle/v1/definition.json` | `85869ef815fcc81adf824ff6251bc215e0a624022aaa5c4838878835a932555d` |
| `cal.definition.decision-checkpoint` | `1.0.0-candidate.1` | `authority/definitions/candidates/0003-single-decision-checkpoint/definitions/decision-checkpoint/v1/definition.json` | `dce0f44b9efd159f7135672847ce0c8082b5b983f8ac7150f5db1564613cc06f` |
| `cal.definition.derived-refresh` | `1.0.0-candidate.1` | `authority/definitions/candidates/0003-single-decision-checkpoint/definitions/derived-refresh/v1/definition.json` | `f017c0403a46551ec8abfef4de24507a0ed42cc1b38acd54ec242683b89af171` |
| `cal.definition.representation-revision` | `1.0.0-candidate.1` | `authority/definitions/candidates/0003-single-decision-checkpoint/definitions/representation-revision/v1/definition.json` | `5bb818e70b0281dc14edcd4dade418335f50df93bc30c607823ecce5b3349850` |
| `cal.definition.semantic-epoch` | `1.0.0-candidate.1` | `authority/definitions/candidates/0003-single-decision-checkpoint/definitions/semantic-epoch/v1/definition.json` | `e138c57bf7a69f958ca966690428bde166ff9d2137f557a14e153e94028272e3` |
| `cal.definition.user-decision-preference` | `1.0.0-candidate.1` | `authority/definitions/candidates/0003-single-decision-checkpoint/definitions/user-decision-preference/v1/definition.json` | `9b557940d24ad90576944e7d1e20ee09dbddc72d3148e52ff3926a6a8f0cdd8f` |
| `cal.definition.workflow-decision-profile` | `1.0.0-candidate.1` | `authority/definitions/candidates/0003-single-decision-checkpoint/definitions/workflow-decision-profile/v1/definition.json` | `8146ff31bf5e48acb3e2026d41bafee1217ede50c7a7ccdb292600337a064f22` |

## Derived rule

```text
For every workflow instance w, its Workflow Decision Profile declares decision_mode none or single. Single mode must resolve exactly one Decision Checkpoint from the profile's allowed checkpoints using the most-specific applicable User Decision Preference or, when no preference exists, an explicit valid profile default. An invalid explicit preference blocks and never silently falls back. The checkpoint may present one closed Decision Bundle, but every decision retains its own Authority Boundary, owner, exact target, digest, effect, scope, outcome, and invalidation conditions. A later decision whose exact target does not yet exist belongs to a separate dependent workflow. Derived Refreshes require validation but no semantic decision.
```

## Classification consequence

A normative-meaning change creates a Semantic Epoch. A canonical encoding change with preserved identity, Semantic Epoch, and normative meaning creates a Representation Revision. Regeneration from unchanged canonical input is a Derived Refresh. Therefore the current CTX08 v3 and v2-to-v3 lineage candidates are identified as open classification drift, not modified by this pack.

## Evaluation posture

Collect all structure, three-voice, source-currentness, owner, projection, registry, drift, orthogonality, and hostile-fixture checks. A PASS proves candidate coherence only. Promotion remains blocked by the open Workflow dependency and then requires one exact definition-owner decision.

## Remaining gate

Resolve the exact Craft Workflow dependency, refresh validation against that source, then obtain one exact definition-owner decision bound to all eight Definition digests and the complete registry and drift postimages.

## Claim ceiling

This package is an eight-Definition candidate and derived-rule basis with authority_effect none. PASS does not admit a Definition, resolve Workflow, adopt an invariant or Constitution, create profiles or preferences, replace CTX08, authorize migration, publish, deploy, or establish stable-release state.
