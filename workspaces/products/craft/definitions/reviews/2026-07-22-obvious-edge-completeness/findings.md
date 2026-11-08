# DomainSpec v2 Obvious-Edge Completeness Review

Review: `2026-07-22-dsv2-obvious-edge-completeness-review`
Attack returns: A1 formal · A2 mechanics · A3 requirements
Revision evidence: verifier V1 · verifier V2

## Scope and non-authority notice

This review examines obvious relationship pressure in:

- `projects/domainspec-v2/definitions/relationships/relationships.yml`
- `projects/domainspec-v2/definitions/relationships/relationships.md`
- `projects/domainspec-v2/impl/spec/features/ui-profile-create-player/SPEC.md`
- `projects/domainspec-v2/impl/spec/features/financial-settlement/SPEC.md`
- `projects/domainspec-v2/impl/spec/features/ui-profile-create-player/generated/residue.json`
- `projects/domainspec-v2/impl/tools/lib/relationship-signatures.ts`
- `projects/domainspec-v2/impl/tools/minted-project/compiler.ts`
- the bounded UI Action/Binding development evidence and owner packet

This document is review evidence only. It is not DS-D8 authority and admits,
widens, renames, or deletes no relationship signature.

Both verifiers confirm the surviving active problem, its MAJOR severity, and
the unresolved repair choice. They require the active gap to remain limited to
the current scope/semantics and enforcement mismatch. Neither `creates` nor
widening is itself classified as active authority.

## Executive verdict

One **MAJOR ACTIVE-GAP** survives: the active `produces-for` authority is
cross-feature and foreign-entity-only, while both exercised feature graphs use
it for same-feature Operation-to-Entity edges.

The implementation is not merely missing a feature-scope check; its behavior
is inverted relative to the authority:

- the relationship validator checks labels and endpoint kinds without
  enforcing `feature_scope`;
- the minted-project compiler rejects every cross-feature endpoint before
  endpoint-kind admission;
- it then admits same-feature connections by active-profile membership and
  endpoint kinds.

The green tests therefore demonstrate validator lag and internally accepted
mismatch, not conformance to the declared authority.

The evidence does not adjudicate the durable repair:

1. A1 proposes a distinct same-feature
   `Operation --[creates]--> Entity` signature.
2. A3 proposes widening and neutralizing `produces-for` into a same/cross-feature
   generic Operation-to-Entity write relation.

Both remain **owner-decision candidates**. The supplied corpus proves
relationship pressure and an invalid current use, but not the D18 non-collapse
distinction between creation and generic writes. The immediate repair is to
fail the contradictory uses closed while the owner runs paired witnesses.

Action-to-Binding also remains **DEFERRED relationship pressure**. The evidence
proves that an Action needs some source-side relationship to its declared
Binding target; it does not establish `invokes` as the preferred or promotable
verb.

## Artifact findings

### Relationship authority — verdict: FIX

| ID | File and quoted evidence | Severity | Disposition | Proposed fix |
| --- | --- | --- | --- | --- |
| REL-01 | `projects/domainspec-v2/definitions/relationships/relationships.yml:52-65` declares `produces-for` as `Operation -> Entity`, `feature_scope: ["cross-feature"]`, with semantics “writes or projects data into an entity owned by another feature.” `relationships.md:48-51` summarizes the target as a “foreign entity.” | MAJOR | ACTIVE-GAP | Fail same-feature `produces-for` closed. Route distinct `creates` versus widened/neutral write semantics to a bounded DS-D8 owner decision. Do not silently broaden the active signature. Confirmed by A1-F1, A2-F1, A3-F1, V1, and V2. |
| REL-02 | `projects/domainspec-v2/impl/tools/lib/relationship-signatures.ts:146-189` reads graph triples and validates active labels/endpoints, but does not enforce declared feature scope. | MAJOR | ACTIVE-GAP | Add scope-aware validation with same-feature and cross-feature mutants after the owner selects the intended semantics. Confirmed by A2-F1, V1, and V2. |
| REL-03 | `projects/domainspec-v2/impl/tools/minted-project/compiler.ts:430-439` raises `CROSS_FEATURE_UNSUPPORTED` whenever source and target feature IDs differ; `:441-455` then admits same-feature connections by relationship ID and endpoint kinds. | MAJOR | ACTIVE-GAP | Reconcile compiler admission with the selected authority contract. The present compiler implements the inverse of cross-feature-only `produces-for`. Confirmed by V1 and V2. |
| REL-04 | `relationships.yml:61` gives `GenerateSettlement --[produces-for]--> Player` only as authority prose/example. No exercised real cross-feature `produces-for` graph was found in the bounded corpus. | MAJOR | DEFER | Require one exercised cross-feature write/projection witness plus scope mutants before either repair is accepted. V1 and V2 correction. |
| REL-05 | `projects/domainspec-v2/impl/tools/lib/relationship-signatures.ts:415-441` rejects generated/noncanonical labels; `:444-471` rejects undeclared source or target concepts; `:474-499` normalizes endpoint types, matches them against the active signature, and emits `unconstructible-edge` on mismatch. | INFO | REJECT | Drop the stale claim that endpoint validation is absent. Literal validator evidence proves label, concept-presence, and endpoint-kind enforcement. The surviving defect is feature-scope omission plus minted-compiler inversion. A2-F3; V1; V2. |

### UI-profile create-player — verdict: FIX

| ID | File and quoted evidence | Severity | Disposition | Proposed fix |
| --- | --- | --- | --- | --- |
| UIP-01 | `projects/domainspec-v2/impl/spec/features/ui-profile-create-player/SPEC.md:40-43` authors same-feature `CreatePlayer --produces-for--> Player`; `:63-73` gives `Player` stable identity and `CreatePlayer` `state_change: yes`. | MAJOR | ACTIVE-GAP | Reject or temporarily remove the edge until the owner authorizes an accurately scoped relation. Retain this as a same-feature creation-positive witness. A1-F1; A2-F1; V1; V2. |
| UIP-02 | `projects/domainspec-v2/impl/spec/features/ui-profile-create-player/SPEC.md:170-179` gives `CreatePlayerAction` `target_kind: Binding`, intent, trigger, and outcomes. `projects/domainspec-v2/impl/spec/features/ui-profile-create-player/generated/residue.json:23-29` records omitted `Action -> Binding` because no active DS-D8 signature exists. The exact owner packet is `projects/domainspec-v2/development/ui-profile-implementation/authority-packet/packet.json:114-118`; it records the pressure, a finite candidate, and “do not admit without DS-D8 owner approval.” The unresolved owner question is at `packet.json:183-190`. | MAJOR | DEFER | Record only **Action -> Binding relationship pressure**. The packet’s candidate verb is input to owner review, not this review’s preferred or promoted name. A future owner decision must determine verb, semantics, endpoint constraints, mutants, graph consequences, and traceability. A1-F2; A2-F2; A3-F6; V1; V2. |
| UIP-03 | `generated/residue.json:32-37` preserves `Hook -> Binding`; other UI pressure is likewise retained as owner residue. | LOW | DEFER | Preserve residue. Do not infer Hook→Binding or Component→Form from co-occurrence or implementation convenience. A1-F2; A2-F4. |

### Financial settlement — verdict: FIX

| ID | File and quoted evidence | Severity | Disposition | Proposed fix |
| --- | --- | --- | --- | --- |
| FIN-01 | `projects/domainspec-v2/impl/spec/features/financial-settlement/SPEC.md:19-35` registers `SettlementTransaction` and `GenerateSettlement` in one feature, then authors `GenerateSettlement --produces-for--> SettlementTransaction`; `:39-48` calls the entity a persisted transaction created by settlement generation; `:72-78` says the operation writes transactions and changes state. | MAJOR | ACTIVE-GAP | Fail the same-feature edge closed pending owner adjudication. Retain it as a second creation-positive witness. A3-F1; V1; V2. |
| FIN-02 | `SPEC.md:35-37` also authors `GenerateSettlement --queries--> SettlementTransaction`. | INFO | NO-GAP IN BOUNDED ROLE | Preserve only as a read comparator. It is not a same-feature non-creation write witness and cannot adjudicate `creates` versus widening. V1; V2. |

## Candidate matrix

### Finite coverage ledger

This ledger is exhaustive over the current finite authority and declared
residue reviewed here. It inventories all 30 active signatures in the three
authority families, plus generated/deferred relationship entries and every
finite DS-D1 endpoint family named by those signatures. “No witness” means no
exercised witness was found in the bounded current corpus; it is not a claim
against future domains.

| Authority family | Authority-present signatures | Exercised in bounded corpus | Residue / deferred transformation | No exercised witness in bounded corpus | Family disposition |
| --- | --- | --- | --- | --- | --- |
| Backend — 16 active | `performs`, `produces`, `produces-for`, `triggers-cross`, `enforces`, `calculates`, `transitions`, `exposes`, `orchestrates`, `applies`, `maps`, `contains`, `queries`, `emits`, `owns`, `belongs-to` (`projects/domainspec-v2/definitions/relationships/relationships.md:44-63`; registry entries at `relationships.yml:20-274`). | `performs`, `produces`, `produces-for`, `enforces`, `calculates`, `transitions`, `exposes`, `maps`, `queries`. `produces-for` is exercised only through the invalid same-feature cases under review. | `event-payload-publisher-composite` remains deferred at `relationships.yml:511-523` and `definitions/reviews/2026-07-12-deferred-relationship-candidates.md:28,36`; `operation-returns-value-object` remains a property-level deferred candidate at `relationships.yml:517-519`; `depends-on` remains deferred at `:513-515`. | `triggers-cross`, `orchestrates`, `applies`, `contains`, `emits`, `owns`, `belongs-to`. No exercised real cross-feature `produces-for` witness was found. | **FIX** only for `produces-for` scope/semantics and enforcement. Preserve all other no-witness/deferred states without a completeness claim. |
| UI — 8 active | `renders`, `wraps`, `composes`, `consumes`, `submits`, `shapes`, `protects`, `displays` (`relationships.md:65-76`; `relationships.yml:276-402`). | `renders`, `wraps`, `consumes`, `submits`, `protects`, `displays`. | `shapes` is authority-present but transformed out of the graph after Adapter normalization: `generated/residue.json:7-13`. Its owner alternatives—retype source, retain Adapter, or defer—remain unresolved at `authority-packet/packet.json:95-102,183-188`. | `composes`; no canonical exercised `shapes` edge. | **KEEP** exercised edges; **DEFER** `shapes`/Adapter adjudication; record `composes` as no-witness. |
| Cross-layer — 6 active | `fetches`, `mutates`, `reflects`, `derives`, `contracts`, `mirrors` (`relationships.md:78-87`; `relationships.yml:404-498`). | `fetches`, `mutates`, `derives`, `contracts`, `mirrors`. | `reflects` is omitted owner residue because the development source identity does not currently supply its canonical endpoint; preserve the owner alternatives rather than inventing a State Indicator identity. | No canonical exercised `reflects` edge. | **KEEP** exercised edges; **DEFER** `reflects`. |
| Generated/non-authored view | `owned-by`, generated from `owns` (`relationships.yml:500-509`). | None required as an authored edge. | Generated navigation only. | Not applicable. | **NO-GAP**; the validator correctly rejects it as a canonical authored label at `relationship-signatures.ts:415-426`. |
| Declared deferred candidates | `depends-on`, `operation-returns-value-object`, `event-payload-publisher-composite` (`relationships.yml:511-523`). | None. | All remain deferred. | All lack the required distinct witness. | **DEFER**. |
| Deprecated | `enforces-cross` (`relationships.yml:525-530`). | Not applicable. | Replaced by `enforces` plus scope metadata. | Not applicable. | **REJECT** resurrection without new non-collapse evidence. |

### Finite DS-D1 endpoint-family coverage

| Endpoint family | Finite kinds appearing in current authority | Bounded disposition |
| --- | --- | --- |
| Backend/domain | `Entity`, `Operation`, `Event`, `Rule`, `Calculation`, `State Machine`, `Interface`, `Query`, `Workflow`, `Policy`, `Mapping`, `Value Object` | Authority-present. The bounded features exercise Entity, Operation, Event, Rule, Calculation, State Machine, Interface, Query, Mapping. Workflow, Policy, and Value Object relationship participation have no exercised witness here. |
| UI | `Page`, `Layout`, `Component`, `Hook`, `Form`, `Action`, `Adapter`, `View Model`, `Guard` | Page, Layout, Component, Hook, Form, Action, View Model, and Guard are exercised through current UI edges. Adapter is a deferred/merge candidate normalized to Mapping, not a settled independent endpoint (`authority-packet/packet.json:56-64`). |
| Cross-layer bridge | `Binding`, `State Indicator`, plus backend/UI kinds already listed | Binding is exercised through `fetches` and `mutates`. State Indicator remains unresolved residue for `reflects`; no identity is invented by this review. |
| Action-source pressure | `Action -> Binding` | Both endpoint kinds are finite in the development evidence, but no active source-side signature exists. Preserve verb-neutral **DEFER** at `authority-packet/packet.json:114-118,183-190`. |
| Component/Form pressure | `Component -> Form` | Finite endpoints, but omission remains preferred pending owner evidence; **REJECT CURRENT CLAIM / DEFER reopening**. |
| Event payload/publisher split | `Operation -> Event` through `produces`; `Entity -> Event` through `emits`; payload/publisher data outside a proven composite edge | **DEFER composite.** Existing producer, entity-source/publisher, and payload roles have not been shown to require one non-collapsing relationship. |
| Transformed Adapter/shapes pressure | Authority says `Adapter --shapes--> View Model`; graph normalizes Adapter to Mapping and omits the edge | **DEFER.** Do not retype to Mapping, activate Adapter, or retire `shapes` without the existing DS-D1/DS-D8 owner decisions. |

| Candidate pressure | Bounded evidence | Classification | Review judgment |
| --- | --- | --- | --- |
| `Operation --creates--> Entity` | Two same-feature identity-bearing creation cases currently misuse cross-feature `produces-for`. | OWNER-DECISION CANDIDATE | A1’s proposal is plausible, but distinct D18 consequences are unproven. It is not itself ACTIVE-GAP authority. |
| Widen/neutralize `produces-for` | The same cases could be modeled as generic writes if lifecycle mode remains in operation postconditions. | OWNER-DECISION CANDIDATE | A3’s proposal is plausible, but it changes current cross-feature/foreign-only semantics and lacks exercised cross-feature proof. |
| Instantiates | No concrete authored edge, rejection, or downstream consumer in the bounded corpus. | NO WITNESSED PRESSURE | This is not a repository-wide NO-GAP claim. |
| Action-source relationship | Action names Binding as target; generated output records the omitted connection. | DEFER | Relationship pressure is real; verb and signature remain unadjudicated. |
| Updates | No exercised same-feature non-creation write comparator was supplied. | NO WITNESSED PRESSURE | Do not infer completeness from generic mutation prose. An actual write comparator is required for D18 adjudication. |
| Deletes | No concrete delete graph or validator rejection was supplied. | NO WITNESSED PRESSURE | No broader completeness claim. |
| Returns | Attacker evidence suggests it may be representable as a signature/card property, but no finite graph obligation was supplied. | DEFER | Require a concrete consumer and validator consequence. A3-F4. |
| Event payload/publisher split | Active `produces` and `emits` separate Operation producer from Entity event-source/publisher roles; payload typing remains metadata. The deferred review has not shown the composite changes a D18 consequence (`projects/domainspec-v2/definitions/reviews/2026-07-12-deferred-relationship-candidates.md:28,36`). | DEFER | Require a concrete event where decomposed payload metadata plus `produces`/`emits` fails a named validation, generation, composition, or implementation obligation. |
| Adapter / `shapes` transformation | Active authority contains `Adapter --shapes--> View Model`, but the UI graph normalizes Adapter to Mapping and records no `shapes` edge (`generated/residue.json:7-13`; `authority-packet/packet.json:56-64,95-102`). | DEFER | Preserve the three owner alternatives: retype source, activate independent Adapter, or defer/retire `shapes`. This review selects none. |
| Depends-on | No finite endpoint pair, direction, or non-collapse witness was supplied. | DEFER | Too generic for admission. A3-F5. |
| Hook→Binding | Explicit residue only. | DEFER | Current omission is intentional and owner-routed. |
| Component→Form | No finite candidate or distinct consequence survives. | REJECT CURRENT CLAIM | Do not infer containment from UI co-occurrence. |
| Other UI residue | State Indicator reflection and other pressures remain explicitly recorded. | DEFER | Recorded omission is not by itself an active representability gap. |

## Preserved disagreement: creates versus widening

A1 argues that creation changes enough of the relationship contract to justify
a distinct signature: same-feature scope, identity creation, persistence, and
creation-specific lifecycle meaning.

A3 argues that creation, update, and generic Operation-to-Entity writes may
share one structural path, with lifecycle mode remaining in operation
postconditions rather than relationship vocabulary.

The current corpus proves neither position under `domainspec-v2-D18`. In
particular:

- `GenerateSettlement --queries--> SettlementTransaction` is only a read
  comparator.
- No same-feature non-creation write comparator is exercised.
- No real cross-feature `produces-for` graph is exercised.
- No paired red/green result demonstrates different reject/allow, derivation,
  projection, composition-path, owner-route, or generated-artifact consequences.

The review therefore refuses consensus. Both repair shapes remain candidates
until the owner receives the missing witnesses.

## Refuted or dropped claims

- **Dropped: CRITICAL severity.** V1 and V2 confirm MAJOR. The mismatch is
  authority-significant but no corruption, system breakage, or global law
  collapse is demonstrated.
- **Rejected: endpoint validation is absent.** Label and endpoint-kind
  validation exists. The defect is feature-scope omission plus compiler
  inversion. A2-F3; V1; V2.
- **Rejected: green tests prove conformance.** They prove the current validators
  accept the lagging implementation.
- **Dropped: `invokes` is the established Action→Binding verb.** The evidence
  establishes relationship pressure only.
- **Rejected: `creates` is already the active gap.** The active gap is the
  current scope/semantics and enforcement contradiction; `creates` is one
  owner-decision candidate repair.
- **Rejected: widening is already the correct repair.** It remains a candidate
  because it would alter the active signature’s foreign/cross-feature meaning.
- **Dropped: the authority example is an exercised cross-feature witness.**
  `relationships.yml:61` is an example, not a compiled feature graph.
- **Dropped: `GenerateSettlement --queries--> SettlementTransaction` is a
  non-creation write comparator.** It is read-only relationship evidence.
- **Demoted: broad NO-GAP findings for instantiates, updates, deletes, and
  returns.** The bounded corpus supports only “no witnessed pressure” or DEFER,
  not completeness.
- **Rejected: Hook→Binding or Component→Form can be inferred.** Current residue
  and non-collapse evidence do not authorize them.
- **Dropped: unwitnessed active signatures automatically indicate gaps.**
  Corpus coverage and authority validity are different questions.
- **Rejected: Event payload and publisher pressure requires one composite
  edge.** The finite authority already separates Operation production through
  `produces`, Entity event-source/publisher semantics through `emits`, and
  payload typing through metadata. The composite remains deferred until
  decomposition is proven insufficient.
- **Rejected: Adapter normalization resolves `shapes`.** It only transforms the
  development graph by replacing Adapter identity with Mapping and omitting the
  edge. The DS-D1 Adapter identity and DS-D8 `shapes` disposition remain owner
  decisions.
- **Rejected: active-authority presence equals exercised coverage.** The ledger
  distinguishes registered signatures from exercised witnesses,
  residue/deferred transformations, and no-witness states.
- **Rejected: this review proves completeness against future domains.** Its
  exhaustive claim is only over the current finite authority, the reviewed
  feature corpus, and declared residue.

## Validation

A2 reports exactly:

- `npm run validate:rels` — **PASS**, 5 specs / 34 edges / 30 signatures.
- `npm run tools:test` — **PASS**, 147/147.

Those results are preserved, but their interpretation is corrected. They show
that current tests do not detect the contradiction:

- relationship validation accepts endpoint-compatible same-feature
  `produces-for`;
- minted compilation forbids all cross-feature endpoints;
- declared authority says `produces-for` is cross-feature-only.

The review independently verified the cited authority, two feature graphs,
residue, validator, and compiler passages. It mutated no authority.

Parent revalidation after integrating this review records:

- `npm run validate:rels` — **PASS**, 5 specs / 34 edges / 30 signatures.
- `npm run audit:retired-orchestration` — **FAIL**, with the review transcript
  accepted as a classified historical negative control and one remaining
  `unused-exception` in the unrelated backend type-test-engine
  `EXECUTION-DISPATCH.json` allowlist entry.
- `npm run tools:test` — **145/147 PASS**; both failures are projections of that
  same unrelated `unused-exception` baseline condition. No failure is caused by
  the review artifacts after their reference classification.

The unrelated backend type-test-engine owner surface was not changed as part of
this bounded definitions review.

### Coverage conclusions by attacker lens

| Attacker lens | Bounded coverage conclusion |
| --- | --- |
| A1 formal | The finite registry/residue sweep establishes one formal contradiction: current same-feature `produces-for` uses do not inhabit the signature’s declared cross-feature/foreign-entity semantics. It also establishes Action→Binding pressure, but neither its verb nor a distinct `creates` relation passes D18 from the supplied witnesses. All other finite candidates are disposed as authority-present, exercised, deferred/residue, rejected-current, or no-witness. |
| A2 mechanics | All 30 active signatures are inventoried across backend, UI, and cross-layer families. Literal validator evidence proves label/concept/endpoint-kind checks at `relationship-signatures.ts:415-499`; literal compiler evidence proves unconditional cross-feature rejection followed by same-feature kind admission at `minted-project/compiler.ts:430-455`. The exact green results—5 specs/34 edges/30 signatures and 147/147 tests—therefore demonstrate validator lag, not scope conformance. |
| A3 requirements | The bounded corpus exercises creation semantics twice but supplies neither an actual same-feature non-creation write comparator nor an exercised cross-feature `produces-for` projection. Therefore requirements evidence proves the need to repair the current mismatch, but cannot choose between `creates` and widening. Instantiates, updates, and deletes remain “no witnessed pressure”; returns, depends-on, the Event composite, Action-source, `reflects`, and transformed `shapes` remain deferred. |

## Dispatch closeout

- Final approver: Vlachopulos — **ACCEPT** after one declared feedback loop.
- Exit reason: `resolved`.
- Task agents: 7 total — 3 attackers, 1 synthesis writer, 2 verifiers, and
  1 auditor.
- Authority mutation: none.
- Result: one confirmed active mismatch, two owner-decision repair candidates,
  and all other reviewed pressure classified without promotion.

## Ordered change requests

1. **Fail the current contradiction closed.** Add red fixtures proving
   same-feature use of the current cross-feature-only `produces-for` is
   rejected, including:
   - `CreatePlayer -> Player`;
   - `GenerateSettlement -> SettlementTransaction`.
2. **Correct validator/compiler alignment.** Enforce declared feature scope in
   relationship validation and remove the minted compiler’s unconditional
   cross-feature rejection in favor of the selected signature’s scope contract.
3. **Run one bounded DS-D8 owner decision for both candidates.** Supply:
   - the two existing same-feature creation-positive witnesses;
   - one actual same-feature non-creation Operation-to-Entity write witness;
   - one exercised cross-feature write/projection witness;
   - same/cross scope mutants;
   - endpoint mutants;
   - a D18/D20–D25 consequence comparison;
   - generated graph and residue deltas for each candidate.
4. **Promote only the adjudicated repair.**
   - If creation changes a tracked non-collapse consequence, consider a
     narrowly defined `creates` signature.
   - If it does not, consider widening/renaming the generic write signature and
     updating all cross-feature/foreign-only semantics consistently.
5. **Keep Action→Binding deferred and verb-neutral.** A future owner decision
   must choose the relationship name and prove distinct semantics before adding
   a signature, profile edge, mutants, regenerated graph, residue retirement,
   or traceability.
6. **Preserve remaining UI pressure as residue** until finite endpoints and
   non-collapse consequences exist.
7. **Add coverage without overstating completeness.** Track unwitnessed active
   signatures separately from this active mismatch.

## Coverage limits

This review is exhaustive over the current finite relationship authority
reviewed here:

- all 16 active backend signatures;
- all 8 active UI signatures;
- all 6 active cross-layer signatures;
- the generated `owned-by` view;
- the three declared deferred candidates;
- deprecated `enforces-cross`;
- the declared UI residue for Action→Binding, Hook→Binding, Component→Form,
  `reflects`, and transformed Adapter/`shapes`;
- every finite DS-D1 endpoint family named by those signatures and residue
  rows.

Within that boundary, every item is classified as authority-present,
exercised, active mismatch, generated-only, residue/deferred,
rejected-current, or no-witness.

This is not proof against future domains, undiscovered requirements, or
relationship pressure outside the reviewed corpus. In particular, no
exercised real cross-feature `produces-for` witness, actual same-feature
non-creation write comparator, canonical `reflects` edge, or canonical
Adapter/`shapes` edge was found. Those absences constrain the current owner
decision; they do not prove repository-wide nonexistence.
