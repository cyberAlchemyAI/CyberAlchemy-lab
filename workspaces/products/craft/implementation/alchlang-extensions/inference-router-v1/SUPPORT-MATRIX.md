# ISB-01: tested service support matrix

Status: completed local support audit, 2026-09-07. Authority effect: none.
Parent: [SERVICE-PLAN.md](SERVICE-PLAN.md). Exact evidence:
support-evidence.json (referenced result or source binding is not imported). Witness source:
[support-audit/audit.test.mjs](support-audit/audit.test.mjs).

## Findings and decisions

The existing compiler can express more of the service than the handwritten host
used. Discovery minima and streaming aggregation do not need a new arithmetic or
inference-specific primitive. Typed module composition, mapped POST arguments and
HTTP error/status declarations already work. Service assembly and runtime binding
are the main remaining work, with concrete limits in the selected profiles.

| Behavior | Classification in the tested path | Evidence | Reuse or extension decision |
| --- | --- | --- | --- |
| Enabled aliases, deduplication, stable ordering | Supported and tested | W01: generated `query`, `distinct`, `sort` | Reuse existing Alch/DomainSpec declarations |
| Independent context/output minima and any streaming per alias | Supported and tested | W02: generated `first(sort(column(...)))` and `exists`; minima come from different rows | Reuse; no new aggregation primitive justified |
| Full discovery list | Expressible pieces, assembly unwired | W03: generated alias list and per-alias summary, joined by native iteration | Prefer a bounded composition mechanism; do not keep aggregation policy native |
| Parameterized declarative query or repeated module binding | Demonstrated profile/compiler gap for these forms | W04/W15 reject query input; W17 rejects foreach bind | ISB-02 selects bounded iteration or correlated-query design if one compiled discovery operation is required; not a claim that no equivalent expression can exist |
| Multiple endpoints | Supported by the `service-v1` assembly slice | `service.alch`; generic service-profile tests | Reuse compiled function bodies; require exact named entries and reject duplicate routes |
| GET and anonymous mode | Demonstrated function-profile gap | W05: historical audit still proves these forms reject | Extend route-local boundary declarations without weakening existing authenticated POST functions |
| Typed local result into mapped remote POST | Supported and tested with controlled HTTP I/O | W06: compiled local module → mapping → authenticated POST → typed result | Reuse module composition and input mappings |
| Public error HTTP status | Supported and tested | W07: authored integration error maps to 502, one attempt | Reuse endpoint error mapping; public nested error envelope still needs a rendering contract |
| Raw provider JSON POST | Binding/profile gap | W08 rejects status-free raw JSON; W09 rejects `http-post`; W16 rejects request-response in the current system-integration transport slot | Add or select a typed raw HTTP binding; do not force providers to return Alch module business statuses |
| SSE provider consumption and output | Runtime/boundary binding gap in selected function path | W10 rejects SSE as invalid JSON; W05 rejects response-mode clause | Reuse declarative payload mappings; bind explicit stream lifecycle and native byte I/O |
| HTTP client cancellation | Concrete adapter wiring defect | W11: `invoke(..., io.signal)` forwards the signal; `handler(Request)` does not forward `Request.signal` | Forward cancellation in the boundary when implementing ISB-04/05; no new language concept needed for this defect |
| System-integration contract formation | Supported and tested; not runtime execution evidence | W12 produces a manifest with `runtime_guarantees_observed:false` | Reuse definition/binding ownership; do not treat generated records as observed guarantees |
| Atomic state/outbox commit, restart reconciliation and conflict rejection | Supported and tested with actual SQLite | W13: compiled DomainSpec Operation commits through existing port, reopens DB, reconciles replay and rejects changed payload | Reuse transaction techniques and conformance obligations |
| Atomic rollback and generic request reservation | Existing transaction semantics supported; inference custody unwired | W14 proves rollback and rejects an empty outbox event list | Define a request-custody port; do not pretend state-plus-event commit is remote-call deduplication |

These classifications concern the exact compiled bindings in the evidence. They
are not a universal impossibility claim about DomainSpec v2. Negative tests prove
specific rejected forms. Positive tests distinguish source expressibility,
compiled execution, controlled transport and real local persistence.

## Source ownership and audit coverage

All paths below are relative to `general-compiler-v1` unless stated otherwise.

- `implementation/src/declarative-profile.ts` lowers mappings, queries, guards
  and result bindings. `implementation/src/function-profile.ts` retains one POST
  endpoint per compiled function. `implementation/src/service-profile.ts` and
  `service-builder.ts` now assemble two or more of those functions as explicit
  service entries; GET and anonymous entry contracts remain unsupported.
- `implementation/src/boundary-runtime.ts` implements generated function schema
  and transport boundaries. Module HTTP validates a declared business-status field,
  consumes JSON and has operator URL/secret references. Error bodies are currently
  `{error: code}`; matching the inference host's `{error: {code}}` needs a contract
  or generic rendering hook, not another handwritten inference-specific table.
- `implementation/docs/MODULE-COMPOSITION.md` and `MODULE-INPUT-MAPPINGS.md`
  describe the already tested composition path. The new minimal fixture uses
  [mapped-call.alch](support-audit/mapped-call.alch) and its two local imports.
- [aliases.alch](support-audit/aliases.alch) and
  [model-summary.alch](support-audit/model-summary.alch) demonstrate existing
  discovery semantics without copied provider secrets or native arithmetic.
- `implementation/src/local-host.ts`, `extensions/local-host-v1/README.md`,
  `extensions/local-host-events-v1/README.md`,
  `extensions/host-lifecycle-v1/README.md` and
  `extensions/host-service-client-v1/README.md` were inspected as related work.
  Their declared producer hosting, event delivery and controller lifecycle are
  different from a generated Node service exposing arbitrary GET/POST routes.
  Their complete Rust/controller suites were not rerun by this audit; their
  compatibility with inference is not claimed. Existing controller route plurality
  does not remove the demonstrated single-function endpoint restriction.
- DomainSpec sources under the bound sibling package:
  `src/typed-backend/declarative-function.ts`,
  `src/system-integration/{types,compiler}.ts`, and
  `src/runtime/{contracts,in-memory,durable}.ts`. The declarative Query contract
  has no parameter slot; the general typed-query family has its own parameterized
  contract, which is a separate reuse lead, not proof of Alch lowering support.
- The current system-integration transport slot accepts message/publish-subscribe,
  not raw HTTP request-response. Its formation contract deliberately does not claim
  runtime guarantees. Preserve the existing message semantics while designing an
  HTTP binding; do not relabel SSE as broker delivery.
- The durable witness imports the sibling's `test/helpers/l1-project.ts`, creates
  a compiled fixture in temporary storage, and runs `dist/runtime/durable.js`
  through Alch's real `DurableSqliteTransactionalOutbox`. This proves local
  state/outbox behavior, not external inference completion or cross-host custody.

## Verification

From this directory, with the existing Node/TypeScript binding:

```sh
node run.mjs audit
node run.mjs test
```

The audit builds the five authored witness modules into temporary Node bundles,
runs 17 tests, and cleans up its generated bundles/databases. It requires the
TypeScript loader adjacent to the configured temporary toolchain. The existing
47-test inference suite remains a separate regression check. No live provider,
paid request, deployment, frozen-source edit or tenant-policy change is performed.

On this machine `/tmp` was full. The successful commands used `TMPDIR=/dev/shm`
with Node 26.8.1. No unrelated files were deleted. That build-location issue was
operational support, not a compiler capability failure. An initial fixture-path
error in the new audit was corrected before the passing run.

## Construction frontier

ISB-01 is complete. ISB-02 is dependency-ready: use the Define package to specify
only the missing service/port meanings and bind the selected reuse decisions.
Prioritize service assembly, raw HTTP/stream interfaces, custody semantics and
error rendering. Keep existing aggregation, mapped module calls, error statuses
and transaction primitives. Exact witnesses should accompany any proposed
extension. The existing host remains the tested behavior baseline.

Operational residue: the compiler owner maintains reproducible builds and writable
temporary storage; provider/tokenizer, durable backend and deployment choices stay
with their respective operators. No such choice currently blocks ISB-02. Tenant
authentication and authorization remain ISB-09, last.

## Open Questions

- ISB-02 must choose bounded repeated composition versus a reusable correlated
  query extension for complete discovery assembly. Existing per-alias aggregates
  already work; an inference-specific aggregate is not justified.
- Which existing Operation/Dependency contract should type raw HTTP effects and
  stream handles without weakening the current message transport profile?
- What exact reserve/settle/inspect interface keeps local request custody distinct
  from remote completion? Reuse transaction primitives without requiring fake events.
- Which generic error rendering contract preserves the public nested error shape?
- How should service-level cancellation, deadlines and concurrency combine with
  existing per-module limits? The HTTP signal-forwarding defect is already known.
- Full Rust/controller compatibility, live providers/tokenizers, durable inference
  storage and tenant identity policy remain outside this audit's evidence scope.
