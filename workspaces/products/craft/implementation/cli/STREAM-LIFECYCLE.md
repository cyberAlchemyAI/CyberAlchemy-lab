# Candidate response stream lifecycle

`compileStreamLifecycle` validates the closed
`domainspec.stream-lifecycle/v1-candidate` contract and emits a copied normalized
contract with a state/frame/identity trace. It is a candidate D45 dependency
realization, not a frozen meta-type or system-integration pub/sub amendment.

The contract fixes lifecycle semantics while allowing authored state names,
provider event discriminators and frame event names. Created/open states are
nonterminal. Completion, failure and cancellation use distinct terminal states;
terminal states cannot reopen or transition again. Exactly seven distinct legal
transitions are required. Unknown fields, duplicate events, invalid bounds,
incompatible frame identities, effect declarations and unsupported shapes reject.
Identity fields are required, non-null scalar values so bindings can preserve and
compare them across every frame.

Four typed local functions own frame mappings. Required inputs distinguish stream
identity, provider event payload and bounded failure code. Required output values
carry the same identity fields. The native `StreamFrameSink` interface is exported
through experimental runtime types, together with session and terminal observation
interfaces. A sink waits for bounded capacity and invokes an accepted callback
synchronously with accepting a frame, allowing an atomic lifecycle commit.

The Alch consumer supplies source lowering, generated pure module calls, generic
SSE parsing/writing and a response session. Local session completion is independent
of the HTTP attempt's actual settlement. No automatic retry or remote termination
claim follows from a deadline or cancellation. Native code is tested only for Node.

## Open Questions

The linked ISB-06 plan (source binding requires reconciliation)
owns the construction boundary and unresolved successor work. Request custody is
ISB-07, independent full-service reuse ISB-08, and tenant authentication and
authorization ISB-09 last. These interfaces do not admit a new runtime or profile.
