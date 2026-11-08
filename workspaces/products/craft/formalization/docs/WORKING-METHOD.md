# Formalization working method

This is a derived human view. The canonical method is
[`method/formalization-method.json`](../method/formalization-method.json).

## Why this exists

A business sentence is not yet a formal claim. A formal theorem is not yet
evidence about running software. This method keeps those meanings apart while
letting them connect through exact JSON artifacts.

The smallest useful path is:

1. **Scope** — choose one practical question, its owner, and its claim ceiling.
2. **BusinessMeaning** — write the rule in domain language with examples,
   counterexamples, boundaries, definitions, and owner acceptance.
3. **Definition binding** — declare every definition the claim uses through
   explicit graph edges. Include transitive dependencies; never infer a
   dependency from a term name.
4. **FormalClaim** — bind one canonical proposition to exact meaning,
   definition closure, formal signature, language profile, assumptions, claim
   ceiling, and identity inputs.
5. **InterpretationModel** — when evaluation needs one, define its types,
   predicates, equality, time, currentness, and vacuity checks as a separate
   evaluation-context artifact. It is not part of the FormalClaim.
6. **Capability assessment** — classify the exact claim and admit one bounded
   TDE, solver, theorem, model-checker, relational, Datalog, or non-pass route.
7. **Projection** — create a preservation-backed representation for the
   admitted route before executable TDE derivation.
8. **Route obligations** — TDE derives executable cases only from an admitted
   projection; theorem and other EVF lanes bind their own exact requests.
9. **Provider evidence** — run exact inputs in an exact environment and keep
   the native result, including unknown, timeout, and failure.
10. **EVF join** — bind evidence back to the exact claim and selected route
   subject: an execution obligation or theorem request. Only an exact, current,
   comparable result can become `PASS_BOUNDED`, and the case package must bind
   that exact EVF join.

## The identities that must not collapse

- BusinessMeaning says what the business intends.
- Definition binding says exactly which accepted definitions the claim uses.
- CanonicalProposition is the formal sentence.
- Formal signature declares the sorts, functions, predicates, and constants
  used by that sentence.
- FormalClaim binds meaning, definitions, signature, proposition, profile,
  assumptions, and ceiling into one semantic identity.
- InterpretationModel says how a later evaluation context interprets or
  realizes terms. It joins outside the FormalClaim.
- A capability assessment says which bounded route may receive the claim.
- An obligation is a consequence selected for checking after route admission.
- A projection is one provider-facing translation.
- Provider evidence says what one tool observed.
- An EVF join says what that evidence can support for one route subject.

A current FormalClaim requires current meaning, acceptance, definition graph,
profile, and identity-algorithm references. `all_current: true` is not enough
by itself: every `PASS_BOUNDED` reference also carries `current: true` with its
exact path, digest, and size.

Changing meaning, a bound definition, signature, proposition, assumptions, or
claim ceiling creates a new FormalClaim. Changing an InterpretationModel
changes the evaluation context, projection, or evidence identity—not the
FormalClaim. Adding another provider creates another projection and evidence
path, not another business truth.

## Minimum governance

The package requires only semantic integrity: named owners, exact identities,
typed non-pass outcomes, deterministic derivation or materialization where
claimed, and explicit ceilings. It does not add promotion, publication,
deployment, or production ceremony.

## First implementation layers

- **L0:** manually take one small Auth Foundation rule through FormalClaim.
- **L1:** take that claim through capability assessment, an admitted
  projection, one route obligation, one provider, and one EVF join.
- **L2:** add the interactive Define CLI/chat authoring experience.
- **L3:** add more formalisms and failure cases without changing meaning.
- **L4:** reuse the method in another domain project.

The Auth project is not changed by this package. It becomes the first consumer
only after the smallest business rule is selected by its owner.
