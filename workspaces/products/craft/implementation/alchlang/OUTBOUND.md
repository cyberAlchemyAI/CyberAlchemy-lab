# Outbound invocation composition

Candidate Node binding, ISB-05. Authority effect: none. Authoring and runnable
inference evidence: [invocation](../alchlang-extensions/inference-router-v1/invocation/README.md).

`outbound-invocation-v1` lowers a bounded sequence to the sibling DomainSpec
`domainspec.outbound-composition/v1-candidate` contract. The DomainSpec compiler
validates stage kinds, interfaces, reference order, fixed binding use and exactly
one HTTP attempt. Alch builds imported functions with the existing DomainSpec
declarative compiler and emits a composition, stage/type trace, child manifests,
source snapshot and an exclusively created bundle with a completion manifest.

```
alchlang check provider-invocation.alch
alchlang build provider-invocation.alch --out /absolute/new/bundle
```

The generated `app/invocation/index.mjs` exports `createInvocation(dependencies,
options)`. Its dependencies are `http: HttpInvocation`, `resolveBinding(identity)`,
optional `stream(session)`, and a monotonic `clock` with `now()` and
`schedule(callback, delayMs)` returning timer cleanup. Clock domains must match
the HTTP adapter. The default uses `performance.now()` throughout. Runtime
options can lower authored timeout, byte and concurrency bounds only.

## Closed authoring model

Top clauses: domain, profile, target, input module interface, output reference,
deadline-ms (1..5000), max-bytes (1..65536), max-concurrent (1..128), max-attempts
(exactly 1). Imports are bounded relative `.alch` paths. Each step has an identifier
and `local`, `binding` or `http` kind. Indented clauses contain JSON values;
arguments are a scope reference or an object mapping argument names to references.
No executable expressions, dynamic destinations, branches, loops or retries exist
in this profile. Pure calculations, queries, rules and mappings belong in the
existing imported functions.

Local steps name a compiled module, argument projection and sanitized failure
code; an optional status guard rejects an unsuccessful selection before effect.
Only provided/provided-or-http and module-local dependencies are accepted in
children, always invoked with `localOnly: true` and cancellation. Thus an absent
provided value cannot fall back to HTTP. Binding steps resolve exact id/version/
model to public metadata only; URLs and secrets stay in operator configuration.
HTTP steps project a body, explicitly omit wrapper fields, identify a response
module input type and choose JSON or a declared stream handoff. Raw HTTP status
has transport meaning; provider JSON need not contain a DomainSpec business
status. The response module validates raw JSON before subsequent local stages.

## Resource custody

The generic interpreter checks cancellation/deadline around local calls and byte
reads and at the effect boundary. Native `sendOnce` uses one POST, manual redirect
handling and an operator-fixed URL/secret. A caller timeout or cancel returns
promptly, without authorizing a retry or proving remote completion.

The concurrency slot remains occupied until both local work ends and the attempt's
`settled` promise resolves. Response rejection, cancel acknowledgment, or a rejected
settlement promise cannot release it. Cancellation acknowledgment is not itself
awaited for release once settlement is independently proven. The native adapter
settles after fetch rejection, body EOF or completed body cancellation, never just
after receiving response headers. This is local resource custody, not proof that
remote inference stopped. Memory idempotency continues consuming separate attempt
and settlement observations until its ISB-07 migration.

## Open Questions

Stream parsing/transitions remain the existing inference adapter (ISB-06).
Custody stays native (ISB-07); full independent service generation is ISB-08.
Rust service parity, live providers, deployment and durable storage are not
established here. Tenant authentication and authorization remain last, ISB-09.
