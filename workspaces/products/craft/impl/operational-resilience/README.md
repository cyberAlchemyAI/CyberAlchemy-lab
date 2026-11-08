# Operational Resilience Generic Contracts

This directory is a candidate-local DomainSpec v2 prototype for generic operational-evidence contracts, deterministic validation, derived foundational controls, and one pure legacy-v1 replay adapter. It implements no live monitoring adapter, workload driver, infrastructure provider, canary controller, deployment transport, rollback actuator, or external write.

The prototype accepts only synthetic repository-local fixtures. A passing result means that one fixture satisfies the local contract and invariants at an explicit evaluation time. It does not mean that a service, environment, tool, profile, infrastructure plan, canary, deployment, or rollback has been validated.

## Local validation

From `projects/domainspec-v2/impl`:

```bash
npm exec -- tsc --project operational-resilience/tsconfig.json --noEmit
node --import tsx --test operational-resilience/test/operational-evidence.test.ts
node --import tsx operational-resilience/src/cli.ts validate operational-resilience/fixtures/valid/c01-c16-pass.json --at 2026-08-24T18:00:00Z
node --import tsx operational-resilience/src/cli.ts derive operational-resilience/fixtures/valid/c01-c16-pass.json --at 2026-08-24T18:00:00Z
node --import tsx operational-resilience/src/legacy-v1-cli.ts normalize operational-resilience/fixtures/legacy-v1/golden/failure-map.input.json --inventory operational-resilience/contracts/legacy-v1-source-inventory.json --at 2026-08-24T20:00:00Z
node --import tsx operational-resilience/src/eligibility-replay-cli.ts evaluate operational-resilience/fixtures/eligibility/golden/replay-request.json --inventory operational-resilience/contracts/legacy-v1-source-inventory.json
```

Every emitted receipt has `evidence_lane: "candidate-local-prototype"` and `authority_effect: "none"`.

The `derive` command evaluates C01, C05, C11, C12, C14, and C15 from the bundle's binding and observations. Supplied control states are used only for comparison. Any divergent claim makes both the derived result and the original `validate` command reject the bundle.

## Legacy-v1 replay boundary

The legacy adapter pins eleven exact v1 source shapes and their repository SHA-256 digests. It normalizes only failure-mapping rows and OTel metric declarations, and only into candidate-local `simulation` observations with zero runtime telemetry, no deployment effect, and no independent-observation claim.

Workflow telemetry, SLO and Prometheus declarations, infrastructure and deployment proposals, and the absent v1 load/canary result families are rejected with stable discriminators. The adapter performs no source discovery or I/O; the CLI is a local JSON wrapper around the pure function. A normalized result is not a complete evaluation bundle and provides no live, deployment, or production evidence.

## Evidence eligibility boundary

The eligibility gate consumes exact legacy-v1 normalization results and their pinned source inventory. The two supported legacy declaration shapes are retained as `replay-only`, receive receipts with no eligible controls and all six foundational controls ineligible, and are never placed in `runtime_admitted_observations`. The `runtime-eligible` label is reserved in the contract but unreachable in this candidate-local lane because no live evidence profile is admitted.

The gate invokes the existing foundational evaluator only after assembling the admitted set. For the legacy replay fixture that set is empty, so the exact derived states are C01 `passed`, C05 `missing`, C11 `not-run`, C12 `not-run`, C14 `passed`, and C15 `missing`. Forged claims and any live-looking, drifted, duplicated, future-dated, malformed, workflow-plane, effect-claiming, independently-observed, or non-zero-telemetry replay fail closed with no assembly and no derived result.

This closes a local evidence-laundering path; it does not admit a runtime profile or prove monitoring, load, fault, infrastructure, canary, deployment, rollback, release, or production behavior. Lifecycle reconciliation remains deferred and `authority_effect` remains `none`.

## Tool evidence profiles (candidate-local)

WP5 adds one closed, offline descriptor contract for seven tool-evidence families: telemetry, health-failure, workload, fault, canary-analysis, deployment-observation, and rollback-observation. Infrastructure-plan and compatibility families remain explicit deferred extensions and are rejected with `PROFILE_FAMILY_DEFERRED_EXTENSION`.

The pure validator consumes four exact caller-supplied UTF-8 JSON byte sequences—the profile descriptor, family inventory, attribute policy, and referent inventory—plus an explicit evaluation instant. It checks their SHA-256 bindings, duplicate JSON keys and identities, the closed JSON Pointer subset, the selected value type, required family safeguards, role-separated producer and offline normalizer referents, referenced schema bytes, expiry, controls C01–C16, proposed-only C17–C20, and the closed attribute policy. Its only output is a deterministic validation result with sorted findings, `runtime_admission: "denied"`, `referent_trust: "unverified"`, and `authority_effect: "none"`.

From `projects/domainspec-v2/impl`, validate one golden profile with:

```bash
node --import tsx operational-resilience/src/tool-evidence-profile-cli.ts validate \
  operational-resilience/fixtures/tool-evidence-profiles/golden/telemetry.json \
  --inventory operational-resilience/contracts/tool-evidence-profile-family-inventory.json \
  --attribute-policy operational-resilience/contracts/tool-evidence-profile-attribute-policy.json \
  --referents operational-resilience/fixtures/tool-evidence-profiles/referents.json \
  --at 2026-08-26T12:37:54Z
```

The CLI accepts only explicit regular local files. It performs no discovery, network access, directory traversal, live tool execution, infrastructure operation, deployment, rollback, or output-path write. Golden and hostile replay tests describe local contract behavior only; a PASS does not establish source authorship, authenticity, trust, runtime admission, observability coverage, operational readiness, release readiness, deployment success, or production truth. Lifecycle reconciliation is deferred.

## Offline tool-profile replay (candidate-local)

WP6 adds an invocation-free pure API, `replayToolEvidenceProfile`, for replaying one WP5-valid profile against one exact repository-local fixture. The caller supplies the descriptor, family inventory, attribute policy, referent inventory, WP5 result, fixture, evaluation context, and explicit evaluation time as bytes. The coordinator recomputes WP5, requires semantic equality with the supplied PASS result, selects one of exactly seven compiled registry entries, resolves the closed JSON Pointer, and emits one generic product-plane simulation observation. The selected scalar is represented only by its canonical JSON SHA-256; it is not asserted as a measured signal.

The static registry has no fallback and never interprets referent bytes as executable code. Replay uses no dynamic import, package resolution, filesystem discovery, process execution, network access, credentials, live tool, infrastructure provider, canary controller, deployment transport, or rollback actuator. Deployment- and rollback-family fixtures still produce ordinary simulation observations with `deployment_effect: false` and `independently_observed: false`.

The sibling `evaluateToolProfileEvidenceEligibility` gate preserves the legacy-v1 gate identity and contract. A successful profile replay is classified only as `replay-only`; `runtime_admitted_observations` and every receipt's `eligible_controls` remain empty. Foundational controls are derived from the empty admitted set, not from the replay observation. Any invalid input or hostile candidate rejects without a normalization observation, eligibility receipt, or derived result.

This lane proves deterministic candidate-local contract behavior only. It does not prove source authenticity, referent trust, tool execution, monitoring coverage, load behavior, fault behavior, canary analysis, infrastructure validity, deployment or rollback success, runtime admission, release readiness, or production truth. Lifecycle reconciliation remains deferred, `referent_trust` remains `unverified`, and `authority_effect` remains `none`.

## Offline replay campaigns (candidate-local)

WP7 adds the pure `composeToolEvidenceReplayCampaign` API for composing two through seven exact WP6 replay inputs and caller-supplied WP6 result bytes into one deterministic audit campaign. It recomputes every item through unchanged WP6, verifies the supplied raw SHA-256 and semantic result, rejects duplicate identities or mixed evaluation times, and sorts accepted projections independently of input order.

The campaign is not an `OperationalEvaluationBundle`: each item retains its own binding, replay-only eligibility receipt, observation, and labeled derived-result partition. The coordinator never derives one cross-binding control state. `runtime_admitted_observations` and aggregate `eligible_controls` are always empty, and any item or campaign finding rejects atomically with no partial projections.

The three golden campaigns and 25 hostile cases prove only deterministic repository-local composition over pinned offline fixtures. They do not execute or authenticate a tool, monitor a service, generate load, inject a fault, analyze a live canary, validate infrastructure, deploy or roll back anything, admit runtime evidence, reconcile lifecycle or ontology state, publish a release, or establish production readiness. Referents remain `unverified`, runtime admission remains `denied`, lifecycle reconciliation remains deferred, and `authority_effect` remains `none`.
