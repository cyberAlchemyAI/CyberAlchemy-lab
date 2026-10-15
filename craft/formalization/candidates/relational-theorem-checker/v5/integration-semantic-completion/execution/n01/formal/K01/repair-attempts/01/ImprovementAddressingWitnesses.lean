import ImprovementAddressingCandidate

set_option autoImplicit false

namespace RelationalSuccessor.CandidateImprovementAddressing.Witnesses
open RelationalSuccessor

-- Synthetic source-shaped records, not an authenticated real inquiry or target.
def ref (name : String) : RevisionRef := ⟨⟨"fixture", name, "1"⟩, name⟩
def policy : SourcePolicy := ⟨ref "sources", ["repository"], ["exact revision"],
  "capture current snapshot", "retain conflicting evidence"⟩
def inquiry : Inquiry := ⟨ref "I", ref "owner", ref "project", [ref "goal"],
  ref "scope", ref "method", "When are recursive rules sound?", policy,
  ["bounded rule theory"], ["external execution"], ["proof or counterexample"],
  ["finite candidate profile"], [], [], [], [], 0, 0, "fixture-time",
  "owner review", "challenge review", "recorded inquiry only"⟩
def target : Target := ⟨ref "T", "Reduce checker latency without losing soundness",
  [ref "scope"], [ref "lesson"], "owner-review-required", inquiry.ref, [ref "measure"]⟩
def role : Role := ⟨ref "investigating-role", "investigate", .investigate⟩
def frame : Frame := ⟨ref "profile", inquiry.ref, target.ref, ref "context",
  inquiry.scope, ref "snapshot", 5, "fixture-time"⟩
def intentRecord : IntentRecord := ⟨ref "intent-record", inquiry.ref, target.ref,
  role.ref, frame⟩
def right : CandidateActsFor.Right := ⟨"change-checker", ref "checker", inquiry.scope⟩
def emptyAuthority : CandidateActsFor.World :=
  ⟨[], [], [], [], [], [], [], [], (fun _ _ => .unknown), [right]⟩
def world : World := ⟨ref "profile", ref "context", ref "snapshot", "fixture-time",
  [ref "project"], [ref "goal"], [ref "scope"], [ref "method"], [policy], [inquiry],
  [target], [role], [intentRecord], [], [], [], [], [], [], emptyAuthority⟩
def claim : Claim := ⟨inquiry, target, role, intentRecord, target.ref, role.code⟩
def protectedState : CandidateActsFor.ProtectedState := ⟨[], [], [], [], []⟩
def outcomeState : OutcomeState := ⟨[], [], [], protectedState, []⟩

theorem legitimate_inquiry : ValidInquiry world inquiry := by
  constructor
  · decide
  · decide
  · decide
  · decide
  · intro goal h
    have same : goal = ref "goal" := by simpa [inquiry] using h
    subst goal
    decide
  · decide
  · decide
  · decide
  · decide
  · simp [NonemptyDistinct, inquiry, policy]
  · simp [NonemptyDistinct, inquiry, policy]
  · decide
  · decide
  · simp [NonemptyDistinct, inquiry]
  · simp [NonemptyDistinct, inquiry]
  · simp [NonemptyDistinct, inquiry]
  · simp [NonemptyDistinct, inquiry]
  · decide
  · decide
  · decide
  · rfl
  · decide

theorem legitimate_addressing : Addresses world claim := by
  exact ⟨legitimate_inquiry, by decide, by decide, by decide,
    rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl⟩

theorem inquiry_without_improvement_target_is_valid :
    ValidInquiry (withoutImprovementContext world) inquiry :=
  inquiry_survives_no_improvement_context world inquiry legitimate_inquiry

theorem inquiry_without_improvement_target_has_no_addressing :
    ¬ ∃ c, Addresses (withoutImprovementContext world) c := by
  rintro ⟨c, h⟩
  exact no_targets_no_addressing (withoutImprovementContext world) c rfl h

theorem valid_inquiry_does_not_imply_improvement_link :
    ValidInquiry (withoutImprovementContext world) inquiry ∧
      ¬ ∃ c, Addresses (withoutImprovementContext world) c :=
  ⟨inquiry_without_improvement_target_is_valid,
    inquiry_without_improvement_target_has_no_addressing⟩

theorem intent_does_not_resolve_target : ¬ Resolved world target frame := by
  intro h
  rcases h.2.2 (ref "measure") (by decide) with ⟨assessment, captured, _⟩
  simp [world] at captured

theorem intent_does_not_measure_improvement : ¬ Improved world target frame := by
  rintro ⟨comparison, captured, _⟩
  simp [world] at captured

theorem intent_does_not_assign_priority : ¬ Prioritized world target frame := by
  rintro ⟨ordering, captured, _⟩
  simp [world] at captured

theorem intent_does_not_authorize_changes : ¬ Authorized world claim right := by
  rintro ⟨delegation, captured, _⟩
  simp [world, emptyAuthority] at captured

theorem resolution_non_entailment_witness :
    Addresses world claim ∧ ¬ Resolved world target frame :=
  ⟨legitimate_addressing, intent_does_not_resolve_target⟩

theorem improvement_non_entailment_witness :
    Addresses world claim ∧ ¬ Improved world target frame :=
  ⟨legitimate_addressing, intent_does_not_measure_improvement⟩

theorem priority_non_entailment_witness :
    Addresses world claim ∧ ¬ Prioritized world target frame :=
  ⟨legitimate_addressing, intent_does_not_assign_priority⟩

theorem authority_non_entailment_witness :
    Addresses world claim ∧ ¬ Authorized world claim right :=
  ⟨legitimate_addressing, intent_does_not_authorize_changes⟩

theorem target_version_substitution_refuses :
    ¬ Addresses world { claim with targetVersionRef := ref "T@2" } := by
  apply mismatched_target_revision_refuses
  decide

theorem role_code_substitution_refuses :
    ¬ Addresses world { claim with addressingRole := "unowned-role" } := by
  apply mismatched_role_code_refuses
  decide

theorem witness_target_substitution_refuses :
    ¬ Addresses world { claim with witness :=
      { intentRecord with target := ref "T@2" } } := by
  apply mismatched_witness_target_refuses
  decide

theorem stale_snapshot_refuses :
    ¬ Addresses world { claim with witness :=
      { intentRecord with frame := { frame with snapshot := ref "stale-snapshot" } } } := by
  apply stale_intent_snapshot_refuses
  decide

theorem missing_witness_refuses :
    ¬ Addresses { world with intentRecords := [] } claim :=
  no_intent_record_no_addressing _ _ rfl

theorem recording_does_not_create_outcomes :
    (record outcomeState intentRecord).resolutions = [] ∧
    (record outcomeState intentRecord).comparisons = [] ∧
    (record outcomeState intentRecord).priorities = [] ∧
    (record outcomeState intentRecord).protectedState = protectedState :=
  ⟨rfl, rfl, rfl, rfl⟩

-- Separate measurement evidence can coexist with the same addressing claim.
-- Non-entailment therefore does not mean that improvement is always false.
def lowerMetric : Metric := ⟨ref "measure", .lower⟩
def comparison : Comparison := ⟨target.ref, lowerMetric, frame, 200, 100⟩
def measuredWorld : World := { world with metrics := [lowerMetric], comparisons := [comparison] }

theorem inquiry_in_measured_world : ValidInquiry measuredWorld inquiry := by
  cases legitimate_inquiry
  constructor <;> assumption

theorem addressing_in_measured_world : Addresses measuredWorld claim := by
  cases legitimate_addressing
  constructor
  · exact inquiry_in_measured_world
  all_goals assumption

theorem separate_evidence_establishes_improvement : Improved measuredWorld target frame := by
  refine ⟨comparison, by decide, rfl, by decide, by decide, rfl, ?_⟩
  decide

theorem addressing_can_coexist_with_measured_improvement :
    Addresses measuredWorld claim ∧ Improved measuredWorld target frame :=
  ⟨addressing_in_measured_world, separate_evidence_establishes_improvement⟩

#print axioms legitimate_inquiry
#print axioms legitimate_addressing
#print axioms inquiry_without_improvement_target_is_valid
#print axioms inquiry_without_improvement_target_has_no_addressing
#print axioms valid_inquiry_does_not_imply_improvement_link
#print axioms intent_does_not_resolve_target
#print axioms intent_does_not_measure_improvement
#print axioms intent_does_not_assign_priority
#print axioms intent_does_not_authorize_changes
#print axioms resolution_non_entailment_witness
#print axioms improvement_non_entailment_witness
#print axioms priority_non_entailment_witness
#print axioms authority_non_entailment_witness
#print axioms target_version_substitution_refuses
#print axioms role_code_substitution_refuses
#print axioms witness_target_substitution_refuses
#print axioms stale_snapshot_refuses
#print axioms missing_witness_refuses
#print axioms recording_does_not_create_outcomes
#print axioms inquiry_in_measured_world
#print axioms addressing_in_measured_world
#print axioms separate_evidence_establishes_improvement
#print axioms addressing_can_coexist_with_measured_improvement
end RelationalSuccessor.CandidateImprovementAddressing.Witnesses
