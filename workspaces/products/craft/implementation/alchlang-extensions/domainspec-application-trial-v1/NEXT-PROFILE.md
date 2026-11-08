# Proposed commerce-compatible profile

Candidate design; no new profile is active. Preserve the current
`domainspec-1.0.0` behavior until a separately tested target contract exists.

## Numeric definition prototype

`AlchLang UInt64` is an exact integer from zero through 18446744073709551615.
Calculation inputs accept bigint, canonical unsigned decimal strings, and safe
integer Numbers. Results are bigint. Overflow, underflow, zero division and
inexact division under rounding=reject remain causal errors. Floor/ceil rounding
uses integer arithmetic. No implicit conversion of an unsafe Number is permitted.

`Target numeric binding` identifies the representation used by every record
field, literal, mapping clause, arithmetic expression and policy comparison. It
must preserve that range or state a narrower domain restriction supplied by the
domain owner. The current commerce source supplies no narrower restriction.

Recommended design: an explicitly versioned exact-UInt64 TypeScript realization
contract in DomainSpec, followed by an AlchLang profile bound to that contract.
Changing the stable 1.0.0 output under the existing identifier would obscure the
compatibility boundary. A safe-integer-only application variant is a separate
modeling decision and is not a transparent migration of this source.

## Ontology and product scaffold additions

Proposed concepts: Numeric Representation Contract, Target Compatibility Gap,
Query Evaluation Contract. A compiler binding selects a Numeric Representation
Contract; a declaration may expose a Target Compatibility Gap; a Query declaration
conforms to its Query Evaluation Contract. These are unregistered prototypes.
They extend the compiler/business model, not the commerce customer's ontology.

Product outcome: a system builder can migrate the unchanged commerce model and
obtain equivalent results and failure behavior across the tested input domain.
Business condition: incompatible input retains its owner, exact source and reason.
No successful migration claim exists while any declaration is omitted or weakened.

## Query definition prototype

OpenOrders reads only supplied rows. It filters status=open, sorts by amount
descending with original-order stability for ties, limits after filtering and
sorting, and projects only order_id and amount. Missing required predicate,
sort or projection values fail causally. Inputs and rows are not mutated; no
provider is inferred. Parameter names and row facts retain the evaluator's
precedence rules. Numeric ordering shares the numeric representation contract.

## Runnable construction sequence

1. Add exact numeric-contract fixtures at 0, 100, 101, MAX_SAFE_INTEGER,
   MAX_SAFE_INTEGER+1, UINT64_MAX-5 and UINT64_MAX, including every arithmetic
   failure and rounding mode. Establish the versioned DomainSpec realization.
2. Independently specify query filter/sort/limit/projection behavior, including
   empty sets, ties, missing fields and stable input order.
3. Lower integer records, parameterized calculations, numeric mappings, queries
   and threshold policies with explicit bindings. Expose checked generated entry
   points; policy selection must not execute a selected calculation.
4. Run the unchanged application against generated code and the original
   evaluator, comparing both values and failures. Require deterministic complete
   artifacts, source traces and no-overwrite behavior.
5. Bind one new candidate digest for product review. Any product approval remains
   a separate owner decision; publication and deployment remain separate effects.

Steps 1 and 2 are product construction. The current target incompatibility blocks
step 3's complete migration, not independent prototype work. Operational packaging
is deferred to the repository maintainer and is not a prerequisite for these
prototypes. This design does not authorize a new published compiler version.
