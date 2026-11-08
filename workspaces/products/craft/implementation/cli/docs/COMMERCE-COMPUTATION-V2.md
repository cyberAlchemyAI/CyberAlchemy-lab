# Checked commerce computation domain

`createCommerceComputationDomainOwner(stage, source)` binds the existing v2
computation contract to a genuine original Core source-stage owner and handle.
Its `check(contract)` first performs the source-bound component comparison.
It then derives the executable type and named-call layout under the source's
configured AST, depth, loop and call bounds.

```typescript
const domains = createCommerceComputationDomainOwner(stage, source);
const domain = domains.check(sourceDerivedComputationContract);
const info = domains.inspect(domain);
domains.assertCurrent(domain);
```

The inspected contract preserves the complete checked domain: bounded strings,
transparent refinements, nested records, closed enums and payloads, bounded
lists, optional none/some and StateMachine outcomes. Symbol bindings retain
the real module/version/file hash and original declaration span for every pure
function and value definition. Names and wire property case remain exact.

The layout accompanies the existing `ExprV1` v2 AST. It introduces no additional
execution language or meta-type. Every executable node has an exact AST path,
checked type and declared owner. Record invariant expressions have their own
paths. Preconditions remain embedded once in the body; the layout does not add
a second execution of their metadata.

Each declared call retains its target kind, parameter order/types, result,
per-function rounding and evaluation-error action. Original hygienic lets
preserve authored named-argument order. A Policy action separately identifies
the chosen Calculation and its exact eventual invocation path, including
argument lets. A future runtime must observe entry at that callsite rather
than infer invocation from a selection record or from another nested call with
the same target name.

Layout array order is compiler traversal order. Runtime evaluation order comes
from the existing checked AST: short-circuit conditions, source-order arguments,
stable cases and source-order collection traversal. The layout is not an eager
evaluation schedule. Schema and call-graph analysis memoize shared dependencies;
repeated references do not expand every possible path through the DAG.

`info.contract_sha256` binds the actual computation and all its constraints.
`info.environment.subject_sha256` binds type/call layout only. It must never
replace the contract identity, original source capture or original owner handle.
Inspections and projection helpers return frozen data; matching JSON, a hash,
copied methods, proxies or casts cannot restore computation-domain custody.

The owner checks its own implementation and its original source-stage parent
before later use. Physical source/code replacement, captured asset changes,
parent disposal and domain disposal reject. A new factory in a process that
has already loaded changed implementation code cannot silently adopt the edit.

## Remaining EC08 implementation

This step implements the checked v2 domain environment. The evaluator, native
TypeScript emission, Rule/Operation argument/result bindings, declared failure
propagation and real generated price/guard component tests remain required.
The unchanged v1 computation checker/evaluator/emitter stays available for its
own previously qualified domain. v2 data cannot be relabeled as v1 by erasing
enums, refinements, optionals, nested values or function-specific behavior.

Later generation must retain exact bigint/decimal semantics, structural equality,
bounded native validation, source identities and full resource accounting.
An evaluated false Rule is a successful Boolean value; arithmetic, validation
and resource errors remain failures with their original source and declared
caller action. Pure code cannot read a store, call a provider or alter lifecycle
state. No per-feature JavaScript business formula or fabricated error callback
can provide the required runtime evidence.

## Open Questions

EC08 remains in progress until its actual generated pure price/guard bindings
and scoped runtime checks pass. EC09 owns bounded boundary codecs/producers;
EC12 owns actual public build/native capture and affected installed replay;
EC13 owns the whole generated pricing slice. Original source/semantic/review
and selected profile/native/application ownership remain separate. Formal claims
are optional. Hosting, TDE, EVF, publication/deployment and live activation remain
deferred.
