---
title: Define Integration API Implementation Layering
status: candidate
updatedAt: 2026-09-08
owner: CyberAlchemy v2 Define runtime owner
scope: capability
authority_effect: none
---

# Define Integration API Implementation Layering

## Context

- Target: stable Define Client API plus extensible Ontology Authoring Adapter Protocol.
- Current state: Define has a working fixed Definition Pack flow, compiled Alch
  semantic decisions, durable session mechanics, and ARE Module Port mechanics.
- Primary users: Define interfaces, ontology authors, and downstream Plan consumers.
- Primary constraint: extend without moving ontology meaning or route authority
  into Define core or ARE.
- Source: [DESIGN.md](DESIGN.md).

## Layering Method

Each layer ends when it unlocks one new implementation decision. Later layers
must preserve exact registration, no fallback, no authority effect, user
confirmation, deterministic receipts, and the existing Definition Pack path.

## Layer Decision Table

| Layer | Decision question | Minimum working unit | Outcome | Risk reduced | Promotion |
| --- | --- | --- | --- | --- | --- |
| L0 | After this layer, we know whether one statically registered ontology stage can run end to end without a Define-core ontology branch. | Generic Alch entries, stage registry, typed facade, and one synthetic adapter through question, answer, readiness, materialization, validation, confirmation, and export. | Implemented testable candidate. | Wrong abstraction and hidden coupling. | Exit evidence passed; eligible for owner review, not admission. |
| L1 | After this layer, we know whether CLI, chat, and tests can share one stable Define Client API. | Client facade over current durable/session runtime and Definition Pack behavior. | Implemented testable candidate. | Interface drift and confirmation bypass. | Exit evidence passed; eligible for owner review, not admission. |
| L2 | After this layer, we know whether the protocol can author one real Product Ontology candidate. | Product adapter, its `.alch` entries, exact ontology selection, and fixtures. | Implemented testable candidate. | Synthetic-only proof and misplaced product semantics. | Exit evidence passed; eligible for owner review, not admission. |
| L3 | After this layer, we know whether dependency-aware composition works for Business Ontology. | Business adapter requiring exact Product receipt and DAG validation. | Implemented testable candidate. | Dependency collapse and stale prerequisite use. | Exit evidence passed; eligible for owner review, not admission. |
| L4 | After this layer, we know whether adding another ontology and handing off to Plan requires configuration only. | Third fixture/real adapter, multiple entry points, and one Plan consumer contract test. | Implemented testable candidate. | Core-edit regressions and unusable handoffs. | Exit evidence passed; stop the in-process layer pending owner review. |

## Layer Details

### L0 — Protocol Proof

Implementation status: **testable candidate complete**.

Included:

- closed descriptor, invocation, result, readiness, artifact, and handoff schemas;
- generic `StageDependency`, `StageResponse`, `StageReadiness`, and
  `StageHandoff` Alch entries;
- immutable stage graph with exact capability bindings;
- typed facade over the existing Module Port;
- one synthetic adapter and in-memory work flow; and
- positive, missing, malformed, duplicate, cycle, effect-smuggling, replay,
  non-collapse, semantic, and orthogonality tests.

Deferred: durable migration, real Product/Business semantics, Plan integration,
discovery, hot reload, admission, release, and deployment.

Exit evidence: fresh compilation is byte-identical; L0 tests pass twice; adding
the synthetic stage changes no Define-core branch; zero-adapter Definition Pack
tests remain green.

Observed evidence on 2026-09-08:

- four Alch entries compiled through composition ontology, Craft/DomainSpec,
  executable entry projection, and service assembly;
- the generated bundle contains 115 manifest-bound files and rebuilt
  byte-identically;
- the focused eight-test suite passed twice;
- the complete Define package passed 52/52 tests; and
- hostile cases covered missing and drifted providers, duplicate/cyclic graph
  declarations, authority-bearing output, deferral, confirmation drift, and
  independent semantic/non-collapse/orthogonality failure.

### L1 — Stable Consumer Boundary

Implementation status: **testable candidate complete**.

Added scope: `createDefineClient` with start/resume/list/next/respond/inspect/
confirm/export operations; CLI and chat adapters call it; current durable
revision, idempotency, access-context, and audit guarantees remain intact.

Deferred: real ontology adapters and cross-stage dependency flow.

Exit evidence: interface parity fixtures, concurrency/replay tests, existing
conversation and durable-runtime tests, and no raw adapter invocation from a
consumer all pass. The focused suite passed twice at 8/8; the complete Define
surface passed 60/60; both Alch verifier paths regenerated byte-identically.

### L2 — Product Ontology Vertical

Implementation status: **testable candidate complete**.

Added scope: one exact Product Ontology authoring adapter, ontology-specific
Alch question/readiness/materialization entries, Definition Pack prerequisite,
candidate serialization, validation, and handoff receipt.

Deferred: Business Ontology and arbitrary graph breadth.

Exit evidence: the selected Alch Product Ontology fixture reaches a
user-confirmed candidate; missing/substituted Definition Pack evidence and
independent language-quality defects block materialization; identical inputs
reproduce bytes and receipts. Focused Product tests pass twice at 3/3, the
complete Node surface passes 63/63, and 61 generated files rebuild identically.

### L3 — Business Ontology Dependency

Implementation status: **testable candidate complete**.

Added scope: Business adapter, exact Product receipt validation, dependency
closure, stale/substituted receipt rejection, and independent branch behavior.

Deferred: untrusted adapters, remote modules, and lifecycle admission.

Exit evidence: Product then Business succeeds; missing, tampered, stale, or
wrong-provider Product evidence blocks only Business; graph and module order are
deterministic under reversed registration input; exact Product and dependency
digests survive in the Business candidate. The focused suite passed twice at
3/3, the complete Define surface passed 66/66, and the 61-file Business bundle
rebuilt byte-identically.

### L4 — Extension And Plan Handoff Proof

Implementation status: **testable candidate complete**.

Added scope: add a third ontology through adapter plus registry configuration,
support more than one declared entry point, and verify a named Plan consumer can
accept the exported receipt without reinterpreting it.

Deferred: runtime discovery, installation, effects, isolation, release, and deployment.

Exit evidence: the source-bound Define System Runtime Ontology adapter was added
through the static composition root with no L4 edits to Define core. Four stages
are selectable, the exact Product → Business → System closure is deterministic,
and omitting System leaves Product bytes unchanged. The candidate Plan consumer
accepts exact bytes and receipts without planning, implementation, or authority
effect and rejects drift or escalation. Focused tests passed twice at 3/3, the
complete Define surface passed 69/69, and the 61-file System bundle rebuilt
byte-identically. The source package itself remains `FLAG` because its DomainSpec
compiler-conformance check is `NOT_EVALUABLE`.

## Non-Regression Guardrails

- Definition Pack remains usable when the ontology adapter registry is empty.
- Semantic grounding, non-collapse, and orthogonality remain independent gates.
- User inference cannot self-confirm.
- Missing capability never becomes `false`, `not-applicable`, or an empty ontology.
- Adapter and route availability remain distinct from admission and activation.
- ARE remains a route selector and never invokes Define stages.
- No registry order, host path, or adapter exception changes portable bytes.

## Recommended Next Layer

The planned L0–L4 in-process construction surface is complete as a local
testable candidate. Stop here for owner review. Any admission, activation,
runtime discovery, untrusted adapter isolation, remote transport, or release
work is a separate objective and authority boundary.

## Open Questions

Open design decisions are owned by [DESIGN.md](DESIGN.md#open-questions).
