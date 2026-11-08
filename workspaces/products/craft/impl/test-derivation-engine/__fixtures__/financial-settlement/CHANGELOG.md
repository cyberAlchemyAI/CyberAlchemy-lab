# financial-settlement — Changelog

All notable changes to the **financial-settlement** feature are documented in this file.

## 2026-04-30

### Added

- **typed postcondition guarantees** — introduced operation-level postcondition classification using State, Persistence, Temporal, Integration, and Audit guarantees.
- **PILOT-DECISIONS.md** — recorded pilot decision-gate outcomes (scope, visibility, strictness, auth, dedupe, audit, failure, decision model, and verification profile).

### Changed

- **operations postconditions formalization** — converted GenerateSettlement postconditions from bullets into ID-based guarantee rows with formal assertions.
- **integration relationship traceability** — integration guarantees now explicitly reference `produces` and `produces-for` semantics when event or cross-feature projection behavior applies.
- **SPEC and TEST-SPEC pilot provenance** — added explicit `## User Stories`, `## Story Coverage Matrix`, and pilot decision provenance references so launch policy and test gate authority are linked.

## 2026-04-24

### Changed

- **settlement error contract** — POST settlement now maps missing player to deterministic not-found response and standard validation payload shape.
- **preview response compatibility** — preview output now exposes canonical settlement fields plus projected aliases for consumer compatibility.
- **contract documentation alignment** — interfaces, operations, queries, and events were normalized to current API semantics.
- **settlement event model** — introduced canonical settlement event types and deterministic use-case emission coverage for SettlementGenerated and PayoutCreated.
- **namespace convergence** — moved settlement use-cases/tests to the canonical `backend/src/use-cases/financial-settlement/` namespace and updated route wiring.
- **settlement runtime observability** — GenerateSettlement now emits O6/O9/O15/O16 telemetry (calculation drift, idempotency/dedup + exposure, reconciliation mismatch, and settlement cycle/workflow metrics).
- **pilot blockers register** — FST-BLK-01 through FST-BLK-05 are closed with implementation and verification evidence.
- **alignment artifacts** — ALIGNMENT-REPORT and LAYERING-ALIGNMENT-REPORT were refreshed to reflect closed event/ownership gaps and remaining observability scope.
- **observability verification evidence** — OBSERVABILITY-REPORT was refreshed to FLAG with no open P0 remediation items (remaining O8/O13 hardening is non-blocking backlog).

## 2026-04-17

### Added

- **CHANGELOG.md** — initialized domain-level changelog for pilot-readiness governance and traceability.
- **states.md** — added settlement execution state machine and idempotency invariants for period side-effects.
- **ALIGNMENT-REPORT.md** — established baseline spec-to-implementation drift findings for settlement contracts.
- **LAYERING-ALIGNMENT-REPORT.md** — established baseline layering findings for settlement policy ownership.

### Changed

- **SPEC.md** — linked state-machine concept coverage and added states aspect to the capability index.
- **SPEC.md** — expanded ownership to include web maintainers for settlement dashboard governance.
- **STORIES.md** — replaced stale auth-pending note with enforced route-permission expectation.
- **history** — 2026-04-16: docs: add human-readable descriptions to all observability metrics.
- **history** — 2026-04-16: fix: move @source links outside yaml fences for markdown preview.
- **history** — 2026-04-16: docs: convert @source to markdown links across all observability specs.
- **history** — 2026-04-16: feat: OTel migration, infra governance skills, domainspec submodule update.
- **history** — 2026-04-15: refactor(observability): migrate feature metrics to OpenTelemetry conventions.
- **history** — 2026-04-15: feat: observability specs for financial-settlement (~57 metrics) and player-onboarding (~61 metrics).
