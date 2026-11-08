# Formalization foundation episode: review and explanation

Candidate review, 2026-10-07. Authority effect: none. Reviewer: Codex `/root`, the same agent that authored the candidate artifacts. This is an attributable agent design review, not independent review or acceptance by the semantic source owners.

The foundations-first work now has seven concrete contracts, eight source-bound foundation cases, an executable finite worked interpreter, and a review of the model. The selected evidence is [attempt 002](../M08/attempt-002/worked-examples.json). Exact verification and dispositions are recorded in [the model review](../../foundations/foundation-review.json) and [the episode status/completion audit](episode-status.json).

The candidate static model is suitable for controlled decoder/prototype work. It does not establish faithful complete formalization of all 183 definitions, a complete joint current theory, or a generic mechanized correctness theorem. Those remain part of the retained full project scope. The final episode scope question is still pending; this review does not silently substitute the foundation slice for the entire goal.

## How to read the evidence

Three kinds of evidence appear here: source text with exact bindings; candidate design judgments; and executed finite checks. Their conclusions differ. A source excerpt shows what the source says. A design judgment selects how to represent it. A model/control execution checks the selected representation. None alone establishes full correspondence with all source meaning.

The production records for M01–M07 are retained as their original draft receipts. Separate `criterion-review.json` files record the subsequent actual candidate review, so the initial state is not rewritten into a fictitious earlier acceptance.

## 1. Definition forms

[The classification contract](../../foundations/definition-kinds.json) distinguishes primitive declaration, explicit abbreviation, genus/differentia, finite enumeration, axiomatic/implicit specification, constructive specification, induction, recursion and operational specification. Non-definitional and unresolved clauses are permitted.

These forms answer different questions. A primitive introduces a symbol without deriving it from narrower vocabulary. An abbreviation gives an expansion. A genus/differentia clause defines a child through its parent plus a condition. An implicit specification characterizes an object by properties and may leave multiple possible objects. A construction describes how to produce an object. Induction selects a least closure; recursion requires its own well-founded/fixed-point meaning. An operational definition characterizes behavior through states and moves.

The checks follow the form. An abbreviation needs typing and dependency checks; an implicit definition needs existence and consistency, with uniqueness only when claimed. A constructive definition may require totality and termination. A transition rule requires subject binding, pre/post/frame conditions and separately selected temporal properties. No one form can make a difficult normative clause disappear.

## 2. Classification axes and granularity

Artifact kind, definitional form, statement role, signature shape and logic features are separate axes. The Lab artifact schema calls these artifacts `definition`; that does not make all their clauses mathematical definitions or axioms.

Classification binds an exact clause segment, source selector, offset and digest. Eight selected real clauses are annotated. Remaining clauses are explicitly outside those annotations' coverage. Six synthetic cases exercise primitive, explicit, implicit, inductive, operational and mixed/unresolved treatment. The taxonomy permits several justified forms on one source rather than forcing a single label.

## 3. Logical roles

[The role contract](../../foundations/statement-roles.json) separates vocabulary definitions, selected axioms, selected premises, hypotheses, constraints, proof obligations, derived claims, observations and explanation.

Defining **Axiom** characterizes axiom records; it does not adopt every proposition described by those records. A selected axiom is an explicit assumption in a scope. A premise is a defeasible proposition adopted to proceed; adoption is not established truth. A hypothesis remains under investigation unless separately selected as a premise. A proof obligation is the target to establish, not an assumption supplying its own proof.

The worked assembler rejects silent adoption of hypotheses, proof targets and explanatory clauses. It also rejects duplicate clause identities, unknown roles and exact target substitution under another identity. Selected evidence-dependent claims are explicitly unsupported without their additional evidence checker. The prototype does not claim to detect every hidden logically equivalent target; generic dependency/statement verification remains later work.

## 4. Signatures and mathematical object types

[The signature contract](../../foundations/signatures.json) declares sorts, constants, total/partial functions, predicates, relations, records, states, transitions and traces. Every function/relation has explicit argument sorts and arity; functions also declare a result sort. Predicates may have arity zero for propositional cases.

A total function has one result for every input tuple. A partial function needs an explicit definedness representation or relational graph and its conditions; an absent result cannot acquire an invented default. Records have fields and identity policy, but field shape cannot authenticate an owner or grant.

The finite interpreter checks total function tables and rejects missing table entries. It rejects unaligned equality, unbound variables and extra AST fields. Partial-function lowering and general record/trace compilation are specified boundaries rather than implemented features of this worked runtime.

## 5. Identity, scope and carrier alignment

A symbol binds to exact definition identity, version, scope and local symbol ID. A displayed name is insufficient. A comparison needs a reviewed common carrier; two nominal types cannot be made disjoint solely to obtain a distinction result.

The first source set contains independent definitions of Premise and Hypothesis despite shared inherited lineage/labels. Those identities are retained. The worked cross-sort test shows that even equal displayed element names do not permit equality between unaligned domains. Full cross-definition carrier alignment is a later reviewed artifact, not inferred by this episode.

## 6. Logical language

[The language contract](../../foundations/logical-language.json) selects a candidate classical many-sorted first-order static core. Terms are variables, constants and total function applications. Formulas include typed predicate applications, equality, negation, conjunction, disjunction, implication, equivalence and quantifiers.

Implication is material implication in this selected core; a source saying “does not imply” requests a countermodel/non-entailment obligation rather than supplying an ordinary connective. Quantifiers bind variables explicitly in their declared sort. Free variables must be bound by an environment or rejected.

The executable worked language is an AST profile of this core. It is not the production parser, interchange schema or generic canonical IR. Unsupported temporal operators are distinguished from malformed input. Later extensions must state their denotation rather than obtain a result through an improvised static translation.

## 7. Mathematical denotation

[The denotation contract](../../foundations/denotation.json) defines a structure assigning domains and interpretations to all declared symbols. An environment assigns variables. Satisfaction `M, env |= phi` is specified independently from an executable Boolean return value.

The controls compare Boolean operations against all four independent truth assignments and quantified relational evaluation against all 64 assignments of the selected two-element signature. A total-function/equality case checks a two-step permutation. This is concrete error detection for those exact cases, not a theorem over arbitrary programs, formulas or structures.

## 8. Truth, information and execution status

Logical false, unknown information, absent representation values and execution unknown are different. Missing historical lineage does not prove that an origin never existed. Missing authorization evidence cannot be turned into a grant or automatically identified with falsehood about a real-world right.

The selected core is classically two-valued for complete well-typed models. An execution that times out or lacks a supported profile has not produced a truth value. The worked runtime returns explicit resource-limit/cancelled outcomes and refuses unsupported operators; neither becomes exhaustive absence. It does not yet implement a production wall-clock timeout controller.

## 9. Open and closed worlds

Incomplete evidence is treated as open information. Closed-world inference is reserved for an explicitly complete enumeration or selected closed record. This is a model policy, not a blanket rule derived from a missing file.

The worked profile completely enumerates its declared predicate assignments under fixed finite domains/functions. That completion permits a bounded absence statement for that profile. It does not make the unformalized real world a closed database or support absence outside the selected bounds.

## 10. Assumptions and non-circular proof

Every selected assumption needs its exact statement, scope, selection basis, evidence posture and revision route. Claims derived under an assumption remain conditional on it.

A preservation target cannot appear in the premises used to establish that same preservation. The toy transition system has good states `s0` and `s1`, a bad state `s2`, and steps `s0 -> s1 -> s2`. The runtime finds the violation at `s1 -> s2`. Had the preservation target been inserted as an axiom, the query would have asked whether ideal allowed behavior was consistent, not whether these actual declared transitions preserved the invariant.

## 11. Theory composition and dependency graphs

[The composition contract](../../foundations/composition.json) distinguishes the source/meaning graph, obligation/evidence graph and execution DAG. Editorial families organize work and do not prove dependency closure.

Explicit semantic dependencies resolve to exact versions. Legitimate mutually defined meanings need joint treatment and selected recursion semantics. A prohibition on value-constraining cycles is a separate property; SCC condensation cannot waive it. The source dependency compiler is specified for later implementation and was not executed here.

One combined model must interpret all included shared symbols and constraints. The control `{p, q, not(p and q)}` has three satisfiable pairs but no joint Boolean assignment. This provides a concrete reason to keep the complete-theory check rather than aggregate family or pairwise results.

## 12. Consistency and non-vacuity

Consistency asks whether there is a model satisfying the selected theory. Non-vacuity additionally requires all declared required populations in the same model. Sort domains and predicate populations are different: the static core uses nonempty domains, while a predicate extension can be empty.

The worked empty-predicate theory is satisfiable. Adding the required inhabitant makes it unsatisfiable at the selected scope. The review records this as a population failure, not an original contradiction. Required inhabitants are hypothetical/model populations under an explicit policy; the episode does not assume a real-world instance exists for every abstract concept.

## 13. Aliases, subtypes, overlap and distinction

An alias needs equivalence, not an unequal-extension witness. A subtype needs inclusion, and properness only when declared. An overlapping relation needs its selected intersection/difference directions. Disjointness needs exclusion plus required inhabitation. Independent axes need countermodels for named forbidden inferences while retaining allowed couplings.

The alias control stays inhabited and cannot satisfy the forced difference query. The subtype control produces a nonempty proper child included in its parent, retaining overlap. A claim-without-grant model is expressible, while a coupled claim-and-grant model is also expressible. These latter cases test representation independence, not a complete formal proof of the actual Authority definition.

## 14. Possible distinction and universal separation

A witness showing a difference says that the distinction is possible under the chosen theory. It does not say all admissible models preserve it. The same unconstrained toy theory has a difference witness and a model with equal predicate extensions.

Universal separation is a separate statement with consistency/population prerequisites and its own required evidence. The worked bounded-entailment helper checks those guards and searches for a countermodel in the exact finite profile. A successful finite exhaustion is still labelled bounded; it is not presented as an unbounded theorem.

## 15. Induction, recursion and fixed points

A recursive equivalence may have more than one fixed point. In the worked example, `a` is initial and `b` has a self-loop. The reachability equivalence admits both `{a}` and `{a,b}`. The least reachable closure is `{a}`.

This example shows why the interpretation must declare induction/leastness, greatestness or well-founded recursion where intended. The runtime computes this small closure; it does not implement a general admitted fixed-point language or prove its generic correctness.

## 16. Operational, temporal, normative and empirical aspects

A static transition relation can represent allowed moves and support an exact preservation query. Full transactions also need subject-bound pre/post states, effects, frames and recovery/atomicity semantics. Those production contracts remain downstream; the old pilot has not been retroactively patched.

Temporal safety, liveness, fairness and horizon conditions must be declared. Permission, obligation and prohibition need selected normative semantics; a “must” is not an observed fact of compliance. Empirical/probabilistic statements require observation/measurement conditions, uncertainty and a selected interpretation. These extension entry contracts exist, but no temporal/deontic/probabilistic provider was executed in this episode.

## 17. Obligation generation and evidence strength

[The obligation contract](../../foundations/obligation-types.json) accounts for source fidelity, typing, closure, consistency, joint inhabitation, class-specific relations, universal properties, transition preservation, selected conservativity and currentness.

The required set is generated independently from a submitter's result list. Omitting or weakening a hard statement cannot produce a ready bundle. Structural validation, checked witnesses, bounded exhaustive results, solver results and mechanized theorems establish different propositions. They cannot be placed into a single label that hides assumptions, bounds or trust.

The handwritten worked interpreter remains trusted. No generic evaluator-soundness or obligation-generator coverage theorem was produced. No proof assistant or SMT solver execution supplies evidence here.

## 18. Source correspondence and the eight first definitions

The source bindings cover Definition, Semantic Primitive, Schema, Axiom, Premise, Hypothesis, Invariant and Governed Model. Selected clauses are annotated and discussed; whole-source fidelity is not claimed.

The Definition source separates completeness from admission. Semantic Primitive distinguishes its local semantic role from programming types. Schema separates shape from truth/authority. Axiom describes a taken-as-given foundational commitment; Invariant describes a must-hold system condition. Premise describes adoption without established truth. Governed Model describes a governed representation, not automatically a mathematical model witness or admitted authority.

Hypothesis has a concrete unresolved conflict: its target-specific normative clause describes investigation without adoption, but inherited formal material describes an adopted premise. The model can represent the conflict and keep the identities separate. Actual correspondence/precedence review is still required before that whole definition counts as faithful. No canonical source was changed.

## 19. Currentness, revision and historical evidence

A changed source, statement, profile or checker changes evidence applicability. A manifest is an integrity instrument; it is not a proof of the statement or source meaning.

During this episode, review identified a weakness in the toy role assembler: identity substitution and unsupported evidence-dependent roles needed explicit handling. The runtime was corrected and the evidence was regenerated as attempt 002. Attempt 001 retains its exact old runtime bytes and evidence. Its results are historical under the old checker, not silently reported as current. This is a concrete revision example; the generic project-wide invalidation engine still needs implementation.

## 20. Review disposition and completion limits

The agent disposition accepts the static candidate metamodel for controlled development. It does not accept all source meanings, activate unsupported fragments, grant rights or perform semantic admission. Source-owner review and independent review have not been simulated.

The foundation contracts and controls are concrete progress toward the objective. The current full-project completion audit remains incomplete: all 183 source digests are verified, but there is no faithful full-current translation set, complete joint theory evidence, reusable production addition/revision workflow or complete source-owner review. The active goal is retained. The next candidate implementation unit is A01.1, consuming the model to implement strict input contracts while keeping unresolved meanings visible.

## Reproduce the review evidence

```bash
python3 -m unittest discover -s docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/units/M08 -p test_controls.py -v
python3 docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/units/M09/review_foundations.py --check
```

The review command checks exact selected artifact bindings without rewriting review evidence. Original pilot and planning snapshots remain intact. Candidate review, test success and source integrity do not imply canonical admission or all-definition consistency.
