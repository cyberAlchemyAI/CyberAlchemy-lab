# ISB-02 service and dependency contracts

Status: candidate definitions and contract prototypes, 2026-09-07.
Authority effect: none. Parent: [SERVICE-PLAN.md](../SERVICE-PLAN.md).
Evidence: [evidence.json](evidence.json). Predecessor:
[ISB-01 support matrix](../SUPPORT-MATRIX.md).

## Decisions

1. Reuse Query, Mapping, Workflow, Operation, State Machine, the existing
   Idempotency Record, and DomainSpec D45/D48 dependency/failure meanings. No new
   DS-D1 meta-type or DS-D8 relationship is introduced.
2. Select **bounded pure query iteration** for discovery assembly. Reuse the tested
   alias and per-alias queries. Do not add correlated-query syntax or a special
   inference aggregate in this version.
3. Name dependency contracts by concern: HTTP Invocation, Response Stream, Request
   Custody. This follows `domainspec-v2-D45`; a universal code-level Port or a new
   logical DomainSpec Interface for every dependency is not required.
4. Specify a separate raw HTTP binding. Preserve existing module HTTP business
   status semantics and message/publish-subscribe transport semantics.
5. Keep one-attempt behavior, bounded memory retention, shared-public scope and
   deferred tenant authentication/authorization. No retry, persistence, tenant
   isolation or real-provider choice is implied by this version.

## Define provenance and scaffolds

The actual Define CLI produced define/cli-result.json (result record excluded)
from [define/cli-input.json](define/cli-input.json): six reuse dispositions and
eight specializations. Reproduction: `node define/run.mjs [output.json]`.
The pack validates, is deterministic under its current context, and has no open
meaning within this bounded scope. `handoff_ready:true` is the CLI's structural
candidate result, not human acceptance, canonical admission or execution authority.
All scripted choices remain agent-authored candidates. Operational and future
implementation questions are recorded below rather than declared resolved.

[scaffolds.json](scaffolds.json) links each business/product node to its exact
Define disposition and records the D65 construction chain. Pure discovery uses
Query/Mapping; state-changing custody uses Operation semantics; orchestration and
stream lifecycle reuse Workflow/State Machine concepts. These are navigation
scaffolds, not promoted ontology records. Original inference definitions and
historical receipts are preserved. The one-attempt limit narrows the predecessor's
conditional maximum of two; it does not enable its unimplemented fallback.

## Normalized service declaration

[service.schema.json](service.schema.json) is a closed candidate JSON Schema.
[service.example.json](service.example.json) declares the four public endpoints,
function signatures, bounded discovery iteration, error policy, limits and runtime
dependencies. It is a **normalized target design**, not syntax already accepted by
the Alch compiler. Functions are unbound candidate declarations; `input_type` and
`output_type` name contract symbols to resolve against generated schema bindings
in ISB-03/04. Passing this schema does not prove those bindings exist or generate
runnable code. Stateless services may omit custody by using null and dependencies
not needed by their routes; a second minimal stateless fixture is checked.

GET routes take no request body and select queries. POST requires JSON. Routes
are unique by method/path, reference a declared function and use a declared error
policy. The initial target is Node HTTP. Unsupported methods, targets, inline
executable code, provider URLs, secret values and undeclared fields reject.
Operator catalogs and invocation context remain trusted inputs supplied by the
host; the public request does not acquire catalog or destination fields.

Prototype limits are explicit: 64 KiB request/response, 16 KiB encoded event,
5-second deadline, two active attempts, one attempt per request, 128 custody
records, 60-second retention and 64 KiB custody item bounds. They are local test
choices, not production recommendations. Encoded bytes, including framing, count
against each relevant limit. Each raw input stream and encoded public output has
its own response-byte budget; a nested operation cannot raise its parent's budget.

### Bounded query iteration

The source query materializes a finite list. For discovery this is sorted distinct
enabled aliases, bounded to 100. `SummaryContext` supplies the same immutable
operator Catalog plus one Alias to the named input Mapping; that Mapping returns
`SummaryInput`, which the item query consumes to produce `ModelSummary`.
Input/output symbols must resolve to actual schema bindings at compilation.

The iterator runs each item query once, sequentially, in source order, within
max_items, the parent deadline and the aggregate encoded output-byte cap. It
collects all results or raises one error; no partial discovery response is returned.
The input Mapping and both queries must have an entirely local, pure dependency
closure. HTTP calls, state-changing Operations, recursive iteration and hidden
bindings reject. An author's `kind:query` label alone is not proof of purity:
ISB-03 must inspect the resolved generated function graph. The current validator
checks declaration kinds and reference/type compatibility only.

Independent minima and any-streaming semantics remain in the existing per-alias
query. The iterator contributes bounded evaluation, not provider-selection policy.

## HTTP Invocation dependency

Exact TypeScript candidate signatures: [dependencies.d.ts](dependencies.d.ts).
Canonical concern-specific descriptors: [dependency-contracts.json](dependency-contracts.json),
validated against the existing DomainSpec D45 dependency schema.

`sendOnce(binding, body, control)` returns an **immediate HttpAttempt handle** with
separate response and settlement promises. The operator-owned resolver validates
binding identity/version and obtains the fixed destination and secret reference.
Only the adapter sees credential values. The authored request cannot supply them.
Invalid configuration rejects before provider work; HTTPS is required except an
explicit numeric-loopback fixture binding. Redirects and retries are disabled.

The response promise yields bounded HTTP status, media type and raw bytes; raw
provider JSON has no required Alch business-status field. Generated policy checks
status/media type and maps JSON or stream payloads. The failure surface is an
allowlisted code, never an exception message or provider diagnostic.

The settlement promise remains observable even if the response promise rejects
on cancellation/deadline. Cancellation requests local transport shutdown; it does
not certify that remote execution or billing stopped. Do not release the active
attempt slot until settlement. A pre-dispatch validation failure settles locally
without an attempt. A stalled transport may hold its slot indefinitely, bounded
by capacity; operator recovery is separate. This is why a lone response Promise
is not an adequate dependency signature.

`control.deadline` is an absolute monotonic timestamp in one host clock domain.
The effective child deadline is the earlier of parent deadline and any binding
limit. Parent Request.signal must propagate through all generated calls. Stop
starting new work when expired/aborted, and never turn late completion into success.

## Response Stream dependency

[stream-state.json](stream-state.json) owns the candidate transition table:

| State | Event | Next state |
| --- | --- | --- |
| created | start | open |
| created | fail / cancel | failed / cancelled |
| open | delta | open |
| open | complete / fail / cancel | completed / failed / cancelled |

Terminal states accept no successor. There is exactly one local terminal decision;
network loss can prevent its delivery. Before start, failure renders an HTTP JSON
error. After start, failure attempts one SSE error while writable. Cancellation
closes locally and does not synthesize successful completion. Every emitted event
uses the identity pinned at start. Started/delta/completed/error retain the current
public wire shapes; there is no public cancelled-event requirement.

Every write awaits downstream capacity and respects encoded event/response caps.
Native code handles UTF-8/CRLF framing, byte reads and socket backpressure; generated
mappings and the declared state machine own payload and transition policy. Unknown
provider events, oversized frames, invalid JSON/UTF-8, early EOF and missing terminal
completion fail closed. Repeated terminal frames never create a second result.
Provider settlement and stream delivery remain separate observations.

## Request Custody dependency

The generated workflow assigns a fresh request ID and computes a versioned SHA-256
fingerprint of canonical validated request data. V1 preserves object-key sorting,
array/text ordering and defaults. Material includes task, messages, optional model,
routing strategy, max_output_tokens, stream and required_context_tokens. It excludes
request ID, scope/key, catalog snapshot, URLs, secrets and transient execution state.
The version is compared separately from the digest. Scope/key form the storage
identity; missing key gives a new independent record. Public scope is currently
shared-public, not a claimed tenant identity. Catalog/decision versions stay pinned
to the first execution; a strategy change conflicts instead of replaying.

| Operation | Required semantics |
| --- | --- |
| reserve | Atomically return one execution token, matching replay, or explicit rejection; conflicting input never executes |
| beginAttempt | Validate token and pin one binding/model/policy identity before send; a second attempt rejects |
| recordOutcome | Record exactly one JSON success, stream success, failure or cancellation; JSON success stores a bounded copied result |
| markTransportSettled | Record local transport release independently of outcome; idempotent notification, not remote-completion evidence |
| inspect | Return operator-only copied metadata without messages, stored results, fingerprints, tokens or secret references |

Reservation has a bounded queue and capacity. Cancellation before linearization
may reject with CANCELLED without a record. Once linearized, reserve returns its
token even if cancellation then arrives; the caller must record cancellation and
mark no-transport settlement instead of starting a provider. Returning a lost-token
failure after creating a reservation is forbidden.

Outcome and transport settlement may arrive in either order. Retention begins at
the later observation, using the host's monotonic clock. Pending or transport-held
records never expire or evict. Unresolved duplicates return REQUEST_IN_PROGRESS;
conflicts return IDEMPOTENCY_CONFLICT. Settled JSON successes replay the original
ID/result, settled streams return STREAM_NOT_REPLAYABLE, and settled failures return
PREVIOUS_REQUEST_FAILED. Capacity exhaustion rejects before an attempt. Expiry
permits a new request; restart discards memory state and invalidates old tokens.
No cross-host or exactly-once guarantee is declared.

Successful outcomes require a begun attempt; failed/cancelled outcomes may precede
it. beginAttempt after an outcome rejects. Each token belongs to one store instance
and record; unknown/stale/forged tokens reject. recordOutcome cannot overwrite an
outcome. All counts are bounded nonnegative integers or null with explicit usage
provenance; null is not zero, and local estimates identify the estimator version.
Remote completion is reported-complete only after a validated provider completion;
local cancellation, failure and transport settlement otherwise retain unknown.
No fake outbox Event is required to reserve or settle a request.

## Error representation

The normalized error policy owns allowlisted code-to-status mapping and the nested
`{request_id?, error:{code}}` envelope. Unknown codes map to INTERNAL_ERROR/500.
Only a host-assigned original request ID is eligible for inclusion. Exception
messages, provider bodies, binding IDs and credentials are excluded. Once SSE
headers are committed, the same sanitized failure code enters the terminal error
payload; the status line does not change. Existing authored endpoint status
semantics are reused; a generic rendering contract supplies the nested shape.

## Verification and remaining implementation

```sh
python3 -m unittest discover -s . -p test_contracts.py -v
node --test definition.test.mjs
node define/run.mjs
```

The evidence also records strict TypeScript checks, including negative signature
witnesses: a response-only promise cannot implement HTTP Invocation, and a plain
caller string cannot be used as an ExecutionToken. Python checks structural closure,
references, selected type equalities, bounds, purity declarations and specification
traces. They do not implement the service, prove full compiler type/purity analysis,
or observe network or storage behavior. The existing 17/47 ISB-01 results remain
historical runtime evidence and are not reclassified as tests of these contracts.

An operational dependency repair was needed: Define's generated decision profile
had stale route-registry provenance and omitted the canonical read-only
CA2-ROUTE-DOMAINSPEC-CORE route. Its candidate policy projection now includes that
route with local-read only; the existing generator rebuilt provenance and all 34
routing tests pass. Canonical registry bytes, prior route policies, consequence
rules and owner decisions were not changed. The Define package suite also passes.
The repair records candidate verification, not governance adoption.

D65: CLI definition delta -> [scaffolds](scaffolds.json) and product prototype ->
normalized service/dependency/state contracts -> later Alch/compiler realization
-> exact generated-service tests in ISB-03..08. Current frontier: ISB-02 complete
as a contract candidate; ISB-03 generated discovery is next. Compiler/runtime
admission and production effects remain separate.

Operational support: compiler owner maintains build/context bindings; inference
operator selects future providers/tokenizers; storage owner selects future durable
semantics; platform owner handles later hosting. Those tasks do not block local
ISB-03 construction. Tenant authentication and authorization remain ISB-09, last.

## Open Questions

- ISB-03 must choose the exact Alch spelling/lowering of bounded pure iteration and
  bind the named type symbols to actual generated schemas. The semantics above are
  selected; correlated-query semantics and effectful loops are out of v1 scope.
- ISB-04..07 must realize these contracts and prove type/purity closure, raw HTTP
  cancellation/settlement, stream transitions and atomic request custody with current
  product tests. Passing the contract tests does not answer those implementation questions.
- Live provider aliases, tokenizer estimates, durable/multi-host storage, production
  limits and recovery remain operator choices outside this candidate.
- Tenant identity and authorization policy, including checks before replay and
  per-tenant discovery, are intentionally deferred to ISB-09.
