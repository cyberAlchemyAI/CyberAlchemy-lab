import InterpretationSemantics

namespace Successor.Interpretation
open Stress

theorem token_functional {κ α : Type} (rows : List (κ × α))
    (unique : (rows.map Prod.fst).Nodup) (token : κ) (a b : α)
    (ha : (token,a) ∈ rows) (hb : (token,b) ∈ rows) : a = b := by
  have equal := Relational.Logic.identity_functional_of_nodup_map Prod.fst rows
    unique (token,a) (token,b) ha hb rfl
  exact congrArg Prod.snd equal

abbrev RequiredActsMapping : Prop :=
  ∀ s raw e d snapshot action redelegated, StoreFunctional s → MapsActs s raw e →
    (Effective d snapshot e action redelegated ↔ LegacyActsEffective s raw d snapshot action redelegated)

theorem acts_mapping_exact : RequiredActsMapping := by
  intro s raw e d snapshot action redelegated functional mapped
  rcases mapped with ⟨_,agent,principal,ref,scope,period,revocation⟩
  constructor
  · rintro ⟨⟨href,ha,hp,ht,hr⟩,actionOK,scopeOK,start,stop,clear,policies,gates,direct⟩
    refine ⟨?_,?_,?_,?_,?_,⟨e.scope,scope,scopeOK⟩,actionOK,start,stop,clear,policies,gates,direct⟩
    · simpa only [href] using ref
    · exact agent.symm.trans ha
    · exact principal.symm.trans hp
    · simpa only [ht] using period
    · simpa only [hr] using revocation
  · rintro ⟨href,ha,hp,ht,hr,⟨interpretedScope,hscope,scopeOK⟩,actionOK,start,stop,clear,policies,gates,direct⟩
    have refEqual := token_functional s.references functional.1 ("delegation",raw.delegationToken) _ _ ref href
    have scopeEqual := token_functional s.scopes functional.2.1 raw.scopeToken _ _ scope hscope
    have periodEqual := token_functional s.periods functional.2.2.1 raw.periodToken _ _ period ht
    have revocationEqual := token_functional s.revocations functional.2.2.2 raw.revocationToken _ _ revocation hr
    exact ⟨⟨refEqual,agent.trans ha,principal.trans hp,periodEqual,revocationEqual⟩,
      actionOK,scopeEqual.symm ▸ scopeOK,start,stop,clear,policies,gates,direct⟩

abbrev RequiredInheritanceMapping : Prop :=
  ∀ s raw g e n, GraphValid g → MapsInheritance s raw e → e ∈ g.inheritances →
    (Origin g ⟨e,n⟩ ↔ LegacyNorm s raw g n)

theorem inheritance_mapping_exact : RequiredInheritanceMapping := by
  intro s raw g e n valid mapped member
  rcases mapped with ⟨id,subject,contract,binding,version⟩
  constructor
  · rintro ⟨_,b,hb,c,hc,matched,norm⟩
    exact ⟨e,member,id,subject,contract,binding,version,b,hb,c,hc,matched,norm⟩
  · rintro ⟨other,ho,hid,_,_,_,_,b,hb,c,hc,matched,norm⟩
    have unique : (g.inheritances.map Inheritance.id).Nodup := valid.2.2.2.2.2.1
    have same := Relational.Logic.identity_functional_of_nodup_map Inheritance.id g.inheritances
      unique e other member ho (id.trans hid.symm)
    subst other
    exact ⟨member,b,hb,c,hc,matched,norm⟩

#print axioms acts_mapping_exact
#print axioms inheritance_mapping_exact
end Successor.Interpretation
