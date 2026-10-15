import PipelineFixture

set_option autoImplicit false
namespace RelationalSuccessor.CandidateIntentSourcePipeline.Controls
open RelationalSuccessor
open RelationalSuccessor.CandidateIntentSourcePipeline
open RelationalSuccessor.CandidateIntentSourcePipeline.Fixture

theorem changed_bytes_refuse : run metadata payloads bindings world [0] sourceAst qualifierAst claim = none := by
  apply no_meaning_refuses
  intro out meaning
  have receiptExact : out.projected.receipt = CandidateCapturedMetadata.Examples.receipt := by
    simpa [metadata, CandidateCapturedMetadata.Examples.context] using meaning.source.1.metadata.owned
  have byteEqual := meaning.source.1.bytes
  rw [receiptExact] at byteEqual
  have heads := congrArg (fun xs : List UInt8 => xs.head?) byteEqual
  have different : CandidateCapturedMetadata.Examples.receipt.artifact.content.head? ≠ ([0] : List UInt8).head? := by decide
  exact different heads

theorem malformed_source_AST_refuses : run metadata payloads bindings world bytes (.null) qualifierAst claim = none := by
  apply no_meaning_refuses
  intro out meaning
  have parsed := (CandidateJsonSource.decode_record_exact _ _).mpr meaning.source.1.ast
  have malformed : CandidateJsonSource.decodeRecord .null = none := rfl
  rw [malformed] at parsed
  cases parsed

def missingRoleRoot : Bindings := { bindings with roles := { bindings.roles with roots := [] } }
theorem missing_owned_role_root_refuses : run metadata payloads missingRoleRoot world bytes sourceAst qualifierAst claim = none := by
  apply no_meaning_refuses
  intro out meaning
  rcases meaning.joined.role.binding with ⟨entry, member, _, _⟩
  have issued := meaning.joined.role.valid.issued entry member
  simp [missingRoleRoot] at issued

def staleClaim : Claim := CandidateIntentSourceContract.Fixture.staleClaim
def staleWorld : FramedWorld := CandidateIntentSourceContract.Fixture.staleFramed
theorem stale_selection_epoch_refuses : run metadata payloads bindings staleWorld bytes sourceAst qualifierAst staleClaim = none := by
  apply no_meaning_refuses
  intro out meaning
  have equal := congrArg Frame.epoch meaning.joined.joined.fullFrame
  have different : staleClaim.selection.frame.epoch ≠ staleWorld.frame.epoch := by decide
  exact different equal

#print axioms changed_bytes_refuse
#print axioms malformed_source_AST_refuses
#print axioms missing_owned_role_root_refuses
#print axioms stale_selection_epoch_refuses
end RelationalSuccessor.CandidateIntentSourcePipeline.Controls
