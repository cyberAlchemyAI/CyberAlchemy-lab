---
title: L4 — workflow integration and proof acceptance
status: not-started
dependsOn: [L3]
---

# L4 — workflow integration and proof acceptance

**Decision question:** After this layer, we know whether maintainers can use the selected checker profiles reliably when reviewing and applying exact relation changes.

**Minimum working unit:** one candidate CLI/CI package, clean replay of an evidence bundle, and a shadow pilot covering an instance addition, an endpoint extension, a kind addition, and an inference-rule change.

## Purpose and boundary

Earlier layers establish model/checker guarantees. L4 prevents the workflow around them from misreporting those guarantees. Correct Lean theorems are insufficient if the submitted statement differs from the required one, the baseline changed, the receipt hides unresolved obligations, or application uses different bytes.

Basic proof audits already belong to L0. L4 packages them for independent submissions, exact evidence exchange, deterministic automation, and review usability. It does not require proof generation to be automated.

## Inputs and outputs

Inputs are the selected semantic/rule profiles, checker and proof modules, exact proposals, required obligations, source snapshot, provider dependencies, and selected proof-submission policy.

Outputs include candidate CLI commands, CI integration, a replayable evidence format, proof acceptance reports, currentness checks, readable review explanations, a pilot assessment, and a scoped release/review recommendation.

Candidate command names are `check-instance`, `check-extension`, `check-proof`, and `replay-evidence`. They are proposed interfaces; no current executable is claimed by this document.

## Operational flow

1. Select and capture the exact baseline and proposal.
2. Decode inputs and reject malformed/unknown profiles before theorem execution.
3. Derive the required obligation inventory independently from the supplied proof bundle.
4. Execute supported decidable checks and verify proofs/witnesses.
5. Audit assumptions, statements, dependencies, evidence method, and currentness.
6. Derive aggregate readiness from every required obligation.
7. Present causes, residual obligations, compatibility effects, and evidence references.
8. At any later authorized application boundary, recapture the selected baseline and verify the exact proposal/evidence bindings before applying.

A file path or theorem name alone is not the required statement identity. Bind the trusted statement and its referenced definitions/environment; normalization of the declaration must occur under the controlled interpretation selected by the verification pipeline.

## Proof acceptance policy

Require exact statement matching, transitive axiom auditing, dependency binding, and fresh replay according to the profile. Reject unfinished proofs and undeclared assumptions. Native evaluation changes the trusted boundary and must be explicitly allowed or replaced with proof-producing evaluation. Build arbitrary submitted Lean code only within the selected isolated environment; stronger external replay is selected when independently supplied proofs require it. [Lean proof validation](https://lean-lang.org/doc/reference/latest/ValidatingProofs/)

The author of a proof cannot satisfy a requirement by declaring the required conclusion as a new axiom. Explicit model premises may be legitimate, but must be visible in the trusted statement and cannot erase the requirement they are supposed to establish.

A stronger replay tool does not prove that the business statement was formalized correctly. Keep meaning-to-statement review as a separate responsibility. Pin versions and record the actual verification policy so results from different trust profiles are not merged as equivalent evidence.

## Evidence bundle and integration

Define the bundle as exact source bindings, normalization/profile identities, base and proposed theory/graph identities, complete obligations, proof/witness artifacts, provider/toolchain dependencies, audit results, currentness evidence, and compatibility report.

Store raw provider outcomes separately from normalized conclusions. The bundle verifier recomputes digests and completeness; it never trusts a submitted `current: true` or `all_passed: true` flag. A missing required obligation blocks aggregate readiness even when all supplied proofs are valid.

Assess existing FormalClaim, theorem request, preservation, and evidence-binding contracts. Some have fixed legacy ownership or theorem-only outcome semantics. Prefer a new explicit adapter/successor contract where needed. Do not force a bounded Alloy result into a theorem-only binding or silently rewrite historical contracts.

Cache only evidence whose complete semantic and operational dependency identities match. A graph change invalidates graph-specific checks; a rule change invalidates affected derivation/independence evidence; a checker or statement change invalidates corresponding proof acceptance. An initial full-replay policy is simpler than an unproved selective invalidation scheme.

## User and CI behavior

The review report should explain the proposed change, selected baseline, obligations satisfied, concrete violations, unresolved requirements, compatibility impact, and next actionable correction. Display a counterexample with the relevant assertions/rule steps rather than a raw solver trace alone.

CI distinguishes violated requirements from unresolved checks and provider failures. Only completed, current evidence satisfying every required obligation can yield ready-for-review under the selected profile. A timeout never becomes an approval recommendation by default.

Freshness must cover relevant registry/profile changes as well as source-file hashes. The application workflow must serialize or otherwise validate against its current authority epoch so a check of one baseline cannot authorize a different one. Exact integration depends on the selected Lab transaction mechanism and remains implementation work.

## Ordered implementation work

1. Freeze the bounded package interfaces and outcome vocabulary.
2. Implement provider execution, statement/dependency audits, and isolated proof replay.
3. Implement evidence-bundle validation and complete-obligation aggregation.
4. Add CLI explanations and CI status handling.
5. Add baseline recapture and exact application-binding checks to a candidate workflow adapter.
6. Run the shadow pilot and compare formal findings with semantic review.
7. Publish a reviewable package/evidence recommendation within the user's later authorized scope.

## Validation and acceptance

| Case | Required observable behavior |
| --- | --- |
| Proof of the wrong statement | Rejected even when it compiles |
| Transitive unfinished proof/custom assumed conclusion | Fails the selected assumption policy |
| Missing required obligation | Aggregate readiness unresolved |
| Missing provider or resource timeout | Explicit execution failure/timeout |
| Changed dependency or baseline | Evidence stale for current proposal |
| Edited proof/receipt metadata | Binding or audit failure |
| Independent conformant-and-admitted facts | Allowed with their distinct justification |
| Legitimate extension | Complete replayable evidence and readable compatibility report |
| Existing valid instances | No unintended validity regression |

Measure actual graph size, obligation count, wall time, memory where available, and proof replay cost in the pilot. These observations determine the next optimization task; no unsupported throughput or scale target is asserted here.

Completion requires clean replay, all workflow controls, the representative pilot, explained review disagreements, and an exact supported-profile inventory. The product can be ready for bounded use while unsupported profiles remain clearly excluded.

## Outcome, cost, and promotion

Maintainers receive a dependable review tool with traceable conclusions and evidence that can be replayed. Risk reduced: false readiness produced by workflow mistakes rather than mathematical reasoning. Cost is medium to high, driven by proof execution, integration contracts, and baseline continuity.

Select a bounded admission use only after reviewing pilot evidence. A recommendation to use the checker is separate from an actual admission/release decision. Preserve every earlier semantic, evidence, and currentness guarantee.

## Deferred scope

Autonomous admission, a general automatic theorem prover, distributed proof execution, unrestricted proof marketplaces, broad solver orchestration, and automatic migration of historical evidence. These are future product questions with their own acceptance evidence.
