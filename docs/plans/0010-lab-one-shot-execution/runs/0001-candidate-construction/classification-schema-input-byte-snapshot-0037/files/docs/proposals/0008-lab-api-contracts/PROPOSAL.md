# Lab local API contracts

Status: **candidate design; no API handlers or server implemented by this package**. This follows [schema review 0001](../0007-lab-integrated-schema-package/reviews/0001/REVIEW.md).

## Produced

- 34 closed operation contracts with exact request/result/error schema bindings.
- Five JSON schemas: correlated call, reply, transport error, adapter-resolved trusted context and the machine-readable contract catalog.
- Four representative messages per operation: invocation, separate domain request, result reply and error reply; two transport errors and one illustrative trusted context.
- Explicit caller/authority requirements, effects, source-cut preconditions, deadlines, idempotency, paging, recovery and completion limits.

The reviewed schema package now has 80 candidate protocol schemas, 79 shape messages and eight additional bootstrap/inspection messages beyond its original version. Existing 143 domain versions, four storage schemas and SQL read model remain unchanged.

## Design choice

Use one **local callable API**: `handle(call, adapter_resolved_trusted_context)`. A future authenticated local stdio adapter can carry UTF-8 JSON calls and replies using these same contracts. CLI or Agent tool adapters delegate to the same application services. The primary implementation path remains local; these contracts introduce no network listener.

The public call contains a scoped context handle. The adapter derives authenticated identity and verifies the associated context. Role/capability names in a message are claims to check; they cannot grant themselves authority.

## Review navigation

1. [Complete operation list and descriptions](API-CONTRACTS.md).
2. [Exact call, reply and trust boundary](INTERFACE.md).
3. [Authority, effects, freshness, hashing, retry and recovery rules](POLICIES.md).
4. [Errors and negative results](ERRORS.md).
5. [Workflow examples](WORKFLOWS.md).
6. [Authoring review and evidence](REVIEW.md).

Machine-readable sources are [api-contracts.json](api-contracts.json), [individual operation records](operations/lab.status.json), [schemas](schemas/api-call.schema.json) and the [example index](examples/index.json). The [authoring receipt](receipts/api-authoring.json) binds exact package files and source schemas.

## Authority and completion

Reading, candidate preparation, ephemeral sessions, bounded local actions, canonical admission, ontology representation, projections, managed files and local installation have different effects. Only `admission.apply` applies the selected artifact admission transaction. A result reply can contain a blocked, denied, failed or indeterminate domain result; returning a reply is not operational success.

One final owner checkpoint can authorize the exact reviewed independent Decision members when the actual package and required evidence exist. Preparation cannot fabricate their owner outcomes. Future unknown effects remain outside that authorization. The selected contracts permit zero runtime activations and no external effects.

## Next implementation dependency

Resolve the selected semantic endpoint and workflow bindings, implement the application services and trusted adapters, then obtain the exact required implementation and operational evidence before admission. This package records contract authoring only.
