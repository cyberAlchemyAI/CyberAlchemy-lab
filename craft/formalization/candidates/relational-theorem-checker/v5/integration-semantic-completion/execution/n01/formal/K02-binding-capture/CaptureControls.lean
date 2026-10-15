import CaptureCatalog
set_option autoImplicit false
namespace RelationalSuccessor.CandidateBindingCapture.Controls
open RelationalSuccessor
open RelationalSuccessor.CandidateBindingCapture
open RelationalSuccessor.CandidateBindingRecords
open RelationalSuccessor.CandidateBindingAst
open RelationalSuccessor.CandidateIntentAddressing (Resolution Role)

def resolutionAst : J := (.object [("schema_version", (.string "cyberalchemy-lab-intent-resolution-qualifier-binding/candidate-v1")), ("binding_revision_key", (.object [("owner", (.string "fixture")), ("artifact", (.string "binding")), ("revision", (.string "1"))])), ("kind", (.string "intent-resolution-qualifier-binding")), ("body", (.object [("token", (.string "resolution:1")), ("target", (.object [("ref", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "ref")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("scope", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "scope")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("intent", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "intent")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("ownerDecision", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "ownerDecision")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("selectedSubjects", (.array [(.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "subject")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])])), ("excludedSubjects", (.array [])), ("satisfactionTests", (.array []))])), ("frame", (.object [("profile", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "profile")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("subject", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "subject")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("target", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "target")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("context", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "context")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("scope", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "scope")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("snapshot", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "snapshot")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("epoch", (.number "42")), ("timeDomain", (.string "fixture-epoch"))]))])), ("owner_review_ref", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "review")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))]))])
def resolutionRecord : Record Resolution := ⟨"cyberalchemy-lab-intent-resolution-qualifier-binding/candidate-v1",⟨"fixture","binding","1"⟩,"intent-resolution-qualifier-binding",⟨"resolution:1",⟨⟨⟨"fixture","ref","1"⟩,"fixture-digest"⟩,⟨⟨"fixture","scope","1"⟩,"fixture-digest"⟩,⟨⟨"fixture","intent","1"⟩,"fixture-digest"⟩,⟨⟨"fixture","ownerDecision","1"⟩,"fixture-digest"⟩,[⟨⟨"fixture","subject","1"⟩,"fixture-digest"⟩],[],[]⟩,⟨⟨⟨"fixture","profile","1"⟩,"fixture-digest"⟩,⟨⟨"fixture","subject","1"⟩,"fixture-digest"⟩,⟨⟨"fixture","target","1"⟩,"fixture-digest"⟩,⟨⟨"fixture","context","1"⟩,"fixture-digest"⟩,⟨⟨"fixture","scope","1"⟩,"fixture-digest"⟩,⟨⟨"fixture","snapshot","1"⟩,"fixture-digest"⟩,42,"fixture-epoch"⟩⟩,⟨⟨"fixture","review","1"⟩,"fixture-digest"⟩⟩
def resolutionFrame : Frame := resolutionRecord.body.frame
def resolutionEnvelope : Envelope := ⟨[1,2],2,resolutionRecord.ownerReview,"synthetic-claimed-digest"⟩
def resolutionPrepared : Prepared Resolution := ⟨resolutionRecord,resolutionEnvelope⟩
def resolutionInput : Input := ⟨resolutionAst,resolutionEnvelope⟩
def resolutionStage : CatalogStage Resolution := ⟨resolutionFrame,resolutionEnvelope.digestProfile,[resolutionPrepared],[resolutionPrepared]⟩

theorem resolution_prepare_accepts : prepareResolution resolutionFrame resolutionEnvelope resolutionAst = some resolutionPrepared := by decide

theorem resolution_wrong_length_refuses : prepareResolution resolutionFrame { resolutionEnvelope with byteLength := 3 } resolutionAst = none := by decide

theorem resolution_empty_digest_refuses : prepareResolution resolutionFrame { resolutionEnvelope with digest := "" } resolutionAst = none := by decide

theorem resolution_empty_profile_digest_refuses : prepareResolution resolutionFrame { resolutionEnvelope with digestProfile := { resolutionEnvelope.digestProfile with digest := "" } } resolutionAst = none := by decide

theorem resolution_stale_epoch_refuses : prepareResolution { resolutionFrame with epoch := 43 } resolutionEnvelope resolutionAst = none := by decide

theorem resolution_null_AST_refuses : prepareResolution resolutionFrame resolutionEnvelope .null = none := by decide

theorem resolution_catalog_stage_accepts : prepareResolutionCatalog resolutionFrame resolutionEnvelope.digestProfile [resolutionInput] [resolutionInput] = some resolutionStage := by decide

theorem resolution_missing_root_refuses : prepareResolutionCatalog resolutionFrame resolutionEnvelope.digestProfile [resolutionInput] [] = none := by decide

theorem resolution_wrong_requested_profile_refuses : prepareResolutionCatalog resolutionFrame { resolutionEnvelope.digestProfile with digest := "different-profile" } [resolutionInput] [resolutionInput] = none := by decide

theorem resolution_mixed_profiles_refuse : prepareResolutionCatalog resolutionFrame resolutionEnvelope.digestProfile [resolutionInput,{ resolutionInput with envelope := { resolutionEnvelope with digestProfile := { resolutionEnvelope.digestProfile with digest := "different-profile" } } }] [resolutionInput,{ resolutionInput with envelope := { resolutionEnvelope with digestProfile := { resolutionEnvelope.digestProfile with digest := "different-profile" } } }] = none := by decide

theorem resolution_identical_retry_accepts : prepareResolutionCatalog resolutionFrame resolutionEnvelope.digestProfile [resolutionInput,resolutionInput] [resolutionInput] = some { resolutionStage with records := [resolutionPrepared,resolutionPrepared] } := by decide

theorem resolution_different_bytes_conflict_refuses : prepareResolutionCatalog resolutionFrame resolutionEnvelope.digestProfile [resolutionInput,{ resolutionInput with envelope := { resolutionEnvelope with content := [3,4] } }] [resolutionInput,{ resolutionInput with envelope := { resolutionEnvelope with content := [3,4] } }] = none := by decide

theorem resolution_unchanged_length_is_not_byte_authentication : prepareResolution resolutionFrame { resolutionEnvelope with content := [3,4] } resolutionAst = some { resolutionPrepared with envelope := { resolutionEnvelope with content := [3,4] } } := by decide

theorem resolution_digest_label_is_not_computation : prepareResolution resolutionFrame { resolutionEnvelope with digest := "uncomputed-label" } resolutionAst = some { resolutionPrepared with envelope := { resolutionEnvelope with digest := "uncomputed-label" } } := by decide

def resolutionUnparsedPolicy : Policies Resolution := ⟨(fun _ _ => False),(fun _ _ _ => False),(fun _ _ => False),(fun _ _ _ _ => False),(fun _ _ => False)⟩

theorem resolution_prepared_syntax_is_not_authentic_capture : ¬ CaptureMeaning resolutionUnparsedPolicy resolutionVersion resolutionKind resolution resolutionFrame resolutionEnvelope resolutionAst resolutionPrepared := by
  apply unparsed_bytes_prevent_capture
  exact fun impossible => impossible

theorem resolution_stage_retains_profile_and_version : resolutionStage.records = [resolutionPrepared] ∧ resolutionPrepared.envelope.digestProfile = resolutionEnvelope.digestProfile ∧ resolutionPrepared.record.schemaVersion = resolutionVersion := by decide

def roleAst : J := (.object [("schema_version", (.string "cyberalchemy-lab-intent-addressing-role-binding/candidate-v1")), ("binding_revision_key", (.object [("owner", (.string "fixture")), ("artifact", (.string "binding")), ("revision", (.string "1"))])), ("kind", (.string "intent-addressing-role-binding")), ("body", (.object [("token", (.string "investigation")), ("target", (.object [("ref", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "role")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("code", (.string "investigation")), ("subjectKind", (.string "project"))])), ("frame", (.object [("profile", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "profile")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("subject", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "subject")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("target", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "target")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("context", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "context")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("scope", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "scope")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("snapshot", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "snapshot")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))])), ("epoch", (.number "42")), ("timeDomain", (.string "fixture-epoch"))]))])), ("owner_review_ref", (.object [("key", (.object [("owner", (.string "fixture")), ("artifact", (.string "review")), ("revision", (.string "1"))])), ("digest", (.string "fixture-digest"))]))])
def roleRecord : Record Role := ⟨"cyberalchemy-lab-intent-addressing-role-binding/candidate-v1",⟨"fixture","binding","1"⟩,"intent-addressing-role-binding",⟨"investigation",⟨⟨⟨"fixture","role","1"⟩,"fixture-digest"⟩,"investigation",.project⟩,⟨⟨⟨"fixture","profile","1"⟩,"fixture-digest"⟩,⟨⟨"fixture","subject","1"⟩,"fixture-digest"⟩,⟨⟨"fixture","target","1"⟩,"fixture-digest"⟩,⟨⟨"fixture","context","1"⟩,"fixture-digest"⟩,⟨⟨"fixture","scope","1"⟩,"fixture-digest"⟩,⟨⟨"fixture","snapshot","1"⟩,"fixture-digest"⟩,42,"fixture-epoch"⟩⟩,⟨⟨"fixture","review","1"⟩,"fixture-digest"⟩⟩
def roleFrame : Frame := roleRecord.body.frame
def roleEnvelope : Envelope := ⟨[1,2],2,roleRecord.ownerReview,"synthetic-claimed-digest"⟩
def rolePrepared : Prepared Role := ⟨roleRecord,roleEnvelope⟩
def roleInput : Input := ⟨roleAst,roleEnvelope⟩
def roleStage : CatalogStage Role := ⟨roleFrame,roleEnvelope.digestProfile,[rolePrepared],[rolePrepared]⟩

theorem role_prepare_accepts : prepareRole roleFrame roleEnvelope roleAst = some rolePrepared := by decide

theorem role_wrong_length_refuses : prepareRole roleFrame { roleEnvelope with byteLength := 3 } roleAst = none := by decide

theorem role_empty_digest_refuses : prepareRole roleFrame { roleEnvelope with digest := "" } roleAst = none := by decide

theorem role_empty_profile_digest_refuses : prepareRole roleFrame { roleEnvelope with digestProfile := { roleEnvelope.digestProfile with digest := "" } } roleAst = none := by decide

theorem role_stale_epoch_refuses : prepareRole { roleFrame with epoch := 43 } roleEnvelope roleAst = none := by decide

theorem role_null_AST_refuses : prepareRole roleFrame roleEnvelope .null = none := by decide

theorem role_catalog_stage_accepts : prepareRoleCatalog roleFrame roleEnvelope.digestProfile [roleInput] [roleInput] = some roleStage := by decide

theorem role_missing_root_refuses : prepareRoleCatalog roleFrame roleEnvelope.digestProfile [roleInput] [] = none := by decide

theorem role_wrong_requested_profile_refuses : prepareRoleCatalog roleFrame { roleEnvelope.digestProfile with digest := "different-profile" } [roleInput] [roleInput] = none := by decide

theorem role_mixed_profiles_refuse : prepareRoleCatalog roleFrame roleEnvelope.digestProfile [roleInput,{ roleInput with envelope := { roleEnvelope with digestProfile := { roleEnvelope.digestProfile with digest := "different-profile" } } }] [roleInput,{ roleInput with envelope := { roleEnvelope with digestProfile := { roleEnvelope.digestProfile with digest := "different-profile" } } }] = none := by decide

theorem role_identical_retry_accepts : prepareRoleCatalog roleFrame roleEnvelope.digestProfile [roleInput,roleInput] [roleInput] = some { roleStage with records := [rolePrepared,rolePrepared] } := by decide

theorem role_different_bytes_conflict_refuses : prepareRoleCatalog roleFrame roleEnvelope.digestProfile [roleInput,{ roleInput with envelope := { roleEnvelope with content := [3,4] } }] [roleInput,{ roleInput with envelope := { roleEnvelope with content := [3,4] } }] = none := by decide

theorem role_unchanged_length_is_not_byte_authentication : prepareRole roleFrame { roleEnvelope with content := [3,4] } roleAst = some { rolePrepared with envelope := { roleEnvelope with content := [3,4] } } := by decide

theorem role_digest_label_is_not_computation : prepareRole roleFrame { roleEnvelope with digest := "uncomputed-label" } roleAst = some { rolePrepared with envelope := { roleEnvelope with digest := "uncomputed-label" } } := by decide

def roleUnparsedPolicy : Policies Role := ⟨(fun _ _ => False),(fun _ _ _ => False),(fun _ _ => False),(fun _ _ _ _ => False),(fun _ _ => False)⟩

theorem role_prepared_syntax_is_not_authentic_capture : ¬ CaptureMeaning roleUnparsedPolicy roleVersion roleKind role roleFrame roleEnvelope roleAst rolePrepared := by
  apply unparsed_bytes_prevent_capture
  exact fun impossible => impossible

theorem role_stage_retains_profile_and_version : roleStage.records = [rolePrepared] ∧ rolePrepared.envelope.digestProfile = roleEnvelope.digestProfile ∧ rolePrepared.record.schemaVersion = roleVersion := by decide

#print axioms resolution_prepare_accepts
#print axioms resolution_wrong_length_refuses
#print axioms resolution_empty_digest_refuses
#print axioms resolution_empty_profile_digest_refuses
#print axioms resolution_stale_epoch_refuses
#print axioms resolution_null_AST_refuses
#print axioms resolution_catalog_stage_accepts
#print axioms resolution_missing_root_refuses
#print axioms resolution_wrong_requested_profile_refuses
#print axioms resolution_mixed_profiles_refuse
#print axioms resolution_identical_retry_accepts
#print axioms resolution_different_bytes_conflict_refuses
#print axioms resolution_unchanged_length_is_not_byte_authentication
#print axioms resolution_digest_label_is_not_computation
#print axioms resolution_prepared_syntax_is_not_authentic_capture
#print axioms resolution_stage_retains_profile_and_version
#print axioms role_prepare_accepts
#print axioms role_wrong_length_refuses
#print axioms role_empty_digest_refuses
#print axioms role_empty_profile_digest_refuses
#print axioms role_stale_epoch_refuses
#print axioms role_null_AST_refuses
#print axioms role_catalog_stage_accepts
#print axioms role_missing_root_refuses
#print axioms role_wrong_requested_profile_refuses
#print axioms role_mixed_profiles_refuse
#print axioms role_identical_retry_accepts
#print axioms role_different_bytes_conflict_refuses
#print axioms role_unchanged_length_is_not_byte_authentication
#print axioms role_digest_label_is_not_computation
#print axioms role_prepared_syntax_is_not_authentic_capture
#print axioms role_stage_retains_profile_and_version
end RelationalSuccessor.CandidateBindingCapture.Controls
