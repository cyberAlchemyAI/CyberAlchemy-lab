# Inference service bindings: DomainSpec v2 and Alch plan

## vLLM engine configuration

Real Qwen/Qwen3.8-27B integration verified through the existing SSH tunnel and Alch/DomainSpec service: JSON and SSE completed with nonempty text and usage, about 2.35 seconds each. Local 228-test candidate remains verified. Prototype is usable at the running local endpoint; broader workloads, remote cancellation and deployment remain separate.
[Setup, protocol limits and open questions](local-pattern/vllm/README.md).

## Complete mocked reference product

Operator review follow-up complete: nested SIGINT/SIGTERM cancellation and failed-suite receipts tested; 217 tests pass against the revised 1465-file workspace candidate. No remaining implementation blocker in the documented mock reference scope. Live issuer/engine, standalone protected distribution and deployment remain separate.
[Operator guide and open questions](local-pattern/product/OPERATOR.md). This is a workspace kit; the public bundle is standalone, while protected/durable rehearsal uses the paired source checkouts.

## Protected/durable product rehearsal

Combined protected/durable HTTP rehearsal passed all 15 checks using Auth Foundation signature verification and Rust authorization, mock inference, encrypted SQLite, clean process restart and SIGKILL recovery. Next: consolidate operator instructions and package/validate the complete reference product for review. No LLM or live issuer required for this fixture rehearsal.
[Evidence and open questions](local-pattern/protected-rehearsal/README.md). The accepted public/memory bundle remains unchanged. Online introspection is a fixture; live issuer behavior is not claimed.

## Mock product demo follow-up

Mock product demo and API walkthrough complete: one command verifies the accepted bundle, starts two mock engines, runs 11 API checks and cleans up; five lifecycle tests pass. Next construction: integrated protected/durable API rehearsal with existing Auth Foundation and mocks, then consolidated product acceptance evidence. No local LLM required.
[Instructions and open questions](local-pattern/demo/README.md). The accepted bundle and acceptance decision are unchanged.

## Accepted local inference reference pattern

The user accepted the exact tested reference pattern. [Decision](local-pattern/ACCEPTANCE.json) binds the verified bundle and evidence. LP-06 is complete; no required pattern work remains. Actual engine compatibility and deployment remain separate.

## Current local inference scope

The owner selected the [local inference pattern](local-pattern/DESIGN-AND-PLAN.md).
Local inference pattern validated: 205 tests plus standalone launcher smoke; explicit loopback/auth policy, opt-in outbound v2 deadlines, generated portable Node bundle and canonical protocol. Next: review the exact candidate. Actual local-engine compatibility, context/tokenizer evidence and hardware budgets are optional operational follow-ups; no commercial provider selection required.

Earlier follow-up sections below are chronological evidence, not the current work queue.
Existing Auth Foundation and durable custody semantics are preserved.

Status: ISB-01 through ISB-09 completed as local candidates, 2026-09-07. Authority effect: none.
Machine work units: [service-plan.json](service-plan.json).
Craft owners: `CTX-LANGUAGE-ALCH-INFERENCE-SERVICE` and
`CTX-DSV2-INFERENCE-SERVICE-BINDINGS`.

## Outcome and scope

An author defines a service's routes, discovery, request flow, stream transitions
and custody policy in Alch, lowered into typed DomainSpec contracts. A compiler
assembles the service using tested runtime ports. Native adapters own sockets,
byte parsing, clocks, secret lookup and storage operations; they do not silently
own product policy. The inference API is the first consumer, with an independent
small service fixture proving reuse.

This is a plan, not implementation or admission. The existing 47-test host
candidate remains intact. Its host-evidence.json (referenced result or source binding is not imported) is historical
baseline evidence, not proof of this proposed generated service. Tenant
authentication and authorization are the final unit at the owner's request.

## Evidence and reuse before extension

The preceding explanation did not establish that DomainSpec lacks these concepts.
Existing source must be exercised before adding syntax, types or adapters:

- [Public normalization](public-request.alch), [host](host.mjs),
  [dispatch](dispatch.mjs), [streaming](streaming.mjs) and
  [custody](idempotency.mjs) identify the behavior to migrate.
- [Module composition](../module-composition-v1/README.md) already demonstrates
  typed local and HTTP calls; inspect its compiler and runtime witnesses.
- [Local host generation](../local-host-v1/README.md),
  [event host](../local-host-events-v1/README.md) and
  [host lifecycle](../host-lifecycle-v1/README.md) provide related bindings, not
  automatic compatibility or acceptance for this service.
- In `../domainspec-core/projects/domainspec-v2`, inspect
  `impl/cli/src/typed-backend/declarative-function.ts`,
  `impl/cli/src/system-integration/{types,compiler}.ts`,
  `impl/cli/src/runtime/{contracts,in-memory,durable}.ts` and their tests.
  These are audit targets, not asserted implementations of inference semantics.

ISB-01 must distinguish a missing Alch expression, missing lowering, missing
DomainSpec compiler support, and an unwired existing runtime binding. A failed
witness must identify which layer fails. New language operations require a
minimal failing example plus general semantics and positive/negative tests.

## Ownership and construction chain

DomainSpec v2 owns normalized typed contracts, compiler validation and reusable
runtime interfaces/conformance. Alch owns author-facing declarations, lowering,
service assembly and inference adoption. Product semantics belong in definitions;
implementation targets supply bounded ports. Node HTTP is the initial target;
Rust/Python parity is not claimed by this plan.

D65: reuse or Define-package candidate definitions -> business/product and agent
ontology scaffolds -> authored Alch plus normalized DomainSpec prototypes ->
compiled service and native ports -> exact local product candidate -> fresh tests
-> later product review. This plan neither edits frozen meta-type baselines nor
requires their unrelated CLI rollout. If a needed change intersects frozen bytes,
identify that precise dependency and select a new candidate version; do not
refresh a digest to imply approval. No ontology-runtime selector is required for
planning; ISB-01 records exact source/record dependencies for subsequent units.

## Product construction sequence

### ISB-01 — Audit existing expression and execution support

Owner: joint. Dependencies: none. Status: completed.

Evidence: [support matrix](SUPPORT-MATRIX.md) and audit receipt (referenced result or source binding is not imported); 17 audit tests and 47 inference regressions pass.

- Classify each behavior as supported and tested, expressible but unwired, runtime-binding gap, or demonstrated semantic/compiler gap.
- Build minimal witnesses for discovery aggregation, multiple routes, mapped provider calls, streaming and atomic custody.
- Inspect existing module composition, local-host/event/lifecycle prototypes and DomainSpec runtime/integration contracts; cite exact sources and tests.

Acceptance:

- SUPPORT-MATRIX.md with source paths, witness commands and results
- Explicit reuse/extension decisions; no inference from file presence alone

### ISB-02 — Define the service and runtime contracts

Owner: joint. Dependencies: ISB-01. Status: completed.

Evidence: [Define-backed contracts](service-contracts-v1/README.md) and
[contract receipt](service-contracts-v1/evidence.json).

- Use the existing Define package for missing meanings; reuse canonical concepts before proposing new types.
- Bind candidate business/product scaffolds to service routes, discovery projection, outbound invocation, stream lifecycle and request custody.
- Specify statuses, cancellation/timeout semantics, uncertainty, bounds, secret references and unsupported-feature rejection.

Acceptance:

- Candidate definition delta and D65 construction mapping
- Versioned normalized contract and exact runtime port interfaces
- No arbitrary executable source or secrets in authored definitions

### ISB-03 — Express discovery and public error policy

Owner: alch. Dependencies: ISB-02. Status: completed.

Evidence: [generated discovery and error policy](discovery/README.md) and
[ISB-03 receipt](discovery/evidence.json).

- Author catalog filtering, alias grouping, conservative limits, capability projection and error/status mappings.
- Reuse existing queries/mappings first; extend only operations proved missing by ISB-01.
- Generate discovery handlers and preserve current public response shape.

Acceptance:

- Model/capability discovery comes from compiled definitions
- Tests for duplicate aliases, disabled offerings, strategy availability and secret redaction
- No handwritten catalog projection or public error policy remains

### ISB-04 — Generate service route assembly

Owner: joint. Dependencies: ISB-03. Status: completed.

Evidence: [generated public service](service/README.md), [construction plan](service/PLAN.md)
and [receipt](service/evidence.json). The existing multi-entry `service.alch`
format remains supported. `public-service.alch` adds the explicit
`public-routes-v1` assembly mode: anonymous GET/POST routes, typed native bindings,
JSON-or-SSE transport validation, bounded HTTP handling and cancellation.
The 69 inference/service tests and three existing multi-entry tests pass.

- Define and lower one service with GET health/models/capabilities and POST inference.
- Reuse existing host-generation capabilities where compatible; bind a thin Node HTTP adapter.
- Reject duplicate routes, incompatible outputs, missing bindings and unsupported stream targets at build time.

Acceptance:

- Buildable multi-endpoint service fixture
- HTTP method/path/media/size-limit and chunked 413 tests
- Deterministic route manifest and source-to-generated trace

### ISB-05 — Bind provider invocation and composition

Owner: joint. Dependencies: ISB-04. Status: completed.

Evidence: [generated invocation](invocation/README.md), [construction plan](invocation/PLAN.md)
and [receipt](invocation/evidence.json). All 79 inference/service tests, 14
DomainSpec contract/composition tests and three legacy service tests pass.

- Compose selection, request mapping, fixed bound provider invocation and response mapping using existing module/integration constructs where possible.
- Keep secret resolution, sockets and clocks behind typed runtime ports.
- Declare one-attempt policy, deadline and concurrency semantics; do not permit user-controlled destinations or implicit retry.

Acceptance:

- Generated orchestration with local and HTTP witnesses
- No transport call on failed validation/selection
- Timeout, ambiguous completion, binding mismatch and overload regressions

### ISB-06 — Bind stream lifecycle and cancellation

Owner: joint. Dependencies: ISB-05. Status: completed.

Evidence: [generated stream lifecycle](stream/README.md), [construction plan](stream/PLAN.md)
and [receipt](stream/evidence.json). All 91 inference/service tests, six
DomainSpec contract tests and three existing service compatibility tests pass.

- Declare started/delta/completed/error/cancelled transitions and exactly one local terminal event.
- Bind incremental parsing and socket backpressure through native stream ports.
- Preserve unknown remote outcome after timeout/cancellation; disallow stream replay.

Acceptance:

- Split UTF-8/CRLF, size caps, partial failure and early EOF witnesses
- Disconnect propagation and no late success after deadline
- No hidden stream transition policy in inference-specific native code

### ISB-07 — Bind request custody and idempotency

Owner: joint. Dependencies: ISB-06. Status: completed.

Evidence: [generated custody](custody/README.md), [construction plan](custody/PLAN.md)
and [receipt](custody/evidence.json). All 98 inference/service tests, 14 DomainSpec
contract tests and three existing service compatibility tests pass.

- Reuse the compiled idempotency policy and audit DomainSpec in-memory/durable runtime contracts before designing a new store abstraction.
- Declare atomic reservation, canonical fingerprint, pending retention and outcome tracking; implement bounded memory port first.
- Keep routing strategy in request identity and catalog snapshot pinned to initial execution.

Acceptance:

- Concurrent duplicate/conflict, expiry and stuck-attempt witnesses
- Storage port conformance suite including cancellation ambiguity
- Explicit memory-only semantics; restart durability remains a separate backend choice

### ISB-08 — Migrate inference and prove reusable generation

Owner: joint. Dependencies: ISB-07. Status: completed.

Evidence: [independent service reuse](reuse/README.md), [native inventory](reuse/NATIVE-INVENTORY.md)
and [receipt](reuse/evidence.json). All 106 service tests, 14 DomainSpec contract
tests and three existing service compatibility tests pass.

- Replace handwritten service behavior only after generated paths pass equivalent tests.
- Carry forward all 47 host baseline tests and add one non-inference service fixture to prove reuse.
- Inventory every remaining native line by runtime-port responsibility; produce fresh candidate evidence and updated source bindings.

Acceptance:

- Generated inference service plus independent minimal service fixture
- All baseline behaviors and new negative witnesses pass
- No hardcoded inference policy in generic adapters; no claim of production or cross-target parity

### ISB-09 — Add tenant authentication and authorization last

Owner: joint. Dependencies: ISB-08. Status: completed local candidate; last.

Owner approval: [structural model](security/README.md) and [decision record](security/STRUCTURAL-MODEL-APPROVAL.json).

- Select identity and authorization contracts when this final unit is reached.
- Enforce tenant-scoped catalogs, keys and current authorization before execution and replay.
- Preserve provider-secret custody and public discovery filtering.

Acceptance:

- Tenant isolation, forbidden model, revoked access on replay and cross-tenant key tests
- Explicit identity/provider decisions recorded before implementation

## Frontier and operational support

ISB-01 through ISB-08 are complete as local candidates. The independent quote
fixture proves Node service/function/operation reuse and the native inventory
classifies 18 files and 738 physical lines. Request admission now joins the
existing compiled discovery, invocation, stream and custody policies.

ISB-09 is complete as the final local candidate: Auth Foundation verification,
flat tenant membership, exact permissions, filtered discovery, current pre-attempt
authorization and principal-private replay checks. [Implementation and evidence](security/IMPLEMENTATION.md)
record 121 service tests, 16 DomainSpec contract tests and three compatibility tests. Durable storage, live providers and deployment
remain separate operational choices; none invalidates this local candidate.

| Operational support | Owner | Affected stage | Treatment |
| --- | --- | --- | --- |
| Reproducible sibling compiler and toolchain | Compiler owners | Audit and subsequent builds | Existing binding; verify before use |
| Providers, aliases, tokenizer estimates | Inference operator | Live integration | Deferred; fixtures remain runnable |
| Persistent storage and recovery | Storage owner | Durable backend | Deferred; memory semantics remain explicit |
| Hosting, DNS/TLS, production budgets | Platform operator | Separate deployment | Deferred, outside this plan |

## Completion evidence

Each implementation unit records exact source paths, selected compiler/binding
versions, generated artifacts and witness results. Unsupported combinations fail
at validation/build time. ISB-08 must cover the original 47 behaviors, not merely
retain a test count, and demonstrate that definitions change generated behavior.
Tests include malicious unknown fields, missing bindings, secret redaction,
concurrent duplicates, ambiguous timeouts, stream cancellation and chunked 413.
Historical evidence is preserved; a successor receipt binds the migrated service.

## Live service-client follow-up

[Live rehearsal](security/live/README.md) passed 12 checks against
the existing HTTPS Keycloak issuer, with a disposable policy and provider. Browser
handoff and explicit session enrollment remain next product work.

## Browser consumer follow-up

[Browser handoff and enrollment](security/browser/README.md) pass 13 lifecycle tests
and seven live-browser checks. Application request interception is explicit test
transport; trusted TLS ingress/callback-origin integration remains next.

## Trusted HTTPS ingress follow-up

[Real HTTPS ingress](security/ingress/README.md) passed eight live checks
without application request interception. The temporary callback registration was
restored. Regression suites: 121 service, 13 lifecycle, two socket and three
compatibility tests. Durable session/revocation design remains next.

## Durable application authentication state follow-up

[Encrypted SQLite state](security/durable/README.md) preserves established sessions and
revocation across restart. Independent connections, abrupt writer exit and
fail-closed storage pass. Validation: 27 authentication, 121 service, two TLS
and three compatibility tests. Current operator policy and Rust authorization
remain owners of grants. Next construction work: bounded token renewal.
Operational support: key custody, backup policy and deployment are operator-owned
residue; no running service was switched.

## Bounded browser renewal follow-up

[OIDC renewal](security/renewal/README.md) preserves original session deadlines,
rotates cookie/CSRF and revokes the previous token. Expired access tokens cannot
invoke inference; no inference replay occurs automatically. Validation: 38
authentication, 121 service, two TLS, three compatibility tests and seven real
Keycloak/browser checks with encrypted SQLite reopening. The application browser
transport is intercepted locally; no running host was replaced.
Next construction: durable inference request custody. Operator key operations,
issuer-wide logout and deployment remain separate residue.

## Durable inference request custody follow-up

[Explicit bounded-sqlite custody](security/durable-custody/README.md) preserves scoped reservations,
attempts and JSON replay across restart. Generated policy remains the decision
owner; current authorization still gates replay. Interrupted requests remain
unresolved and cannot automatically execute again. Validation: 13 durability,
121 service, 38 authentication, two TLS and three compatibility tests.
Next construction: operator reconciliation of uncertain outcomes. Key/backup
operations and deployment are separate operator-owned residue.

## Trusted operator reconciliation follow-up

[The reconciliation port](security/reconciliation/README.md) requires current operator
authorization, trusted terminal evidence and an unchanged reviewed record. Atomic
closure fences late workers, preserves write-once outcomes and records encrypted
operator/evidence metadata under existing retention. Reconciliation does not
dispatch another inference. Validation: 28 custody/reconciliation, 121 service,
38 authentication, two TLS and three compatibility tests.
Next construction: provider-specific evidence verification. Management HTTP,
audit export, keys and deployment remain separately owned integrations.

## Provider evidence readiness

[Source inspection and plan](security/provider-evidence/PLAN.md) confirm that the current
provider protocol is fixture-only and lacks durable provider-operation correlation.
The first real provider/API product must be selected before provider-specific
verification can be implemented. Existing reconciliation remains the tested
candidate; this planning step changes no runtime behavior.

## Open Questions

- The [ISB-01 support matrix](SUPPORT-MATRIX.md) answers the tested construct
  questions. Broader target/profile compatibility remains untested.
- ISB-03 resolved bounded pure iteration syntax and its structural interfaces.
  ISB-04 resolved route-level type binding for Node; Rust service parity is not claimed.
- Which existing runtime contract can provide atomic request reservation without
  conflating transactional outbox semantics with remote inference completion?
- ISB-04 extends the existing service profile with explicit public route assembly
  and a generic Node adapter. Further targets remain separately untested.
- Live providers/tokenizers and durable-storage guarantees remain operator-owned
  future choices. They do not block local generation and conformance.
- ISB-09 exact interface binding and replay enforcement are complete. Production
  issuer/client configuration, policy/session lifecycle and live TLS rehearsal remain
  [operational questions](security/IMPLEMENTATION.md#open-questions).
