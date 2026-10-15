import DerivationSoundness

namespace Inference

-- Independent finite enumeration: all lists of length n drawn from the domain.
def choices (domain : List Value) : Nat → List (List Value)
  | 0 => [[]]
  | n + 1 => domain.flatMap fun v => (choices domain n).map (v :: ·)

theorem choices_complete (domain : List Value) (values : List Value)
    (inside : ∀ v ∈ values, v ∈ domain) : values ∈ choices domain values.length := by
  induction values with
  | nil => simp [choices]
  | cons v rest ih =>
      apply List.mem_flatMap.mpr
      refine ⟨v, inside v (by simp), ?_⟩
      apply List.mem_map.mpr
      exact ⟨rest, ih (fun x hx => inside x (List.mem_cons_of_mem v hx)), rfl⟩

def groundRule (T : Theory) (r : Rule) (values : List Value) : Option GroundInstance :=
  if decide (SubstitutionValid T r values) then do
    let head ← instantiate values r.head
    let body ← instantiateBody values r.body
    pure { rule := r.key, substitution := values, head := head, body := body }
  else none
def groundInstances (T : Theory) : List GroundInstance :=
  T.rules.flatMap fun r => (choices T.domain r.variables.length).filterMap (groundRule T r)

theorem ground_rule_captures_instance {T : Theory} {r : Rule} {i : GroundInstance}
    (key : r.key = i.rule) (substitution : SubstitutionValid T r i.substitution)
    (head : instantiate i.substitution r.head = some i.head)
    (body : instantiateBody i.substitution r.body = some i.body) :
    groundRule T r i.substitution = some i := by
  unfold groundRule
  rw [if_pos (by simpa using substitution)]
  simp [head, body, key]

theorem ground_instances_complete {T : Theory} {i : GroundInstance}
    (valid : ValidInstance T i) : i ∈ groundInstances T := by
  rcases valid with ⟨r, member, key, substitution, head, body⟩
  have length : i.substitution.length = r.variables.length := by
    have eq := congrArg List.length substitution.1
    simpa using eq
  have selected := choices_complete T.domain i.substitution substitution.2
  rw [length] at selected
  exact List.mem_flatMap.mpr ⟨r, member,
    List.mem_filterMap.mpr ⟨i.substitution, selected,
      ground_rule_captures_instance key substitution head body⟩⟩

abbrev Saturated (T : Theory) (C : List Atom) : Prop :=
  ∀ i ∈ groundInstances T, (∀ a ∈ i.body, a ∈ C) → i.head ∈ C
instance (T : Theory) (C : List Atom) : Decidable (Saturated T C) := by unfold Saturated; infer_instance
abbrev ClosureValid (T : Theory) (F C : List Atom) (certificates : List (List Step)) : Prop :=
  TheoryValid T ∧ InitialValid T F ∧ C.Nodup ∧ (∀ a ∈ C, AtomValid T a) ∧
  (∀ a ∈ F, a ∈ C) ∧ Saturated T C ∧
  ∀ a ∈ C, ∃ steps ∈ certificates, checkDerivation T F steps a = true
instance (T : Theory) (F C : List Atom) (certificates : List (List Step)) :
    Decidable (ClosureValid T F C certificates) := by unfold ClosureValid; infer_instance
def checkClosure (T : Theory) (F C : List Atom) (certificates : List (List Step)) : Bool :=
  decide (ClosureValid T F C certificates)

theorem closure_checker_iff (T : Theory) (F C : List Atom) (certificates : List (List Step)) :
    checkClosure T F C certificates = true ↔ ClosureValid T F C certificates := by simp [checkClosure]
theorem checked_closure_is_closed {T : Theory} {F C : List Atom} {certificates : List (List Step)}
    (checked : checkClosure T F C certificates = true) : Closed T F C := by
  have valid := (closure_checker_iff T F C certificates).mp checked
  refine ⟨valid.2.2.2.2.1, ?_⟩
  intro i instance_valid premises
  exact valid.2.2.2.2.2.1 i (ground_instances_complete instance_valid) premises
theorem checked_closure_has_no_extra {T : Theory} {F C : List Atom} {certificates : List (List Step)}
    (checked : checkClosure T F C certificates = true) : ∀ a ∈ C, Derivable T F a := by
  have valid := (closure_checker_iff T F C certificates).mp checked
  intro a member
  rcases valid.2.2.2.2.2.2 a member with ⟨steps, _, accepted⟩
  exact derivation_certificate_sound T F steps a accepted
theorem checked_closure_exact {T : Theory} {F C : List Atom} {certificates : List (List Step)}
    (checked : checkClosure T F C certificates = true) (a : Atom) :
    a ∈ C ↔ Derivable T F a := by
  exact ⟨checked_closure_has_no_extra checked a,
    derivable_in_every_closed_model (checked_closure_is_closed checked)⟩
theorem checked_closure_is_least {T : Theory} {F C : List Atom} {certificates : List (List Step)}
    (checked : checkClosure T F C certificates = true) (M : List Atom) (model : Closed T F M) :
    ∀ a ∈ C, a ∈ M := by
  intro a member
  exact derivable_in_every_closed_model model (checked_closure_has_no_extra checked a member)
theorem absent_from_checked_closure_not_derivable {T : Theory} {F C : List Atom}
    {certificates : List (List Step)} (checked : checkClosure T F C certificates = true)
    (a : Atom) (absent : a ∉ C) : ¬ Derivable T F a := by
  intro derived
  exact absent ((checked_closure_exact checked a).mpr derived)

-- A positive saturation step consumes one pending head. This measure is finite
-- and strictly decreases even if the pending inventory initially has duplicates.
def enabled (current remaining : List Atom) (i : GroundInstance) : Bool :=
  decide (i.head ∈ remaining ∧ i.head ∉ current ∧ ∀ a ∈ i.body, a ∈ current)
theorem enabled_head_is_pending {current remaining : List Atom} {i : GroundInstance}
    (active : enabled current remaining i = true) : i.head ∈ remaining := by
  have h : i.head ∈ remaining ∧ i.head ∉ current ∧ ∀ a ∈ i.body, a ∈ current := by
    simpa [enabled] using active
  exact h.1
theorem saturation_measure_decreases {current remaining : List Atom} {i : GroundInstance}
    (active : enabled current remaining i = true) :
    (remaining.erase i.head).length < remaining.length := by
  have member := enabled_head_is_pending active
  have positive : 0 < remaining.length := List.length_pos_of_mem member
  rw [List.length_erase_of_mem member]
  omega

def saturateFuel (instances : List GroundInstance) :
    Nat → List Atom → List Atom → Option (List Atom)
  | 0, current, remaining =>
      match instances.find? (enabled current remaining) with
      | none => some current
      | some _ => none
  | fuel + 1, current, remaining =>
      match instances.find? (enabled current remaining) with
      | none => some current
      | some i => saturateFuel instances fuel (current ++ [i.head]) (remaining.erase i.head)

theorem saturation_sufficient_fuel (instances : List GroundInstance) (fuel : Nat) :
    ∀ current remaining, remaining.length ≤ fuel →
      ∃ result, saturateFuel instances fuel current remaining = some result := by
  induction fuel with
  | zero =>
      intro current remaining bound
      cases h : instances.find? (enabled current remaining) with
      | none => exact ⟨current, by simp [saturateFuel, h]⟩
      | some i =>
          have decreases := saturation_measure_decreases (List.find?_some h)
          omega
  | succ fuel ih =>
      intro current remaining bound
      cases h : instances.find? (enabled current remaining) with
      | none => exact ⟨current, by simp [saturateFuel, h]⟩
      | some i =>
          have decreases := saturation_measure_decreases (List.find?_some h)
          have smaller : (remaining.erase i.head).length ≤ fuel := by omega
          rcases ih (current ++ [i.head]) (remaining.erase i.head) smaller with ⟨result, done⟩
          exact ⟨result, by simpa [saturateFuel, h] using done⟩

def saturate (instances : List GroundInstance) (current remaining : List Atom) : List Atom :=
  (saturateFuel instances remaining.length current remaining).getD []

theorem saturation_never_exhausts (instances : List GroundInstance) (current remaining : List Atom) :
    ∃ result, saturateFuel instances remaining.length current remaining = some result :=
  saturation_sufficient_fuel instances remaining.length current remaining (by omega)

-- The actual computation terminates by the decreasing finite pending inventory
-- with a proved sufficient structural recursion bound;
-- adequacy is certified separately so operational resource failure is unknown.
abbrev RequiredClosureAdequacy : Prop :=
  ∀ (T : Theory) (F C : List Atom) (certificates : List (List Step)),
    checkClosure T F C certificates = true → ∀ a, a ∈ C ↔ Derivable T F a
theorem audited_closure_adequacy : RequiredClosureAdequacy := by
  intro T F C certificates checked a
  exact checked_closure_exact checked a

end Inference
