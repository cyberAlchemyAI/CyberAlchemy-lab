import StressLaws
import StressCheckers

namespace Stress

theorem acts_checker_sound (ds : List Delegation) (s : Snapshot) (e : ActsEdge)
    (action : String) (redelegated : Bool)
    (h : checkActs ds s e action redelegated = .yes) :
    ActsHolds ds s e action redelegated := by
  unfold checkActs at h
  split at h
  · contradiction
  · split at h
    · contradiction
    · split at h
      · contradiction
      · split at h
        · contradiction
        · split at h
          · assumption
          · contradiction

theorem acts_checker_iff_when_known (ds : List Delegation) (s : Snapshot) (e : ActsEdge)
    (action : String) (valid : ActsInventoryValid ds s e action)
    (resolved : DelegationResolved ds e) (known : InterpretationKnown ds s e) :
    checkActs ds s e action false = .yes ↔ ActsHolds ds s e action false := by
  unfold checkActs
  rw [if_neg (not_not_intro valid), if_neg (not_not_intro resolved),
    if_neg (not_not_intro known), if_neg (by intro h; cases h.1)]
  by_cases effective : ActsHolds ds s e action false <;> simp [effective]

theorem origin_in_candidates (g : Graph) (f : Fact) (h : Origin g f) : f ∈ candidateFacts g := by
  rcases h with ⟨edgeMem, b, _, c, contractMem, _, normMem⟩
  simp only [candidateFacts, List.mem_flatMap, List.mem_map]
  exact ⟨f.edge, edgeMem, c, contractMem, f.norm, normMem, rfl⟩

theorem closure_exact (g : Graph) (f : Fact) : f ∈ closure g ↔ Origin g f := by
  simp only [closure, List.mem_eraseDups, List.mem_filter, decide_eq_true_eq]
  exact ⟨fun h => h.2, fun h => ⟨origin_in_candidates g f h, h⟩⟩

theorem closure_equals_derivability (g : Graph) (f : Fact) :
    f ∈ closure g ↔ Derives g f := by
  rw [closure_exact, derives_iff_origin]

theorem inheritance_checker_sound (g : Graph) (budget : Nat)
    (h : checkInheritance g budget = .yes) :
    GraphValid g ∧ InheritanceKnown g ∧ InheritanceMatches g ∧
      workUnits g ≤ budget := by
  unfold checkInheritance at h
  split at h
  · contradiction
  · rename_i valid
    split at h
    · contradiction
    · rename_i known
      split at h
      · contradiction
      · rename_i matched
        split at h
        · contradiction
        · rename_i bounded
          exact ⟨Decidable.not_not.mp valid, Decidable.not_not.mp known,
            Decidable.not_not.mp matched, Nat.le_of_not_gt bounded⟩

theorem certificate_check_iff (g : Graph) (steps : List Step) :
    checkCertificate g steps = true ↔ CertificateValid g steps := by
  simp [checkCertificate]

theorem certificate_checker_sound (g : Graph) (steps : List Step)
    (h : checkCertificate g steps = true) :
    ReplayShape steps ∧ ∀ s ∈ steps, Derives g s.fact := by
  have valid := (certificate_check_iff g steps).mp h
  exact ⟨valid.1, fun s hs => origin_has_derivation g s.fact (valid.2 s hs)⟩

end Stress
