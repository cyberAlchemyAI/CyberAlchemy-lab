import MetadataProjection
import IntentAddressingCheck

set_option autoImplicit false
namespace RelationalSuccessor.CandidateIntentSourceContract
open RelationalSuccessor

abbrev World := CandidateIntentAddressing.World
abbrev Claim := CandidateIntentAddressing.Claim
abbrev Projected := CandidateCapturedMetadata.Projected

structure FramedWorld where
  world : World
  frame : Frame

structure WorldFrameAligned (w : FramedWorld) : Prop where
  profile : w.world.profile = w.frame.profile
  context : w.world.context = w.frame.context
  scope : w.world.scope = w.frame.scope
  snapshot : w.world.snapshot = w.frame.snapshot
  timeDomain : w.world.timeDomain = w.frame.timeDomain

def worldFrameCheck (w : FramedWorld) : Bool :=
  decide (w.world.profile = w.frame.profile) && decide (w.world.context = w.frame.context) &&
  decide (w.world.scope = w.frame.scope) && decide (w.world.snapshot = w.frame.snapshot) &&
  decide (w.world.timeDomain = w.frame.timeDomain)

theorem world_frame_check_exact (w : FramedWorld) :
    worldFrameCheck w = true ↔ WorldFrameAligned w := by
  have fields : WorldFrameAligned w ↔ w.world.profile = w.frame.profile ∧
      w.world.context = w.frame.context ∧ w.world.scope = w.frame.scope ∧
      w.world.snapshot = w.frame.snapshot ∧ w.world.timeDomain = w.frame.timeDomain := by
    constructor
    · intro h; exact ⟨h.profile, h.context, h.scope, h.snapshot, h.timeDomain⟩
    · rintro ⟨a,b,c,d,e⟩; exact ⟨a,b,c,d,e⟩
  rw [fields]
  simp only [worldFrameCheck, Bool.and_eq_true, decide_eq_true_eq, and_assoc]

structure Joined (w : FramedWorld) (projected : Projected) (claim : Claim) : Prop where
  addresses : CandidateIntentAddressing.Addresses w.world claim
  worldFrame : WorldFrameAligned w
  projection : claim.resolution = projected.resolution
  fullFrame : claim.selection.frame = w.frame

def joinCheck (w : FramedWorld) (projected : Projected) (claim : Claim) : Bool :=
  CandidateIntentAddressing.Checker.check w.world claim && worldFrameCheck w &&
    decide (claim.resolution = projected.resolution) && decide (claim.selection.frame = w.frame)

theorem join_check_exact (w : FramedWorld) (projected : Projected) (claim : Claim) :
    joinCheck w projected claim = true ↔ Joined w projected claim := by
  simp only [joinCheck, Bool.and_eq_true, CandidateIntentAddressing.Checker.check_exact,
    world_frame_check_exact, decide_eq_true_eq]
  constructor
  · rintro ⟨⟨⟨a,b⟩,c⟩,d⟩; exact ⟨a,b,c,d⟩
  · intro h; exact ⟨⟨⟨h.addresses,h.worldFrame⟩,h.projection⟩,h.fullFrame⟩

theorem joined_epoch_exact (w : FramedWorld) (projected : Projected) (claim : Claim)
    (joined : Joined w projected claim) : claim.selection.frame.epoch = w.frame.epoch :=
  congrArg Frame.epoch joined.fullFrame

theorem wrong_epoch_refuses (w : FramedWorld) (projected : Projected) (claim : Claim)
    (wrong : claim.selection.frame.epoch ≠ w.frame.epoch) : joinCheck w projected claim = false := by
  have notJoined : ¬ Joined w projected claim := fun joined => wrong (joined_epoch_exact w projected claim joined)
  cases checked : joinCheck w projected claim with
  | false => rfl
  | true => exact False.elim (notJoined ((join_check_exact w projected claim).mp checked))

theorem different_resolution_refuses (w : FramedWorld) (projected : Projected) (claim : Claim)
    (wrong : claim.resolution ≠ projected.resolution) : joinCheck w projected claim = false := by
  cases checked : joinCheck w projected claim with
  | false => rfl
  | true => exact False.elim (wrong ((join_check_exact w projected claim).mp checked).projection)

#print axioms world_frame_check_exact
#print axioms join_check_exact
#print axioms joined_epoch_exact
#print axioms wrong_epoch_refuses
#print axioms different_resolution_refuses
end RelationalSuccessor.CandidateIntentSourceContract
