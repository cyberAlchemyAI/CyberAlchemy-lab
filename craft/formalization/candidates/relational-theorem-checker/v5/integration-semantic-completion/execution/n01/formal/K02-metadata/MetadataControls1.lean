import MetadataFixture

set_option autoImplicit false
namespace RelationalSuccessor.CandidateCapturedMetadata.Controls
open RelationalSuccessor
open RelationalSuccessor.CandidateCapturedMetadata
open RelationalSuccessor.CandidateCapturedMetadata.Examples

def single (r : Receipt) : Context :=
  { context with records := [r], roots := [r], identities := [r.identity], owners := [r.owner], scopes := [r.scope] }

def alteredFrame : Frame := { frame with epoch := frame.epoch + 1 }
def otherRef : RevisionRef := revision "other-source"

theorem invalid_single_refuses (r : Receipt) (invalid : ¬ ReceiptMeaning (single r) r) :
    resolve (single r) frame sourceRef = none := by
  apply invalid_context_refuses
  intro valid
  exact invalid (valid.completeRecords r (by simp [single]))

def wrong_receipt_frame : Receipt := { receipt with frame := alteredFrame }
theorem wrong_receipt_frame_refuses : resolve (single wrong_receipt_frame) frame sourceRef = none := by
  apply invalid_single_refuses
  intro meaning
  have failed := meaning.frame
  have different : ¬ (wrong_receipt_frame.frame = context.frame) := by decide
  exact different (by simpa only [single] using failed)

def wrong_schema : Receipt := { receipt with schema := otherRef }
theorem wrong_schema_refuses : resolve (single wrong_schema) frame sourceRef = none := by
  apply invalid_single_refuses
  intro meaning
  have failed := meaning.schema
  have different : ¬ (wrong_schema.schema = context.schema) := by decide
  exact different (by simpa only [single] using failed)

def wrong_source_kind : Receipt := { receipt with artifact := { artifact with sourceKind := "other-kind" } }
theorem wrong_source_kind_refuses : resolve (single wrong_source_kind) frame sourceRef = none := by
  apply invalid_single_refuses
  intro meaning
  have failed := meaning.sourceKind
  have different : ¬ (wrong_source_kind.artifact.sourceKind = wrong_source_kind.artifact.body.kind) := by decide
  exact different (by simpa only [single] using failed)

def wrong_identity_frame : Receipt := { receipt with identity := { identity with frame := alteredFrame } }
theorem wrong_identity_frame_refuses : resolve (single wrong_identity_frame) frame sourceRef = none := by
  apply invalid_single_refuses
  intro meaning
  have failed := meaning.identityFrame
  have different : ¬ (wrong_identity_frame.identity.frame = wrong_identity_frame.frame) := by decide
  exact different (by simpa only [single] using failed)

def wrong_identity_source : Receipt := { receipt with identity := { identity with source := otherRef } }
theorem wrong_identity_source_refuses : resolve (single wrong_identity_source) frame sourceRef = none := by
  apply invalid_single_refuses
  intro meaning
  have failed := meaning.identitySource
  have different : ¬ (wrong_identity_source.identity.source = wrong_identity_source.artifact.ref) := by decide
  exact different (by simpa only [single] using failed)

def wrong_identity_token : Receipt := { receipt with identity := { identity with token := "wrong-node" } }
theorem wrong_identity_token_refuses : resolve (single wrong_identity_token) frame sourceRef = none := by
  apply invalid_single_refuses
  intro meaning
  have failed := meaning.identityToken
  have different : ¬ (wrong_identity_token.identity.token = wrong_identity_token.artifact.body.node_id) := by decide
  exact different (by simpa only [single] using failed)

def wrong_owner_frame : Receipt := { receipt with owner := { owner with frame := alteredFrame } }
theorem wrong_owner_frame_refuses : resolve (single wrong_owner_frame) frame sourceRef = none := by
  apply invalid_single_refuses
  intro meaning
  have failed := meaning.ownerFrame
  have different : ¬ (wrong_owner_frame.owner.frame = wrong_owner_frame.frame) := by decide
  exact different (by simpa only [single] using failed)

def wrong_owner_source : Receipt := { receipt with owner := { owner with source := otherRef } }
theorem wrong_owner_source_refuses : resolve (single wrong_owner_source) frame sourceRef = none := by
  apply invalid_single_refuses
  intro meaning
  have failed := meaning.ownerSource
  have different : ¬ (wrong_owner_source.owner.source = wrong_owner_source.artifact.ref) := by decide
  exact different (by simpa only [single] using failed)

def wrong_owner_token : Receipt := { receipt with owner := { owner with token := "wrong-owner" } }
theorem wrong_owner_token_refuses : resolve (single wrong_owner_token) frame sourceRef = none := by
  apply invalid_single_refuses
  intro meaning
  have failed := meaning.ownerToken
  have different : ¬ (wrong_owner_token.owner.token = wrong_owner_token.artifact.body.owner_ref) := by decide
  exact different (by simpa only [single] using failed)

def wrong_owner_scope : Receipt := { receipt with owner := { owner with scope := otherRef } }
theorem wrong_owner_scope_refuses : resolve (single wrong_owner_scope) frame sourceRef = none := by
  apply invalid_single_refuses
  intro meaning
  have failed := meaning.ownerScope
  have different : ¬ (wrong_owner_scope.owner.scope = wrong_owner_scope.frame.scope) := by decide
  exact different (by simpa only [single] using failed)

def wrong_scope_frame : Receipt := { receipt with scope := { scope with frame := alteredFrame } }
theorem wrong_scope_frame_refuses : resolve (single wrong_scope_frame) frame sourceRef = none := by
  apply invalid_single_refuses
  intro meaning
  have failed := meaning.scopeFrame
  have different : ¬ (wrong_scope_frame.scope.frame = wrong_scope_frame.frame) := by decide
  exact different (by simpa only [single] using failed)

def wrong_scope_source : Receipt := { receipt with scope := { scope with source := otherRef } }
theorem wrong_scope_source_refuses : resolve (single wrong_scope_source) frame sourceRef = none := by
  apply invalid_single_refuses
  intro meaning
  have failed := meaning.scopeSource
  have different : ¬ (wrong_scope_source.scope.source = wrong_scope_source.artifact.ref) := by decide
  exact different (by simpa only [single] using failed)

def wrong_scope_token : Receipt := { receipt with scope := { scope with token := "wrong-scope" } }
theorem wrong_scope_token_refuses : resolve (single wrong_scope_token) frame sourceRef = none := by
  apply invalid_single_refuses
  intro meaning
  have failed := meaning.scopeToken
  have different : ¬ (wrong_scope_token.scope.token = wrong_scope_token.artifact.body.scope_ref) := by decide
  exact different (by simpa only [single] using failed)

def wrong_scope_value : Receipt := { receipt with scope := { scope with scope := otherRef } }
theorem wrong_scope_value_refuses : resolve (single wrong_scope_value) frame sourceRef = none := by
  apply invalid_single_refuses
  intro meaning
  have failed := meaning.scopeValue
  have different : ¬ (wrong_scope_value.scope.scope = wrong_scope_value.frame.scope) := by decide
  exact different (by simpa only [single] using failed)

def wrong_owner_join : Receipt := { receipt with scope := { scope with ownerBinding := otherRef } }
theorem wrong_owner_join_refuses : resolve (single wrong_owner_join) frame sourceRef = none := by
  apply invalid_single_refuses
  intro meaning
  have failed := meaning.ownerJoin
  have different : ¬ (wrong_owner_join.scope.ownerBinding = wrong_owner_join.owner.ref) := by decide
  exact different (by simpa only [single] using failed)

def missing_root : Context := { context with roots := [] }
theorem missing_root_refuses : resolve missing_root frame sourceRef = none := by
  apply invalid_context_refuses
  intro valid
  have meaning := valid.completeRecords receipt (by simp [missing_root, context])
  simpa [missing_root] using meaning.issued

def missing_identity : Context := { context with identities := [] }
theorem missing_identity_refuses : resolve missing_identity frame sourceRef = none := by
  apply invalid_context_refuses
  intro valid
  have meaning := valid.completeRecords receipt (by simp [missing_identity, context])
  simpa [missing_identity] using meaning.identityOwned

def missing_owner : Context := { context with owners := [] }
theorem missing_owner_refuses : resolve missing_owner frame sourceRef = none := by
  apply invalid_context_refuses
  intro valid
  have meaning := valid.completeRecords receipt (by simp [missing_owner, context])
  simpa [missing_owner] using meaning.ownerOwned

def missing_scope : Context := { context with scopes := [] }
theorem missing_scope_refuses : resolve missing_scope frame sourceRef = none := by
  apply invalid_context_refuses
  intro valid
  have meaning := valid.completeRecords receipt (by simp [missing_scope, context])
  simpa [missing_scope] using meaning.scopeOwned

#print axioms invalid_single_refuses
#print axioms wrong_receipt_frame_refuses
#print axioms wrong_schema_refuses
#print axioms wrong_source_kind_refuses
#print axioms wrong_identity_frame_refuses
#print axioms wrong_identity_source_refuses
#print axioms wrong_identity_token_refuses
#print axioms wrong_owner_frame_refuses
#print axioms wrong_owner_source_refuses
#print axioms wrong_owner_token_refuses
#print axioms wrong_owner_scope_refuses
#print axioms wrong_scope_frame_refuses
#print axioms wrong_scope_source_refuses
#print axioms wrong_scope_token_refuses
#print axioms wrong_scope_value_refuses
#print axioms wrong_owner_join_refuses
#print axioms missing_root_refuses
#print axioms missing_identity_refuses
#print axioms missing_owner_refuses
#print axioms missing_scope_refuses
end RelationalSuccessor.CandidateCapturedMetadata.Controls
