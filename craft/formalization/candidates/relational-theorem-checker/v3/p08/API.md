# Fresh local candidate application API

Use one `ShadowContext(resource_policy)` instance for preparation and commit. The public input policy is the unchanged closed P01 resource policy. A whole application deadline includes proposal checking, mapped checking, independent successor registration and publication. Required memory enforcement is refused before a worker launches when the host lacks delegated controls; advisory mode remains explicitly advisory.

```python
context = ShadowContext(policy)
initialized = context.bootstrap(new_owned_store_path, identity_extension_request)
store = Store(new_owned_store_path)
raw = exact_request_bytes
review = store.review(request, raw, mappings=mapped_requests)
result = context.apply(review, raw, store, mappings=mapped_requests)
```

`bootstrap` freshly registers the exact initial baseline; an identity-extension request has equal `before` and `after`. Creation is restricted to a new directory below P08's `stores/`. Direct unqualified initialization is permitted only for explicitly labeled metadata fault probes.

`Store.review` records an exact local candidate review. Its default reviewer is `author-integration-fixture`; it is not user feedback or project authority. The review binds the ordered mapped request list and each context identity in addition to proposal and head. A changed condition, interpretation, epoch or list therefore invalidates that review.

`prepare` returns `prepared-candidate-shadow` and an opaque handle only after all fresh checks finish. `commit(handle, store)` accepts that handle once in the same live context. A new context and a saved result cannot supply it. `apply` composes both operations. A stale starting generation returns `stale-head` without publishing. Failure outcomes retain candidate-only authority and must never be interpreted as an absence theorem.

Every applied successor has an immutable snapshot and separately qualified registration. The transaction binds proposal qualification, successor registration, and fresh mapped completions. Different mapped contexts remain individually checked; no cross-context truth merging is supported.

Runtime qualification evidence from the accepted P07 API is written under P07's `consumer-runs/P08*` directories. P08 implementation, schemas, metadata stores, mapped jobs, reports and recovery documentation remain inside P08. That runtime side effect uses the accepted API's ownership boundary and does not modify an accepted source artifact.

See [recovery.md](recovery.md) for exact crash outcomes and what to preserve on reconciliation. A recovered committed application is reported as applied; an exception is never treated as proof that the head was unchanged.
