# Request custody profile

`request-custody-v1` targets Node HTTP. Its closed top-level declarations are
`domain`, `profile`, `target`, `import Policy`, `limits`, `identity`, `decisions`
and `lifecycle`. Configuration values use JSON; imports are pure local Alch
functions contained beneath the source directory. Unknown declarations, escaping
imports, unsafe identity names, incompatible policy shapes, raised bounds,
multiple attempts and expiry before both observations reject during checking.

`alch check source.alch` validates and `alch build source.alch --out new-directory`
materializes a standalone hashed bundle. It exports `createCustody(options)`;
options bind `dispatch` and `createStore`, with optional lower limits/clock.
The generated policy uses local-only invocation. `createStore` implements the
DomainSpec RequestCustody interface; `dispatch` must await `beforeAttempt` before
any transport and emit actual transport settlement plus stream terminal events.
Local failure is not evidence of remote termination. Custody lifetime remains
independent of the provider caller's deadline.

Reference: [inference custody](../alchlang-extensions/inference-router-v1/custody/README.md).

## Open Questions

Durable backends, other targets and independently reusable service evidence are
owned by the [inference service plan](../alchlang-extensions/inference-router-v1/SERVICE-PLAN.md#open-questions).
