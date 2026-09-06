# First-Class Category Boundary Research

Dispatch: `2026-07-02-first-class-category-boundary`

## Agent 1 - Lawvere, F. William

**1. Formal Answer**

Repeated morphism broadness alone does **not** create a category. Unsourced math: general category theory knowledge.

A category needs:

- **Objects:** the things being related, e.g. DomainSpec meta-types or concrete concepts.
- **Morphisms:** typed arrows between objects, e.g. `Rule -> Operation` or `Entity -> Entity`.
- **Identity:** each object must have a do-nothing self-arrow, meaning the object remains itself across the graph.
- **Composition:** if `A -> B` and `B -> C`, there must be a lawful composed path `A -> C` where the semantics still make sense.
- **Closure:** composing accepted arrows cannot produce an undefined or incoherent relation.
- **Associativity:** multi-step paths must mean the same thing regardless of grouping.

So "many useful arrows" is evidence, not proof. Broad repeated arrows justify promotion only when they form a stable typed graph fragment with lawful composition. Otherwise they are a projection/detail.

Repo fit: DomainSpec already frames taxonomy as node alphabet, relationships as edge-law, and composability as realization in code ([synthesis.md](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/research/2026-07-01-composability-edges-taxonomy-synthesis.md:31), [synthesis.md](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/research/2026-07-01-composability-edges-taxonomy-synthesis.md:55), [synthesis.md](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/research/2026-07-01-composability-edges-taxonomy-synthesis.md:78)).

A **subcategory** is justified when a subset of objects/arrows inherits identities and composition from the larger graph. A **functor-like translation** maps root concepts and arrows into implementation projections while preserving identity and composition; this matches the current decision that root owns authority and implementation consumes projections ([edge-signature-authority-decisions.md](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/reformulate-batch1/governance/edge-signature-authority-decisions.md:53), [edge-signature-authority-decisions.md](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/reformulate-batch1/governance/edge-signature-authority-decisions.md:82), [edge-signature-authority-decisions.md](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/reformulate-batch1/governance/edge-signature-authority-decisions.md:111)).

**2. Promotion Criteria**

Promote a DomainSpec thing to first-class authority only if all hold:

1. It has a stable object class or typed relation family, not one local convenience.
2. Its arrows have typed endpoints and crisp semantics.
3. It composes into meaningfully different downstream behavior or code, matching the repo rule that an edge is admissible iff it composes into different code ([synthesis.md](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/research/2026-07-01-composability-edges-taxonomy-synthesis.md:72)).
4. It preserves closure: legal paths stay legal and interpretable.
5. It has examples and non-examples.
6. It has a root authority home, with implementation as direct consumer or projection.
7. It is not merely a field, label, metadata flag, or signature property.
8. It survives the "Yoneda" intuition: the concept can be recovered from its relations, not just from a field list ([category-theory-domainspec-language-synthesis.md](/home/vrondelli/projects/domainspec-core/.arcanum/inventory/entries/category-theory-domainspec-language-synthesis.md:40), [2026-06-21-category-theory-domainspec-language-cards.md](/home/vrondelli/projects/domainspec-core/.arcanum/inventory/entries/evidence-cards/2026-06-21-category-theory-domainspec-language-cards.md:52)).

**3. R3 Applications**

- **Entity relation family:** promote. The decision already selects first-class semantic `Entity -> Entity` relations such as `owns`, `belongs-to`, and `depends-on`, with direction and inverse semantics still needing definition ([edge-signature-authority-decisions.md](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/reformulate-batch1/governance/edge-signature-authority-decisions.md:145)). Formally, this is not "broadness alone"; it is a repeated object-pair family whose arrows change graph navigation and typed meaning.

- **Saga signatures:** conditionally promote. Saga is already a meta-type for cross-feature transactional orchestration with compensation and rollback semantics ([TAXONOMY.md](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/impl/spec/TAXONOMY.md:220)). Promote `Saga --[orchestrates]--> Operation[]` only if Saga has distinct composition laws from Workflow: participants, cross-context failure handling, compensation, and invariants. If it is only Workflow plus `scope: cross-feature`, keep it as Workflow metadata.

- **Edge labels vs signatures:** labels are names; signatures are typed arrows with source, target, semantics, and composition rule. `Operation -> ValueObject returns` is likely a signature property, not an edge, per R3 synthesis ([synthesis.md](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/research/2026-07-01-composability-edges-taxonomy-synthesis.md:65)). Promote signatures, not decorative labels.

**4. Examples**

First-class:

- `Rule -> Operation` via `enforces`: has typed endpoints, execution semantics, and code realization ([RELATIONSHIPS.md](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/impl/spec/RELATIONSHIPS.md:102)).
- `Workflow -> Operation[]` via `orchestrates`: composes multiple operations into a process ([RELATIONSHIPS.md](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/impl/spec/RELATIONSHIPS.md:138)).
- `Entity -> Entity` semantic family, if `owns` / `belongs-to` / `depends-on` get crisp direction and non-examples.

Non-examples:

- A field reference hidden in an Entity table.
- A broad verb like `references` without composition semantics.
- `returns ValueObject` when it is just output shape.
- Saga as a separate edge source if it only duplicates Workflow with one metadata flag.

**5. Recommendation**

Promote first-class authority when a concept or relation family forms a closed, typed, composable graph fragment whose implementation projection must preserve its laws; broad repeated arrows are only the smoke, not the fire.

## Agent 2 - Wittgenstein, Ludwig

**Domain-Language Answer**

A concept or relation becomes first-class when it stops being mere wording and starts carrying model obligations: people make different domain decisions because it exists, examples/non-examples can be sorted by it, invariants attach to it, and implementation must preserve it rather than invent it.

Local evidence points the same way: DomainSpec's taxonomy is the node alphabet, relationships are the edge-law, and composability is how those edges become executable realization ([synthesis.md](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/research/2026-07-01-composability-edges-taxonomy-synthesis.md:31), [synthesis.md](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/research/2026-07-01-composability-edges-taxonomy-synthesis.md:72)). First-class authority belongs at root definitions/authority; `impl/` should consume or project it, not originate it ([domainspec-v2-CONSTITUTION.md](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/authority/constitutions/domainspec-v2-CONSTITUTION.md:47), [edge-signature-authority-governance-pack.md](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/reformulate-batch1/governance/edge-signature-authority-governance-pack.md:97)).

**Promotion Signals**

Promote when these are true:

- **Ubiquitous-language stability:** domain speakers use the word consistently enough that replacing it with `reference` loses meaning. General DDD/domain-modeling principle.
- **Examples and non-examples:** the candidate has clear included/excluded cases, as required for R3 verbs like `owns`, `belongs-to`, and `depends-on` ([edge-signature-authority-decisions.md](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/reformulate-batch1/governance/edge-signature-authority-decisions.md:176)).
- **User decisions:** an owner has decided the distinction matters; here, Entity-to-Entity semantic relations were selected as first-class candidates ([edge-signature-authority-decisions.md](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/reformulate-batch1/governance/edge-signature-authority-decisions.md:145)).
- **Invariants:** the term carries rules that can be violated, such as lifecycle, ownership, compensation, or endpoint constraints.
- **Workflow consequences:** choosing the term changes behavior, validation, navigation, or proof obligations.
- **Implementation independence:** it is not just how one database, DTO, or file currently points at another; root authority can define it and implementation can project it ([edge-signature-authority-governance-pack.md](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/reformulate-batch1/governance/edge-signature-authority-governance-pack.md:225)).

**R3 Applications**

- **`owns`, `belongs-to`, `depends-on`:** good first-class candidates only if each gets direction, endpoint rules, examples, non-examples, and whether inverse labels are aliases or distinct signatures. Otherwise they become prettier `references`.
- **Saga vs Workflow:** Workflow already means orchestration within one feature; Saga means cross-feature/bounded-context orchestration with compensation and end-state invariants ([TAXONOMY.md](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/impl/spec/TAXONOMY.md:201), [TAXONOMY.md](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/impl/spec/TAXONOMY.md:220)). Saga deserves first-class status if those cross-boundary guarantees produce distinct relation/proof obligations; otherwise fold it into Workflow plus metadata.
- **`references` smell:** `references` is usually implementation language. It says "there is a pointer," not "what domain relationship holds." Keep it as a projection/detail unless the domain itself has a reference-like concept with rules.

**Risks**

- **Relation explosion:** every natural verb becomes an edge. Control it with the admissibility rule: promote only non-redundant distinctions with different consequences.
- **Ambiguous direction:** `A owns B` and `B belongs-to A` must not both enter the law without a direction rule.
- **Inverse labels:** decide whether inverse names are display aliases or separate legal edge signatures.
- **Aggregate-boundary confusion:** ownership in the model is not automatically aggregate ownership, database containment, or write authority. Mark the boundary explicitly.

**One-Line Recommendation**

Promote a concept or relation only when it is a stable domain distinction with owner-backed meaning, examples/non-examples, invariants, and executable consequences; otherwise keep it as an implementation projection or descriptive detail.

## Agent 3 - Fong, Brendan

## Fong, Brendan - Lane 3 Report

### 1. Machine-Contract Answer

A DomainSpec relation deserves first-class authority when it changes what machines can compose, reject, derive, or project. The test is: **does this relation create a distinct typed composition obligation, or is it only a human navigation/detail label?**

Promote it when:

- It has admissible typed endpoints, not just a label. Current R3 explicitly wants validators checking endpoint signatures, not label membership only ([governance pack](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/reformulate-batch1/governance/edge-signature-authority-governance-pack.md:277)).
- It makes a forbidden edge unconstructible, e.g. `Operation --[enforces]--> Value Object` must fail ([governance pack](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/reformulate-batch1/governance/edge-signature-authority-governance-pack.md:280)).
- It composes into different code or validation behavior. Existing synthesis says an edge earns admissibility iff it composes into different code ([taxonomy synthesis](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/research/2026-07-01-composability-edges-taxonomy-synthesis.md:72)).
- It belongs on the contract plane: finite signatures consumed by validators, not ontology/research confidence fields ([ontology synthesis](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/research/2026-07-01-spec-as-ontology/synthesis.md:22)).
- It is root-owned authority, with `impl/spec/RELATIONSHIPS.md` only a projection ([decisions](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/reformulate-batch1/governance/edge-signature-authority-decisions.md:82), [governance pack](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/reformulate-batch1/governance/edge-signature-authority-governance-pack.md:97)).

If it only improves wording, browsing, explanation, diagramming, or reverse lookup, keep it as projection/detail.

### 2. Minimal Schema / Signature Criteria

A first-class relation signature should minimally carry:

- `id` / `verb`: canonical machine key and human verb.
- `source_type`: allowed source concept type or union.
- `target_type`: allowed target concept type or union.
- `direction`: canonical obligation direction.
- `multiplicity`: `one`, `optional`, `many`, `ordered_many`, etc.
- `composition_behavior`: what code/spec relation must exist because of this edge.
- `inverse_or_dual`: generated inverse view, paired relation, or explicitly none.
- `validation_obligation`: endpoint check, code realization check, projection sync, fixtures.
- `projection_rules`: how it appears in `relationships.md` and `impl/spec/RELATIONSHIPS.md`.

The old validator currently parses only canonical edge labels from markdown tables and checks whether feature rows use those labels ([validator](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/impl/tools/validate-relationships.ts:43), [validator](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/impl/tools/validate-relationships.ts:72)). That is label authority, not signature authority.

### 3. R3 Applications

**Semantic Entity relation family:** promote. The decision already selects a first-class semantic Entity relation family with `owns`, `belongs-to`, and `depends-on`, provided SWU-R3A defines direction, examples, non-examples, and inverse handling ([decisions](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/reformulate-batch1/governance/edge-signature-authority-decisions.md:176)). My rule: canonize `owns` and generate `belongs-to` as its inverse unless they impose different validation behavior.

**Saga signatures:** promote only if Saga has distinct machine behavior: cross-feature orchestration, participants, compensation, and residue rules. If it is merely `Workflow` with `scope: cross-feature`, fold it into Workflow metadata ([decisions](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/reformulate-batch1/governance/edge-signature-authority-decisions.md:188)).

**`produces` vs `emits`:** current docs make `Operation -> Event` mean successful completion causes an event, while `Entity -> Event` means the entity is the event source ([RELATIONSHIPS](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/impl/spec/RELATIONSHIPS.md:66), [RELATIONSHIPS](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/impl/spec/RELATIONSHIPS.md:182)). Keep both only if they validate different obligations. Better split: `Operation --[publishes]--> Event` for execution cause, and `Event --[describes-change-to]--> Entity` for event subject. Then `Entity --[has-event]--> Event` can be a generated navigation view.

**Labels vs endpoint signatures:** labels are presentation. Endpoint signatures are law. `enforces` alone is not meaningful authority; `Rule --[enforces]--> Operation` is.

### 4. Human Notation Recommendation

Use two levels:

```text
Signature: Rule --[enforces]--> Operation
Instance:  MaxAmountRule --[enforces]--> ProcessPayment
```

For multiplicity and scope:

```text
Workflow --[orchestrates ordered 1..*]--> Operation
Saga --[orchestrates cross-feature ordered 1..*]--> Operation
```

For inverse views:

```text
Canonical: Entity --[owns]--> Entity
Generated: Entity <--[belongs-to]-- Entity
```

Canonical arrows should point in the direction of the machine obligation. Reverse navigation should be generated unless it carries distinct validation behavior.

### 5. One-Line Recommendation

Make a relation first-class only when its typed signature creates a distinct composition or validation obligation; otherwise keep it as a generated human projection.

## Agent 4 - Lakatos, Imre

Read-only report completed. No files edited.

## First-Class Authority Boundary

A DomainSpec thing earns first-class authority when it becomes a progressive problem-solving unit: it repeatedly explains real cases, survives counterexamples, forces sharper distinctions, and changes what validators, owners, or implementers must do.

The test is not "does this sound ontological?" It is:

1. **Witness:** a real use case breaks or stalls without it.
2. **Stable contrast:** it is not interchangeable with an existing concept after examples and non-examples.
3. **Validator consequence:** promotion changes admissibility, derivation, projection sync, or conformance checks.
4. **Decision consequence:** an owner must choose differently because the distinction exists.
5. **Projection boundary:** root authority owns the term/signature; implementation only consumes or projects it.

Repo evidence fits this: R3 root authority is now project-wide, with relationship authority moving to `definitions/relationships/` and `impl/spec/RELATIONSHIPS.md` demoted to projection/view (`projects/domainspec-v2/development/reformulate-batch1/governance/edge-signature-authority-decisions.md:53`, `:82`, `:111`). The governance pack says root definitions/authority own edge verbs, endpoint signatures, cardinality, scope, status, and promotion posture (`projects/domainspec-v2/development/reformulate-batch1/governance/edge-signature-authority-governance-pack.md:97`).

## Kill Criteria

Reject or defer promotion when the candidate has:

- **No witness:** no real spec, novice use, toy, validator, or implementation failure depends on it.
- **No stable contrast:** examples collapse into an existing type, edge, status, or metadata field.
- **No validator consequence:** nothing changes in edge admissibility, conformance, derivation, or projection sync.
- **No new decision:** owners would make the same routing/promotion call either way.
- **Just relabeling:** it renames a projection/detail without moving authority or blocking contradiction.

This is the adversarial rule: a concept is not promoted because it is elegant; it is promoted because refusing it keeps producing unresolved failures.

## R3 Stress Tests

**Entity semantic relation family:** promote. The novice witness found no Entity-to-Entity edge, making ordinary relations like `Loan->Copy`, `Loan->Patron`, and `Copy->Branch` unrepresentable (`projects/domainspec-v2/development/reformulate-batch1/HANDOFF-novice-test-edge-findings.md:24`). The decision record already selects first-class semantic Entity relations such as `owns`, `belongs-to`, and `depends-on`, with direction/examples/non-examples still required (`.../edge-signature-authority-decisions.md:176`). This passes witness, contrast, and decision tests.

**Saga signatures:** keep as high-pressure candidate until the owner chooses. Current `RELATIONSHIPS.md` has `orchestrates` only as `Workflow -> Operation[]` (`projects/domainspec-v2/impl/spec/RELATIONSHIPS.md:22`) and no Saga signature; the novice handoff calls Saga orphaned (`.../HANDOFF-novice-test-edge-findings.md:36`). Saga research shows distinct obligations: participants, compensation, temporal safety, freshness, and state transitions (`projects/domainspec-v2/research/dcb-saga-correctness/PROOF-OBLIGATIONS.md:11`, `:40`). Promote Saga only if those obligations are not reducible to Workflow plus cross-feature metadata.

**references / owns / belongs-to / depends-on:** do not promote all names equally. `references` is a generic projection-ish relation unless it has a stable semantic contrast. `owns`, `belongs-to`, and `depends-on` are better first-class candidates because they imply different directionality and validator questions. But `owns`/`belongs-to` may be inverse views, so promote the family first; promote individual verbs only after examples/non-examples prove they are not duplicate signatures.

**Category status:** keep as candidate/rationale, not promoted authority. The decision record says category-theory language remains rationale and validators consume finite signatures (`.../edge-signature-authority-decisions.md:213`). Category framing may guide discovery, but it earns authority only when it yields finite root-owned signatures, definitions, and checks.

## Lifecycle

**candidate:** named because a failure, analogy, or research pressure exists; may live in research/governance packs.

**research-backed:** has witnesses, counterexamples, alternatives, and residue. It can recommend promotion but cannot mutate authority.

**authority:** root-owned canonical human/machine surface with owner decision, definition/signature, examples/non-examples, and validator/projection implications.

**implementation projection:** generated or checked view consumed by tools/code/docs; it never originates or silently overrides authority.

## One-Line Recommendation

Promote only distinctions that repeatedly solve real failures and create new root-owned validation or owner-decision consequences; otherwise keep them as candidate research or implementation projection.
