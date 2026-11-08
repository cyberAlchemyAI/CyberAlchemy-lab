# Original Operation callsites and pure computation components

An Operation can call a Calculation, Rule, Mapping, Policy or StateMachine.
The source-call binding connects that exact source call to its checked pure
callee and the source caller's outcome handling. It does not execute the entire
Operation or create an authenticated request, transaction or native context.

This is EC08 candidate component work. The parent domain and pure runtime are
described in [COMMERCE-COMPUTATION-V2.md](COMMERCE-COMPUTATION-V2.md) and
[COMMERCE-COMPUTATION-RUNTIME-V2.md](COMMERCE-COMPUTATION-RUNTIME-V2.md).

## Binding source calls

`createCommercePureCallOwner` requires a genuine Core source-stage owner/handle
and a genuine checked computation-domain owner/handle for the same source
capture. It checks an `EffectPlanV1` proposal against the original captured
Operation through the existing semantic component. A matching JSON proposal
remains data; the private factory issues and retains its own call binding token.
Cloned owners, cloned tokens and serialized inspections cannot restore it.

`paths(plan)` lists the original pure call paths. This is source layout, not an
execution schedule. `bind(plan, path)` retains:

- The original caller selector, module identity, declaration span and plan hash.
- The exact call path, enclosing role expression, original arguments and
  named-argument hygienic lets.
- The original pure callee's identity, span, signature, contract hash, rounding
  and declared error action.
- Lexical caller error/false actions and original transaction requirements.
- Native observations, private contexts and local projection requirements that
  the actual caller still needs to satisfy at their original positions.

Parent disposal or source/implementation replacement invalidates the binding.
There is no public callback, formula, context-constructor or evaluator argument.

## Example: PlaceOrder

In the current ecommerce source, the three relevant paths are:

| Original Operation path | Pure callee | Original outcome handling |
| --- | --- | --- |
| `$.body[18].value.expression` | `Orders.MerchandiseSubtotal` | `on-error fail calculation-failed` |
| `$.body[19].condition.expression` | `Orders.CanPlaceOrder` | `on-false reject quote-ineligible` |
| `$.body[20].value.expression` | `Orders.PayableTotal` | `on-error fail calculation-failed` |

The eligibility call retains the private `customer.customerId` source argument.
Supplying a scalar customer ID to the isolated Rule component does not acquire
that private context or authenticate the supplied customer. The generated
Operation must obtain the original context through its native owner before
evaluating the source argument. The binding preserves that requirement.

`evaluateBoundParameters(handle, bytes)` evaluates already-bound pure parameters
through the genuine domain evaluator. A subtotal input therefore contains the
callee's `lines` parameter; it does not pretend to execute the caller's earlier
quote query or evaluate `quote.lines` against a private Operation frame. Source
argument acquisition and full caller execution remain the later role/native
composition work. The captured budget applies to this checked pure evaluation;
it does not establish a shared whole-Operation or caller-loop account.

## Outcome handling

A successful pure value retains its wire result. For a completed direct Bool
guard, `true` proposes continuation and `false` retains the caller's original
false action. A pure call inside `Rule(value) and anotherCondition` is only part
of the guard, so its Bool is returned as a value. The adapter cannot treat it as
the result of the entire guard.

Parameter validation errors retain their original fault and phase without
becoming a false guard or a business error action. Pure evaluation errors retain
their original expression/index/call paths, callee error actions and the
caller's lexical `on-error` action reference. Error actions and false actions
remain distinct. Calls in a handler expression do not inherit that same handler.

Actions are proposals for the original caller. A transaction action explicitly
requires original proven rollback before application. The pure adapter never
performs rollback, commits a write, sends a request or acknowledges an event.
Return/invoke-return actions remain hashed source-action references; the adapter
does not serialize or execute those action expressions.

## Generated artifacts

`compileCommercePureCallBundle` emits two TypeScript members: the actual checked
pure computation and an outcome adapter importing that deterministic sibling.
The manifest binds every member hash, the complete source-call inspection and
the underlying pure component manifest. The adapter exports
`evaluateBoundParameters(bytes)`. It takes no injected module or evaluator.
Its fixed typed outcome helper must exactly match the owning runtime helper.

Tests must load the actual generated siblings and compare results, source action
proposals, faults and fuel with the source-bound reference component. Strict
TypeScript checks and source/member correspondence are separate checks. These
are pure-component artifacts; selecting/capturing an installed realization or
executing the full original caller requires the later plan joins.

## Open Questions

Actual caller argument/context acquisition, shared caller-expression accounting,
transaction execution and complete Operation generation remain original
EC11/EC12/EC13 work. EC09 owns native codecs and identity/clock producer assets.
The current test receipts and unresolved EC08 closure questions are owned by
`implementation/craft-alchlang-commerce-2026-10-16/evidence/EC08/` at repository
root. Formal claims are optional. Local hosting, TDE, EVF, publication, deployment
and live services remain deferred.
