# Formalization review: relations, obligations and logical typing

This is the next candidate review in the foundations-first episode. The full 183-definition assurance goal remains active. A05, A06 and C01 now have verified software criteria and forty-two tests: seventeen relation controls, eleven obligation controls and fourteen typed-IR controls. They do not establish whole-definition assurance for any admitted source.

The earlier [foundation review](../M09/REVIEW.md) explains the complete conceptual model. The [source/correspondence review](../A04/REVIEW.md) explains exact capture, currentness, clause accounting and the Hypothesis conflict. This review covers the newly executable formalization aspects and their limitations.

| Aspect | Implemented behavior | Evidence and remaining boundary |
| --- | --- | --- |
| Alias | Generates `forall x. P(x) iff Q(x)` on an explicitly aligned carrier | Equal extensions satisfy the selected model control; a false alias produces a model-local counterexample. A universal obligation remains separate. |
| Subtype | Generates directed inclusion; properness adds a parent-minus-child target | Ordinary inclusion allows equal extensions. Selected properness rejects the collapsed control. Reverse direction is explicit. |
| Overlap and distinction | Intersection and selected left/right difference targets remain separate | One witness permits a distinction. An all-model requirement has a universal query type and requires separate proof evidence. |
| Disjointness | Generates absence of intersection while retaining required populations | Both concepts can be inhabited jointly without overlap. A single overlapping model refutes that model-local condition. |
| Independent axes | Generates a countermodel target for each named forbidden implication | No automatic Cartesian-product demand. Explicit allowed coupling remains separate from forbidden inference. |
| Frame conditions | Compares exact before/after values against intended axes and recorded couplings | An undeclared side effect fails the control; a recorded allowed coupling passes it. Boolean/integer differences are preserved. A coupling declaration grants no authority. |
| Populations | Requires one required, explicitly exempt or unresolved entry per selected endpoint | Empty required extensions produce `vacuous-required-population` before relation support. Missing policy entries fail. Exemptions retain a review gate; unresolved entries retain their existential target. |
| Carrier alignment | Requires an exact digest-bound shared-carrier record | Equal labels alone do not align carriers. The current supported mapping is an explicit identity shared-carrier mapping; other mapping semantics remain unsupported. |
| Required denominator | Generates requirements before comparing submitted manifests | Removing a logical target, gate or prerequisite, weakening a statement/strength, substituting context, or reusing stale hashes is rejected. |
| Joint inhabitation | Generates one conjunction of all required populations in one selected theory | Separate incompatible witnesses cannot satisfy this requirement. Individual population obligations also remain present. |
| Review and administrative obligations | Keeps source fidelity, currentness, dependency closure and policy checks separate from logical formulas | No fabricated FOL predicate represents source-owner acceptance. Exact required-set comparison does not verify evidence truth. |
| Change classes | Adds explicit conservativity or meaning/constraint review requirements | A noninitial change needs an exact prior binding. Conservativity still needs its own formal evidence; unchanged tests do not prove it. |
| Signature identity | Namespaces each symbol by exact definition ID/version, interpretation scope and local symbol ID | A retained origin tuple explains the canonical hash. Same labels across identities, versions or scopes remain separate. |
| Variables and quantifiers | Checks closed formulas with lexical variable environments | An unbound variable fails. Nested shadowing restores the outer environment. The compiler renames global symbols without substituting or capturing variables. |
| Predicates and relations | Checks ordered argument lists against declared arity and sorts | Wrong arity, undeclared predicates and ill-sorted arguments fail before evaluation. No symmetry or transitivity is inferred from a relation label. |
| Constants and functions | Checks result sorts and supported total-function signatures | Repeated arguments and zero-arity predicates are valid. Partial functions require a separate lowering/semantics contract and remain unsupported in this core. |
| Equality | Requires an explicitly common sort | Cross-sort equality fails. Distinct nominal sorts do not themselves prove semantic non-collapse or disjointness. |
| Boolean structure | Supports negation, conjunction, disjunction, implication and equivalence | Empty conjunction/disjunction have their selected classical meanings. Unknown operators stay unsupported; malformed shapes stay errors. |
| Typed composition | Composes exact IRs without automatic name unification; selected alignment records union carriers | A cross-definition query is ill-sorted before alignment and well-sorted after the explicit record. This establishes type compatibility, not equivalence or source fidelity. |
| Integrity and determinism | Regenerates standalone IR from its exact bound input; regenerates composition from separately selected inputs/alignment records | A caller cannot repair a forged declaration merely by recomputing its digest. Canonical signatures are sorted; original input ordering remains bound as provenance. |
| Unsupported semantics | Retains partial, temporal, inductive, deontic and empirical extensions as explicit unsupported selections | A recursive equation does not establish leastness; static typing does not establish transition preservation or a probabilistic law. |
| Source fidelity and readiness | Typechecking and model-local controls do not set readiness | Actual source meaning, currentness, dependencies, population and proof evidence remain independent requirements. All new controls have `authority_effect: none`. |

## Relation semantics

The relation compiler generates exact canonical formulas from the fixed policy. A submitted `required_statements` list cannot replace them; an empty list does not erase them. Distinct source definitions also cannot collapse into the same predicate identity merely because the caller supplied equal labels.

Universal and existential targets answer different questions. Alias equivalence and subtype inclusion require a universal-property result. A selected separating model can establish permitted difference or non-entailment. It cannot establish that every admissible model separates the concepts. An all-model properness or distinction request therefore has a different query type and evidence requirement even when the displayed difference formula is the same.

Seven synthetic worked controls are recorded with their exact derived targets. They include a valid alias, false alias, proper subtype, collapsed properness, overlapping concepts with both differences, an empty-population alias and named independent implications. Their outcomes are model-local; no current admitted definition is claimed translated by those examples.

## Required obligations and evidence dimensions

A06 binds the selected theory, signature, exact source references, assumption context, change class and reviewed candidate policy bytes. It always generates consistency and joint-population requirements, plus selected relation/population targets and necessary review gates. Unary declared predicate endpoints cannot disappear by dropping their binding or population policy. Nonunary population scopes retain an explicit profile-review gate rather than silently inheriting the unary implementation.

The logical manifest conforms to the frozen A01 input vocabulary. Exact versions and digests live in `source_refs`; identifier-valued dependency references remain identifiers. This distinction was caught by validation and corrected without changing the frozen decoder.

The total manifest includes logical targets **and** administrative/semantic-review gates. A population exemption does not grant itself acceptance: its exact review subject remains required. An additive extension adds a conservativity requirement against its exact predecessor. Source fidelity is required for assurance readiness; candidate logical checks can still run while their meaning correspondence remains pending and explicitly limited.

`verify_submission` regenerates the denominator from separately selected inputs before comparing the submission. A matching manifest proves only required-set identity. It does not validate a model, theorem, reviewer's authority, source correspondence or proof result. Those dimensions must be checked by later provider, replay and evidence-join stages.

## Typed IR and source identity

C01 compiles the supported static many-sorted first-order fragment. It checks symbol kinds, arities, argument/result sorts and lexical variables, then rewrites global names into canonical scoped identities. The origin tuple remains readable alongside the hash; hashing alone does not prove meaningful source identity or source fidelity.

The exact original interpretation is retained and bound. Standalone IR integrity is checked by regenerating its typed form from that input. Composition integrity additionally needs independently selected input IRs and alignment records. Typechecking a formula relative to a supplied signature is a narrower statement than establishing that the signature came from particular current sources.

An explicit shared-carrier record makes selected cross-definition formulas well-sorted. It does not prove the carrier map faithful to source prose, make the predicates equivalent, require their extensions nonempty or prove them distinct. Required populations and relation proof targets remain downstream obligations.

## Actual source boundary

The current Hypothesis packet remains character-accounted but logically unresolved. C01 reports `unsupported-or-unresolved-logic-feature` for its current interpretation, with source fidelity pending and readiness false. This is the expected boundary: twenty-four accounted source text units do not supply a selected logical signature or resolve the conflict between investigation and adopted-Premise meaning.

A meaning clarification is pending for that candidate interpretation. Original source bytes remain preserved. No source-owner acceptance, source rewrite, alias merge or canonical admission has been inferred.

## Review disposition and next work

This agent self-review accepts the three software surfaces for controlled static denotation and evaluator work. It is not independent review, source-owner fidelity review or a generic soundness/completeness theorem.

The next unit is **C02: independent denotation and evaluator**, followed by exact dependency/SCC composition and the remaining assumption, provider, replay and all-definition translation/evidence work. C02 must validate complete nonempty structures and interpret formulas under explicit environments. Model satisfaction must remain independent from a checker returning `true`, and absent, unsupported, cancelled or exhausted execution must not become logical falsehood or unrestricted absence.

The project baseline still contains 183 current identities and 189 admitted versions. Its actual whole-definition proof and owner-fidelity counts remain zero. The final full-project review and completion audit remain unfinished.
