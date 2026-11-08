# First real provider evidence adapter

Scope disposition: deferred outside the owner-selected [local inference pattern](../../local-pattern/DESIGN-AND-PLAN.md). The provider choice below is historical and is not a blocker for current work.

Status: source-backed planning candidate; provider selection pending. No verifier
implementation or provider-compatibility claim is made by this plan.

## Source findings

- [Dispatch contract](../../DISPATCH.md) explicitly identifies a fixture protocol
  and requires selection of a real provider contract and matching mappers.
- [Request mapper](../../provider-request.alch) emits fixture messages/model/
  max_tokens/stream. It does not carry the custody request identifier or fingerprint.
- [Response mapper](../../provider-response.alch) accepts answer/stop_reason and
  optional token counts. It does not retain a provider response/operation identifier.
- [HTTP adapter](../../../../alchlang/src/http-invocation-adapter.ts) sends
  only content-type and bearer authorization headers and returns status, media
  type and bytes. It does not persist provider correlation headers.
- Reconciliation port (source binding requires reconciliation)
  requires exact request, scope, fingerprint and provider-attempt evidence.
  A retrieved result alone cannot satisfy that binding without trusted correlation.

## Product construction

Current frontier: the trusted reconciliation port is implemented and tested;
real-provider verification is unbound. D65 chain: approved custody meanings →
selected provider contract and correlation design → authored provider mappings and
native evidence adapter → exact contract/transport/restart tests. No ontology
record or selector is required.

1. Select the provider and exact API product. Verify its official contract for
   durable result retrieval, terminal status, request correlation, retention and
   streaming. Determine which crash windows are recoverable; do not assume that
   every API exposes a queryable operation or that a missing result proves failure.
2. Define and persist trustworthy local-to-provider correlation at the earliest
   supported boundary. Bind local scope/request/fingerprint, provider binding and
   provider operation identity. Existing uncorrelated records stay unresolved.
3. Author the provider request/response mapping. Keep provider schema translation
   in Alch/DomainSpec and endpoint/credential custody in the trusted adapter.
4. Implement resolveEvidence with an operator-fixed origin/account, bounded reads,
   cancellation/deadline, strict result schema and exact correlation checks. The
   caller supplies an opaque reference, never a fetch URL or replacement outcome.
5. Test matching/foreign requests, wrong account/model/binding, pending/missing
   results, cancellation, oversize responses, restart and replay authorization.
   Live paid inference and operational activation require their own exact scope.

Runnable now: source inspection and this plan. Completed during this turn.
Causal blocker for provider-specific code: no real provider/API product is selected
in the repository or conversation. The user has been asked for that choice.

## Operational support

Operator-owned credentials, account retention settings, optional live rehearsal,
audit export and deployment are separate residue. They do not block local fixture
and contract tests once the provider/API contract is selected. No credentials,
running hosts, provider configuration or existing custody records were changed.

## Open Questions

Required next decision: which real inference provider and API product should be
implemented first? This is a target clarification, not an implementation approval.
After selection, official API evidence must resolve correlation and retrieval
support. Unrecoverable crash windows must remain explicitly unresolved.
