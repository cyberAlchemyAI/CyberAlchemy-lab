# Typed Coupling Invariant: candidate formalization review

This is a partial translation of the exact current `cal.definition.typed-coupling-invariant@1.0.0-candidate.1` source. It adds a scoped, typed representation obligation and checks finite authored models and records. It has no authority effect. Source-owner fidelity, carrier embedding, complete dependency interpretation, temporal ordering and whole-definition proof remain pending.

The selected Definition source digest is `2358180b511b4297dfd53c8942125c811b3495c6fd73ce0b59ea7f68309aaaf1`. The source's embedded historical candidate posture is retained. The current registry separately admits these exact source bytes; that admission supplies neither approval of this interpretation nor proof that an implementation obeys the invariant.

## Definition, invariant and artifact classification

The source artifact is a Definition/v1 record about an invariant. It does not itself instantiate a live invariant carrier, assert that every system obeys the rule, or grant its named owner permission. Its inherited formal expression describes normalized semantic identity, carrier `type.invariant`, owner scope and source set. Those axes need an exact reviewed mapping. This candidate does not reduce them to printed-label equality or equate an artifact with its represented meaning.

The practical concept is narrower than “everything related must be linked.” When a decision, validation, promotion or implementation relies on one object constraining or changing with another, that coupling must be represented explicitly. An unrelated idea can remain unlinked. An ordinary typed relation can exist without becoming a value-constraining coupling. Nonorthogonality is interpreted within the selected use and scope rather than being inferred from file adjacency, shared labels or missing records.

## Signature and types

The candidate uses eight nonempty sorts: Use, Object, Relation, Kind, OwnerRoute, EvidenceRef, ReviewEffect and Scope. Eight total selectors connect uses and relations to ordered source/target Objects and Scope, and relations to Kind and OwnerRoute. Twenty-five predicates/relations distinguish four reliance roles, coupling classification, explicit vector metadata, evidence/effect bindings and six independent outcomes. There are 41 declarations altogether.

Source and target use the same Object sort, allowing meaningful equality and ordered comparison. This candidate does not invent a universal source!=target rule. It also does not impose one relation per use, an injective owner assignment, or a unique representative across unrelated uses. Every total selector is completely interpreted in each supplied model. Total mathematical selectors are not a claim that a malformed real record contains every field; explicit metadata predicates and bounded record checks retain that distinction.

## Static logical rule

Let `Relied(u)` mean that the selected use relies on a constraint or co-change for at least one of the four named roles. The selected rule is:

```text
Relied(u) iff DecisionReliance(u) or ValidationReliance(u)
             or PromotionReliance(u) or ImplementationReliance(u)
Relied(u) implies NonOrthogonal(u)
Orthogonal(u) implies not NonOrthogonal(u)
Relied(u) implies exists r:
  Represents(u,r)
  and TypedRelation(r)
  and explicit(named_source, named_target, direction, kind, owner)
  and named(relationKind(r))
  and exists e: HasEvidence(r,e)
  and exists effect: HasReviewEffect(r,effect)
      and (ValidationEffectDescription(effect)
           or PromotionEffectDescription(effect))
  and useSource(u) = relationSource(r)
  and useTarget(u) = relationTarget(r)
  and useScope(u) = relationScope(r)
```

These are selected normative constraints in a classical many-sorted first-order fragment with equality. They characterize allowed models; they are not measurements of actual reliance or implementation compliance. The source's list of dependency, bridge, constraint, influence and co-change relations is retained in correspondence; an exact taxonomy or mapping of those meanings to current Relation Kinds is not proved by the generic representation rule.

The quantifier requires at least one complete representative for each relied use. It is not a global rule that every recorded relation is complete or that every surplus representation has the same meaning. Such stronger carrier-validity, uniqueness and agreement claims need their own reviewed statements.

## Clause accounting and losses

All 22 required source units are inventoried and every character is assigned to one of 25 exact spans. Four clauses are encoded constraints, nine are explanations and twelve are deferred obligations. Complete character accounting means that nothing was silently dropped; it does not mean that all clauses have been translated faithfully.

Deferred content includes normalized classification/identity/owner/carrier alignment, accepted source relationships, the minimum-for-review meaning, excluded authority effects, exact source-currentness scope, source-schema/projection obligations and the claim ceiling. The six findings preserve trigger/scope, effect mapping, carrier/identity classification, ordered endpoints, no automatic outcome, and closure questions. All are unresolved; no owner decision is simulated.

## Existence and non-vacuity

One required population is a hypothetical ReliedCoupling witness. With the selected theory, that witness forces a complete representative, evidence and a qualifying review-effect description together. Twenty-four other population declarations remain unresolved, including the individual role and outcome populations; the source does not require a current instance of every role or an actual promotion.

A model with no relied uses satisfies the universal constraints but fails the required population obligation. This control separates vacuous truth from the candidate's selected non-vacuous demonstration. Hypothetical witnesses are mathematical examples, not world instances created in the Lab.

## Checked denotation and forbidden inferences

The independent evaluator checks 41 supplied finite controls. It checks missing vector components, mismatched source/target/scope, the reliance-role equivalence, orthogonality contradictions, absent representation, the four roles, multiple roles on one use, neutral promotion descriptions, independently true outcomes and malformed interpretations. Ill-sorted function results, nontotal functions, bad tuple arity and duplicate tuples are rejected structurally.

Seven query targets stay outside the theory. Six ask whether a complete represented coupling implies actual promotion, actual validation, admission, authority, runtime activation or publication. A valid T+I countermodel makes each target false. The seventh shows an ordinary typed relation without any relied coupling represented by that relation. These checks show that the partial theory does not entail those conclusions. They do not prove a conclusion impossible when separately justified, nor establish source-owner fidelity or a mechanized theorem for the full Definition.

The positive controls permit self-links where no selected Kind prohibition is stated, multiple reliance roles, and a nonorthogonal but unused idea with no new coupling. Missing classification is not interpreted as factual orthogonality or as proof of no dependency.

## Bounded record profile

The pure candidate profile checks a selected use and explicit relation records. It compares ordered endpoints and scope, requires named Kind/owner, nonempty unique evidence references and a validation/promotion description whose authority effect is none. Twenty-five synthetic cases include sixteen rejections. A neutral description `none` is accepted only as a candidate representation choice; its adequacy under the source effect requirement remains a review question.

The profile accepts no record requirement for an unrelied use. It rejects a missing representative for a relied use and rejects an effect description that purports to grant authority. It performs no runtime actions and creates no canonical relation. Its closed shape is an illustrative candidate profile, not a promoted replacement for Typed Relation/v2.

## Actual source, carrier and catalog observations

Twelve source checks validate the exact Definition/v1 record, bound schema/generator digests, two deterministic renders, existing projection, selected legacy section, admission record and current Definition lookup. The selected local CAV2-D16 section is 2,604 bytes with digest `69e2347abb4169fe6ac983da31997e79beea9e8719dba9b963700e60da0363fc`. The producer-declared legacy path is absent. Matching the selected local copy and recorded section does not authenticate the declared live producer or repository identity.

The admitted-current Typed Relation/v2 contract and its positive fixture are checked read-only. Forty-one exact current Relation Kind descriptor paths and digests are selected. Forty-seven actual checks bind the carrier/catalog observations. Sixty-three historical example observations compare ordered pairs, current qualifier contracts, owner/evidence metadata and no authority effect. Sixty-two are compatible with those selected checks. The older `relation.conforms-to` example supplies `['receipt:remaining-18-model-validation']` where the current qualifier contract requires a string. That mismatch is retained rather than rewriting the historical example or weakening the current contract.

Two actual schema probes expose the effect-mapping boundary: the unchanged fixture is accepted, while adding a literal top-level `review_effect` field is rejected by the closed schema. The carrier has explicit scope, owner, evidence and endpoint payloads, but no dedicated validation/promotion/blocking effect field. Its `authority_effect: none` and a Kind's generic operational-effect prose do not, without review, satisfy the source's separate review-effect meaning. Qualifiers or containing policies could provide a mapping, but that mapping has not been supplied and approved here. This is not a blanket whole-source conformance failure.

The selected Typed Relation/v2 schema enumerates forty Kinds; the selected current catalog has forty-one. Those are distinct versioned surfaces. The candidate does not extend the carrier schema or claim that its selected fixture demonstrates the later forty-first Kind.

## Semantic extensions and temporal ordering

The selected legacy source section additionally names a blocking effect, direction or symmetry, and recording the typed relation *before* the coupling influences authority, routing, validation or implementation. The current reconstructed Definition's bounded normative basis uses validation or promotion effect and explicit direction. The first static candidate does not silently widen its effect-role enumeration or equate ordered endpoints with a reviewed symmetry policy.

The temporal “before influence” condition needs states/events, exact action binding and an ordering/preservation obligation. This candidate has no trace or temporal semantics and supplies no unbounded operational proof. Unknown/untypeable couplings should remain visible as open questions, blockers, residue or candidate notes under a reviewed policy; merely leaving a predicate unclassified is not a complete executable implementation of that policy.

## Dependencies, cycles and combined assurance

Ten exact semantic uses are authored: Definition, Invariant, Typed Relation, Relation Kind, Classification Orthogonality Invariant, Validation, Authority Promotion, Effect, Evidence and Authority. The reachable declared graph contains 45 nodes and 105 edges, with 31 missing counterpart interpretation packets. One fourteen-member strongly connected component has 48 internal edges and remains unclassified. A dependency cycle is not automatically a forbidden value-constraining cycle or a legitimate fixed point; its edge meanings and cycle policy require review.

Fourteen current partial drafts now account for 319 source units and 469 clauses: 159 encoded, 115 explanatory and 195 deferred; 129 required and 200 unresolved populations. Each has a separately evaluated supplied model witness. Those local, qualified witnesses do not establish a shared-meaning joint model. Of 183 current identities, 169 still lack a per-definition draft. Owner-accepted whole translations and whole-definition proofs remain zero.

## Validation, preservation and next work

The initial no-op target mutant and wrong registry collection name were corrected with their code and failed logs retained. The blanket historical-example compatibility expectation was replaced by exact accounting of the observed mismatch; its failed attempt is retained too. A fresh replay also exposed nondeterministic ordering from iterating a set of control field names. That attempt and all six results are retained; controls now iterate sorted names. Final replays check contract structure, model denotation, source bindings, bounded profile, dependency selection and inventory. The closeout rechecks 201 source files and all 1,530 predecessor files, seals this candidate's exact output bytes and keeps the goal active.

The next definition priority is Classification Orthogonality Invariant. Its source meaning is needed to review the nonorthogonality trigger and keep independent axes separate. Subsequent obligations include current effect/scope embedding, temporal ordering, complete dependency meanings, forbidden-cycle checks and actual owner fidelity. The episode is not complete, and this agent self-review is not an owner acceptance decision.
