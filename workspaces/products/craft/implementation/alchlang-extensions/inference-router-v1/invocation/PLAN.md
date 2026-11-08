# ISB-05 construction plan

Completed local candidate, owner-directed local implementation; authority effect: none.

## Construction boundary

Reuse the [Define-backed dependency meanings](../service-contracts-v1/README.md)
and their business/product scaffolds. DomainSpec owns a closed normalized
request/response composition contract and the HTTP attempt interface; Alch owns
its syntax, typed module linking and generated bundle. Existing declarative
functions remain the mapping/selection compiler. Raw HTTP is a new dependency,
not a change to status-bearing module-http or pub/sub system integration.

Implement sequential typed local calls, fixed binding resolution and exactly one
HTTP attempt. Author stage wiring, status rejection, byte/deadline/concurrency
bounds and public result projection. Native adapters own operator URL/secret
configuration, monotonic time, sockets and cancellation. Caller outcome and
actual transport settlement remain independent. Stream parsing/lifecycle and
custody stay at the existing boundaries until ISB-06/07.

## Verification and frontier

Run normalized-contract negative tests, generated local and loopback HTTP
witnesses, cancellation/late-settlement tests and all existing inference/service
regressions. Verify compiler bindings, bundle inventories and paired Craft
links before marking ISB-05 complete. Runnable work is this unit; no live-provider
or deployment dependency exists. Compiler owners own reproducible local builds;
operators own future providers, tokenizers, storage and hosting. Tenant security
remains ISB-09.

## Open Questions

No blocking choice for the local candidate. Stream lifecycle generation,
atomic custody, independent full-service reuse and tenant security remain owned
by [the shared plan](../SERVICE-PLAN.md#open-questions).
