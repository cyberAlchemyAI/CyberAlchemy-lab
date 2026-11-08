# Guarded bindings prototype

A guarded binding is an ordered module invocation with a Boolean predicate.
`bind shipping from ShippingPrice when HasPrice` evaluates the guard before
resolving credentials, validating module arguments, or starting transport. False
means skipped, with no output root and no module request. Guard errors fail the
invocation. A guard can use input and earlier bindings only.

Existing Rule, Query and Mapping definitions retain their meanings. The compiler
checks conditional output availability through named rules and ordered Boolean
short circuiting. It uses structural implication (and/or/not and rule expansion),
not a general theorem prover. It rejects unproved reads and forward dependencies.
Result conditions are all evaluated; only the unique selected value is evaluated.
Each guard and the final behavior use separate memoization scopes on both targets.

Ontology scaffolds derive guard expressions and dependencies from source, without
admission. Trace events distinguish binding-guard, module-skipped, module-start,
module-result and module-error; guard errors use binding-error.

Product candidate: checkout with local and HTTP shipping guarded by a pricing rule.
Success evidence: matching Node/Rust outcomes and traces, zero shipping calls for
no-price/ambiguous results, and rejected unsafe/cyclic contracts.

## Open Questions

Deferred: should later versions support conditional provider-GET bindings,
input mappings from prior module outputs, stronger logical implication, or shared
guard/result memoization? None is needed for this candidate. Live provider identity
and deployment remain operational work outside this construction scope.
