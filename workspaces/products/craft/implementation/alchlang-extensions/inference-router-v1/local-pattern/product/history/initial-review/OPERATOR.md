# Inference reference product: operator guide

This workspace reference package brings together the accepted Alch/DomainSpec
local inference bundle, the mock API demo, the protected/durable process rehearsal,
and one consolidated validation command. It requires no local LLM or paid provider.
The base pattern is accepted; this combined product candidate has a separate review.

## Commands

From the CyberAlchemy-v2 checkout:

```bash
tools/inference-reference verify
tools/inference-reference demo
tools/inference-reference serve
tools/inference-reference rehearse
tools/inference-reference validate /absolute/new/evidence-directory
```

`demo` starts two deterministic engines plus the accepted public service, runs
11 API checks, then stops. `serve` runs the same checks and leaves the service
available at its printed loopback address until Ctrl+C. Ports are allocated
automatically. `rehearse` builds the protected/durable composition in temporary
storage, exercises 15 checks across actual process restarts, then removes it.
`validate` runs the complete eight-suite acceptance matrix and saves logs plus a
candidate-bound RESULT.json. It refuses an existing output directory, checks
the candidate before and after execution, and records failure without claiming
completion if any suite fails. Never refresh a manifest to conceal drift.

## Package and prerequisites

This is an exact workspace kit: product/manifest.json identifies its source and
runtime inputs by hash. The public Node bundle under generated/local-pattern is
standalone and remains unchanged. The protected/durable rehearsal uses the paired
DomainSpec and Auth Foundation checkouts; it is not a standalone protected server
distribution. Keep those directories in their current sibling layout.

The shared tools/toolchain/run launcher supplies Node, Cargo and the C linker.
The repository-installed TypeScript compiler is used for generated test builds.
Required package dependencies already present in the checkouts include jose and
tsx. No command installs tools, downloads models, initializes submodules, changes
issuer settings, or deploys a service. Temporary builds need writable disk space;
TMPDIR may select another suitable directory.

## Operator and caller responsibilities

The operator configures engine endpoints, aliases, upstream credentials, resource
limits and custody. The caller supplies a conversation, an optional public model
alias, output allowance, stream mode and optionally an idempotency key. Callers
cannot change engine URLs, raise operator limits or choose engine credentials.

For manual API use, run `serve` and substitute its printed address:

```bash
curl http://127.0.0.1:PORT/v1/models
curl http://127.0.0.1:PORT/v1/capabilities
curl http://127.0.0.1:PORT/v1/inference \
  -H 'Content-Type: application/json' -H 'Idempotency-Key: example-1' \
  -d '{"task":"text.generate","input":{"messages":[{"role":"user","content":"Hello"}]}}'
curl -N http://127.0.0.1:PORT/v1/inference \
  -H 'Content-Type: application/json' \
  -d '{"task":"text.generate","model":"local-chat-b","stream":true,"input":{"messages":[{"role":"user","content":"Hello"}]}}'
```

The mock outputs are fixed labels. Automatic selection chooses A; explicit
local-chat-b chooses B. SSE emits started/delta/completed. Discovery reports
declared capabilities; health is liveness, not model readiness.

## Modes and security

| Mode | Client identity | Storage and lifecycle |
| --- | --- | --- |
| Public demo/serve | Public local callers; exact loopback Host/Origin boundary | Bounded memory; state disappears on exit |
| Protected/durable rehearsal | Disposable signed access tokens; real Auth Foundation signature verifier and Rust authorization | Encrypted temporary SQLite; same key across worker restarts; removed after the test |

The rehearsal proves scope is tenant plus principal, membership alone does not
replace permission, and current authorization gates replay. Its online token
introspection function is a no-op fixture. It does not demonstrate a live issuer,
OIDC login, refresh or issuer-wide logout. Never use its fixture identity port as
a production authentication configuration.

Upstream no-auth applies only to an explicitly configured numeric loopback engine.
It does not disable client authentication in protected mode. The existing protected
host and Auth Foundation configuration remain owners of actual issuer/policy wiring.

## Engine configuration and limits

The standalone bundle contains configuration.example.json and PROTOCOL.md.
Its explicit local bindings support none or bearer upstream authentication;
bearer secrets are referenced by environment name. It accepts the versioned
alch-local-text/v1 protocol. Another wire protocol needs declarative mappings
and, where necessary, a reusable stream codec.

The reference deadline is at most 30 seconds; operator overrides can tighten it.
The opt-in DomainSpec outbound v2 permits authored ceilings up to 300 seconds;
legacy v1 remains limited to five seconds. Reference request/response totals are
64 KiB, concurrency is two, and each request has one attempt. ContextBound is an
operator-attested conservative input-token bound across the configured catalog,
combined with the requested output allowance. The fixture's bound is not a real
model tokenizer estimate.

## Replay, shutdown and recovery

Matching retained JSON keys replay without executing again. Changed input conflicts;
streams do not replay. Public memory custody is lost on restart. Durable custody
retains completed results and unresolved attempts across restart, with current
authorization required before replay. Retention begins only after an outcome and
transport settlement; the reference uses 60 seconds for settled records.

Ctrl+C stops the demo service and both fixtures. The rehearsal also tests SIGKILL
during an attempt: its retained key stays unresolved/non-executable. A lost response
does not prove inference stopped, and the product does not automatically retry or
invent completion evidence. Existing operator reconciliation is a separate trusted
integration. Do not delete unresolved state merely to force execution.

For an eventual persistent deployment, the operator must retain its encryption key,
define backup/retention procedures, configure actual identity verification and set
measured limits. The rehearsal deliberately supplies none of those operational
policies to a running deployment.

## Validation and review

The consolidated matrix runs product identity checks, mock-demo lifecycle tests,
protected/durable process integration, local-pattern conformance, service regressions,
authentication/session regressions, custody/TLS tests and independent service
compatibility. Expected total: 214 tests. The 11 demo checks and 15 protected
checks are exercised inside those tests, not added again to the total.

Review the exact candidate manifest, its matching successful validation receipt,
the role/configuration boundaries above and the claim ceiling in REVIEW.md.
All three product controls are distinct: existing base-pattern acceptance,
combined-product review, and any later deployment authorization.

## Open Questions

No engine or issuer choice blocks this mocked workspace reference product.
Optional follow-ups are a standalone protected distribution, live issuer integration,
real-engine compatibility, tokenizer evidence and hardware performance budgets.
Product owner owns candidate acceptance; platform/auth/storage operators own later
live configuration, keys and deployment. No deployment is performed by this kit.
