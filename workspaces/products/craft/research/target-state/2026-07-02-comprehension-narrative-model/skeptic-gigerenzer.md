---
node_type: research
is_session: false
status: skeptic-review
created: 2026-07-02
authored_by: skeptic (Gigerenzer lens — ecological rationality / novice witness / completeness under real conditions)
dispatch: 2026-07-02-spec-comprehension-model
role: SKEPTIC-A (tensioned against SKEPTIC-B / Feyerabend — cut-further)
attacks: ./candidate-model.md
reads:
  - ../../impl/spec/TAXONOMY.md
  - ../../impl/spec/RELATIONSHIPS.md
  - ../../impl/spec/__fixtures__/mt/*.md            # all 28 ok/bad fixtures read 2026-07-02
  - ../../impl/spec/meta-types/**/*.schema.yml       # 7 schemas read 2026-07-02
claim_discipline: claim ≤ proof — [DISK] = verified on disk 2026-07-02; [HYP] = argued, not measured.
---

# Skeptic (Gigerenzer) — The reduction loses completeness at the connective/lifecycle cliff

## 1. Verdict

**THE REDUCTION LOSES COMPLETENESS.** M2's example-first comprehension unit is clean for the
behavioral core but **collapses for 5 of 14 backend types — every connective type, the lifecycle
type, and Enum** — and two of those (Event, State Machine) sit inside the candidate's own CORE-6;
do not adopt until a novice actually authors a spec that forces Enum / Interface / Mapping / State
Machine and the hidden-tier is shown *not* to mis-fire at that exact moment.

## 2. Minimal-pair coverage audit — the 14 backend types [DISK]

Bar (from the Money exemplar): a **genuine discriminating pair** = the `-bad.md` negative flips to a
**named nearest-neighbour sibling** on **one clean axis**, AND the negative's discriminating value
*would itself validate as that sibling's positive* (a real crossing), not merely a missing attribute.

| # | Type | Category | Discriminating pair? | Evidence (file → what the negative actually is) |
|---|------|----------|----------------------|--------------------------------------------------|
| 1 | Entity | structural | **YES — crossed** | `entity-bad.md` Money(no id+Equality) = `value-object-ok.md` Money(PASS). Same concept both ways. Axis: identity vs equality. |
| 2 | Value Object | structural | **YES — crossed** | `value-object-bad.md` Account(id) validates as `entity-ok` shape. Reverse leg of Entity crossing. |
| 3 | **Enum** | structural | **NO — malformed** | `enum-bad.md` Status{code,label} is a field-table with *no `Value` column*. Schema `distinguisher: vs Entity`, but Status has no Identity=yes and no Equality → it is **not a valid Entity either**. Negative validates as **nothing**. No backend "Common Confusion" row even names Enum. |
| 4 | Operation | behavioral | **YES — crossed** | `operation-bad.md` GetPaymentStatus(state_change=no) = `query-ok.md` GetPaymentStatus(PASS). Same concept crossed. Axis: state_change. |
| 5 | Query | behavioral | **YES — crossed** | `query-bad.md` ChargeCard(state_change=yes) validates as `operation-ok` shape. Reverse leg. |
| 6 | Calculation | behavioral | **YES — clean flip** | `calculation-bad.md` IsEligible(formal_return_type=boolean) validates as `rule-ok` (boolean). Names sibling Rule; negative IS a valid Rule. |
| 7 | Rule | behavioral | **YES — crossed** | `rule-bad.md` RetryRule(strategy) = `policy-ok.md` RetryPolicy(strategy). Same "Retry" concept crossed. |
| 8 | Policy | behavioral | **YES — crossed** | `policy-bad.md` MaxAmountPolicy(boolean) = `rule-ok.md` MaxAmountRule(boolean). Same "MaxAmount" concept crossed. |
| 9 | Workflow | behavioral | **YES — crossed** | `workflow-bad.md` WireTransfer(cross-feature) = `saga-ok.md` WireTransferSaga(cross-feature). Same concept crossed. Axis: scope. |
| 10 | Saga | behavioral | **YES — crossed** | `saga-bad.md` OrderFulfillment(intra-feature) = `workflow-ok.md` OrderFulfillment(intra). Same concept crossed. |
| 11 | **Interface** | connective | **NO — malformed** | `interface-bad.md` PaymentThing = *missing `interface_kind`*. Schema `distinguisher: vs Mapping`, but PaymentThing also has no `direction` → **not a valid Mapping**. Pure missing-attribute. |
| 12 | **Event** | connective | **NO — intent-flip only** | `event-bad.md` CompletePayment(temporal=present) header says "→ Operation"; schema `distinguisher: vs Operation`. But Operation's criterion is state_change=yes, which CompletePayment **does not declare** → it would **not validate as `operation-ok`**. Names a sibling it can't become. |
| 13 | **Mapping** | connective | **NO — malformed** | `mapping-bad.md` ShapeShift = *missing `direction`*. Schema `distinguisher: vs Interface`, but ShapeShift has no `interface_kind` → not a valid Interface. Pure missing-attribute. |
| 14 | **State Machine** | lifecycle | **NO — intent-flip only** | `state-machine-bad.md` PaymentKind(has_transitions=no) header says "→ flat Enum"; schema `distinguisher: vs Enum`. But Enum's criterion needs a `Value` table; PaymentKind is an Attribute/Value table → would **not validate as `enum-ok`**. Names a sibling it can't become. |

**Headline: 9 of 14 backend types have a genuine discriminating pair; 5 of 14 fail.**
The 5 failures are **Enum, Interface, Mapping** (malformed-only negatives) and **Event, State Machine**
(intent-flip-only: the negative names a sibling it would not validate as). [DISK]

**The hole clusters by category, and it is NOT where the candidate looked:**
- Structural 2/3, **Behavioral 7/7**, **Connective 0/3**, **Lifecycle 0/1**.
- The candidate's own R2 guessed the risk was "behavioral/lifecycle" (Workflow, Saga, State Machine).
  **Behavioral is in fact the strongest category (7/7 crossed).** The real cliff is **connective +
  lifecycle + Enum** — a mis-diagnosis in the candidate that my audit corrects with file evidence.

## 3. Per-move completeness critique

### M2 — example-first comprehension unit: **does not generalize** [DISK]
M2 is the load-bearing move and it is the one that breaks. It says surface "the existing crossed
fixtures" as the author's entry point. That entry point **exists for 9 types and is absent or fake for
5**. Worse for the candidate: **2 of its own CORE-6 (Event, State Machine) are in the failing 5.** At the
exact concepts M1 tells the novice to *internalize first*, the on-disk asset M2 leans on is an
intent-flip that the validator would not accept as the named sibling. And **Enum — a structural type,
the very category lens-example called "the strongest form of the device" — has no pair at all.** The
"clean for structural types" claim is [DISK]-false for 1 of 3 structural types.

### M3 — projected, not authored, machine forms: **projection is real, but inherits M2's hole** [DISK]
Every schema **does** carry a `distinguisher: {vs, rule}` — so "project, don't author" is disk-true even
for the failing types. But projecting `distinguisher: vs Mapping` for Interface renders comprehension
*theater*: the projected prose asserts a contrast the **only on-disk example does not demonstrate** (the
negative is "you forgot interface_kind," not "this is really a Mapping"). M3 honestly says it fires
"only for discriminable types" — which means for 5 backend types M3 supplies **nothing**, M2 supplies
**nothing**, and the author meeting Interface / Mapping / Enum / Event / State Machine gets neither a
real pair nor a pair-backed discriminator. Two moves, same five holes.

### M1 — tiering "completeness in the type system, comprehensibility in learning order": **a real deferral, argued as a separation** [HYP, grounded]
The separation is partly a dodge. Authoring a *real* spec still forces a pick from all 25. Concrete
[DISK] worked case: a novice modelling `PaymentMethod` must choose among **Enum** (M1: SUPPORTING,
hidden), **State Machine** (M1: CORE), **State Indicator** (M1: GENERIC, "never learn"), and **Value
Object** (M1: CORE). The decision spans three tiers; hiding 19 types does not remove it — it **defers
first contact with Enum to mid-spec**, the worst moment to stop and "learn on demand," and the Enum
asset waiting there is the malformed-only fixture (#3 above). That is the novice cliff, on disk.
The per-domain author-declarable lens compounds it: **who declares core-vs-generic?** A novice cannot
rank subdomains before understanding the 25 — declaring the lens presupposes the expertise distillation
was meant to supply. Chicken-and-egg (R1, sharpened).

### M1 shadows — collapsing 11 UI types to "a one-line dictionary": **loses edge-participation completeness** [DISK]
`RELATIONSHIPS.md` uses the "shadow" UI types as **first-class edge endpoints**, with signatures their
backend counterparts do **not** share:
- **Guard** is `source_of` `protects`(→Page) and `mirrors`(→Rule). **Rule** is `source_of` `enforces`
  only (`rule.schema.yml` edge_participation). Guard ≠ Rule at the graph level.
- **View Model**: `shapes`(Adapter→VM), `displays`(Component→VM), `derives`(VM→Entity).
- **Binding**: `fetches`(→Query), `mutates`(→Operation). **Adapter**: `shapes`(→VM). **State Indicator**:
  `reflects`(→State Machine).
"Guard = Rule, client-side" as a dictionary line is fine for *learning the word* but **false as a
completeness claim**: a UI-carrying spec that draws its knowledge graph needs Guard/Binding/Adapter/
View-Model/State-Indicator as distinct typed nodes to type `protects`/`mirrors`/`fetches`/`mutates`/
`shapes`/`reflects`/`derives`. The distillation lens's "shadows were never independent completeness" is
disk-refuted at the edge layer.

### M4 — narrative only for target-state, and the owner's actual goal [DISK + HYP]
The owner's goal is "understand the proposed abstractions of a **NEW spec**." Comprehending a specific
spec = reading **that spec's concept graph** (the per-spec `registry.md` node+edge map, `RELATIONSHIPS.md`
L396–420), not the generic 25-type catalog. Distilling the **catalog** (M1) teaches the *language once*;
it does not help you read *this feature's proposed abstractions*. M4 restricts narrative to the
target-state doc — so the everyday "here is what this feature's graph proposes" comprehension unit is
served by **neither M1 (generic) nor M4 (target-state only)**. The candidate under-serves the exact
artifact the owner named. [HYP — the per-spec map is the true comprehension unit; argued, not measured.]

## 4. What must be added / verified before adoption — the novice-witness test

Adopt nothing until this **ecological-rationality probe** runs (completeness under real authoring, the
novice who does *not* already hold the 25):

1. Recruit an author who has never seen `TAXONOMY.md`. Give them **only the distilled CORE-6, taught
   example-first per M2** (the crossed fixtures).
2. Hand them a small domain to spec whose correct model **necessarily forces the 5 failing types**:
   at least one Enum, one Interface, one Mapping, one State Machine, one Event (e.g. the
   payment-processing example with the answer-key removed).
3. Measure, per forced type: (a) did they pick the correct meta-type; (b) at the moment they hit
   Enum/Interface/Mapping, was the on-disk asset (the fixture) sufficient to resolve the choice or did
   they stall / mis-type; (c) did hiding 19 types cause a mis-type a flat-25 presentation would have
   prevented.
4. **Pre-registered failure condition (fix BEFORE running):** if ≥1 of {Enum, Interface, Mapping, State
   Machine, Event} is mis-typed **and** the author attributes the failure to the hidden tier or the
   missing/fake pair, the reduction loses completeness at the cliff → **do not adopt M1/M2 as written**;
   first author genuine crossed fixtures for the 5 failing types (make Interface↔Mapping and
   Event↔Operation and State-Machine↔Enum *real* crossings, not missing-attribute negatives).

Until that probe runs, the candidate rests on [HYP] "distillation improves comprehension" — which its own
R4 concedes is unmeasured — while the [DISK] evidence shows its comprehension asset is missing at 5 of 14
types.

## 5. Residue I concede to the cut-further side (Feyerabend)

For the **8 crossed types** (Entity, VO, Operation, Query, Rule, Policy, Workflow, Saga), M3's stack
(positive + discriminating negative + named axis + thin definition + 4 projected machine forms) is
**genuinely more ceremony than the lesson needs**. lens-example is right that for those types "the author
never needed the sentence" — the crossed fixture pair **plus a one-line axis label** is the whole lesson;
the thin definition and the projected machine lane are redundant there. So Feyerabend wins on the 8: cut
to pair + axis. **But my concession is bounded and exactly inverted for the failing 5** — Enum, Interface,
Mapping, Event, State Machine have no clean pair, so there the answer is *more* scaffolding (author a real
crossing), not less. Feyerabend's "cut further" is correct only where the pair is already clean, and
correct nowhere the completeness hole actually lives.
