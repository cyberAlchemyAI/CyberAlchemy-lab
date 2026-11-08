import InferenceCore

namespace Inference

inductive Step where
  | base (conclusion : Atom)
  | apply (ground : GroundInstance) (premises : List Nat)
  deriving DecidableEq, Repr
def Step.conclusion : Step → Atom
  | .base a => a
  | .apply i _ => i.head
def resolvePremises (previous : List Atom) : List Nat → Option (List Atom)
  | [] => some []
  | i :: indices => do
      let a ← previous[i]?
      let rest ← resolvePremises previous indices
      pure (a :: rest)
abbrev StepValid (T : Theory) (F previous : List Atom) : Step → Prop
  | .base a => a ∈ F
  | .apply i indices => ValidInstance T i ∧ resolvePremises previous indices = some i.body
instance (T : Theory) (F previous : List Atom) (step : Step) :
    Decidable (StepValid T F previous step) := by cases step <;> unfold StepValid <;> infer_instance
def ChainValid (T : Theory) (F previous : List Atom) : List Step → Prop
  | [] => True
  | step :: rest => StepValid T F previous step ∧
      ChainValid T F (previous ++ [step.conclusion]) rest
def chainDecidable (T : Theory) (F previous : List Atom) :
    (steps : List Step) → Decidable (ChainValid T F previous steps)
  | [] => isTrue True.intro
  | step :: rest => @instDecidableAnd (StepValid T F previous step)
      (ChainValid T F (previous ++ [step.conclusion]) rest) inferInstance
      (chainDecidable T F (previous ++ [step.conclusion]) rest)
instance (T : Theory) (F previous : List Atom) (steps : List Step) :
    Decidable (ChainValid T F previous steps) := chainDecidable T F previous steps
abbrev CertificateValid (T : Theory) (F : List Atom) (steps : List Step) (query : Atom) : Prop :=
  TheoryValid T ∧ InitialValid T F ∧ AtomValid T query ∧
    ChainValid T F [] steps ∧ query ∈ steps.map Step.conclusion
instance (T : Theory) (F : List Atom) (steps : List Step) (query : Atom) :
    Decidable (CertificateValid T F steps query) := by unfold CertificateValid; infer_instance
def checkDerivation (T : Theory) (F : List Atom) (steps : List Step) (query : Atom) : Bool :=
  decide (CertificateValid T F steps query)

theorem resolved_premises_are_previous {previous : List Atom} {indices : List Nat} {body : List Atom}
    (resolved : resolvePremises previous indices = some body) : ∀ a ∈ body, a ∈ previous := by
  induction indices generalizing body with
  | nil =>
      simp [resolvePremises] at resolved
      subst body
      simp
  | cons i rest ih =>
      cases hi : previous[i]? with
      | none => simp [resolvePremises, hi] at resolved
      | some a =>
          cases hr : resolvePremises previous rest with
          | none => simp [resolvePremises, hi, hr] at resolved
          | some tail =>
              simp [resolvePremises, hi, hr] at resolved
              subst body
              intro b hb
              rcases List.mem_cons.mp hb with eq | member
              · subst b
                exact List.mem_of_getElem? hi
              · exact ih hr b member

theorem step_sound {T : Theory} {F previous : List Atom} {step : Step}
    (checked : StepValid T F previous step)
    (earlier : ∀ a ∈ previous, Derivable T F a) : Derivable T F step.conclusion := by
  cases step with
  | base a => exact .base checked
  | apply i indices =>
      exact .apply i checked.1 (fun a ha => earlier a (resolved_premises_are_previous checked.2 a ha))

theorem chain_sound {T : Theory} {F previous : List Atom} {steps : List Step}
    (checked : ChainValid T F previous steps)
    (earlier : ∀ a ∈ previous, Derivable T F a) :
    ∀ a ∈ steps.map Step.conclusion, Derivable T F a := by
  induction steps generalizing previous with
  | nil => simp
  | cons step rest ih =>
      have derived := step_sound checked.1 earlier
      have extended : ∀ a ∈ previous ++ [step.conclusion], Derivable T F a := by
        intro a ha
        rcases List.mem_append.mp ha with old | fresh
        · exact earlier a old
        · have eq := List.mem_singleton.mp fresh
          subst a
          exact derived
      intro a ha
      rcases List.mem_cons.mp ha with fresh | old
      · subst a
        exact derived
      · exact ih checked.2 extended a old

theorem derivation_checker_iff (T : Theory) (F : List Atom) (steps : List Step) (query : Atom) :
    checkDerivation T F steps query = true ↔ CertificateValid T F steps query := by
  simp [checkDerivation]

theorem derivation_certificate_sound (T : Theory) (F : List Atom) (steps : List Step) (query : Atom)
    (accepted : checkDerivation T F steps query = true) : Derivable T F query := by
  have checked := (derivation_checker_iff T F steps query).mp accepted
  exact chain_sound checked.2.2.2.1 (by simp) query checked.2.2.2.2

abbrev RequiredDerivationSoundness : Prop :=
  ∀ (T : Theory) (F : List Atom) (steps : List Step) (query : Atom),
    checkDerivation T F steps query = true → Derivable T F query
theorem audited_derivation_soundness : RequiredDerivationSoundness := derivation_certificate_sound

end Inference
