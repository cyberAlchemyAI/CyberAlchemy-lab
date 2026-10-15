import ContextProjection

namespace Successor.Projection
open Relational Successor

theorem edge_tuple_exact (e : Assertion) (x : ConformanceTuple) :
    edgeTuple e = some x ↔ ∃ ver ev,
      e.kind = .conformsTo ∧ e.qualifiers = .conformance x.scope ver ev ∧
        e.source = x.subject ∧ e.target = x.target := by
  cases hk : e.kind <;> cases hq : e.qualifiers <;> simp [edgeTuple,hk,hq]
  constructor
  · intro hx
    subst x
    exact ⟨rfl,rfl,rfl⟩
  · rintro ⟨hscope,hs,ht⟩
    cases x
    simp_all

theorem project_edge_exact (g : Relational.Graph) (e : Assertion) (x : ConformanceTuple) :
    projectEdge g e = some x ↔ ∃ ver ev,
      Relational.Logic.ConformsAt g e x.scope ver ev ∧ e.source = x.subject ∧ e.target = x.target := by
  unfold projectEdge
  split
  · rename_i checked
    have valid : InstanceValid g e := by simpa only [decide_eq_true_eq] using checked
    rw [edge_tuple_exact]
    constructor
    · rintro ⟨ver,ev,hk,hq,hs,ht⟩
      exact ⟨ver,ev,⟨hk,hq,valid⟩,hs,ht⟩
    · rintro ⟨ver,ev,⟨hk,hq,_⟩,hs,ht⟩
      exact ⟨ver,ev,hk,hq,hs,ht⟩
  · rename_i unchecked
    have invalid : ¬ InstanceValid g e := by simpa only [decide_eq_true_eq] using unchecked
    constructor
    · intro impossible; cases impossible
    · rintro ⟨ver,ev,hconf,_,_⟩
      exact False.elim (invalid hconf.2.2)

theorem projection_exact : Successor.Required.ProjectionExact project := by
  intro g x
  unfold project
  split
  · rename_i checked
    have hg : Inv g := by simpa only [decide_eq_true_eq] using checked
    constructor
    · intro hit
      rcases List.mem_filterMap.mp (List.mem_eraseDups.mp hit) with ⟨e,he,hit⟩
      rcases (project_edge_exact g e x).mp hit with ⟨ver,ev,hconf,hs,ht⟩
      exact ⟨hg,e,he,ver,ev,hconf,hs,ht⟩
    · rintro ⟨_,e,he,ver,ev,hconf,hs,ht⟩
      apply List.mem_eraseDups.mpr
      exact List.mem_filterMap.mpr ⟨e,he,(project_edge_exact g e x).mpr ⟨ver,ev,hconf,hs,ht⟩⟩
  · rename_i unchecked
    have invalid : ¬ Inv g := by simpa only [decide_eq_true_eq] using unchecked
    constructor
    · intro impossible; cases impossible
    · intro h; exact False.elim (invalid h.1)

theorem kind_projection_exact : Successor.Required.KindProjectionExact projectKinds := by
  intro g r k
  unfold projectKinds
  split
  · rename_i checked
    have hg : Inv g := by simpa only [decide_eq_true_eq] using checked
    constructor
    · intro hit
      rcases List.mem_map.mp (List.mem_eraseDups.mp hit) with ⟨n,hn,heq⟩
      exact ⟨hg,n,hn,congrArg Prod.fst heq,congrArg Prod.snd heq⟩
    · rintro ⟨_,n,hn,hr,hk⟩
      exact List.mem_eraseDups.mpr (List.mem_map.mpr ⟨n,hn,Prod.ext hr hk⟩)
  · rename_i unchecked
    have invalid : ¬ Inv g := by simpa only [decide_eq_true_eq] using unchecked
    constructor
    · intro impossible; cases impossible
    · intro h; exact False.elim (invalid h.1)

theorem existential_view_exact : Successor.Required.ExistentialViewExact project projectUnary := by
  intro g r
  simp only [projectUnary,List.mem_eraseDups,List.mem_map]

theorem support_exact (g : Relational.Graph) (x : ConformanceTuple) :
    x ∈ project g ↔ ∃ s, Supports g x s := by
  rw [projection_exact]
  constructor
  · rintro ⟨hg,e,he,ver,ev,hconf,hs,ht⟩
    exact ⟨⟨e,ver,ev⟩,hg,he,hconf,hs,ht⟩
  · rintro ⟨s,hg,he,hconf,hs,ht⟩
    exact ⟨hg,s.assertion,he,s.version,s.assessment,hconf,hs,ht⟩

theorem kind_encoding_injective : Successor.Required.KindEncodingInjective := by
  intro a b h
  cases a <;> cases b <;> simp [kindName] at h ⊢

#print axioms projection_exact
#print axioms kind_projection_exact
#print axioms existential_view_exact
#print axioms support_exact
#print axioms kind_encoding_injective
end Successor.Projection
