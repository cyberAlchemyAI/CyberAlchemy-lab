# Common semantic foundations for the proposed batch

This is a proposed specification. It supplies the common interpretation of all 41 definitions and does not promote them to canonical authority. Each individual definition keeps its formula, notation, operational interpretation and non-normative intuition together.

## Independent data and exactness

An exact semantic reference is `(kind, identity, revision, contentCommitment)`. Existing raw source formats do not necessarily contain this tuple; source adapters must resolve and bind it. Same-named references are not equated without an independently justified exact resolution. A content commitment is meaningful under a named byte representation and hash assumption; it does not authenticate an issuer.

`W` contains independently supplied captured artifact bodies, typed witness catalogs, reference and role catalogs, scope-inclusion records, evidence observations and assessment policies, time-domain/window records, norm origins, authorization roots, identity classes, ownership records, and the selected semantic theory. This describes the input contract to formal model implementation; it does not claim those providers already exist. The relation checker may read W, but its success cannot define W or its facts.

The complete frame `f` binds the context revision, owner/role resolution policy, scope, source snapshot, evaluation epoch, time domain, optional session, meaning revision, qualifier-catalog revisions, evidence policy, byte/hash profile and historical/live claim profile. Earlier observations can support historical attribution when their exact recorded epoch and evaluation snapshot are retained. Recorded and evaluation epochs are not silently equated.

`WF(W)` requires unique exact catalog keys, well-typed references, available committed bodies for selected references, well-formed scope and time relations, consistent identity assignment within the selected governed identity model, and the declared theory's constraints. Scope inclusion is reflexive and transitive within one owned scope domain. Whether distinct scope codes denote the same region is determined by the owned policy, not inferred from spelling. Evidence may disagree: well-formedness does not remove conflicts by assumption.

`CompleteOwnedInputs(W,e,f)` means every finite catalog/criterion/ancestor/norm derivation required by the selected profile is supplied completely according to an independent owned derivation. Missing authenticity, missing ancestry or unobserved live status cannot become complete by a checker flag. Completeness is bounded by the exact profile; it makes no assertion about all real-world facts.

## Base meaning

For kind k and independent normalized witness w:

```text
Base_k(W,e,f,w) :=
  selectedDefinition(W,f) = exact proposed revision for k
  ∧ e.kind = k
  ∧ (kind(e.source),kind(e.target)) ∈ allowedPairs_k
  ∧ capturedExact(W,e.source) ∧ capturedExact(W,e.target)
  ∧ keys(e.qualifiers) = requiredFields_k
  ∧ every required qualifier has a unique typed catalog interpretation
  ∧ w is in the independently supplied primary-witness catalog for k
  ∧ w.boundSource = e.source ∧ w.boundTarget = e.target
  ∧ witness owner/scope/context/snapshot/epoch joins obey f's profile
  ∧ independently admitted provenance supports this declared claim tier
```

Normalized `boundSource` and `boundTarget` are common witness-catalog fields. Relation-specific fields further constrain their roles. Normalization must be proved from actual source bodies; declaring a normalized field does not implement or prove its projection.

The distinct claim tiers are: recording an attributable declaration; checking supplied observations as of a pinned snapshot; establishing a verified local state transition; and establishing an observed external effect. A stronger tier needs stronger independent evidence. A payload saying `completed` does not itself prove an external operation completed.

`Admissible_f(a)` requires exact subject/proposition/criterion/target/frame joins, content and issuer provenance admitted by the selected independently resolved policy, and any required owner acceptance. That provenance may rely on an external authentication provider. The trust assumption must appear in future proof certificates; this specification does not supply it. An arbitrary Boolean named `admissible` cannot replace this interpretation.

## Logical meaning versus available knowledge

`Meaning_k(W,e,f)` is a mathematical predicate about an independent world. A bounded checker has qualified, refuted, unknown, conflict or unsupported diagnostic outcomes under its explicit profile. Missing data does not prove the mathematical predicate false. A decoder refusal is not a theorem about external truth.

Conditions use strong Kleene truth tables:

| AND | yes | no | unknown |
|---|---|---|---|
| yes | yes | no | unknown |
| no | no | no | no |
| unknown | unknown | no | unknown |

| OR | yes | no | unknown |
|---|---|---|---|
| yes | yes | yes | yes |
| no | yes | no | unknown |
| unknown | yes | unknown | unknown |

Negation exchanges yes and no and preserves unknown. Conflict is diagnostic metadata, not a fourth Boolean truth value or a permission. Empty conjunction is yes and empty disjunction is no only for a well-formed owned expression/criterion set, not as a way to omit required criteria.

Evidence aggregation is a separately selected policy. In the proposed successor criterion policy, positive and negative sets contain only admissible exact assessments: positive only yields yes, negative only no, neither unknown, both conflict. Distinct propositions do not share a polarity verdict. Duplicate normalized references do not increase weight under the proposed set policy. A quorum policy would require a new reviewed version.

## Record effect

Let the state be `(W,R)`, with immutable relation log R. Appending an exact witnessed row changes only R:

```text
record((W,R),row) = (W,R ∪ {row})       if row is new and qualifies
record((W,R),row) = (W,R)               if the same exact row exists
record((W,R),row) = refusal, no change  if its identity conflicts with existing bytes
```

Recording preserves the independent W, including authority, ownership, identity, admission and runtime state. This local postcondition does not prove arbitrary additional inference rules preserve those boundaries. Materialization witnesses an earlier verified transition; recording the relation does not perform that transaction again.

## Recursive inference

For a separately reviewed positive rule theory T, `F_T(X)` adds rule conclusions whose premises are already in X. Closure is the least fixed point generated by iterating F from actual seed facts. Each derived fact has a finite derivation tree rooted in supplied facts or explicit premise-free axioms of T. Thus `Review → Ready → Review` derives neither fact from an empty seed. A premise-free rule would be an explicit starting axiom requiring separate review.

Positive closure does not describe nonmonotone lifecycle selection, negation-as-failure, external observations or time advancement. Those need different transition/evaluation contracts. Succession cycles are a separate data-validation question; they do not supply inference seeds or justify replacement.

## Forbidden conclusions and theorem obligations

Each of the 148 inherited forbidden-conclusion IDs retains its independent typed predicate and relation namespace. Its proposed non-entailment target is:

```text
∃ W,e,f. WF(W) ∧ Meaning_k(W,e,f) ∧ ¬ Conclusion_id(W, anchoredParticipants(e,f))
```

Endpoint participants are bound by the exact witness roles. Additional operation, criterion, policy, issuer, model or transition witnesses range over independently owned catalogs with exact participant/frame joins. They are not asserted conclusion flags. Full formal models must specialize these existential joins and prove the concrete anchors; original generic anchor descriptions are retained transparently in the obligation index and are not yet compiled theorem terms.

Non-entailment says a relation is insufficient to establish a conclusion by itself. It does not prohibit independent evidence for both in another world. A synthetic example is not yet a valid countermodel under the complete source theory. Full-rule closure may impose additional protected-boundary obligations beyond individual countermodels.

Qualifier obligations ask for exact field-to-role interpretation and refinement. Effect obligations ask for the specified record delta and applicable composed-state preservation. Non-entailment obligations ask for valid independently checked full-theory countermodels. Satisfiability, checker equivalence, source refinement, authenticity and every ordered-pair branch are further prerequisites, not interchangeable proofs.

## Legacy profile boundary

K10, K14 and K25 have eight already discharged literal qualifier meanings in original F0. Its exact formal predicate remains `Relational.InstanceValid` in pinned `v1/formal/core/RelationalSemantics.lean`. It uses nonempty literal tokens and supplied accepted assessments. F0 effect tokens are not restricted by the stronger successor's three-effect catalog, and an F0 materialization receipt does not prove actual execution.

New `Meaning_k` for these kinds explicitly requires `typedSuccessor`. `LegacyQualified_k` remains separately named and profile-indexed. No equivalence between their claim strengths is asserted. A compatibility adapter must preserve old acceptance while exposing the returned claim profile, rather than calling legacy token validity verified execution or complete criterion fulfillment.

## Definition completion and remaining formalization work

The batch supplies proposed interpretation packages for all 41 relations, 82 qualifier fields, 41 effects, 148 conclusion definitions and 550 signature branches, plus eight shared choices and seven extension bridges. Satisfiability, concrete typed implementation, raw source refinements, exact conclusion-anchor elaboration and full-theory proofs remain N01/N02 work. Schema field inventory and reviewed meanings do not discharge those obligations.
