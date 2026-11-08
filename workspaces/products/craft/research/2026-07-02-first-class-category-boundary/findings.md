# First-Class Category Boundary Findings

Dispatch: `2026-07-02-first-class-category-boundary`

A DomainSpec relation becomes first-class only when it is a stable domain distinction that changes root-owned validation, composition, derivation, projection, or owner decisions; broad recurrence is evidence for review, not proof of authority.

## Verdict Matrix

| candidate | owner/precedent | witnessed? | sound? | verdict | next use |
| --- | --- | --- | --- | --- | --- |
| first-class promotion rubric | Consolidates existing DomainSpec precedent: C1/root authority (`projects/domainspec-v2/authority/constitutions/domainspec-v2-CONSTITUTION.md:44-53`), AUTH-1..3 (`projects/domainspec-v2/development/reformulate-batch1/governance/edge-signature-authority-decisions.md:53-112`), D3 edge-law admissibility (`projects/domainspec-v2/definitions/DEFINITIONS.md:99-113`), D4 executable typed graph (`projects/domainspec-v2/definitions/DEFINITIONS.md:144-152`), spec-as-ontology two-plane boundary (`projects/domainspec-v2/research/2026-07-01-spec-as-ontology/synthesis.md:20-24`), category cards, DDD/domain language, ontology promotion discipline [Precedent]. | Yes as a rubric synthesis across [Lawvere], [Wittgenstein], [Fong], [Lakatos], [Precedent], [Non-vacuity], [Definitional]. | Yes if tightened around non-redundant law and concrete downstream obligation [Definitional]. | Accept with tightening. | Use as the R3 promotion gate before adding or rejecting relationship signatures. |
| root ownership as placement | Root authority is already selected: `definitions/relationships/` owns relationship authority and `impl/spec/RELATIONSHIPS.md` is projection/view (`projects/domainspec-v2/development/reformulate-batch1/governance/edge-signature-authority-decisions.md:57-83`, `:86-112`; `projects/domainspec-v2/authority/constitutions/domainspec-v2-CONSTITUTION.md:44-53`) [Precedent]. | Yes as an owner decision. | Sound only as authority placement after promotion, not as evidence that promotion is deserved [Definitional]. | Accept as placement requirement, not promotion criterion. | Put promoted relationship law in root `definitions/relationships/relationships.yml`; treat impl files as consumers/projections. |
| Entity semantic relation family | Owner selected first-class semantic Entity relation family (`owns`, `belongs-to`, `depends-on`) with required direction, examples, non-examples, and inverse handling (`projects/domainspec-v2/development/reformulate-batch1/governance/edge-signature-authority-decisions.md:145-178`) [Precedent]. | Yes. Novice use found no Entity-to-Entity edge, making `Loan->Copy`, `Copy->Title`, `Loan->Patron`, `Reservation->Title`, and `Copy->Branch` unrepresentable (`projects/domainspec-v2/development/reformulate-batch1/HANDOFF-novice-test-edge-findings.md:24-34`; `projects/domainspec-v2/development/comprehension-novice-test/stall-dataset.md:41`) [Non-vacuity]. | Conditional. Promote the family, not every verb name; each member still needs non-redundant law [Definitional]. | Survive. | Add a root Entity-to-Entity family with per-signature endpoint/admissibility rules and examples/non-examples. |
| owns | Owner-selected candidate inside Entity semantic family (`edge-signature-authority-decisions.md:153-178`) [Precedent]. | Partly. Product brief says the library owns physical copies (`projects/domainspec-v2/development/comprehension-novice-test/task.md:20-23`) [Non-vacuity]. | Sound only if ownership has distinct validation/composition behavior and an inverse policy [Definitional]. | Refine. | Define `Entity --[owns]--> Entity` with examples/non-examples; generate inverse as `owned-by` unless a distinct inverse law is approved. |
| belongs-to | Owner-selected candidate, but inverse ambiguity is explicitly called out (`edge-signature-authority-decisions.md:153-178`) [Precedent]. | Yes, but it cuts against naive inverse collapse: a copy belongs to a title and a branch in the brief (`projects/domainspec-v2/development/comprehension-novice-test/task.md:22-23`, `:34-35`) [Non-vacuity]. | Sound as a distinct membership/home-assignment relation if witnessed; unsound as automatic inverse of `owns` [Definitional]. | Refine. | Define whether `belongs-to` means membership, catalog classification, home assignment, or generated inverse; do not silently equate it with `owns^-1`. |
| depends-on | Named in owner-selected candidate family (`edge-signature-authority-decisions.md:153-178`) [Precedent]. | No concrete R3 witness differentiates it from generic reference [Non-vacuity]. | Underdefined until dependency kind and validation consequence are named [Definitional]. | Kill for current promotion; defer as candidate. | Keep out of current authority until a witness proves reject/allow behavior different from `references` or field-level dependency. |
| Saga signatures | Saga remains an open owner decision (`edge-signature-authority-decisions.md:180-205`) [Precedent]. Saga has formal scope/compensation language (`projects/domainspec-v2/definitions/meta-types/meta-types.md:410-445`). | Yes pressure: Saga is orphaned from current relationship signatures (`HANDOFF-novice-test-edge-findings.md:36-44`; `stall-dataset.md:42`) and DCB proof obligations name participants, compensation, cross-context activation, and temporal safety (`projects/domainspec-v2/research/dcb-saga-correctness/PROOF-OBLIGATIONS.md:11-36`, `:38-49`) [Non-vacuity]. | Conditional. Sound only if Saga has laws not reducible to Workflow plus `scope: cross-feature` [Definitional]. | Refine / conditional survive. | Decide whether Saga gets `Saga --[orchestrates]--> Operation[]` with cross-feature/compensation obligations, or collapses into Workflow metadata. |
| produces/emits split | Current `RELATIONSHIPS.md` distinguishes `produces` as `Operation -> Event` and `emits` as `Entity -> Event` (`projects/domainspec-v2/impl/spec/RELATIONSHIPS.md:13-27`, `:66-73`, `:182-189`) [Precedent]. | Yes. Operation card contradicts the table by listing `emits` as Operation-sourced and omitting `produces` (`projects/domainspec-v2/development/reformulate-batch1/HANDOFF-novice-test-edge-findings.md:46-59`; `projects/domainspec-v2/impl/spec/meta-types/behavioral/operation.schema.yml:21-23`) [Non-vacuity]. | Sound as endpoint split because source type changes admissibility [Definitional]. | Survive as endpoint split. | Reconcile R3 so `Operation -> Event` uses `produces`; `Entity -> Event` uses `emits`; reject Operation as source of `emits`. |
| Source --[verb]--> Target notation | Useful display convention, not authority [Fong], [Precedent]. | Yes as notation in research lanes; no witness that notation itself changes validation. | Unsound as promotion criterion; sound as display for root-owned signatures [Definitional]. | Kill as authority; keep as notation. | Use only to render canonical signatures and instances. |
| category-theory framing | Existing category cards and research are precedent/rationale, but validators consume finite signatures [Precedent]. | Yes as explanatory rationale in [Lawvere] and [Fong]. | Sound only if phrased as typed composable graph fragment unless identities, composition, closure, and associativity are formalized [Definitional]. | Keep as rationale. | Say "typed composable graph fragment" in R3; reserve "category" for future formal law. |

## Canonical Promotion Rubric

### Mandatory Promotion Criteria

Promote a DomainSpec concept or relation to first-class authority only when all of the following hold:

1. **Stable contrast:** it names a durable domain distinction that does not collapse into an existing type, edge, field, status, metadata flag, browsing label, or pointer after examples and non-examples are tested [Wittgenstein], [Lakatos], [Definitional].
2. **Examples and non-examples:** it has enough positive and negative cases that an owner, validator, and implementer can tell when the relation applies [Wittgenstein], [Precedent].
3. **Typed signature:** it has source type, target type, direction, multiplicity/order when relevant, and endpoint admissibility rules [Fong], [Definitional].
4. **Inverse/dual policy:** if a reverse name exists, authority says whether it is generated navigation, a dual, or a separate signature with separate obligations [Fong], [Definitional].
5. **Concrete downstream obligation:** promotion changes at least one validation, composition, derivation, projection, fixture, or code-generation obligation compared with the non-promoted baseline [Fong], [Lakatos], [Definitional].
6. **Interpretable composition:** accepted paths involving the relation remain meaningful when composed with neighboring accepted signatures [Lawvere], [Definitional].
7. **Named obligations:** it carries explicit obligations that can be checked, challenged, or projected, not just a nicer label [Fong], [Lakatos].
8. **Witnessed decision pressure:** a real use case, owner decision, validator failure, novice stall, implementation contradiction, or proof obligation shows that refusing the distinction leaves residue [Lakatos], [Non-vacuity].

### Placement And Authority Requirement

After promotion, the authority home is root-owned DomainSpec language, not implementation-local description. For R3, that means root `definitions/relationships/relationships.yml` and its human companion own the signatures; `projects/domainspec-v2/impl/spec/RELATIONSHIPS.md` is a projection or sync-checked view (`edge-signature-authority-decisions.md:57-83`, `:86-112`; `domainspec-v2-CONSTITUTION.md:44-53`) [Precedent].

Root ownership is therefore a placement requirement, not evidence that a candidate deserves promotion [Definitional].

### Useful Signals

These signals justify review but do not prove promotion by themselves:

- Recurrence across many specs or feature packs [Lawvere].
- Stable domain language that survives paraphrase better than `reference` or `pointer` [Wittgenstein].
- Human navigation value, when paired with machine obligations [Fong].
- Category-theory rationale about typed arrows, composition, and projection preservation [Lawvere].
- Useful inverse display or reverse navigation, if authority separates generated views from canonical signatures [Fong].

### Kill Criteria

Reject or defer promotion when any of these hold:

- No witness or real pressure exists [Lakatos], [Non-vacuity].
- The candidate has no stable contrast after examples/non-examples [Definitional].
- Promotion changes no validation, composition, derivation, projection, fixture, code, or owner decision [Fong], [Lakatos].
- It merely relabels an implementation pointer, browsing aid, notation convention, or markdown display [Wittgenstein], [Definitional].
- It duplicates an inverse/dual law ambiguously, such as treating `belongs-to` as the automatic inverse of `owns` without proving that the inverse name has the same or different obligations [Fong], [Non-vacuity].
- It is only broad recurrence. Repeated arrows are smoke, not fire [Lawvere].

## R3 Implications

### Entity Semantic Relation Family

Promote the Entity-to-Entity relation family as first-class R3 work, because current relationship authority cannot express ordinary library-domain structure: `Loan->Copy`, `Loan->Patron`, `Reservation->Title`, `Copy->Title`, and `Copy->Branch` were unrepresentable in the novice witness (`HANDOFF-novice-test-edge-findings.md:24-34`; `stall-dataset.md:41`) [Non-vacuity].

This does not promote every candidate verb. It promotes the family as a root-owned authority surface, then requires each relation name to survive endpoint, contrast, inverse, and obligation tests [Definitional].

Concrete use:

```text
Signature candidate: Entity --[owns]--> Entity
Instance candidate:  Library --[owns]--> Copy

Signature candidate: Entity --[belongs-to]--> Entity
Instance candidate:  Copy --[belongs-to]--> Title
Instance candidate:  Copy --[belongs-to]--> Branch
```

The second and third examples show why `belongs-to` should not be automatically collapsed into `owns^-1`: title membership and branch home-assignment may be distinct from ownership (`task.md:22-23`, `:34-35`) [Non-vacuity].

### owns / belongs-to Inverse Policy

Define `owns` first only if it carries a domain obligation such as lifecycle authority, containment, custody, write responsibility, or ownership-bound validation. If a reverse navigation is needed, generate `owned-by`, not `belongs-to`, unless `belongs-to` is separately witnessed and defined.

Recommended policy:

```text
Canonical: Entity --[owns]--> Entity
Generated inverse: Entity --[owned-by]--> Entity
Distinct candidate: Entity --[belongs-to]--> Entity
```

`belongs-to` may survive as membership, catalog classification, or home-assignment. It should not enter authority as an unexamined inverse label.

### depends-on

Kill `depends-on` for current R3 promotion. The decision record names it as a possible Entity-to-Entity verb, but the current evidence does not show a concrete R3 witness where `depends-on` changes reject/allow behavior compared with a generic reference or field-level dependency [Non-vacuity], [Definitional].

Next acceptable path: name the dependency kind, endpoint admissibility, cycle or ordering behavior if any, and at least one fixture where validation differs.

### Saga Signatures

Saga remains conditional. Current relationship authority has `orchestrates` as `Workflow -> Operation[]` only (`projects/domainspec-v2/impl/spec/RELATIONSHIPS.md:22`, `:138-144`), while the novice witness found Saga orphaned (`HANDOFF-novice-test-edge-findings.md:36-44`; `stall-dataset.md:42`) [Non-vacuity]. Saga definitions and DCB work create real pressure: cross-feature scope, participants, compensation, cross-context activation, temporal safety, and rollback obligations (`meta-types.md:410-445`; `PROOF-OBLIGATIONS.md:11-36`, `:38-49`).

Promote Saga signatures only if those obligations remain distinct from Workflow plus `scope: cross-feature`.

Concrete decision fork:

```text
Option A: Saga --[orchestrates]--> Operation[]
Requires: cross-feature scope, participant ownership, compensation/residue obligations.

Option B: Workflow --[orchestrates]--> Operation[]
With: scope = intra-feature | cross-feature
Result: Saga collapses into Workflow metadata/specialization.
```

### produces / emits Endpoint Split

Keep the split because endpoints create different admissibility:

```text
Operation --[produces]--> Event
Entity --[emits]--> Event
```

Current evidence supports this as a real correction, not vocabulary polish. `RELATIONSHIPS.md` says `produces` is `Operation -> Event` and `emits` is `Entity -> Event`, while the Operation card lists `emits` as Operation-sourced and omits `produces` (`RELATIONSHIPS.md:13-27`, `:66-73`, `:182-189`; `operation.schema.yml:21-23`; `HANDOFF-novice-test-edge-findings.md:46-59`) [Non-vacuity], [Fong].

R3 should reject `Operation --[emits]--> Event` and require `Operation --[produces]--> Event`.

### Source --[verb]--> Target

Keep this as notation only. It is useful for displaying a root-owned signature, but `Source --[verb]--> Target` is not itself authority and is not a promotion criterion [Fong], [Definitional].

## Human / Machine Notation

Use two levels: signature for authority, instance for concrete concepts.

```text
Signature: Rule --[enforces]--> Operation
Instance:  MaxAmountRule --[enforces]--> ProcessPayment
```

For Entity semantics:

```text
Canonical: Entity --[owns]--> Entity
Generated inverse: Entity --[owned-by]--> Entity
Distinct candidate: Entity --[belongs-to]--> Entity
```

Do not automatically render `belongs-to` as the inverse of `owns`. If the only need is reverse navigation, generate `owned-by`. If `belongs-to` means membership, title classification, branch home-assignment, or another domain relation, it needs its own examples, non-examples, endpoint law, and validation/composition consequence [Non-vacuity], [Definitional].

The human notation can be markdown-friendly and diagram-friendly. The machine authority should be structured, for example:

```yaml
id: enforces
source_type: Rule
target_type: Operation
direction: canonical
multiplicity: many_to_many
inverse_or_dual: none
validation_obligation:
  - reject_non_rule_source
  - reject_non_operation_target
composition_behavior:
  - operation_execution_is_gated_by_rule
projection:
  markdown: "Rule --[enforces]--> Operation"
```

## Plain-Language Category-Theory Answer

Repeated morphisms are evidence, not proof. A category needs objects, morphisms, identities, composition, closure, and associativity. A broad family of arrows is not automatically a category, and it is not automatically first-class DomainSpec authority [Lawvere].

For R3, the precise wording should be:

> DomainSpec is defining a typed composable graph fragment.

Use "category" only as rationale unless DomainSpec formalizes the full category laws: object set, morphism set, identity arrows, legal composition, closure, and associativity. Until then, category-theory language helps discover and explain laws, but validators should consume finite root-owned signatures [Lawvere], [Fong], [Precedent], [Definitional].

## Next Decisions

1. Decide Saga: first-class `Saga --[orchestrates]--> Operation[]` with distinct cross-feature/compensation obligations, or fold Saga into Workflow plus cross-feature metadata.
2. Define `owns` and `belongs-to` with examples, non-examples, endpoint rules, inverse/generated-view policy, and validation consequences.
3. Kill or defer `depends-on` until a witness names dependency kind and different reject/allow behavior.
4. Implement root `definitions/relationships/relationships.yml` with endpoint signatures, admissibility, inverse/dual policy, examples/non-examples, and projection rules.
5. Treat `projects/domainspec-v2/impl/spec/RELATIONSHIPS.md` as projection/view only, generated or sync-checked from root authority.
