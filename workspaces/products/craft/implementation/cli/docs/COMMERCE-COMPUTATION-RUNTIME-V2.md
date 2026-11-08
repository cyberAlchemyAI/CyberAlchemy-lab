# Original-source computation execution and TypeScript emission

This is the EC08 candidate pure component. The checked domain owner described in
[COMMERCE-COMPUTATION-V2.md](COMMERCE-COMPUTATION-V2.md) supplies the original
source-checked v2 contract. The reference evaluator executes that contract. The
TypeScript emitter produces one direct function per expression and declaration.
The emitter carries a fixed typed helper template, which remains available when
the compiler itself runs as built JavaScript. Tests check its exact correspondence
to the owning value-kernel source, and the manifest records its digest. No compiler
API package is needed by this emitter or by its generated module.
The generated module has a declared `node:util` builtin dependency and no private
repository import, serialized expression interpreter or caller-supplied formula.
This work does not create a selected native basis or an application owner.

`evaluateCommerceComputation` returns the existing success/error wire result.
`evaluateCommerceComputationObserved` also identifies input validation, expression
execution and output validation, and returns bounded Policy decisions and
the declared error actions of entered pure declarations. Both require the genuine
domain owner and handle; changed source, changed implementation, disposed parents
and matching JSON substitutes cannot restore custody.

`compileCommerceComputationTypeScript` returns source plus a manifest tying its
hash to the original module identity, full source capture, checked contract,
typed expression layout, implementation epochs, declaration spans and generated
function names. Its standalone exports are `evaluate(bytes)` and
`evaluateObserved(bytes)`. Capturing and admitting this component as part of a
selected installed realization remains downstream work.

## Values and boundaries

Input and output are UTF8 JSON bytes. UInt64 uses canonical decimal strings on
the wire and exact bounded bigint arithmetic internally. JSON numbers, duplicate
decoded object keys, extra or missing fields, malformed UTF8 and invalid Unicode
scalars reject. The public evaluator takes an actual non-shared Uint8Array;
proxy, object and typed-array constructor hooks are not a business-input API.

Records have closed fields, recursive declared types and source invariants.
Scalar refinements retain minimum/maximum UTF8 and scalar lengths, their finite
source pattern and exact equality. Collection predicates remain declared Rules.
Compiler-owned invariant/predicate executors inspect checked values; application
code cannot supply an invariant callback. Structural validation precedes semantic
constraints so a predicate can inspect its own checked argument. Completed list
values receive their full predicate; an unfinished map/filter builder receives
only the partial size/capacity check.

Entirely nullary enums use their declared wire string and native variant name.
Algebraic or mixed enums use `{ "tag": "WireVariant", "fields": { ... } }` on
the wire and `{ kind: "Variant", fields: { ... } }` internally. Variant payloads
retain their declared fields. A single payload binder receives that payload;
a multiple-field binder receives the narrowed variant.

An optional is native `{ kind: "none" }` or `{ kind: "some", value }` and wire
`null` or the value. Nested optional boundary schemas explicitly reject with
`UnsupportedCapability`: the selected null-or-value wire convention cannot
distinguish `none` from `some(none)`. No nested optional support is inferred.

## Execution and errors

Expressions retain source order. Named arguments keep their existing hygienic
lets; positional arguments evaluate left to right. Boolean operators short
circuit. Record/enum construction, refinement validation, structural equality,
optional/variant narrowing, lists and declared pure calls retain their v2 types.
Each declaration uses its own rounding choice. Preconditions execute once in
their existing embedded body; the precondition metadata is not executed again.

Map, filter, fold, indexed fold, bounded repeat, bounded while/until and
end-exclusive range retain explicit bounds. Sorting decorates source items once,
compares declared keys in order and preserves equal-key source order. Modes are
exact numeric, Unicode scalar lexical and fixed ASCII-digit-run natural order.
Source state machines produce proposal values; they do not perform transitions
against an external store. Their initial/terminal declarations remain metadata
and their fallback reason remains the authored reason.

A Rule returning `false` is a successful Bool. Arithmetic, resource, domain and
iteration errors remain failures with original expression, index and call paths.
An entered declaration's `on-evaluation-error` action is reported separately
from the underlying evaluation fault. A failure while evaluating a callee's
arguments does not claim that the callee was entered. Policy observation also
distinguishes selecting a Calculation from entering its exact invocation site.

The original input/output/intermediate byte, item, loop, call and fuel limits
remain in force. Node, call, iteration, comparison and bounded byte/key work are
metered. Each node, entered call, loop iteration and sort comparison costs a
unit; UTF8 byte work costs one unit per started 32 bytes. Finite refinement
matching meters its explicit state work. Checked immutable values and append-only
list prefixes reuse their sizing work. These units are an explicit candidate v2
runtime cost model; the captured 100000-unit allowance is unchanged.
Observations use their separate bounded diagnostic allowance and can
report truncation without changing execution results.

## Verification scope

The execution suite lives in
`test/commerce/commerce-computation-execution.test.ts`. It loads real original
ecommerce source contracts and separate source-authored fixtures, emits and
imports standalone TypeScript, and compares results, faults, paths, fuel and
observations with reference execution. Literal expected outcomes independently
check pricing, guard booleans, arithmetic failures, loop results and sort order.
The durable current result and any retained failed attempts belong to
`implementation/craft-alchlang-commerce-2026-10-16/evidence/EC08/` at repository
root. A test file or successful typecheck alone is not a completion receipt.

## Open Questions

Selected native capture/build/replay, caller Operation error-branch binding,
value-codec integration and full application joins remain the original
downstream plan obligations. A lossless nested-optional boundary representation
needs an explicit future ABI decision if that domain is selected. Local hosting,
TDE, EVF, live services and publication remain deferred. Formal claims remain
optional.
