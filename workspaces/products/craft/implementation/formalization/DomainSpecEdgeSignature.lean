/-
Copyright (c) 2026 Victor Boscaro. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Victor Boscaro

# DomainSpec edge-signature type-checker + adequacy instrument (extended)

A **decidable, executable** type-checker for a DomainSpec concept graph, extended past the
24/29 spec vocabulary toward the target class **"any code that models a domain."** Two
typed objects are separated, which is the whole point of this file:

* **residue** — edges that are *mis-typed between KNOWN meta-types* (a modeling error).
* **escapes** — edges the vocabulary *could not classify* (`opaque` node / `other` edge):
  the **escape hatch**. They degrade gracefully (accepted, never rejected) but are
  **counted**. The escape set is the adequacy meter: where it concentrates is exactly
  which meta-type the vocabulary is missing for the target domain class.

This makes "is the vocabulary enough to model any domain?" an *empirical, measurable*
question (run it on a corpus, watch `escapes` shrink / concentrate), not a proof — no
finite fixed vocabulary is provably complete for an open class.

## Layers in this file (honest typing)

* **SPEC core (24 meta-types, 29 edges)** — faithful transcription of the DomainSpec
  normative model (`Arcanum/definitions/`, DS-D1/D2/D7/D8 + DS-P1/P2/P3). The
  `spec*`/`dsD7_*`/`dsP2_*`/`dsP3_*` theorems are the fidelity proofs over this core.
* **EXTENSIONS (candidates, clearly marked NON-spec)** — `aggregate`, `boundedContext`
  (DDD concepts the spec lacks), the `associates` structural edge with `Cardinality`
  (entity↔entity multiplicity, the ER/UML gap), and the escape hatch (`opaque`/`other`).
  These are *candidate* additions to test against real domain models, not spec.

NOT a novelty claim — construction to serve the domainspec ecosystem.
-/

import Mathlib.Data.List.Basic

namespace DomainSpec
namespace EdgeSignature

/-! ## DS-D1 — meta-types (24 spec) + extensions -/

/-- DomainSpec meta-types: 13 backend + 11 UI (spec), plus extensions:
`aggregate`, `boundedContext` (DDD candidates) and `opaque` (escape hatch). -/
inductive MetaType
  -- 𝓜_B (13 backend, spec)
  | entity | valueObject | enumType | operation | query | calculation | rule
  | policy | workflow | «interface» | event | mapping | stateMachine
  -- 𝓜_U (11 UI, spec)
  | page | layout | component | viewModel | hook | form | action | guard
  | binding | adapter | stateIndicator
  -- EXTENSIONS (non-spec candidates)
  | aggregate          -- DDD consistency boundary (backend)
  | boundedContext     -- DDD context container (spans layers → neutral)
  | opaque             -- escape hatch: an unclassifiable node
  deriving DecidableEq, Repr

/-- Governance layers. `neutral` holds the cross-cutting / unclassifiable types. -/
inductive Layer | backend | ui | neutral
  deriving DecidableEq, Repr

/-- DS-D1 layer assignment, total over all meta-types (one arm each so equation lemmas
reduce cleanly under `decide`). Extensions: `aggregate` is backend; `boundedContext` and
`opaque` are `neutral` (not in the backend/UI partition). -/
def layer : MetaType → Layer
  | .entity => .backend
  | .valueObject => .backend
  | .enumType => .backend
  | .operation => .backend
  | .query => .backend
  | .calculation => .backend
  | .rule => .backend
  | .policy => .backend
  | .workflow => .backend
  | .«interface» => .backend
  | .event => .backend
  | .mapping => .backend
  | .stateMachine => .backend
  | .page => .ui
  | .layout => .ui
  | .component => .ui
  | .viewModel => .ui
  | .hook => .ui
  | .form => .ui
  | .action => .ui
  | .guard => .ui
  | .binding => .ui
  | .adapter => .ui
  | .stateIndicator => .ui
  | .aggregate => .backend
  | .boundedContext => .neutral
  | .opaque => .neutral

/-- `𝓜_B` — the 13 SPEC backend meta-types (extensions excluded for fidelity). -/
def mB : List MetaType :=
  [.entity, .valueObject, .enumType, .operation, .query, .calculation, .rule,
   .policy, .workflow, .«interface», .event, .mapping, .stateMachine]

/-- `𝓜_U` — the 11 SPEC UI meta-types. -/
def mU : List MetaType :=
  [.page, .layout, .component, .viewModel, .hook, .form, .action, .guard,
   .binding, .adapter, .stateIndicator]

/-- The extension meta-types (non-spec candidates + escape hatch). -/
def mExt : List MetaType := [.aggregate, .boundedContext, .opaque]

/-- Domain objects an `associates` edge may connect (entities / aggregates). -/
def domainObjects : List MetaType := [.entity, .aggregate]

/-! ## DS-D7 — edge families (29 spec) + extensions -/

/-- DomainSpec typed edges: 15 backend + 8 intra-UI + 6 cross-layer (spec), plus
`associates` (structural domain association) and `other` (escape hatch). -/
inductive Edge
  -- 𝓡_B (15 backend, spec)
  | performs | produces | producesFor | triggersCross | enforcesCross | enforces
  | calculates | transitions | exposes | orchestrates | applies | maps | contains
  | reads | emits
  -- 𝓡_U (8 intra-UI, spec)
  | renders | wraps | composes | consumes | submits | shapes | protects | displays
  -- 𝓡_X (6 cross-layer, spec, UI → backend)
  | fetches | mutates | reflects | derives | contracts | mirrors
  -- EXTENSIONS (non-spec)
  | associates         -- structural entity↔entity / aggregate association
  | other              -- escape hatch: an unclassifiable edge
  deriving DecidableEq, Repr

/-- Edge families of DS-D7, plus the `extension` bucket. -/
inductive EdgeFamily | backend | intraUI | crossLayer | extension
  deriving DecidableEq, Repr

/-- DS-D7 family assignment. -/
def family : Edge → EdgeFamily
  | .performs | .produces | .producesFor | .triggersCross | .enforcesCross | .enforces
  | .calculates | .transitions | .exposes | .orchestrates | .applies | .maps | .contains
  | .reads | .emits => .backend
  | .renders | .wraps | .composes | .consumes | .submits | .shapes | .protects
  | .displays => .intraUI
  | .fetches | .mutates | .reflects | .derives | .contracts | .mirrors => .crossLayer
  | .associates | .other => .extension

/-! ## DS-D8 — the signature operator σ -/

/-- An edge signature: allowed source meta-types × allowed target meta-types. -/
abbrev Sig := List MetaType × List MetaType

open MetaType in
/-- The DS-D8 signature operator σ. `other` has the empty signature (it never
type-checks via σ — it is accepted only through the escape hatch in `EdgeValid`). -/
def sig : Edge → Sig
  -- 𝓡_B
  | .performs      => ([entity],      [operation])
  | .produces      => ([operation],   [event])
  | .producesFor   => ([operation],   [entity])
  | .triggersCross => ([event],       [operation])
  | .enforcesCross => ([rule],        [operation])
  | .enforces      => ([rule],        [operation])
  | .calculates    => ([calculation], [operation])
  | .transitions   => ([event],       [stateMachine])
  | .exposes       => ([«interface»], [operation, query])
  | .orchestrates  => ([workflow],    [operation])
  | .applies       => ([policy],      [operation])
  | .maps          => ([mapping],     [entity, «interface»])
  | .contains      => ([entity],      [valueObject])
  | .reads         => ([query, operation], [entity])
  | .emits         => ([entity],      [event])
  -- 𝓡_U
  | .renders       => ([page],        [component])
  | .wraps         => ([layout],      [page])
  | .composes      => ([component],   [component])
  | .consumes      => ([component],   [hook])
  | .submits       => ([form],        [action])
  | .shapes        => ([adapter],     [viewModel])
  | .protects      => ([guard],       [page])
  | .displays      => ([component],   [viewModel])
  -- 𝓡_X (UI → backend)
  | .fetches       => ([binding],        [query])
  | .mutates       => ([binding],        [operation])
  | .reflects      => ([stateIndicator], [stateMachine])
  | .derives       => ([viewModel],      [entity])
  | .contracts     => ([form],           [«interface»])
  | .mirrors       => ([guard],          [rule])
  -- EXTENSIONS
  | .associates    => ([entity, aggregate], [entity, aggregate])
  | .other         => ([], [])

/-! ## DS-D2 — concept graphs, and DS-D8/P1 with the escape hatch -/

/-- A DomainSpec concept graph (DS-D2). -/
structure ConceptGraph (V : Type) where
  τ : V → MetaType
  edges : List (V × Edge × V)

/-- An edge **uses the escape hatch** iff it is an `other` edge or touches an `opaque`
node. Such edges are accepted (graceful degradation) but tracked as an adequacy gap. -/
def UsesEscape {V} (τ : V → MetaType) (e : V × Edge × V) : Prop :=
  e.2.1 = Edge.other ∨ τ e.1 = MetaType.opaque ∨ τ e.2.2 = MetaType.opaque

instance {V} (τ : V → MetaType) (e : V × Edge × V) : Decidable (UsesEscape τ e) := by
  unfold UsesEscape; infer_instance

/-- DS-D8 edge validity **with the escape hatch**: an edge is valid iff it uses the
escape hatch OR its endpoints' meta-types lie in the edge's σ-signature. Escapes are
valid (never a modeling error); genuine type confusion among classified types is not. -/
def EdgeValid {V} (τ : V → MetaType) (e : V × Edge × V) : Prop :=
  UsesEscape τ e ∨ (τ e.1 ∈ (sig e.2.1).1 ∧ τ e.2.2 ∈ (sig e.2.1).2)

instance {V} (τ : V → MetaType) (e : V × Edge × V) : Decidable (EdgeValid τ e) := by
  unfold EdgeValid; infer_instance

/-- **Graceful degradation**: an escape-hatch edge is always valid (never rejected). -/
theorem escape_is_valid {V} (τ : V → MetaType) (e : V × Edge × V)
    (h : UsesEscape τ e) : EdgeValid τ e := Or.inl h

/-- DS-P1 well-typedness: every edge is valid. -/
def WellTyped {V} (G : ConceptGraph V) : Prop := ∀ e ∈ G.edges, EdgeValid G.τ e

/-- **The type-checker is decidable** — `WellTyped` compiles to a runnable check. -/
instance {V} (G : ConceptGraph V) : Decidable (WellTyped G) := by
  unfold WellTyped; infer_instance

/-! ## The two typed objects — residue (errors) and escapes (adequacy gaps) -/

/-- The **residue**: edges that are genuine modeling errors — mis-typed between known
meta-types (and not escapes). Empty iff well-typed. -/
def residue {V} (G : ConceptGraph V) : List (V × Edge × V) :=
  G.edges.filter (fun e => !decide (EdgeValid G.τ e))

/-- The **escapes**: edges the vocabulary could not classify (the adequacy meter). -/
def escapes {V} (G : ConceptGraph V) : List (V × Edge × V) :=
  G.edges.filter (fun e => decide (UsesEscape G.τ e))

/-- **Collapse + completeness.** The residue is empty iff the graph is well-typed. -/
theorem wellTyped_iff_residue_empty {V} (G : ConceptGraph V) :
    WellTyped G ↔ residue G = [] := by
  constructor
  · intro h
    apply List.filter_eq_nil_iff.mpr
    intro e he
    simp [h e he]
  · intro h e he
    by_contra hbad
    have : e ∈ residue G :=
      List.mem_filter.mpr ⟨he, by simp [hbad]⟩
    rw [h] at this
    simp at this

/-! ## DS-P2 — the backend/UI partition (spec core stays clean under extensions) -/

/-- DS-P2 disjointness: no meta-type is both spec-backend and spec-UI. -/
theorem dsP2_disjoint : ∀ m ∈ mB, m ∉ mU := by decide

/-- DS-P2 completeness (extended): every meta-type is spec-backend, spec-UI, or an
extension — the extensions are exactly what falls outside the spec partition. -/
theorem dsP2_cover : ∀ m : MetaType, m ∈ mB ∨ m ∈ mU ∨ m ∈ mExt := by
  intro m; cases m <;> decide

/-- Spec-backend types are on the backend layer. -/
theorem specBackend_layer : ∀ m ∈ mB, layer m = .backend := by decide

/-- Spec-UI types are on the UI layer. -/
theorem specUI_layer : ∀ m ∈ mU, layer m = .ui := by decide

/-! ## DS-P3 + σ-consistency — the load-bearing check on the σ table -/

/-- **σ is family-scoped (includes DS-P3).** Spec backend edges connect backend↔backend;
intra-UI connect UI↔UI; cross-layer go UI → backend (DS-P3). A mistyped spec signature
makes this `decide` fail. (Extension edges have `family = extension`, so all three spec
clauses hold vacuously.) -/
theorem sig_family_scoped (r : Edge) :
    (family r = .backend →
      (∀ m ∈ (sig r).1, layer m = .backend) ∧ (∀ m ∈ (sig r).2, layer m = .backend)) ∧
    (family r = .intraUI →
      (∀ m ∈ (sig r).1, layer m = .ui) ∧ (∀ m ∈ (sig r).2, layer m = .ui)) ∧
    (family r = .crossLayer →
      (∀ m ∈ (sig r).1, layer m = .ui) ∧ (∀ m ∈ (sig r).2, layer m = .backend)) := by
  cases r <;> decide

/-- DS-P3 on its own: every cross-layer edge is directed UI → backend. -/
theorem dsP3_crosslayer_direction (r : Edge) (h : family r = .crossLayer) :
    (∀ m ∈ (sig r).1, layer m = .ui) ∧ (∀ m ∈ (sig r).2, layer m = .backend) :=
  ((sig_family_scoped r).2.2) h

/-- The `associates` extension edge connects domain objects (entities / aggregates) on
both ends — the structural ER/UML association the spec lacks. -/
theorem sig_associates_domain :
    (∀ m ∈ (sig .associates).1, m ∈ domainObjects) ∧
    (∀ m ∈ (sig .associates).2, m ∈ domainObjects) := by decide

/-! ## DS-D7 — counts (spec fidelity: 13 + 11 = 24 meta-types, 15 + 8 + 6 = 29 edges) -/

/-- All 29 SPEC edges. -/
def specEdges : List Edge :=
  [.performs, .produces, .producesFor, .triggersCross, .enforcesCross, .enforces,
   .calculates, .transitions, .exposes, .orchestrates, .applies, .maps, .contains,
   .reads, .emits,
   .renders, .wraps, .composes, .consumes, .submits, .shapes, .protects, .displays,
   .fetches, .mutates, .reflects, .derives, .contracts, .mirrors]

/-- The full extended edge vocabulary (spec + extensions). -/
def allEdges : List Edge := specEdges ++ [.associates, .other]

theorem specMeta_count : (mB ++ mU).length = 24 := by decide
theorem dsD7_spec_count_total : specEdges.length = 29 := by decide
theorem dsD7_spec_count_backend :
    (specEdges.filter (fun r => decide (family r = .backend))).length = 15 := by decide
theorem dsD7_spec_count_intraUI :
    (specEdges.filter (fun r => decide (family r = .intraUI))).length = 8 := by decide
theorem dsD7_spec_count_crossLayer :
    (specEdges.filter (fun r => decide (family r = .crossLayer))).length = 6 := by decide

/-- `allEdges` is complete over the (extended) edge type. -/
theorem allEdges_complete : ∀ r : Edge, r ∈ allEdges := by
  intro r; cases r <;> decide

theorem ext_count_total : allEdges.length = 31 := by decide
theorem ext_count_extension :
    (allEdges.filter (fun r => decide (family r = .extension))).length = 2 := by decide

/-! ## Association cardinality (the ER/UML multiplicity the spec lacks) -/

/-- Association multiplicity on the target end. -/
inductive Cardinality | one | optional | many
  deriving DecidableEq, Repr

/-- A structural association between two domain objects, carrying a target cardinality
(`Order --[many]--> LineItem`). The edge-type is `associates`; this enriches it with the
multiplicity the plain σ cannot express. -/
structure CardAssoc (V : Type) where
  src : V
  dst : V
  mult : Cardinality

/-- A cardinal association is valid iff both ends are domain objects. -/
def CardAssocValid {V} (τ : V → MetaType) (a : CardAssoc V) : Prop :=
  τ a.src ∈ domainObjects ∧ τ a.dst ∈ domainObjects

instance {V} (τ : V → MetaType) (a : CardAssoc V) : Decidable (CardAssocValid τ a) := by
  unfold CardAssocValid; infer_instance

/-! ## Non-vacuity — the checker rejects errors, accepts escapes, integrates extensions -/

/-- Ill-typed `Page --enforces--> Component` (a genuine error, not an escape). -/
def badGraph : ConceptGraph Bool where
  τ := fun b => if b then .page else .component
  edges := [(true, .enforces, false)]

theorem badGraph_not_wellTyped : ¬ WellTyped badGraph := by decide
theorem badGraph_residue : residue badGraph = [(true, .enforces, false)] := by decide
theorem badGraph_no_escapes : escapes badGraph = [] := by decide

/-- Well-typed `Entity --performs--> Operation`. -/
def goodGraph : ConceptGraph Bool where
  τ := fun b => if b then .entity else .operation
  edges := [(true, .performs, false)]

theorem goodGraph_wellTyped : WellTyped goodGraph := by decide
theorem goodGraph_residue_empty : residue goodGraph = [] := by decide

/-- Escape hatch via an `other` edge between two entities: **accepted** (well-typed) but
**tracked** in `escapes` — the adequacy gap, not a rejection. -/
def escapeGraph : ConceptGraph Bool where
  τ := fun _ => .entity
  edges := [(true, .other, false)]

theorem escapeGraph_wellTyped : WellTyped escapeGraph := by decide
theorem escapeGraph_residue_empty : residue escapeGraph = [] := by decide
theorem escapeGraph_is_tracked : escapes escapeGraph = [(true, .other, false)] := by decide

/-- Escape hatch via an `opaque` node: an otherwise-illegal `enforces` edge from an
unclassifiable node is **accepted and tracked**, not mis-typed or rejected. -/
def opaqueGraph : ConceptGraph Bool where
  τ := fun b => if b then .opaque else .component
  edges := [(true, .enforces, false)]

theorem opaqueGraph_wellTyped : WellTyped opaqueGraph := by decide
theorem opaqueGraph_is_tracked : escapes opaqueGraph = [(true, .enforces, false)] := by decide

/-- Extension integration: `Aggregate --associates--> Entity` type-checks cleanly. -/
def aggregateGraph : ConceptGraph Bool where
  τ := fun b => if b then .aggregate else .entity
  edges := [(true, .associates, false)]

theorem aggregateGraph_wellTyped : WellTyped aggregateGraph := by decide

/-- Cardinality witness: `Order --[many]--> LineItem` (both entities) is a valid
cardinal association. -/
def orderHasManyItems : CardAssoc Bool := ⟨true, false, .many⟩

theorem orderHasManyItems_valid :
    CardAssocValid (fun _ => MetaType.entity) orderHasManyItems := by decide

end EdgeSignature
end DomainSpec
