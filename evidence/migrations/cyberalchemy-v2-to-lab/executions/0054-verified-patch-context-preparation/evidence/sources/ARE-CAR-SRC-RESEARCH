# Coding-Agent Runtime — Decision-Ready Product and Architecture Findings

**Dispatch:** `2026-09-03-cyberalchemy-are-coding-agent-runtime`  
**Writer:** Baez, John  
**Research status:** exact-binding closure `ready`; architecture hypothesis awaiting owner decisions  
**Current conformance:** `not_evaluable`  
**Authority ceiling:** this artifact selects no architecture or dependency and grants no implementation, adoption, acceptance, publication, deployment, external-effect, security, performance, replay, cache, traceability, quality, dependency, or production-fitness claim. [ECB-003, ECB-007–012; CR-003–006, CR-010–012]

## Executive finding

The decision-ready product hypothesis is a small coding-agent loop that turns an exact, authority-bounded request into an independently verified patch candidate while keeping product meaning, reasoning state, transport, effect permission, execution, and acceptance under distinct owners. The smallest plausible path is to extend the existing CyberAlchemy-v2 and ARE candidate seams, keep Codex App Server as transport, retain mini-swe-agent only as pinned loop precedent and benchmark, and evaluate BAML only as a pinned parser benchmark. This is an architecture hypothesis, not an owner decision. [ECB-001, ECB-002, ECB-004, ECB-007, ECB-012; CR-010–012, CR-020–024]

The hypothesis survives review only in this bounded form because the repository already contains candidate mechanisms for context closure, append-only reasoning state, journaling, effect-gate adaptation, dispatch, replay, gateway transport, and continuation. Creating a new coordinator, result ledger, or sandbox owner is unsupported until an owner map proves a missing obligation and rules out duplication. [ECB-002, ECB-012; CR-021–023]

Current evidence does not show that the candidate is fast, safe, durable, authenticated, exactly-once, traceability-preserving, conformant, or production-ready. The only local latency measurement is historical, the App Server canary lacks the distributions needed for fitness claims, 15 acceptance-bound wrapper digests have drifted, BAML's modular seam lacks a pinned `0.225.0` source binding, and the four-way benchmark has not run. [ECB-003, ECB-007, ECB-008, ECB-010, ECB-011; CR-003–006]

## Evidence vocabulary and immutable selectors

- `L-ARE-README`: `cyberAlchemy-v2/development/agent-reasoning-engine/README.md:6-140`, SHA-256 `5434e26b5cf8edee325d89f67da99ed6b9351f6130684bb1c58c94344698f3e0`. [ECB-001]
- `L-ARE-ARCH`: `cyberAlchemy-v2/development/agent-reasoning-engine/design/ARCHITECTURE.md:46-162`, SHA-256 `1958758a104c19af9966fd1460097c18fbf919e480da45e5c8dcc0b5f4ffe0de`. [ECB-001, ECB-012]
- `L-CONTEXT`: `context-basis-runtime/src/context-envelope.mjs:41-243`, SHA-256 `93c98f5451946420fee121053e9861e79ff2e2596256ea2d4b3794b28c40f81e`. [ECB-002]
- `L-LIFECYCLE`: `context-basis-runtime/src/lifecycle.mjs:14-35`, SHA-256 `f9d2fbc104653fee51eb007ff27189631d1855f8dc09c4cc70a633069ff5b13e`. [CR-003]
- `L-STATE`: `reasoning-state-runtime/index.mjs:94-135,207-316,543-806`, SHA-256 `22d9e2705782df56cf922edb4bda3893609ea10bae003a6c67c218679e22ccd0`. [ECB-002]
- `L-JOURNAL`: `runtime-journal/index.mjs:94-268`, SHA-256 `e74998467cac6dd04b462d58b73ae98c55ac5412dc7c901d5c06686e92666b37`. [CR-021, CR-022]
- `L-GATEWAY`: `codex-app-server-wrapper/src/gateway.mjs:51-290`, SHA-256 `6ea479d604a4664afab1bcaee76d39249b9052fe197e02c15f58705c8e8532d1`. [ECB-002, ECB-008, ECB-009]
- `L-RPC`: `codex-app-server-wrapper/src/rpc-client.mjs:180-235`, SHA-256 `9e505e5d7340c2ab6eb931763f307307d6665a57d00280900ba407fe0d6c3ea8`. [ECB-008, ECB-009]
- `L-CONTINUE`: `codex-app-server-wrapper/src/continuation.mjs:68-145`, SHA-256 `a13910408b1875e0725e1cf7beda739ba27ab73e5554f36c7fb74f0952779368`. [ECB-002]
- `L-ASSESS`: `reasoning-state-runtime/evidence/implementation-recovery-conformance-assessment.candidate.json`, SHA-256 `30a4f2e506557743bb55f46e09c8c9870d434ede7f9d0cf72e28610215d44382`. [ECB-003]
- `L-CANARY`: `codex-integration/receipts/2026-09-01-live-app-server-canary-v2-final.json`, SHA-256 `1c93f930be47bc8e4eafd0ac637742a4a63619825a68898da7bb8b782759530f`. [ECB-003, ECB-010]
- `L-BINDING`: `codex-integration/implementation-binding.v2.json`, SHA-256 `e0efea7a88a2c369ede8cce08f9337039b94a6ae44419ca53959e80d7e55cbaf`. [ECB-003]
- `E-MINI`: [`SWE-agent/mini-swe-agent@a83fcae82d2a08f0ee0c688f9d137b3566c097f8`](https://github.com/SWE-agent/mini-swe-agent/tree/a83fcae82d2a08f0ee0c688f9d137b3566c097f8), release `v2.4.6`; exact selectors include [`default.py:88-190`](https://github.com/SWE-agent/mini-swe-agent/blob/a83fcae82d2a08f0ee0c688f9d137b3566c097f8/src/minisweagent/agents/default.py#L88-L190), [`__init__.py:43-80`](https://github.com/SWE-agent/mini-swe-agent/blob/a83fcae82d2a08f0ee0c688f9d137b3566c097f8/src/minisweagent/__init__.py#L43-L80), [`local.py:24-30,72-92`](https://github.com/SWE-agent/mini-swe-agent/blob/a83fcae82d2a08f0ee0c688f9d137b3566c097f8/src/minisweagent/environments/local.py#L24-L92), and [`interactive.py:124-181`](https://github.com/SWE-agent/mini-swe-agent/blob/a83fcae82d2a08f0ee0c688f9d137b3566c097f8/src/minisweagent/agents/interactive.py#L124-L181). [ECB-004]
- `E-MINI-BENCH`: [`SWE-bench/swe-bench.github.io@193160a463a435d05cf44a1fa9dc5eac832113c3`, `data/leaderboards.json`](https://raw.githubusercontent.com/SWE-bench/swe-bench.github.io/193160a463a435d05cf44a1fa9dc5eac832113c3/data/leaderboards.json), mini-swe-agent `2.0.0` row only. [ECB-005]
- `E-BAML`: [`BoundaryML/baml@da2a673b52dceea8bc592462ab3b0ba2d965f65e`](https://github.com/BoundaryML/baml/tree/da2a673b52dceea8bc592462ab3b0ba2d965f65e), BAML v0 `0.225.0`; exact selectors include [`engine/Cargo.toml:1-26,191-196`](https://github.com/BoundaryML/baml/blob/da2a673b52dceea8bc592462ab3b0ba2d965f65e/engine/Cargo.toml#L191-L196), [`generator.rs:13-37`](https://github.com/BoundaryML/baml/blob/da2a673b52dceea8bc592462ab3b0ba2d965f65e/engine/baml-lib/baml-types/src/generator.rs#L13-L37), [`jsonish/README.md:5-24`](https://github.com/BoundaryML/baml/blob/da2a673b52dceea8bc592462ab3b0ba2d965f65e/engine/baml-lib/jsonish/README.md#L5-L24), [`retry_policy.rs:31-60`](https://github.com/BoundaryML/baml/blob/da2a673b52dceea8bc592462ab3b0ba2d965f65e/engine/baml-runtime/src/internal/llm_client/retry_policy.rs#L31-L60), [`fallback.rs:68-94`](https://github.com/BoundaryML/baml/blob/da2a673b52dceea8bc592462ab3b0ba2d965f65e/engine/baml-runtime/src/internal/llm_client/strategy/fallback.rs#L68-L94), [`events.rs:15-33,100-164`](https://github.com/BoundaryML/baml/blob/da2a673b52dceea8bc592462ab3b0ba2d965f65e/engine/baml-lib/baml-types/src/tracing/events.rs#L15-L33), and [`storage.rs:31-51,76-93`](https://github.com/BoundaryML/baml/blob/da2a673b52dceea8bc592462ab3b0ba2d965f65e/engine/baml-runtime/src/tracingv2/storage/storage.rs#L31-L51). [ECB-006]
- `E-BAML-NIGHTLY`: BAML Language nightly `baml-language-0.18.1-nightly.20260902.a`, commit `ceccb6f91047270a82500a2905444c975005fc4b`; it is a separate unstable line and is not the candidate seam. [CR-085]

`L-*` and `E-*` identify exact source evidence. `CR-*` identifies the reconciled claim in `synthesis-revised.md`; `ECB-*` identifies the final closure disposition in `evidence-closure.md`. Architectural inferences and design candidates remain non-authoritative even when their evidence bindings are exact. [ECB-001–012]

## Product thesis

The product to evaluate is not a new autonomous agent framework. It is a thin, inspectable coding loop that composes existing owners so a person can submit a bounded change request, see rapid model progress, approve exact effects, reconnect without inventing semantic state, and receive a patch candidate whose base, postimage, checks, residue, and causal receipts can be independently inspected. [ECB-001, ECB-002, ECB-009, ECB-012; CR-010–012, CR-020–024, CR-050]

Its irreducible relation is:

```text
query -> propose -> authority decision -> runtime approval
      -> execute -> observe -> append -> continue
```

Mini-swe-agent `v2.4.6` demonstrates this relation in source through `run`, `step`, `query`, and `execute_actions`; it does not demonstrate that its messages, shell actions, retries, environment, persistence, or completion semantics are suitable here. [E-MINI `default.py:88-190`; ECB-004; CR-011]

The differentiating product proposition is owned composition: CyberAlchemy-v2 retains meaning and effect authority; ARE retains explicit context/reasoning state, provenance, receipts, and continuation constraints; App Server remains transport; a selected execution mechanism enforces an already-decided capability; and independent verification remains distinct from runtime success and owner acceptance. [L-ARE-README; L-ARE-ARCH; ECB-001, ECB-009; CR-020–024, CR-050, CR-070–073]

## User-experience target

The target interaction is a fast local session whose visible states correspond to durable candidate facts rather than optimistic UI inference. The user should see request authentication/routing, context lock, model streaming, action proposal, authority decision, runtime approval, effect progress, authenticated result, verification, and terminal `BLOCKED`, `COMPLETE`, or exactly one eligible-successor state. Partial output is display-only and cannot authorize a tool, checkpoint state, or imply completion. [ECB-009; CR-024, CR-030, CR-063]

The default interaction mode is hypothesized as `approve-each` for the first slice, with `observe` and later `approve-bounded-batch` available only as capability-bound, default-deny modes. Separately owner-authorized autonomy remains a future decision; regex whitelists and “yolo” are killed. [CR-072, CR-100, CR-110–117]

Reconnect should restore delivery to the same semantic frontier without treating an App Server transcript as ARE state. It must either resume from a persisted acknowledgement cursor under a credential bound to consumer, lane, epoch, expiry, and nonce, or stop with `DELIVERY_AMBIGUOUS`; the current same-process gateway does not yet provide authenticated durable reconnect. [L-GATEWAY; L-RPC; ECB-008, ECB-009; CR-022, CR-023, CR-063]

“Fast” is a test target, not present product copy. The candidate target is low synchronous overhead before `turn/start`, rapid first feedback, and measured p50/p95/p99/p99.9/max tails without weakening exact dependency checks, effect order, durable evidence, or independent postimage verification. Current Ferrari/slick, safety, traceability, and performance-fitness claims are killed. [ECB-010, ECB-011; CR-005, CR-075, CR-080–085]

## Reusable CyberAlchemy-v2 and ARE assets

| Existing asset | Evidence-backed reuse posture | Required closure before stronger claim |
|---|---|---|
| CyberAlchemy-v2 meaning, routing, definitions, ontology status, and effect authority | Preserve current owner; consume exact records/selectors/digests only. [L-ARE-README; L-ARE-ARCH; ECB-001; CR-020] | No coding-loop or runtime surface may promote, admit, or replace this authority. [ECB-001; CR-020] |
| ARE Context Envelope and selected-dependency closure | Build from owned / extend-owned candidate. [L-CONTEXT; L-LIFECYCLE; ECB-002; CR-021] | Prove exact-current-byte conformance and cache invalidation; do not scan unrelated ontology on the hot path. [ECB-003, ECB-010; CR-003, CR-040–042] |
| ARE Reasoning State, epochs, frontiers, checkpoints, and replay | Build from owned / extend-owned candidate. [L-STATE; ECB-002; CR-021] | Close cross-process locking, branches, multi-writer safety, compaction, distributed durability, and authenticated results. [CR-021, CR-022, CR-050, CR-060–063] |
| ARE actor/runtime journal | Reconcile before extension. [L-JOURNAL; L-ARE-ARCH; CR-021, CR-022] | Merge causal facts into the existing owner or prove non-overlap; no second authoritative event/result ledger. [ECB-012; CR-022] |
| ARE effect-gate adapter, future dispatcher, and idempotent-attempt receipt seams | Map and extend only if the missing coding/effect obligations are proven. [L-ARE-ARCH; ECB-012; CR-021, CR-022] | Prove whether atomic effect/result evidence belongs here or in a separately bounded participating-kernel store. [ECB-012; CR-060–062] |
| ARE gateway/RPC and persistent per-consumer session | Build from owned / extend-owned transport candidate. [L-GATEWAY; L-RPC; ECB-002; CR-021–023] | Default-deny authentication, durable sequences/cursors/acks, cross-process reconciliation, and ambiguous-outcome handling. [ECB-008, ECB-009; CR-063] |
| ARE receipt-bound dual-lane continuation | Build from owned / extend-owned candidate. [L-CONTINUE; ECB-002; CR-021] | Close exactly-once delivery contract, acknowledgements, and branch/fork/merge semantics. [CR-021, CR-063] |
| Existing semantic receipt binding | Preserve identities outside any model parser. [L-ARE-README; L-STATE; CR-050] | A typed boundary must prove raw-byte capture and lossless identity/receipt projection. [ECB-007; CR-085] |

These are owned candidates, not dependencies “adopted” by this research and not currently conformant components. Fifteen wrapper-file digests differ from the historical binding, so the historical test/canary receipts cannot establish current-byte behavior. [ECB-002, ECB-003; CR-003; Lakatos REPAIR]

## Exact mini-swe-agent findings

At pinned release `v2.4.6` / commit `a83fcae82d2a08f0ee0c688f9d137b3566c097f8`, mini-swe-agent implements a compact loop over replaceable duck-typed `Model`, `Environment`, and `Agent` protocols. Its useful precedent is the coordinator topology and its explicit limit/error/timeout behavior, not its state or authority model. [E-MINI `default.py:88-190`, `__init__.py:43-80`, `local.py:72-92`; ECB-004]

Its mutable provider-shaped message list, whole-file trajectory rewrite, lack of run-level resume, arbitrary bash-string action, provider retry loop, raw local shell, incompletely constrained containers, unsigned observations, and non-atomic multi-action execution are incompatible with the hypothesized ownership and failure boundaries. A crash after effect execution but before append/save can duplicate an effect. [E-MINI `default.py:88-190`, `local.py:24-30,72-92`, `interactive.py:124-181`; ECB-004, ECB-009; research.md §§Required replacements, Security findings]

The exact official leaderboard artifact records a 76.8% result over 500 SWE-bench Verified instances, 32.896 average calls, and `$0.7539` average cost for mini-swe-agent `2.0.0` with Claude 4.5 Opus high. It does not establish `v2.4.6` quality, startup speed, latency, security, or suitability for this runtime. [E-MINI-BENCH; ECB-005; CR-004]

Disposition: retain the four-stage loop as precedent, adapt explicit limit/failure events into ARE-owned typed records, benchmark the exact `v2.4.6` runtime, and reject a wholesale fork, library dependency, authoritative mini-swe trajectory, production environment policy, built-in provider transport/retry, or novelty claim. [ECB-004, ECB-010; CR-110–117]

## Exact BAML findings

Pinned BAML v0 `0.225.0` / commit `da2a673b52dceea8bc592462ab3b0ba2d965f65e` supplies a compiler, generated clients, schema-aligned JSONish parsing, structured streaming, retry/fallback machinery, test surfaces, and ephemeral tracing. These source facts are bound, but they prove neither truth of parsed content nor integration fitness. [E-BAML exact selectors; ECB-006]

BAML’s forgiving coercion may be useful against malformed model syntax, while its generated types may provide a narrow candidate-payload boundary. ARE identities, request/state/schema/provider/version digests, exact request bytes, raw response/SSE bytes, and parse receipts must remain in an outer envelope; model echoes, BAML call IDs, and ephemeral collector records are not authority or durable receipts. [E-BAML `jsonish/README.md:5-24`, `events.rs:15-33,100-164`, `storage.rs:31-51,76-93`; ECB-006, ECB-007; CR-022–024, CR-050]

The desired modular `request` / `parse` seam is documented only in live, unversioned documentation rather than at an exact `0.225.0` implementation selector. There is no applicable local cold-start or per-call distribution, and the pinned release commit records provider-dependent integration failures and collector cleanup errors. Therefore BAML remains benchmark-only pending pinned-source API proof, generated-artifact and transitive-lock closure, license notices, raw-byte capture, complete attempt/failure projection, partial-effect exclusion, replay mutants, and predeclared latency/quality margins. [ECB-007; CR-085; Lakatos REPAIR; Popper BLOCK]

Reject from the primary path BAML-owned provider transport, retry/fallback orchestration, collector-as-ledger, preview HTTP deployment, and the separate BAML Language nightly. None may duplicate App Server transport, ARE state, authority, receipts, or loop ownership. [E-BAML `retry_policy.rs:31-60`, `fallback.rs:68-94`, `storage.rs:31-51,76-93`; ECB-006, ECB-007; CR-022, CR-085, CR-110–117]

## Adopt / adapt / benchmark / reject matrix

| Subject | Disposition | Exact decision boundary |
|---|---|---|
| CyberAlchemy-v2 authority owners | **Preserve, not adopt** | They remain the source of meaning and effect authority; runtime consumers cannot promote or substitute. [ECB-001; CR-020] |
| ARE context, reasoning state, gateway, continuation | **Build from owned / extend-owned candidate** | Exact-current-byte conformance is deferred; close named durability, auth, branch, and replay obligations before stronger claims. [ECB-002, ECB-003; CR-021] |
| ARE journal/effect/dispatcher seams | **Reconcile/map before extension** | Extend or merge only after proving the missing obligation and ruling out duplicate causal ownership. [ECB-012; CR-022] |
| mini-swe query/propose/execute/observe topology | **Adapt pattern only** | Re-express transitions and failures as ARE-owned typed events. [ECB-004; CR-011] |
| mini-swe `v2.4.6` | **Benchmark only** | Exact pinned behavioral/latency comparator; no production adoption. [ECB-004; CR-080] |
| mini-swe state, persistence, retry, environments, completion markers | **Reject** | They cannot own state, transport, authority, sandbox, or correctness. [ECB-004, ECB-009; CR-110–117] |
| BAML v0 generated/schema/parser surface | **Benchmark only** | No selection until pinned modular-API source proof and all closure fixtures pass. [ECB-006, ECB-007; CR-085] |
| BAML high-level transport, retries/fallbacks, collector ledger, HTTP | **Reject from primary path** | They duplicate transport, hide attempts, or create a second state/process surface. [ECB-006, ECB-007; CR-110–117] |
| BAML Language nightly | **Reject/defer** | Separate unstable product line; no compatibility evidence. [CR-085] |
| New coordinator, result ledger, or sandbox owner | **Deferred / unsupported pending owner map** | No exact size or necessity proof; no owner decision. [ECB-012; CR-022] |
| “Ferrari,” current safety, traceability, cache, security, performance, production fitness | **Killed as present claims** | May re-enter only as separately witnessed benchmark or governance outcomes. [ECB-010; CR-005, CR-075–085] |

## Ownership and trust boundaries

| Boundary | Owner or candidate owner | Trusted input | Output status |
|---|---|---|---|
| Meaning, definitions, routing, ontology status, effect authority | CyberAlchemy-v2 owners | Exact owner records/selectors/digests | Authority decision; not replaceable by model/runtime. [ECB-001; CR-020] |
| Context selection, reasoning frontier, semantic reduction, provenance, receipts, continuation constraints | ARE | Exact owner records plus authenticated runtime facts | Inspectable candidate state; never hidden chain-of-thought. [L-ARE-README; L-STATE; ECB-001, ECB-002] |
| Model request/turn streaming and reconnect delivery | Codex App Server plus ARE wrapper | Authenticated, exact transport envelope | Transport events only; no semantic or lifecycle authority. [L-GATEWAY; L-RPC; CR-023, CR-063] |
| Candidate parsing | Direct parser baseline; BAML only if selected after benchmark | Captured raw bytes plus pinned parser/schema | Untrusted typed candidate; no effect from partials. [ECB-006, ECB-007; CR-024, CR-085] |
| Runtime approval | Codex permission mechanism constrained by CyberAlchemy capability | Immutable action and capability digest | Execution permission, not product authority or correctness. [ECB-001, ECB-009; CR-050] |
| Effect enforcement | Existing mapped effect/dispatcher seam or owner-selected participating kernel | Capability-bound action | Authenticated result or typed ambiguity; ownership unselected. [ECB-009, ECB-012; CR-060–073] |
| Verification | Independent verifier | Exact base/post trees, allowlist, receipts, validation environment | Verification evidence only; cannot fill owner acceptance. [CR-050, CR-073] |
| Acceptance | Human/product owner | Immutable candidate digest plus complete evidence | Separate future decision; never inferred here. [CR-050; final claim ceiling] |

Trust does not flow from parse success, model identity, partial output, tool syntax, UI mode, exit zero, patch creation, test PASS, replay, cache hit, or completion text. Each remains a candidate fact until the named owner and evidence boundary resolves it. [CR-024, CR-041, CR-050, CR-073, CR-110–117]

## Minimal runtime state machine

```text
RECEIVED -> AUTHENTICATED -> ROUTED -> CONTEXT_LOCKED
 -> PREFLIGHT_RECORDED -> TURN_STREAMING -> FINAL_BYTES_CAPTURED
 -> CANDIDATE_PARSED -> CANDIDATE_VALIDATED -> ACTION_PROPOSED
 -> EFFECT_AUTHORITY_DECIDED -> AWAITING_RUNTIME_APPROVAL
 -> CAPABILITY_APPROVED -> INTENT_DURABLE -> EFFECT_RUNNING
 -> RESULT_AUTHENTICATED -> OBSERVATION_DURABLE -> POSTIMAGE_VERIFIED
 -> PATCH_CANDIDATE -> CHECKPOINTED -> COMPLETION_CANDIDATE
 -> BLOCKED | COMPLETE | one ELIGIBLE_SUCCESSOR
```

This state machine is a design candidate. It explicitly orders effect authority before constrained runtime approval and runtime approval before effect execution; it repairs the historical canary’s ambiguous `effect_before_approval` field by requiring separate assertions for `effect_decision_before_runtime_approval` and `runtime_approval_before_effect_execution`. [ECB-009; CR-006, CR-030]

Typed terminal or blocking failures include `AUTHN_FAILED`, `AUTHZ_STALE`, `DELIVERY_AMBIGUOUS`, `EFFECT_AMBIGUOUS`, `PROVENANCE_UNVERIFIED`, `CACHE_INVALID`, `DEPENDENCY_DRIFT`, `SANDBOX_ESCAPE_ATTEMPT`, `RESULT_UNTRUSTED`, `PARTIAL_STREAM_TERMINATED`, `DURABILITY_FAILED`, `SCHEMA_INVALID`, `CAPABILITY_DENIED`, `LIMIT_EXCEEDED`, and `POSTIMAGE_MISMATCH`. Timeout, overload, telemetry loss, durability uncertainty, incomplete recovery, or a real effectful failure defaults to no further effect. Replay performs no model call or effect. [ECB-009; CR-030, CR-061–063, CR-070–073]

## Component and data-flow hypothesis

```text
CyberAlchemy-v2 exact authority records
  -> ARE selected-dependency closure + Context Envelope
  -> ARE Reasoning State frontier
  -> persistent per-consumer Codex App Server transport
  -> raw response/SSE capture
  -> [direct parser baseline | BAML 0.225.0 benchmark parser]
  -> strict local candidate validation
  -> CyberAlchemy-v2 effect-authority decision
  -> immutable capability-bound runtime approval
  -> existing mapped effect-gate / future-dispatcher seam
  -> owner-selected participating execution mechanism
  -> kernel-authenticated result
  -> ARE observation/checkpoint/completion candidate
  -> independent exact-postimage verifier
  -> BLOCKED | COMPLETE | one eligible successor
```

The diagram binds no BAML integration and no new coordinator, result ledger, or sandbox component. Each bracketed or owner-selected component is contingent on the owner decisions below and on a `mechanism -> existing owner/store -> missing obligation -> duplicate ruled out` proof. [ECB-007, ECB-012; CR-012, CR-022]

Before `turn/start`, the candidate hot path should contain only a verified compiled route/profile, exact selected-dependency digest/freshness check, immutable Context Envelope projection, one preflight append, and forwarding through an already-running per-consumer gateway. Semantic evaluation, continuation derivation, frontier sealing, and risk-aligned durable checkpointing occur after completion and before any successor or effect. This is a design hypothesis whose latency and traceability consequences remain unmeasured. [L-CONTEXT; L-STATE; L-GATEWAY; ECB-010; CR-010, CR-040–042]

## Event and receipt model

Every authoritative candidate event must bind schema ID/version, run, branch, runtime epoch, durable sequence, parent and state digests, monotonic time, producer identity/signature, and provenance. Delivered transport events additionally require a durable sequence/digest and persisted acknowledgement. [ECB-009; CR-050, CR-063]

The minimum causal event vocabulary is `ModelRequested`, `ModelChunk`, `FinalBytesCaptured`, `ActionProposed`, `EffectAuthorityDecided`, `ApprovalBound`, `ActionStarted`, `ResultAuthenticated`, `ObservationRecorded`, `PostimageVerified`, `Checkpoint`, `CompletionCandidate`, and typed failure events. `ModelChunk` and BAML partials are UX projections only. [ECB-009; CR-024, CR-030, CR-050]

Candidate action identity is domain-separated and canonical:

```text
action_id = H(
  domain = "ca2-action-v1",
  run, branch, parent_state, base_tree, target,
  operation, canonical_arguments,
  tool_digest, runtime_digest, sandbox_digest,
  authority_capability_digest
)
```

This formula is a design requirement, not an implemented identity guarantee. [ECB-009; CR-050]

An immutable approval capability binds authenticated subject, issuer and delegation, operations/resources, limits, tool/runtime/sandbox digests, monotonic bounds, nonce, revocation epoch, usage semantics, action identity, and signature. Any drift yields `AUTHZ_STALE`. Runtime approval cannot widen that capability. [ECB-009; CR-050]

A tool result must be authenticated by the execution mechanism and bind attempt identity, sandbox identity, monotonic times, exit/output/artifact/resource digests, and result-commit identity. An observation derives only from this authenticated result; a model-produced summary remains untrusted. [ECB-009; CR-050]

A completion receipt binds exact base and post trees, allowlisted changes, patch digest, independent validation receipts and environment, residue, blockers, budgets, continuation, and a distinct owner-acceptance field. Runtime or verifier success must leave owner acceptance empty until a separate immutable decision fills it. [CR-050, CR-073]

## Safe tool and effect path

One action is proposed and canonically identified before authority or execution. CyberAlchemy-v2 decides the permitted effect envelope; the runtime approval mechanism checks that immutable capability; the enforcement mechanism executes only within it; the authenticated result is durably correlated before observation; and an independent verifier rehashes the exact postimage before a patch candidate can advance. [ECB-001, ECB-009; CR-050, CR-060–073]

Exactly-once is a permitted claim only for an effect class whose participating kernel atomically commits the effect and authenticated terminal result under one idempotency transaction and returns the committed result for duplicate keys. Other effects are at-most-once dispatch: recovery must return a committed result, authenticate a kernel-known result, or block `EFFECT_AMBIGUOUS`; it must never blindly retry an ambiguous effect. This remains an unwitnessed design requirement. [ECB-009; residue `participating_kernel_atomic_effect_result_not_witnessed`; CR-060–062]

Candidate sandbox enforcement uses descriptor-relative, no-follow access under preopened allowlisted roots; closed inherited descriptors and environment; contained descendants; pinned executable/runtime/rootfs/sandbox digests; dropped capabilities; resource limits; default-deny egress; scoped secret handles; and fail-closed telemetry/enforcement behavior. The enforcement owner is not selected and no security property is established. [ECB-009, ECB-012; CR-070]

Multi-action output decomposes into separate capability-bound actions. The first real effectful failure blocks every successor; no transaction, rollback, compensation, or correctness is implied. [CR-071]

## App Server and reconnect model

Codex App Server remains a transport candidate, not a state, authority, continuation, or acceptance owner. A persistent gateway should be per consumer and per lane; sharing one upstream session across plan and human lanes is rejected because it conflates delivery and authority contexts. [L-GATEWAY; L-RPC; CR-021–023, CR-063, CR-110–117]

Reconnect is default-deny. The candidate credential binds session, consumer, lane, runtime epoch, monotonic expiry, nonce, and acknowledgement cursor; each event sequence/digest and acknowledgement is persisted. A missing credential, stale epoch, forged consumer/lane, cursor gap, unacknowledged ambiguous delivery, or cross-process mismatch yields `AUTHN_FAILED`, `AUTHZ_STALE`, or `DELIVERY_AMBIGUOUS`, with no inferred continuation or effect. [ECB-008, ECB-009; CR-030, CR-063]

The current gateway preserves only same-process in-memory session state and has no witnessed authenticated durable reconnect or exactly-once delivery. The present capability claim is killed; reconnect remains a design and benchmark target. [L-GATEWAY; L-RPC; ECB-008, ECB-010]

## Speed, stable-prefix, and cache plan

Stable material is hypothesized to include route/profile, definition closure, selected ontology/source records, repository policy, system/tool/action/result schemas, canonicalizer, compiler/generator/runtime and transitive-lock digests, provider/model/options, and compact task digests. Volatile material includes the frontier, current user message, observations, diff/postimage, budgets, approval, and result. [CR-040]

Cache keys must domain-separate every stable identity above. Missing, stale, or mismatched members yield `CACHE_INVALID`; no cache hit can prove authority, approval, currentness, effect success, conformance, or acceptance. Provider prompt-cache behavior is an optimization signal only. [ECB-009, ECB-010; CR-041]

Measurements must record stable/volatile/cached/uncached tokens, output and reasoning tokens, exact request/response bytes, first differing prefix byte, invalidation reason, call and cost, timing partitions, parser variant, patch/result digest, and focused-check outcome. Warm and cold semantic equivalence must be independently checked under invalidation mutants. [ECB-010, ECB-011; CR-042, CR-080–085]

Proposed thresholds are experiment thresholds only:

| Surface | p50 | p95 | Required tails |
|---|---:|---:|---|
| Route/profile | 5 ms | 15 ms | p99, p99.9, max |
| Warm context | 25 ms | 100 ms | p99, p99.9, max |
| First feedback | 150 ms | 500 ms | p99, p99.9, max |
| Approved tool-dispatch overhead | 20 ms | 75 ms | p99, p99.9, max |
| Same-process reconnect | 75 ms | 250 ms | p99, p99.9, max |
| Cross-process reconciliation | 500 ms | 2 s | p99, p99.9, max |
| Small task excluding user wait | 20 s | 120 s | p99, p99.9, max |

Historical warm context p95 `94.26293 ms` over 100 iterations does not validate current bytes, any other surface, or these thresholds. [ECB-003, ECB-010; CR-003, CR-075]

## Benchmark and chaos plan

The bound prospective fixture compares four variants: `mini-v2.4.6`, `current-ARE`, `ARE+BAML-0.225.0`, and `combined-slice`. It holds constant task strata, model ID and reasoning effort, exact prompt bytes, base tree, environment/container and sandbox/network digests, retry policy, tools, and resources. It requires at least 30 cold process runs and 100 warm runs per variant and task class. [ECB-011; CR-080]

No benchmark run is ready until the owner approves one immutable pre-run manifest by exact digest. That manifest must bind, before execution:

- each variant's exact source revision and digest, build artifact digest, and complete transitive-lock digest, including the named **direct-parser baseline** against which BAML variants are compared;
- the exact task-corpus revision, the complete ordered instance-ID allowlist, and each instance's declared task stratum;
- the exact prompt and configuration bytes, model and provider identities, reasoning parameters, and parser identity/version/schema digest for every variant;
- the base-tree digest; environment or container, sandbox, network-policy, and tool digests; resource limits; retry policy; run counts; cold/warm classification; and the independent verifier identity, source/build digest, configuration, and decision surface; and
- for every quality metric, a numerical non-inferiority margin, the named baseline, the aggregation and statistical comparison rule, the treatment of missing, cancelled, timed-out, invalid, and failed runs, and a mechanical pass/fail rule that requires no post-run judgment. [ECB-011; CR-080–085]

The approved manifest digest must be carried by every run and result receipt; any pre-run or run-time mismatch is `DEPENDENCY_DRIFT` or `SCHEMA_INVALID` and excludes the run according to the manifest's predeclared treatment rather than permitting an analyst to repair the cohort after seeing outcomes. Benchmark readiness remains `not_evaluable` until the owner approves that exact immutable manifest. Approval authorizes only the prospective benchmark fixture named by the manifest; it does not select an architecture or dependency and does not establish fitness, conformance, acceptance, publication, deployment, or effect authority. [ECB-003, ECB-007, ECB-009, ECB-011; CR-030, CR-080–085]

Raw samples and p50/p95/p99/p99.9/max must cover route, context, initialization, request build, first feedback, transport, parsing, dispatch, tool runtime, reconnect, recovery, verification, and whole-task time. Each run also records bytes, token partitions, prefix differences, invalidation cause, calls/cost, trees, patch, checks, telemetry loss, hardware/OS/load, exact source/compiler/runtime/lock digests, and timestamps. [ECB-011; CR-081, CR-082]

Quality reports independently validated resolution rate, empty patches, regressions, failures, wall time, model calls, cost, and focused-check outcome. Each metric is evaluated only by the manifest's predeclared numerical margin, baseline, aggregation/statistical rule, missing/failed-run treatment, and mechanical pass/fail rule. The mini-swe `2.0.0` leaderboard result is context only and cannot substitute for this controlled comparison. [E-MINI-BENCH; ECB-005, ECB-011; CR-004, CR-084]

Chaos and adversarial mutants cover cursor replay/gaps, duplicate action IDs, every kill point around effect/result commit, after-effect-before-observation death, partial stream termination, missing terminal event, malformed/truncated/forged payloads, stale capabilities, unsigned results, schema/dependency/canonicalizer drift, symlink/path races, inherited-secret attempts, egress, DNS/socket behavior, oversized output, child timeout, multi-action partial failure, overload, and telemetry loss. [ECB-009, ECB-011; CR-083]

BAML remains benchmark-only unless its pinned modular API is found in exact source and the experiment proves generated/transitive closure, notices, exact raw-byte preservation, every retry/fallback attempt projection, no effect from partials, replay at pinned and next versions, expected cache-prefix behavior, and the predeclared latency/quality margins. [ECB-007, ECB-011; CR-085]

Current ARE validation must bind exact current bytes and invoke the absolute Linux Node runtime. Focused PASS can support only its named checks and cannot imply architecture selection, fitness, conformance, admission, acceptance, or deployment. [ECB-003; CR-002, CR-003, CR-084]

## Smallest vertical slice

The smallest candidate experiment is one temporary fixture repository and branch, one existing ARE state owner, one persistent App Server consumer, one non-network descriptor-relative execution sandbox, one allowlisted patch, `approve-each`, and one independent postimage verifier. The same request runs through the manifest-named direct-parser baseline and BAML benchmark parser, with crashes injected before execution, after effect/before observation, and during participating-kernel commit. The slice cannot run until the owner approves the exact immutable pre-run manifest defined above, including its variant/source/build/lock identities, corpus revision and instances/strata, prompt/config/model/provider/reasoning/parser identities, base/environment/sandbox/network/tool/resource/retry identities, verifier binding, and metric-specific numerical non-inferiority and mechanical decision rules. Benchmark and vertical-slice readiness remain `not_evaluable` until that approval exists; success afterward produces bounded receipt evidence only. [ECB-011, ECB-012; CR-080–085, CR-100]

Proposed package boundaries are hypotheses, not authorized files:

| Boundary | Candidate responsibility | Prohibited ownership |
|---|---|---|
| Existing `agent-reasoning-engine/context-basis-runtime/` | Exact selected-dependency closure and immutable Context Envelope projection. [L-CONTEXT; L-LIFECYCLE; ECB-002] | No effect authority, sandboxing, or acceptance. [ECB-001] |
| Existing `agent-reasoning-engine/reasoning-state-runtime/` | Run/branch/frontier/event/checkpoint and receipt projection. [L-STATE; ECB-002] | No second App Server transcript ledger or hidden chain-of-thought. [CR-021, CR-022] |
| Existing `agent-reasoning-engine/runtime-journal/` plus architecture-declared actor/effect seams | Candidate causal/event integration after reconciliation. [L-JOURNAL; L-ARE-ARCH; ECB-012] | No new result ledger until duplication is ruled out. [CR-022] |
| Existing `agent-reasoning-engine/codex-app-server-wrapper/` | Persistent transport, raw-byte capture, delivery sequence/ack candidate. [L-GATEWAY; L-RPC; ECB-002] | No semantic state, effect authority, or acceptance. [CR-023] |
| Temporary fixture-only parser adapter | Direct baseline and pinned BAML `0.225.0` benchmark conversion into a closed `NextActionCandidate`. [ECB-006, ECB-007] | No production dependency, transport, retry, authority, state, or receipt owner. [CR-085] |
| Temporary fixture-only execution adapter | One descriptor-relative, egress-denied, allowlisted patch effect with authenticated result candidate. [ECB-009; CR-070, CR-100] | No general sandbox or effect ownership claim. [ECB-012] |
| Independent fixture verifier | Exact base/post-tree, allowlist, patch, residue, and check verification. [CR-073, CR-100] | No owner acceptance or conformance claim. [CR-050] |

No new production package path is selected because the necessity and non-duplication of a coordinator, result ledger, and sandbox owner are deferred. Any surviving slice requires a separate D65 construction binding over exact files and current bytes. [ECB-012; CR-022; owner decision 11]

## Dependency and integration risks

- **ARE drift:** 15 wrapper-file digests differ from historical binding; current conformance and fitness are deferred to exact-current-byte replay. [ECB-003; CR-003]
- **BAML source gap:** the modular API is not bound to pinned `0.225.0` implementation source, so seam suitability and performance are deferred. [ECB-007]
- **BAML generated/lock/notices:** generated artifacts, transitive dependencies, compiler/runtime identities, and Apache-2.0 notice handling require explicit closure before selection. [ECB-006, ECB-007; CR-085]
- **BAML semantic coercion:** JSONish can coerce malformed output, so strict local post-validation and ambiguity mutants are mandatory. [E-BAML `jsonish/README.md:5-24`; ECB-006]
- **Hidden attempt risk:** mini-swe and BAML retries/fallbacks can hide multiple provider attempts and must not imply safe effect retries. [E-MINI; E-BAML `retry_policy.rs:31-60`, `fallback.rs:68-94`; ECB-004, ECB-006]
- **mini-swe dependency posture:** `v2.4.6` is Alpha and uses broad dependency ranges; wholesale adoption is killed. [ECB-004; Lakatos PASS]
- **Transport ambiguity:** current gateway/RPC lacks authenticated durable reconnect and delivery acknowledgement. [ECB-008, ECB-009]
- **Durability ambiguity:** no witnessed participating-kernel atomic effect/result commit, cross-process lock, branch/merge, compaction, or distributed durability exists. [ECB-003, ECB-009; CR-021, CR-060–063]
- **Sandbox ownership:** enforcement ownership and exact effect classes are unselected; runtime approval cannot substitute for effect authority. [ECB-001, ECB-012; CR-022, CR-070]
- **Inventory degradation:** repository Inventory is discovery-only and its diagnostic count has drifted; no match/no-match can close a claim. [CR-001; residue]

## Reviewer verdicts carried forward

- **Lakatos — REPAIR:** ownership separation and mini-swe precedent survive; existing ARE mechanisms are reclassified as build-from-owned / extend-owned candidates; new coordinator/result-ledger/sandbox necessity is deferred; BAML is benchmark-only; false novelty and present fitness claims are killed. No component adoption or architecture choice follows. [ECB-001, ECB-002, ECB-004, ECB-007, ECB-012]
- **Popper — BLOCK / performance fitness `not_evaluable`:** historical p95 and the one canary cannot establish current or combined-runtime fitness; the exact four-way benchmark, tails, bytes/tokens, cache causality, recovery mutants, and quality margin are required. Ferrari/slick, safety, traceability, cache, BAML-fit, and performance-fit claims remain killed. [ECB-003, ECB-010, ECB-011]
- **Taleb — BLOCK construction/acceptance:** default-allow auth, reconnect impersonation, cursor/ack gaps, unsigned observations, floating approvals, incomplete action identities, non-atomic idempotency, sandbox escape paths, cache drift, patch-success collapse, and unmeasured tails remain open. Typed failure, capability, result, sandbox, cache, and independent-verification obligations survive only as candidate requirements. [ECB-008, ECB-009, ECB-010, ECB-012]

These verdicts leave the research writer-ready but do not remove either reviewer block. [evidence-closure.md Handoff verdict and Closure checks]

## Owner decisions required

The research recommends no implicit answers. The owner must separately decide:

1. Whether a distinct coding-loop obligation remains after mapping ARE’s existing orchestration, actor journal, effect-gate, dispatcher, receipt, replay, gateway, and continuation seams. [ECB-012; CR-021, CR-022]
2. Whether atomic effect/result evidence extends ARE or belongs to a separately bounded participating-kernel store, with one-way authoritative linkage and no second causal ledger. [ECB-012; CR-022, CR-060–062]
3. Which owner enforces sandbox/isolation without duplicating CyberAlchemy-v2 authority, ARE effect gating, or Codex runtime permission. [ECB-001, ECB-012; CR-022, CR-070]
4. Whether to authorize the four-variant benchmark, its exact selectors, controls, run counts, thresholds, tails, mutants, and quality non-inferiority margin. [ECB-011; CR-075, CR-080–084]
5. Whether to authorize the pinned BAML source-proof and parser benchmark; selection remains a later decision even if it passes. [ECB-007; CR-085]
6. Which owner controls reconnect credentials, revocation, cursor persistence, acknowledgements, and cross-process reconciliation. [ECB-008, ECB-009; CR-022, CR-063]
7. Which effect classes, if any, can participate in atomic effect/result commit; every other class retains `EFFECT_AMBIGUOUS` on uncertain recovery. [ECB-009; CR-060–062]
8. Which branch, fork, merge, lock, compaction, multi-writer, and durability semantics ARE must support. [ECB-002, ECB-003; CR-021]
9. Whether to approve the default-deny capability-bound modes `observe`, `approve-each`, `approve-bounded-batch`, and any separately authorized autonomy boundary. [CR-072]
10. What constitutes independent postimage verification and how its immutable receipt binds, without substituting for owner acceptance. [CR-050, CR-073]
11. If the candidate survives, whether to authorize a separate D65 construction binding over explicit production files and exact current-byte validation. [ECB-003, ECB-012; CR-084, CR-100]

Until those decisions exist, the architecture remains a falsifiable research hypothesis. [CR-010–012; final claim ceiling]

## Bound, deferred, and killed dispositions

| Closure ID | Disposition preserved |
|---|---|
| `ECB-001` | **Bound:** CyberAlchemy-v2 meaning/effect authority and ARE reasoning/context ownership remain separate. |
| `ECB-002` | **Bound:** existing Context Envelope, Reasoning State, gateway, and continuation are extend-owned candidates, not dependencies to adopt. |
| `ECB-003` | **Deferred:** current ARE conformance and performance fitness await exact-current-byte replay. |
| `ECB-004` | **Bound as precedent; production adoption killed:** mini-swe’s minimal loop is positive precedent only. |
| `ECB-005` | **Bound with narrow ceiling:** the 76.8% artifact applies only to mini-swe-agent `2.0.0` and its exact model/config. |
| `ECB-006` | **Bound:** pinned BAML v0 source supplies the enumerated compiler/parser/stream/retry/test/ephemeral-trace mechanisms. |
| `ECB-007` | **Deferred:** modular-seam suitability and performance; BAML remains benchmark-only. |
| `ECB-008` | **Killed as current capability claim:** authenticated, durable, exactly-once gateway reconnect. |
| `ECB-009` | **Bound as candidate obligations only:** default-deny credentials, persisted cursors/acks, domain-separated actions, immutable capabilities, authenticated results, and fail-closed ambiguity. |
| `ECB-010` | **Killed as present claim; deferred as benchmark target:** Ferrari latency and traceability/safety preservation. |
| `ECB-011` | **Bound as candidate fixture specification:** four-way benchmark and chaos plan; unverified until run. |
| `ECB-012` | **Deferred:** necessity and non-duplication of a new coordinator, result ledger, or sandbox owner. |

Killed ideas additionally include a mini-swe fork/library or novelty claim; alternate authoritative message/transcript/collector ledgers; BAML without pinned proof or with duplicate transport/retries; model identities, partial-driven effects, or unsigned observations; default-allow or same-UID authentication; floating approval; raw host shell; inherited state/secrets; unpinned runtime; path escape; yolo; blind retry; non-atomic exactly-once; full ontology scans or process startup on the hot path; provider-cache freshness; incomplete cache keys; cursor gaps; replay effects; hidden attempts; Inventory absence claims; and every present architecture, security, performance, traceability, cache, dependency, or production-fitness assertion. [CR-110–117; ECB-004, ECB-007–010]

## Residues

- `inventory_lookup_readiness_blocked_and_diagnostic_count_drifted` [CR-001]
- `current_are_exact_byte_conformance_not_evaluable` [ECB-003]
- `baml_modular_api_pinned_source_binding_missing` [ECB-007]
- `four_variant_benchmark_not_run` [ECB-011]
- `authenticated_durable_reconnect_not_witnessed` [ECB-008, ECB-009]
- `participating_kernel_atomic_effect_result_not_witnessed` [ECB-009]
- `sandbox_enforcement_owner_unselected` [ECB-012]
- `new_component_non_duplication_unproved` [ECB-012]
- `all_ferrari_safety_traceability_and_production_fitness_claims_not_evaluable` [ECB-010]

## Final claim ceiling

The surviving hypothesis is limited to extending owned ARE candidates where ownership already exists; retaining pinned mini-swe-agent as loop precedent and benchmark; evaluating pinned BAML as a parser benchmark after its exact-source gap is closed; and experimentally testing missing authentication, delivery, durability, effect, sandbox, cache, and verification obligations without creating duplicate owners. [ECB-001, ECB-002, ECB-004, ECB-007, ECB-009, ECB-011, ECB-012]

No architecture has been selected. No component or dependency has been adopted. Current conformance, latency, security, replay, cache behavior, traceability, quality, dependency fitness, and production fitness are all `not_evaluable`. This research does not authorize implementation, acceptance, publication, release, deployment, or any external effect. [ECB-003, ECB-007–012; CR-003–006; evidence-closure.md Handoff verdict]
