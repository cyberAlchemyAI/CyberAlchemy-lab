import LessonUseCandidate

set_option autoImplicit false

namespace CandidateLessonUse.Controls
open CandidateLessonUse

def ref (name : String) : Ref := ⟨name, 1⟩
def frame : Frame := ⟨ref "session", ref "owner", ref "scope", ref "snapshot", 10⟩
def application (posture : Posture) : Application :=
  ⟨ref "application", ref "lesson", ref "assessment", posture, frame,
    [ref "conflict"], [ref "override"]⟩
def assessment : Assessment :=
  ⟨ref "assessment", ref "application", ref "lesson", frame, "context assessment"⟩
def policy : Policy :=
  ⟨ref "policy", ref "owner", ref "scope", 0, 20,
    [(ref "governing", 2), (ref "subordinate", 1)]⟩
def evidence (posture : Posture) : DispositionEvidence :=
  ⟨ref "disposition", ref "application", ref "lesson", frame, posture,
    ref "governing", "captured disposition basis"⟩
def conflict : Conflict :=
  ⟨ref "conflict", ref "application", frame, ref "governing", ref "subordinate"⟩
def override : Override :=
  ⟨ref "override", ref "application", frame, ref "conflict", ref "governing",
    "higher ranked instruction"⟩
def claim (posture : Posture) : Claim :=
  ⟨application posture, ref "lesson", ref "lesson", posture, ref "assessment",
    ref "policy", assessment, policy, evidence posture, frame⟩
def world (c : Claim) : World :=
  ⟨[c.application], [ref "lesson"], [c.assessment], [c.policy],
    [⟨ref "governing", ref "owner", ref "scope"⟩,
     ⟨ref "subordinate", ref "owner", ref "scope"⟩],
    [c.disposition], [conflict], [override], [frame]⟩
def used : Claim := claim .used
def declined : Claim := claim .declined

theorem actual_use_model : AppliesLesson (world used) used := by decide
theorem deliberate_non_use_model : AppliesLesson (world declined) declined := by decide
theorem actual_use_check : check (world used) used = true := by decide
theorem deliberate_non_use_check : check (world declined) declined = true := by decide
theorem selection_refused : check (world (claim .selected)) (claim .selected) = false := by decide
theorem presentation_refused : check (world (claim .presented)) (claim .presented) = false := by decide

theorem label_without_evidence_refused :
    check { world used with evidence := [] } used = false := by decide
theorem unknown_assessment_refused :
    check { world declined with assessments := [] } declined = false := by decide

def staleLesson : Claim := { used with lessonQualifier := ⟨"lesson", 0⟩ }
theorem stale_lesson_refused : check (world staleLesson) staleLesson = false := by decide
def wrongPosture : Claim := { used with postureQualifier := .declined }
theorem inconsistent_posture_refused : check (world wrongPosture) wrongPosture = false := by decide
def wrongAssessment : Claim := { used with assessmentQualifier := ref "other-assessment" }
theorem assessment_join_refused : check (world wrongAssessment) wrongAssessment = false := by decide
def wrongPolicy : Claim := { used with precedenceQualifier := ref "other-policy" }
theorem precedence_join_refused : check (world wrongPolicy) wrongPolicy = false := by decide
def staleSnapshot : Claim := { used with frame := { frame with snapshot := ⟨"snapshot", 0⟩ } }
theorem stale_snapshot_refused : check (world staleSnapshot) staleSnapshot = false := by decide

def expiredPolicy : Claim := { used with policy := { policy with finish := 9 } }
theorem expired_policy_refused : check (world expiredPolicy) expiredPolicy = false := by decide
def futurePolicy : Claim := { used with policy := { policy with start := 11 } }
theorem future_policy_refused : check (world futurePolicy) futurePolicy = false := by decide
def wrongOwner : Claim := { used with policy := { policy with owner := ref "different-owner" } }
theorem wrong_policy_owner_refused : check (world wrongOwner) wrongOwner = false := by decide
def missingRank : Claim := { used with policy := { policy with ranks := [] } }
theorem missing_precedence_refused : check (world missingRank) missingRank = false := by decide
def duplicateRank : Claim :=
  { used with policy := { policy with ranks := policy.ranks ++ [(ref "governing", 0)] } }
theorem ambiguous_rank_refused : check (world duplicateRank) duplicateRank = false := by decide
def reversedRanks : Claim :=
  { used with policy := { policy with ranks := [(ref "governing", 1), (ref "subordinate", 2)] } }
theorem lower_priority_winner_refused : check (world reversedRanks) reversedRanks = false := by decide

def droppedConflict : Claim :=
  { used with application := { used.application with conflicts := [] } }
theorem unretained_conflict_refused : check (world droppedConflict) droppedConflict = false := by decide
theorem invented_conflict_refused :
    check { world used with conflicts := [] } used = false := by decide
def droppedOverride : Claim :=
  { declined with application := { declined.application with overrides := [] } }
theorem unretained_override_refused : check (world droppedOverride) droppedOverride = false := by decide
theorem invented_override_refused :
    check { world declined with overrides := [] } declined = false := by decide
theorem absent_override_basis_refused :
    check { world declined with overrides := [{ override with basis := "" }] } declined = false := by decide
theorem missing_governing_instruction_refused :
    check { world used with instructions := [] } used = false := by decide

def emptyLedger : Ledger := ⟨[], [], [], [], [], []⟩
def recorded : Ledger := { emptyLedger with rows := [(ref "relation", used)] }
theorem record_appends_exact_claim :
    record (ref "relation") used emptyLedger = some recorded := by decide
theorem record_retry_unchanged :
    record (ref "relation") used recorded = some recorded := by decide
theorem record_conflict_refused :
    record (ref "relation") declined recorded = none := by decide

end CandidateLessonUse.Controls
