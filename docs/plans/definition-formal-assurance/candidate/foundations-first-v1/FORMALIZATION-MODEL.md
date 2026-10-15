# Formalization foundations: types, logic and semantics first

Candidate design draft, 2026-10-07. Authority effect: none. This is the first-priority model requested by the user. It specifies a model to review and implement; it supplies no owner fidelity approval, complete translation or formal proof. [The revised DAG](dag.json) places its nine production/review tasks before the existing implementation plan.

## What is being classified

The Lab Definition/v1 schema fixes `classification.semantic_kind` to `definition`. This describes the artifact. It cannot distinguish the logical roles of its content. A Definition artifact about **Axiom** defines what an axiom is; it does not itself assert every proposition called an axiom. A Definition about **Invariant** defines the concept; a particular invariant still has a separately selected scope and proposition to check.

Classification is per clause, with several independent axes. A source can mix them, and unresolved classification is allowed. Names, aliases and source ancestry are evidence to inspect rather than a classifier.

| Axis | Question | Candidate values |
| --- | --- | --- |
| Definitional form | How does the clause introduce meaning? | Primitive declaration; explicit abbreviation; genus/differentia; finite enumeration; axiomatic/implicit specification; constructive specification; inductive/recursive specification; operational specification; non-definitional; unresolved |
| Statement role | What role does the proposition play in reasoning? | Definition; selected axiom; selected premise; hypothesis; constraint; proof obligation; derived claim; observation/measurement; explanation/example; unresolved |
| Signature shape | What mathematical object is introduced? | Sort; constant; total/partial function; predicate; relation; record; state; transition; trace; unresolved |
| Logic requirements | Which semantic features does it require? | Propositional; first-order; finite cardinality; equality; inductive/fixed-point; temporal; normative/deontic; empirical/probabilistic; combinations; unresolved |

Record artifact identity and scope separately. “Primitive” here is a role in a selected semantic vocabulary; it does not authenticate a Lab Semantic Primitive or imply a programming-language primitive. Logic requirement flags do not prove support by any provider.

## Definition forms and their distinct checks

| Form | Meaning or candidate pattern | Required check |
| --- | --- | --- |
| Primitive | Introduce an uninterpreted sort, function or predicate within an exact signature | Boundary and dependency agreement; consistent interpretation; required populations; no accidental source meaning lost |
| Explicit abbreviation | `New(x) iff expression(x)` using existing meanings | Well-typed expression and dependencies; introduction does not impose an unintended old-vocabulary restriction |
| Genus/differentia | `Child(x) iff Parent(x) and Difference(x)` | Inclusion and required child inhabitant; properness only if declared; retain intended overlap |
| Finite enumeration | `Member(x) iff x=a or x=b ...` | Exact member identity/cardinality policy; no unintended scope merging; enumeration completeness at the declared scope |
| Axiomatic/implicit | Specify an object by properties rather than one expansion | Joint satisfiability and required existence; uniqueness only when claimed; underdetermination and assumptions visible |
| Constructive | Give a construction from admitted inputs | Input conditions, totality/termination when required, output characterization and correspondence |
| Inductive/recursive | Base and constructor/recursive cases | Well-foundedness or explicit least/greatest fixed-point semantics; positivity/monotonicity where applicable; an ordinary recursive equivalence alone is insufficient |
| Operational | Define allowed state changes, effects and observations | Exact subject/state binding, pre/post/frame conditions, reachable states, required atomicity and preservation; liveness requires a separate trace claim |

These forms are not mutually exclusive and are not an admitted taxonomy. Choice of a form cannot discard a source clause that is difficult to encode. An “explicit” definition can still reference a provisional premise, require operational semantics or be ill-founded.

## Statement roles: theory, assumptions and obligations

A clause record needs its exact source selector/digest, candidate formal expression, role, scope, dependencies, interpretation rationale and unresolved conflicts. Source selection and role selection are reviewed decisions.

| Role | Treatment |
| --- | --- |
| Definition | Adds or characterizes vocabulary; check the chosen definitional form and its effect on existing meaning |
| Selected axiom | Enters the assumption set with explicit source/scope and commitment; its asserted world truth remains an assumption, not established by a solver |
| Selected premise | Enters a named conditional reasoning context as a defeasible working proposition; adoption and truth remain separate |
| Hypothesis | Remains a proposition under investigation; it is not adopted merely by being recorded |
| Constraint | Describes permitted models/states in a declared scope; a consistency check can use it, but that alone does not establish operational compliance |
| Proof obligation | A target to establish from independently justified premises; never added to those premises to prove itself |
| Derived claim | Carries the exact claimed statement and its dependencies; becomes supported only by evidence at the required strength |
| Observation/measurement | Has observation conditions, method, uncertainty and evidence; does not silently become a universal law |
| Explanation/example | Helps interpretation without introducing normative axioms |

An invariant can be a constraint when checking whether a set of allowed states is consistent, and a proof obligation when checking whether an implementation preserves it. Those are different queries and must keep distinct assumption sets. Normative “must” is not evidence that actual behavior complies. A policy description needs a selected normative interpretation or explicit scope-conditioned allowed-state constraint, not an automatic factual assertion.

## Signature and candidate logical core

The first core is a candidate **classical many-sorted first-order language** for static structure: named sorts; scope-qualified constants, functions and predicates; equality; Boolean connectives; and explicit quantifiers. This is a proposed starting fragment, not an implementation or a claim that every definition fits it.

```text
term    := variable | constant | function(term, ...)
formula := predicate(term, ...) | term = term
         | not formula | formula and formula | formula or formula
         | formula implies formula | formula iff formula
         | forall variable:sort . formula
         | exists variable:sort . formula
```

Arity, argument/result sorts, binding and free-variable policy are explicit. Identifiers bind to exact semantic identity and scope; equal printed labels do not unify them. Comparison requires a reviewed common-carrier map. Creating two nominally disjoint sorts cannot serve as evidence that two meanings are distinct.

The initial core has nonempty sort domains by default; predicate extensions may be empty. Required predicate populations are separate obligations. Any empty-sort profile or changed domain convention is an explicit extension, not a silent evaluator shortcut. Total functions have declared signatures; partial functions require explicit definedness and result representation, or a relation encoding with separately stated functionality conditions.

Recursive/inductive, temporal, normative/deontic and empirical/probabilistic features receive explicit semantic extension contracts and supported-fragment declarations. They are not translated into static predicates merely to obtain a result. A finite trace search does not establish unbounded eventual completion. A probability, conviction or evidence score does not establish logical truth.

## Denotation and information state

A mathematical structure `M` assigns domains to sorts and interpretations to constants/functions/predicates. An environment maps variables to domain elements. Define `M, env |= phi` independently of any executable evaluator. For example, existential quantification requires an actual domain witness; implication is evaluated against its declared classical semantics.

Record truth semantics separately from epistemic and execution status:

- **Unknown information:** we lack a needed lineage component or observation. It is not evidence that the underlying proposition is false.
- **Absent value:** no value exists in the selected representation, under its declared meaning. It does not automatically mean an unknown historical event never occurred.
- **Execution unknown:** timeout, unsupported logic or missing provider. This is not a truth value of the theory.
- **False:** a counterexample or model interpretation makes an exact proposition false.

Closed-world behavior is valid only for explicitly complete enumerations or selected closed records. An open-world source cannot be made false by a missing record. The candidate classical core does not acquire three-valued truth from an `unknown` status string; any alternate logic needs its own denotation and evidence rules.

## Theory assembly and required checks

A conceptual formalization record is:

```text
F = (exact_source, signature, clause_map, clause_roles, dependencies,
     selected_assumptions, semantic_profile, obligations, evidence, review)
```

This notation is a design sketch, not an installed schema. Build a theory from exact reviewed vocabulary, source-correspondent selected assumptions and scoped constraints. Keep the target queries separate. Shared meanings use reviewed alignment; recursive dependencies are analyzed jointly with declared semantics. Forbidden value-constraining cycles remain independent obligations.

For the selected consistency query:

```text
T = included definitions + selected assumptions + scoped constraints/couplings
I = all declared required population obligations

Find M such that M satisfies T.
Find one M such that M satisfies T and I together.
Then check every required relationship at its declared direction and strength.
```

For a permissible distinction, a model of `T and I` with `exists x (A(x) xor B(x))` is a witness. Requiring such a difference in **every** admissible model is stronger and needs its own entailment claim. Alias equivalence, subtype inclusion/properness, overlap, disjointness and independent-axis forbidden inferences each use their own exact requirements.

Proof strengths remain separate: structural validation; checked model witness; exhaustive bounded result; solver result; independently verified proof; mechanized theorem under audited assumptions. Required strength follows the proposition and review policy. No result list can reduce the required set to the statements it happened to solve.

## First real source set and ambiguity handling

The [foundation source queue](foundation-source-queue.json) binds all eight current F01 identities and reproduces their exact current normative and formal voices. Work first with Definition, Semantic Primitive, Schema, Axiom, Premise, Hypothesis, Invariant and Governed Model. These are a priority sample, not an asserted dependency-closed theory.

The current **Hypothesis** target-specific statement describes investigation without adoption; its inherited formal expression describes a proposition adopted to proceed, and its source aliases include Premise. **Premise** has its own independent identity and a target-specific working-adoption meaning. This is a correspondence/precedence ambiguity. Do not merge the identities, turn a hypothesis into an assumption or silently rewrite either source. M08 must present the exact conflict and candidate treatment for actual review. Formal expression presence alone cannot override reviewed source precedence.

**Schema** describes shape conformance and explicitly distinguishes it from truth and authority. **Axiom** describes a foundational commitment; **Invariant** describes a must-hold condition on system behavior. The formalization model must preserve those distinctions even though all four live in Definition artifacts.

## Small worked controls before automation

1. **Definition versus assertion:** defining `Hypothesis(h)` characterizes hypothesis records; it does not assert the investigated proposition `h` as true.
2. **Subtype:** a synthetic `Child(x) iff Parent(x) and Marked(x)` allows overlap. Require a child witness and, only when properness is intended, a parent that is not a child.
3. **Invariant preservation:** a synthetic finite system has `Good(s0)`, `Good(s1)`, `not Good(s2)`, `Next(s0,s1)` and `Next(s1,s2)`. The target `Good(s) and Next(s,t) implies Good(t)` fails at `(s1,s2)`. Do not add that target as an axiom and then claim the transition implementation preserves it.
4. **Recursive meaning:** `Reachable(s) iff Initial(s) or exists p (Reachable(p) and Next(p,s))` can be underdetermined without selected inductive/fixed-point semantics. M04/M05 must state that semantics before interpreting it as reachability.
5. **Joint consistency:** `{p, q, not(p and q)}` has satisfiable pairs but an inconsistent conjunction. Family-local checks cannot replace one combined theory.
6. **Information:** missing grant evidence is a missing/unknown status. A provenance record does not supply the grant and does not establish authorization by itself.

These are candidate examples reasoned about in the design. They are not executed tests or complete translations of the actual definitions. Future M08 records real outcomes and exact limitations; actual source fidelity remains pending.

## First deliverable and exit gate

M01–M09 produce a concrete taxonomy, role policy, signatures, grammar, denotation, composition rules, obligation matrix and worked foundation cases, followed by actual model-design review. Candidate drafts are provided here so review has substance. Outstanding correspondence or required logic decisions block lowering; no approval is simulated.

Only after that gate does A01 implement strict decoding of the chosen model. The later canonical IR, evaluator, provider adapters, addition/revision workflow, all-current translation and combined theory retain their previous required checks. This request changes priority and adds explicit design work; it does not waive source fidelity, non-vacuity, exact evidence or full combined consistency.
