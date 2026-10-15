import RecursiveConservativity
namespace Successor.Recursive
open Inference Inference.Extension
abbrev HeadCover (is : List GroundInstance) (cur pending : List Atom) : Prop :=
  ∀ i ∈ is, i.head ∈ cur ∨ i.head ∈ pending
abbrev InstanceClosed (is : List GroundInstance) (cur : List Atom) : Prop :=
  ∀ i ∈ is, (∀ a ∈ i.body, a ∈ cur) → i.head ∈ cur
-- The pending head inventory is complete for the independently enumerated
-- instances. This invariant is necessary: termination alone is not adequacy.
theorem saturation_state (is : List GroundInstance) (P : Atom → Prop)
    (step : ∀ i ∈ is, (∀ a ∈ i.body, P a) → P i.head) (fuel : Nat) :
    ∀ cur pending result, HeadCover is cur pending →
      (∀ a ∈ cur, P a) → saturateFuel is fuel cur pending = some result →
      (∀ a ∈ cur, a ∈ result) ∧ (∀ a ∈ result, P a) ∧ InstanceClosed is result := by
  induction fuel with
  | zero =>
      intro cur pending result cover sound done
      cases found : is.find? (enabled cur pending) with
      | none =>
          have eq : cur = result := by simpa [saturateFuel,found] using done
          subst result
          refine ⟨fun _ h => h,sound,?_⟩
          intro i hi body
          rcases cover i hi with present | waiting
          · exact present
          · by_cases present : i.head ∈ cur
            · exact present
            · have active : enabled cur pending i = true := by unfold enabled; exact decide_eq_true ⟨waiting,present,body⟩
              exact False.elim ((List.find?_eq_none.mp found i hi) active)
      | some i => simp [saturateFuel,found] at done
  | succ fuel ih =>
      intro cur pending result cover sound done
      cases found : is.find? (enabled cur pending) with
      | none =>
          have eq : cur = result := by simpa [saturateFuel,found] using done
          subst result
          refine ⟨fun _ h => h,sound,?_⟩
          intro i hi body
          rcases cover i hi with present | waiting
          · exact present
          · by_cases present : i.head ∈ cur
            · exact present
            · have active : enabled cur pending i = true := by unfold enabled; exact decide_eq_true ⟨waiting,present,body⟩
              exact False.elim ((List.find?_eq_none.mp found i hi) active)
      | some i =>
          have active : i.head ∈ pending ∧ i.head ∉ cur ∧ ∀ a ∈ i.body, a ∈ cur := by
            simpa [enabled] using List.find?_some found
          have member : i ∈ is := List.mem_of_find?_eq_some found
          have newCover : HeadCover is (cur ++ [i.head]) (pending.erase i.head) := by
            intro j hj
            rcases cover j hj with present | waiting
            · exact Or.inl (List.mem_append.mpr (Or.inl present))
            · by_cases eq : j.head = i.head
              · exact Or.inl (by simp [eq])
              · exact Or.inr ((List.mem_erase_of_ne eq).mpr waiting)
          have newSound : ∀ a ∈ cur ++ [i.head], P a := by
            intro a ha
            rcases List.mem_append.mp ha with old | new
            · exact sound a old
            · have eq : a = i.head := by simpa using new
              subst a
              exact step i member (fun b hb => sound b (active.2.2 b hb))
          have recurse : saturateFuel is fuel (cur ++ [i.head]) (pending.erase i.head) = some result := by
            simpa [saturateFuel,found] using done
          have final := ih _ _ _ newCover newSound recurse
          exact ⟨fun a ha => final.1 a (List.mem_append.mpr (Or.inl ha)),final.2⟩
theorem reference_saturation_exact (T : Theory) (F : List Atom) :
    ∃ C, saturateFuel (groundInstances T) (groundInstances T).length F ((groundInstances T).map GroundInstance.head) = some C ∧
      ∀ a, a ∈ C ↔ Derivable T F a := by
  let is := groundInstances T
  let pending := is.map GroundInstance.head
  rcases saturation_sufficient_fuel is is.length F pending (by simp [pending]) with ⟨C,done⟩
  have cover : HeadCover is F pending := by
    intro i hi
    exact Or.inr (List.mem_map.mpr ⟨i,hi,rfl⟩)
  have state := saturation_state is (Derivable T F)
    (fun i hi body => Derivable.apply i (ground_instances_sound hi) body) is.length F pending C cover
    (fun _ h => Derivable.base h) done
  have closed : Closed T F C := ⟨state.1,fun i valid body => state.2.2 i (ground_instances_complete valid) body⟩
  exact ⟨C,done,fun a => ⟨state.2.1 a,derivable_in_every_closed_model closed⟩⟩
#print axioms saturation_state
#print axioms reference_saturation_exact
end Successor.Recursive
