# Candidate outbound composition

`compileOutboundComposition` validates `domainspec.outbound-composition/v1-candidate`
normalized contracts and returns a copied contract, expanded output shape and
ordered typed stage trace. This is candidate construction evidence, not admission
or an extension of the frozen system-integration pub/sub profile.

The contract supports sequential local function calls, versioned operator binding
resolution and exactly one raw request/response HTTP invocation. Unknown fields,
unsafe or forward references, incompatible module arguments, optional object
traversal, unbounded limits, dynamic destinations and retries reject. Raw response
JSON is assigned the declared decoder input interface and must pass that compiled
decoder at runtime. Existing status-bearing module-http semantics are unchanged.

`src/runtime/http-invocation.ts` supplies concern-specific D45 interfaces, exported
as types through the experimental runtime entry. `HttpAttempt.response` and
`HttpAttempt.settled` are independent: a caller can fail or cancel before actual
resource custody ends. Only resolved settlement is evidence for releasing a slot;
there is no automatic retry or claim that remote execution stopped. Secrets and
URLs are operator configuration, absent from authored invocation data.

Alch is the first lowering/runtime consumer. Its
construction plan (source binding requires reconciliation)
links the Define-backed meanings, D65 scaffolds, authoring and evidence. Node is
the only realized target. The normalized contract and tests are independent of
inference product names.

## Open Questions

Stream lifecycle and atomic request custody remain ISB-06/07 in the
shared plan (source binding requires reconciliation).
This candidate does not define tenant security or change admitted meta-types.

## Local inference outbound v2 candidate

The opt-in domainspec.outbound-composition/v2-candidate contract permits declared
deadlines from 1 to 300000 ms. V1 remains capped at 5000 ms. One-attempt, byte,
concurrency and typed composition checks are unchanged; runtime overrides may
only tighten the authored limits. HttpBindingPolicy explicitly selects https or
loopback scope and bearer or none authentication. No-auth requires loopback; the
HTTP runtime validates the fixed URL and forbids non-loopback destinations in that
scope. This is an operator binding, not caller authentication or an engine completion
guarantee. Evidence and open questions: local pattern (source binding requires reconciliation).
