---
title: L3 — inference discipline and semantic independence
status: not-started
dependsOn: [L2]
---

# L3 — inference discipline and semantic independence

**Decision question:** After this layer, we know whether explicit rules can derive permitted conclusions while preserving selected forbidden-justification boundaries through indirect chains.

**Minimum working unit:** a restricted finite rule profile, a checked legitimate derivation, a general boundary theorem, an indirect-leakage control, and a checked independence witness for one selected implication.

## Purpose and boundary

The current records list forbidden inferences using labels such as admission, runtime-conformance, and new-authorization. Those labels are review guidance until they are mapped to exact predicates, scopes, and justification rules.

Distinguish global logical independence from workflow justification. A relation can coexist with a protected fact while providing no legitimate reason to derive it. Existing admitted state can legitimately seed admission facts; the presence of conformance alongside them is not a violation.

## Inputs and outputs

Inputs are the selected theory, exact finite base facts, proposed rules/couplings, protected conclusion definitions, and L2 rule-change obligations. The trusted authority/evidence adapter supplies any root justification facts, with exact target, effect, scope, and epoch bindings.

Outputs include a rule contract, declared derivation semantics, proof certificates, a certificate checker and soundness theorem, checked closure evidence, protected-conclusion proofs, coupling assessment, and countermodels with explicit scope.

## Initial rule language

Use positive, function-free, range-restricted rules over a finite active domain. Every head variable occurs in a positive body premise. Qualifier literals and version/scope values must come from the selected finite input/profile; rules cannot invent arbitrary new identities or fetch external facts during closure.

Declare each rule's identifier, typed predicates, premises, conclusion, qualifier constraints, scope/version matching, and justification role. Validate that each relation conclusion uses a declared pair. Symmetry, transitivity, and inverse equivalence exist only through explicit rules.

Positive closure is monotone: repeatedly add justified ground facts until no rule adds another fact. The finite profile makes termination demonstrable, but a large grounding may exceed the runtime budget; then the result is timeout/unknown, not completed closure.

Start with a direct checker in the formal implementation. A fast external Datalog engine may later compute candidates, but it must not define the trusted semantics merely by returning tuples.

## Certificate and saturation checking

A derivation certificate is a finite DAG with base-fact leaves and rule-application nodes. Each step must bind the exact rule/version, a ground substitution, previously checked premises, and the typed conclusion. Reject cyclic certificates, missing premises, and unbound substitutions.

Required proof sketch:

```text
derivation_certificate_sound:
  checkDerivation(T,F,certificate,conclusion)=true
  -> Derivable(T,F,conclusion)
```

That theorem proves a positive derivation, not the absence of one. For finite non-derivability, additionally check that the proposed closure contains every base fact and every ground rule consequence, and that every included derived fact has a valid derivation. The resulting set equals the least fixed point; absence from it is meaningful for that exact profile and fact set.

Early termination or checking only supplied proof paths cannot establish non-derivability. Rule dependency graphs help identify candidate leakage paths, but graph reachability alone is not a proof that a derivation exists or is impossible.

## Protected-conclusion semantics

Select precise protected predicates, such as `Admitted(targetVersion,effect,scope,epoch)`. Define root justification facts with the same binding dimensions. A freely supplied string such as `application_receipt_ref` cannot act as a verified authority root.

A useful theorem says every derivation of a selected protected conclusion contains an appropriately matching checked root justification in its proof lineage. Prove it by induction over derivations after checking every rule that can produce that conclusion or an intermediate justification.

This is stronger and more useful than assuming the initial fact set contains no protected facts. It allows existing legitimate admission and new conformance to coexist while forbidding conformance-only justification.

Exercise a direct illegal rule and an indirect chain, for example conformance -> a misleading intermediate assessment -> admission. The intermediate predicate does not conceal the missing root. A legitimate bridge with independent exact authorization facts must remain usable.

## Independence and countermodels

For a selected theory `T`, test the implication `ConformsTo(a,c,q) -> Admitted(a)`. A countermodel must satisfy `T`, make the conformance premise true, and falsify the admission conclusion. It establishes non-entailment of that implication; it does not establish that every conformance assertion is unadmitted.

Specify both directions separately when claiming independence of two axes. Claims that arbitrary changes on one axis leave another unchanged require a model transformation/noninterference theorem, not merely different predicate names or one counterexample.

Alloy can search candidate finite models. Translate and replay a found witness against the exact selected theory. Record integer semantics and object/trace scope where applicable; absence of a witness remains bounded-search evidence. [Alloy specification](https://alloytools.org/spec.html)

## Ordered implementation work

1. Map selected forbidden-inference labels to precise predicates and justification boundaries.
2. Define and validate the finite rule language.
3. Specify derivability, closure, and certificate semantics.
4. Implement/prove derivation checking and closure certification.
5. Prove selected protected-conclusion lineage requirements.
6. Discharge L2 rule-change obligations and replay indirect-chain controls.
7. Add countermodel discovery only where it reduces the cost of a selected non-entailment question.

## Validation and acceptance

Acceptance cases include a legal rule application, an invalid ground substitution, a cyclic proof, a scope/version mismatch, an omitted applicable rule in a claimed complete closure, a direct authority leak, an indirect leak, and independently justified admission coexisting with conformance.

Completion requires generic certificate soundness, selected boundary proofs, a completed closure demonstration, and checked witness or unresolved status for every required independence claim. No inference profile is called safe merely because a solver found no small counterexample.

## Outcome, cost, and promotion

The operator can trace why a conclusion follows and identify which coupling introduces a forbidden justification. Risk reduced: semantics and authority leaking through indirect chains. Cost is high, dominated by precise provenance boundaries and rule proof coverage.

Proceed to L4 when the selected rule/extension profiles are fully evidenced. Preserve all earlier validity and compatibility guarantees, and ensure derived assertions retain their derivation posture rather than becoming admitted instances automatically.

## Deferred scope

Unrestricted negation, generated function terms, temporal reasoning, arithmetic automation, universal independence of every kind pair, and external reasoning engines as trusted oracles. Additional profiles require their own semantics, termination/correctness arguments, and evidence ceilings.
