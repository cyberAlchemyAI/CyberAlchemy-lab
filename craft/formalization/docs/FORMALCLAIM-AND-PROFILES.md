# FormalClaim identity and formal profiles

This is a derived explanation. Canonical contracts are JSON and JSON Schema.

## One claim, several ways to check it

A FormalClaim has one canonical proposition, one declared formal signature,
and one exact accepted-definition closure. We may check that meaning with Lean,
SMT, TLC, Alloy, Souffle, generated runtime
tests, or another provider. These are not separate FormalClaims unless a
meaning-bearing input changes.

Each provider gets a projection. The projection records its domain, finite
bound when present, result semantics, known losses, and preservation direction.
This makes provider diversity useful without creating several competing truth
sources.

## Current and candidate FormalClaim contracts

`FormalClaimSourcePayload/v2` is the current implemented source envelope and the
current TDE intake. It contains one canonical proposition and exact business,
profile, and interpretation bindings. It deliberately excludes proof terms,
solver outcomes, executable profiles, and release state.

`FormalClaimSource/v3-candidate` is retained as predecessor evidence. It bound
an InterpretationModel into claim identity and is superseded by the v4
candidate design.

`FormalClaimSource/v4-candidate` exact-binds accepted BusinessMeaning through
an explicit definition graph and carries its own formal signature. It has no
InterpretationModel field. A later evaluation request may join an exact
InterpretationModel as external context, but that join does not redefine the
claim. Until TDE changes its intake, a v4 candidate still requires one exact v2
projection and explicit admission. An adapter cannot repair, add, or
reinterpret meaning.

FormalClaim identity changes when any of these change:

- BusinessMeaning identity;
- explicit definition-binding graph and its accepted definition closure;
- formal signature;
- canonical proposition semantic identity;
- meaning-bearing formal-language profile semantics;
- assumptions, domain, universe, time, or currentness rules;
- claim ceiling.

InterpretationModel identity, provider version, native syntax, runtime
environment, or execution limit does not change the FormalClaim. Those changes
invalidate an evaluation context, projection, or evidence binding.

A claim marked current must bind current meaning, business acceptance,
definition graph, language profile, and identity algorithms. Every definition
edge is explicit and digest-bound; consumers may materialize a
definition-complete envelope, but copied external references remain opaque
traceability metadata and the envelope is derived, not definition authority. A v2
projection, when attached, must also be exact and current. Schemas carry path,
digest, size, and currentness; a consuming runtime must dereference those
identities before treating the claim as current.

## Profile roles

- **Lean/DTT:** canonical proposition and separate EVF theorem-provider route.
  It uses an exact FormalClaimLeanBinding, theorem request, runtime binding, and
  theorem evidence. A checked theorem is bounded to the exact Lean model. It
  is not runtime conformance evidence.
- **FOL core:** a precise source language with an explicit signature and
  definition closure. It is not itself an executor.
- **SMT/SFOL:** a solver route. `sat`, `unsat`, `unknown`, and timeout keep their
  native meanings.
- **TLA/TLC:** bounded temporal state exploration, not an unbounded theorem.
- **Alloy:** bounded relational instances or counterexamples under exact scope.
- **Souffle:** finite closed-world derivation under exact facts and rules.

The registry describes candidate semantics and routing. It does not admit a
profile or prove provider availability.
