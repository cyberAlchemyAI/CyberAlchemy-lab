---
title: L2 — model evolution and extension compatibility
status: not-started
dependsOn: [L1]
---

# L2 — model evolution and extension compatibility

**Decision question:** After this layer, we know whether a proposed change preserves the specific guarantees it claims, and whether it changes the old vocabulary's meaning.

**Minimum working unit:** one supported new endpoint pair, one supported new relation kind, generated obligations, preservation evidence, and a report classifying compatibility and affected prior evidence.

## Purpose and boundary

L1 checks a selected frozen model. L2 lets that model evolve without treating every addition as harmless. A new pair can widen an existing predicate. A new kind can introduce constraints on old nodes. A rule can create a new conclusion through an old chain. Each change needs obligations matched to its actual effects.

The first supported profiles should be additive instance changes, additive pair changes with named invariant checks, and fresh relation definitions with no hidden constraints on old facts. Semantic strengthening, removal, lifecycle transitions, and rule changes must be classified; unsupported proof requirements remain open.

Full rule-boundary checking is L3 work. L2 may generate and display those obligations but cannot mark a rule-changing proposal completely ready until they are discharged.

## Inputs and outputs

Inputs are exact base and proposed snapshots, a normalized diff, selected graph/instance inventories, L1 semantic coverage, and an explicit compatibility request. Compatibility is a named property with scope, not a general `safe` label.

Proposed outputs include a change proposal contract, semantic diff, required obligation set, checked proofs/model witnesses, compatibility classification, invalidation report, and an evidence bundle. Each obligation names the source of its requirement so a new proposal cannot silently omit it.

## Change classes and obligation matrix

| Change | Obligations that must be considered |
| --- | --- |
| Instance addition | Endpoint/qualifier/reference validity and affected graph invariants |
| Pair addition | New kinds resolve; explicit pair permission; qualifier applicability; preservation of old cases and global invariants |
| Fresh kind | Fresh signature, closed qualifiers, semantic definition, non-vacuity, interactions, and any claimed conservativity |
| Qualifier revision | Exact type/value diff, valid old-instance handling, meaning preservation or declared migration |
| Constraint strengthening | Which old models/instances become invalid and whether revision is intentionally incompatible |
| Pair/kind removal or withdrawal | Affected assertions, historical interpretation, unresolved current references |
| Inference-rule revision | New derivation obligations and protected-conclusion impacts, discharged with L3 |
| Rename/alias/inverse change | Identity preservation, explicit endpoint mapping, and intended equivalence obligations |

The proposal class is inferred from the normalized diff and compared with the author's label. Calling a qualifier change an instance addition does not reduce its obligation set.

## Three different compatibility properties

**Selected-data compatibility:** every assertion in the declared old inventory remains interpretable and valid under the new profile. A finite recheck establishes this property for that inventory only.

**Invariant preservation:** for the supported proposal mechanism, a valid base graph and a successful extension check imply the declared invariants for the resulting graph/theory. Establish this against independent predicates, as in L0.

**Model conservativity:** every model of the base theory has an expansion to the extended theory with the same old interpretation. Proving this expansion property is a sufficient semantic route to show that old-language consequences have not been strengthened. One successful fixture or one satisfiable new model is not enough.

Pair additions change the admissibility relation of an existing kind. They should normally be reported as an explicit permitted widening, even when all selected old instances remain valid. Do not call that unchanged old semantics merely because the change is backward compatible for the selected data.

For a fresh derived kind `New(x,y) iff DefinitionUsingOldVocabulary(x,y)`, an expansion construction may be straightforward if it imposes no additional old constraints. A declaration such as "every old node must have exactly one New target" requires stronger existence and uniqueness properties of the old model and may fail conservativity.

## Consistency and proof obligations

Require a model witness satisfying the actual included theory and relevant relations. Record its universe, interpretation, assumptions, and nonempty use cases. An empty relation may be logically legitimate, but is insufficient to demonstrate a claimed useful relationship when the chosen acceptance question requires instances.

For supported profiles, define theorem sketches:

```text
extension_check_sound:
  BaseValid(T,G) -> checkExtension(T,G,delta)=true
  -> DeclaredRequirements(T,G,delta)

selected_instances_preserved:
  Compatible(delta) -> OldSelectedValidInstancesRemainValid(T,delta)

definitional_extension_expands:
  BaseModel(T,M) -> ExtendedModel(extend(T,delta),expand(M,delta))
  and reduct(expand(M,delta))=M
```

The first theorem must include obligation-generation coverage. Proving a verifier accepts the submitted obligation list is insufficient if the proposer can leave required obligations out. In initial implementation, derive the list using a small reviewed change-class matrix; later prove coverage for that supported matrix.

Bind both old and new semantics. A proof about the old theory is not evidence about a renamed or strengthened new predicate, even if its display name and theorem identifier stay unchanged.

## Ordered implementation work

1. Define proposal types, exact base binding, and machine-derived diff classification.
2. Select the first extension profiles and their compatibility meanings.
3. Generate requirements and an explicit dependency/invalidation map.
4. Implement finite checks for selected-data preservation and reference closure.
5. Prove preservation for supported additive profiles.
6. Provide consistency witnesses and, where claimed, model-expansion proofs.
7. Present rule obligations as awaiting L3 until inference evidence exists.

## Validation and acceptance

Controls must exercise a valid pair addition, a fresh derived kind, a changed qualifier type, a contradictory constraint, a new existence constraint not guaranteed by the base model, an old-instance regression, a misleading proposal class, and a proof reused against changed semantics.

Verify that a failed proof attempt yields unresolved evidence unless an actual violation/countermodel is checked. A compatibility report can correctly identify an intentional breaking revision; that is a successful analysis result, not permission to apply it under an additive-extension policy.

Completion requires required-obligation coverage, a checked supported pair extension, a checked supported kind extension, explicit compatibility classifications, and controls demonstrating that stronger claims are not inferred from weaker evidence.

## Outcome, cost, and promotion

The reviewer sees what changes, which guarantees survive, what becomes invalid, and what needs replay. Risk reduced: apparently small changes altering old meaning or reusing irrelevant proofs. Cost is high, dominated by profile design and expansion/preservation proofs.

Continue to L3 after the supported extension profiles work. Narrow the supported profile when arbitrary constraint interactions resist automation; retain the proposal and its unresolved requirements without fabricating a negative theorem.

## Deferred scope

Automatic conservativity for arbitrary theories, general proof discovery, unrestricted constraints, and autonomous migration/application. Preserve L0/L1 correctness, faithful mappings, and currentness boundaries. Every semantic revision is visible, even when it preserves the selected data.
