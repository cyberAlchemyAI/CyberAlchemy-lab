# P04 implementation plan and design review

P04 begins only after accepted P03 evidence. This document prepares the implementation; it is not an implementation or completion claim.

## Definition and theorem first

Use the retained Inference.Atom, Theory and AtomValid definitions. An absence diagnostic requires a valid exact predicate key, a declared predicate with matching arity/sorts, domain membership for each value, and a completed checked closure. The formal target is:

`absence(T,C,a) -> AtomValid(T,a) and complete(C) and a not-in C`.

With the independently checked closure adequacy hypothesis `a in C iff Derivable(T,F,a)`, absence implies `not Derivable(T,F,a)`. This conclusion applies to the selected finite positive profile and its fixed supplied initial facts. It is not absence in every larger model, absence in an unselected source language or falsity of an externally supplied claim.

## Public interface

`describe(request, result, query=None, context=None, trace_nodes=256, output_bytes=32768)` returns a closed Explanation variant. Recursive qualified results must pass P03 saved inspection before closure/certificates are read. Reading bound payload bytes must check the exact buffer digest before decoding. No explanation creates a replay event or application authority.

For recursive queries, reject malformed JSON atom shapes first. Unknown predicate identity, version or digest is outside-profile. A known predicate with wrong arity or sorts is invalid-query. Correct sorts with an undeclared finite-domain value is outside-profile. A well-typed in-profile request against incomplete computation is incomplete. Only inspected complete computation can yield present or absent-in-complete-profile. Without a query, return a summary variant.

## Trace and supports

Build a bounded certificate DAG rather than recursively duplicating premise trees. Each apply node includes the exact rule key, ordered variable-slot substitution and earlier premise indices. Recheck each premise conclusion against the bound rule instance. Base source observations retain all supports for the exact atom; other base atoms remain explicitly supplied truth, including independent root receipts.

A rendering cutoff is distinguishable from incomplete closure. Do not disguise omitted premises as source leaves. If the output byte envelope cannot retain the required support information, return an incomplete explanation without an absence/readiness claim. Keep target, scope and target-kind data visible in the worked trace; unary summaries lose those distinctions.

## Mapped stress variants

A dedicated read-only interpreter imports only the accepted mapping adapter, validates the exact request/schema/source/interpretation, rechecks every module/dependency source and compiled binding, and regenerates the exact concrete witness source using the displayed checked fields. It performs no new qualification or application.

Inheritance explanations expose separate potential norms, condition verdict, active norms and active conflicts. Fulfillment remains not-established and admission remains not-derived. Delegation explanations expose the exact agent/principal/delegation/action/scope/epoch and the mapped typed verdict. They do not advertise chain support or whole-graph qualification. Do not render unused caller-modifiable typed-response certificates as checked facts.

## Validation and review

Use actual inspected combined and staged witnesses with the same typed query. Show an exact positive target/scope/kind derivation, a complete wrong-scope empty cycle, a timed-out result and a supplied root/ordinary leaf. Query controls cover unknown id, wrong version/digest, wrong arity, wrong sorts, undeclared scope and malformed reference values.

Hostile evidence controls alter a support leaf, remove a split module, mutate a mapped active norm, change a mapped verdict, and introduce forward/cyclic certificate indices. These must fail inspection or trace validation. Rendering tests prove bounded DAG expansion, distinguish cutoff from an incomplete search, and bound output.

Review that every displayed claim is a consequence of the inspected exact bytes, every untrusted input remains labeled, both layouts share one path, and no mapped norm/delegation verdict upgrades admission or fulfillment.
