# Independent denotation for the supported static fragment

This mathematical specification defines satisfaction. A Boolean implementation is checked against it; the definition of satisfaction does not refer to an implementation returning `true`.

A signature Σ contains sort names, constants, total functions and predicates/relations with ordered argument sorts. A structure M assigns a nonempty set Dₛ to each sort s, a member of Dₛ to each constant of sort s, a total function Dₛ₁ × … × Dₛₙ → Dₜ to each function symbol, and a subset of Dₛ₁ × … × Dₛₙ to each predicate. For arity zero, the product contains the empty tuple. Thus a zero-arity predicate is either true or false by membership of that tuple. Predicate extensions may be empty; population obligations are separate.

An environment η assigns each in-scope variable a member of its declared sort. Terms denote their variable assignments, constant interpretations, or the application of the interpreted total function to their argument denotations.

Satisfaction M,η ⊨ φ is defined inductively:

- A predicate application holds exactly when its denoted argument tuple belongs to that predicate's interpreted extension.
- Equality holds exactly when both terms denote the same member of their explicitly common carrier. Ill-sorted equality is not a proposition in this fragment.
- Negation holds when its operand does not hold. Conjunction holds when all operands hold; disjunction holds when at least one holds. Empty conjunction is true and empty disjunction is false.
- Implication holds when the antecedent does not hold or the consequent holds. Equivalence holds when both operands have the same truth value.
- A universal quantification over s holds when the body holds under every environment η[x ↦ d] for d ∈ Dₛ. Existential quantification holds when it holds under at least one such environment. A nested binding shadows x only within its body.

M ⊨ T means every selected theory formula holds. Required inhabitation means the same M satisfies every selected population formula as well as T. Inspecting a target under that M gives model-local truth. Universal entailment T,I ⊨ q requires every admissible structure satisfying the selected theory and populations to satisfy q; evaluating one structure does not establish that statement.

The implementation in C02 evaluates finite structures with named string atoms. It requires complete interpretations and verifies exact tuple arity, sort membership and total-function coverage. Named atoms are representations, not authenticated business records. Carrier identities remain exact canonical sort identities; equal atom labels in separate sorts do not authorize cross-sort equality.

A missing domain or symbol interpretation is an incomplete model and is outside truth evaluation. A declared empty predicate is a valid complete interpretation and can make a formula false. An unknown observation, absent source record or unavailable value is not automatically mapped to an empty predicate. An explicit domain atom named `unknown` has only the meaning assigned by a separately selected data/profile interpretation.

Unsupported operators/profiles, malformed structures, cancellation and resource limits have no Boolean truth result. They cannot justify logical falsehood, satisfiability absence, universal validity or source fidelity. The resource controls bound this implementation's work, not the mathematical meaning of quantification.

Partial functions, induction/leastness, temporal traces, deontic rules and probabilistic observations require their separate semantics contracts. The static evaluator does not infer those semantics from labels, record shapes or a recursive equivalence.

The controls compare the implementation with hand-derived truth tables, quantifier examples and independently stated set conditions. They do not establish a generic soundness/completeness theorem, source-owner fidelity, model existence outside a supplied witness, or unrestricted entailment.
