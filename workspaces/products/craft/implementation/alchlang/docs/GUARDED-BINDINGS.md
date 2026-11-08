# Guarded module bindings

In `declarative-function-v1`, a module binding may carry a Boolean condition:

```alch
rule HasPrice:
  meaning "Pricing produced a usable item quote."
  condition pricing.status == "quoted"

result QuoteCheckout:
  bind pricing from ItemPrice
  bind shipping from ShippingPrice when HasPrice
  when NoPrice yield NoPriceResponse
  when AmbiguousPrice yield AmbiguousResponse
  when ShippingUnavailable yield ShippingUnavailableResponse
  when Quoted yield QuotedResponse
```

This fragment belongs to the complete examples in
[`guarded-bindings-v1`](../../alchlang-extensions/guarded-bindings-v1/README.md).
Both `module-local` and `module-http` support guards. A guard can use existing
Rules, Queries, Mappings, Calculations and SFOL predicates whose root dependencies
are input or previously bound outputs. Bindings run in authored order; the compiler
rejects forward references and cycles. Other integration transports retain their
existing unguarded behavior.

A false guard skips the call before credentials, argument resolution, or transport.
The skipped binding has no output. The enclosing endpoint still validates its
input envelope, including embedded module inputs, before any binding executes.
A guard evaluation error fails the invocation; it is not a false condition.

## Safe reads

Use the guard first in a conjunction:

```alch
rule Quoted:
  condition HasPrice and shipping.status == "available"
```

A selected result mapping can read shipping when its case condition implies
`HasPrice`. An assertion can use `not HasPrice or shipping.request_id == input.request_id`.
The reversed conjunction, an unconditional shipping read, or a mapping selected
by a no-price case fails compilation. A later binding's guard must also protect
any reads of earlier conditional outputs.

DomainSpec checks these rules through the expression graph, including named
declarations, mappings and quantifiers. Its proof is conservative: structural
`and`, `or`, `not`, repeated predicates and named Rule expansion. It does not infer
arbitrary arithmetic relationships, prove predicate completeness or perform
automatic scheduling. Equivalent predicates outside this fragment may need an
explicit shared Rule. Passing a preceding assertion is not used to narrow later
reads; use explicit guard conditions.

## Generated behavior and evidence

Alch lowers the guard into the DomainSpec typed composition contract. DomainSpec
emits predicate code for Node and Rust; no expression interpreter is shipped.
Each guard and final result evaluation has its own memoization scope, so a Rule
may appear more than once in a trace. Observers cannot change invocation behavior.

`binding-guard` records the binding and Boolean decision; `module-skipped` records
a skipped module. Invoked modules retain `module-start`, `module-result`, and
`module-error`. Guard evaluation failures emit `binding-error`. Traces preserve
the source declaration and module scope.

The derived ontology includes the result's guarded binding contract, a
`conditionally-binds` reference, and dependencies from the integration to its
guard declarations. These are compiler-derived scaffolds, not admitted relations.

The controlled conformance suite checks outcomes, errors, requests and ordered
decisions on both targets. A separate assertion checks zero shipping requests and
zero Shipping starts for no-price and ambiguous-price cases. This evidence does
not establish a live provider's identity, production readiness or deployment.

Open questions: [candidate specification](../../alchlang-extensions/guarded-bindings-v1/SPEC.md#open-questions).

Guarded bindings can also use [module-input mappings](MODULE-INPUT-MAPPINGS.md).
A false guard skips the Mapping as well as the module call.
