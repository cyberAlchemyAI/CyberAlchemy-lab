# Declarative functions (prototype)

`profile declarative-function-v1` declares read-only behavior through existing Mapping, Query, Rule and Calculation meanings. Alch parses declarations into a typed contract; the selected DomainSpec 1.0.0 public API validates and generates the behavior module. A transport-only runtime provides schema validation, integration fetching and HTTP handling. The emitted bundle contains no flow interpreter.

Example with derived ontology: `../../extensions/derived-ontology-v1/quantity-price.alch`. Ontology blocks and IDs are optional; see [ontology derivation and inspection](ONTOLOGY.md).

```sh
node dist/cli.js check ../extensions/declarative-function-v1/quantity-price.alch
node dist/cli.js build ../extensions/declarative-function-v1/quantity-price.alch --target node-http --out /tmp/new-quote-bundle
```

The output directory must not exist. Build DomainSpec and Alch first. Version 1.0.0 alone is insufficient: the selected public API must expose `DECLARATIVE_FUNCTION_PROFILE` and `compileDeclarativeFunction`. A build without that feature fails explicitly. This is an opt-in local profile, not a claim that every published 1.0.0 package supports it.

## Declarations

```text
mapping PriceRow:
  meaning "Convert a provider row to exact minor units."
  input row: Price
  target PriceTier
  field priceId = row.id
  field amountMinor = decimal(row.raw_amount.value, 2)
  ...

query Cheapest:
  meaning "Every eligible row for which no cheaper eligible row exists."
  from p in Eligible
  where not (exists q in Eligible: q.amountMinor < p.amountMinor)
  select p

rule UniquePrice:
  meaning "Exactly one cheapest witness exists."
  condition exactly_one p in Cheapest: true
```

The mapping excerpt is abbreviated; `...` is not syntax. A Mapping declares a target record and every required field. It may accept one typed input or depend on named root/declaration values. A Query has a finite source, binding, boolean filter and projection. A Rule returns Bool. Declaration order does not determine evaluation order; references form a checked acyclic graph. Derived collections and zero-input mappings are memoized per invocation.

Expressions support field paths, literals, scalar calls and boolean/comparison operators. `exists`, `forall`, and `exactly_one` quantify finite collections. `one(collection)` produces a witness only when cardinality is exactly one. `column`, `distinct` and `sort` are typed collection projections; there are no user-authored lambdas, arbitrary object expressions, assignments or procedural flow clauses.

UInt64 values use bigint throughout this profile. `decimal(text, scale)` rejects negative, noncanonical, overprecise and overflowing amounts. `format(value, scale)` formats exact amounts. `uint64` converts a safe integer or canonical integer string; `optional_uint64` preserves a null/missing value for `coalesce`. Scale must be a literal from 0 to 18. Optional paths must be handled explicitly; mixed Int/UInt64 comparisons are rejected. Existing core Calculation declarations generate through the established exact UInt64 backend.

## Results and bindings

A `result` declaration is the outer read-only Query composition:

```text
result QuotePrice:
  bind snapshot from Prices
  require lower(input.request.currency_code) == "usd" else "QUOTE_UNSUPPORTED_CURRENCY"
  when NoPrice yield EmptyQuote
  when UniquePrice yield SelectedQuote(one(Cheapest))
  when AmbiguousPrice yield AmbiguousQuote
```

Exactly one result condition must match at runtime. Only its output mapping is evaluated. Assertions must be Bool; all results must match the endpoint's named output record. Schema constraints are also enforced by the boundary at runtime. Input-only assertions consisting of supported scalar operators are checked before fetching; snapshot-dependent assertions run after binding validation.

`schema`, `integration`, core `ontology`, and `endpoint` clauses retain the boundary forms documented in FUNCTIONS.md, with `result QuotePrice` replacing the endpoint's `flow` reference. Secrets remain environment references; request size, timeout, upstream size, method/path, output schema and status mappings are authored in the same `.alch` file. Integration transport is the explicit Alch node-http target adapter; it is not a claim of provider-neutral DomainSpec runtime conformance.

The generated package exports `invoke` and `handler` from `index.mjs`, plus a Node HTTP launcher. `ontology.json` records the source-linked generated ontology, `composition.json` records DomainSpec-owned typed behavior, `composition-trace.json` records meanings and declaration dependencies, and `behavior.mjs` contains generated code. The core DomainSpec graph/certificate covers its original core scope; the additional composition artifact is a candidate contract extension, not part of that certificate. Compiler dependency references are not fabricated ontology edges.

## Open questions and limits

This bounded prototype is TypeScript/Node-only and read-only. It adds no new meta-type, registry admission or factory automation. Integrating composition into the full DomainSpec project certification pipeline and adding other language targets remain open. Cheapest-price quantification is quadratic in the bounded snapshot size (at most 1000 rows here). Logical conditions are executable predicates, not a claim of an external theorem prover's certification.

Construction status, acceptance requirements, test evidence and deferred operational work are owned by `../../extensions/declarative-function-v1/PLAN.md` and its README.
