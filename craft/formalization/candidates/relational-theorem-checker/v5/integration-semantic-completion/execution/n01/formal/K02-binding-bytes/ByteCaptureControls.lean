import OriginalByteControls

import ScalarConversionControls

set_option autoImplicit false

set_option maxRecDepth 65536

set_option maxHeartbeats 10000000

namespace RelationalSuccessor.CandidateBindingBytes.Controls

def resolutionEnvelope : CandidateBindingCapture.Envelope := ⟨resolutionBytes,2621,resolutionExpected.ownerReview,"uncomputed fixture digest"⟩

def resolutionPrepared : CandidateBindingCapture.Prepared CandidateIntentAddressing.Resolution := ⟨resolutionExpected,resolutionEnvelope⟩

def resolutionStage : CandidateBindingCapture.CatalogStage CandidateIntentAddressing.Resolution := ⟨resolutionExpected.body.frame,resolutionEnvelope.digestProfile,[resolutionPrepared],[resolutionPrepared]⟩

theorem resolution_original_capture_accepts : prepareBytes CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution resolutionExpected.body.frame resolutionEnvelope = some resolutionPrepared := by

  apply (prepare_bytes_exact CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution resolutionExpected.body.frame resolutionEnvelope resolutionPrepared).mpr
  apply (prepared_bytes_components CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution resolutionExpected.body.frame resolutionEnvelope resolutionPrepared).mpr
  exact ⟨(CandidateBindingCapture.envelope_check_exact resolutionEnvelope).mp (by decide),
    (record_bytes_exact CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution resolutionBytes resolutionExpected).mp original_resolution_bytes_accept,rfl,rfl⟩

theorem resolution_original_capture_outcome : classifyCaptureBytes CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution resolutionExpected.body.frame resolutionEnvelope = .prepared resolutionPrepared := by

  exact (prepared_outcome_matches_entrypoint CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution resolutionExpected.body.frame resolutionEnvelope resolutionPrepared).mpr resolution_original_capture_accepts

theorem resolution_original_entry_bytes_retained : resolutionPrepared.entry.content = resolutionBytes := by

  rfl

theorem resolution_original_catalog_accepts : prepareCatalogBytes CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution (fun value => value.ref.key) resolutionExpected.body.frame resolutionEnvelope.digestProfile [resolutionEnvelope] [resolutionEnvelope] = some resolutionStage := by

  simp only [prepareCatalogBytes,prepareManyBytes,resolution_original_capture_accepts]
  decide

theorem resolution_stale_frame_outcome : classifyCaptureBytes CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution { resolutionExpected.body.frame with epoch := 43 } resolutionEnvelope = .staleFrame resolutionExpected := by

  apply (stale_frame_outcome_exact CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution { resolutionExpected.body.frame with epoch := 43 } resolutionEnvelope resolutionExpected).mpr
  exact ⟨(CandidateBindingCapture.envelope_check_exact resolutionEnvelope).mp (by decide),
    (record_bytes_exact CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution resolutionBytes resolutionExpected).mp original_resolution_bytes_accept,by decide⟩

theorem resolution_wrong_length_outcome : classifyCaptureBytes CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution resolutionExpected.body.frame { resolutionEnvelope with byteLength := 2622 } = .invalidEnvelope := by

  apply (invalid_envelope_outcome_exact CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution resolutionExpected.body.frame { resolutionEnvelope with byteLength := 2622 }).mpr
  intro meaning
  have impossible := meaning.length
  change 2622 = 2621 at impossible
  omega

theorem resolution_old_AST_interface_accepts_unparsed_bytes : CandidateBindingCapture.prepare CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution resolutionExpected.body.frame { resolutionEnvelope with content := [1,2],byteLength := 2 } resolutionAst = some { resolutionPrepared with envelope := { resolutionEnvelope with content := [1,2],byteLength := 2 } } := by

  decide

theorem resolution_new_byte_interface_refuses_unparsed_bytes : prepareBytes CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution resolutionExpected.body.frame { resolutionEnvelope with content := [1,2],byteLength := 2 } = none := by

  rfl

theorem resolution_unsupported_scalar_outcome : classifyRecordBytes CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution [34,92,117,100,56,48,48,34] = .unsupportedScalar (.string [55296]) := by

  simp only [classifyRecordBytes,CandidateScalarConversion.escaped_unpaired_is_unsupported]

theorem resolution_malformed_UTF8_outcome : classifyRecordBytes CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution [34,255,34] = .invalidSyntax := by

  simp only [classifyRecordBytes,CandidateScalarConversion.malformed_utf8_is_invalid]

theorem resolution_supported_null_is_invalid_record : classifyRecordBytes CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution [110,117,108,108] = .invalidRecord .null := by

  have parsed : CandidateJsonParser.parseDocumentBytes [110,117,108,108] = some CandidateJsonBytes.RawValue.null := by rfl
  simp only [classifyRecordBytes,CandidateScalarConversion.classifyBytes,parsed,CandidateScalarConversion.convertValue]
  rfl

def roleEnvelope : CandidateBindingCapture.Envelope := ⟨roleBytes,1848,roleExpected.ownerReview,"uncomputed fixture digest"⟩

def rolePrepared : CandidateBindingCapture.Prepared CandidateIntentAddressing.Role := ⟨roleExpected,roleEnvelope⟩

def roleStage : CandidateBindingCapture.CatalogStage CandidateIntentAddressing.Role := ⟨roleExpected.body.frame,roleEnvelope.digestProfile,[rolePrepared],[rolePrepared]⟩

theorem role_original_capture_accepts : prepareBytes CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role roleExpected.body.frame roleEnvelope = some rolePrepared := by

  apply (prepare_bytes_exact CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role roleExpected.body.frame roleEnvelope rolePrepared).mpr
  apply (prepared_bytes_components CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role roleExpected.body.frame roleEnvelope rolePrepared).mpr
  exact ⟨(CandidateBindingCapture.envelope_check_exact roleEnvelope).mp (by decide),
    (record_bytes_exact CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role roleBytes roleExpected).mp original_role_bytes_accept,rfl,rfl⟩

theorem role_original_capture_outcome : classifyCaptureBytes CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role roleExpected.body.frame roleEnvelope = .prepared rolePrepared := by

  exact (prepared_outcome_matches_entrypoint CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role roleExpected.body.frame roleEnvelope rolePrepared).mpr role_original_capture_accepts

theorem role_original_entry_bytes_retained : rolePrepared.entry.content = roleBytes := by

  rfl

theorem role_original_catalog_accepts : prepareCatalogBytes CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role (fun value => value.ref.key) roleExpected.body.frame roleEnvelope.digestProfile [roleEnvelope] [roleEnvelope] = some roleStage := by

  simp only [prepareCatalogBytes,prepareManyBytes,role_original_capture_accepts]
  decide

theorem role_stale_frame_outcome : classifyCaptureBytes CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role { roleExpected.body.frame with epoch := 43 } roleEnvelope = .staleFrame roleExpected := by

  apply (stale_frame_outcome_exact CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role { roleExpected.body.frame with epoch := 43 } roleEnvelope roleExpected).mpr
  exact ⟨(CandidateBindingCapture.envelope_check_exact roleEnvelope).mp (by decide),
    (record_bytes_exact CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role roleBytes roleExpected).mp original_role_bytes_accept,by decide⟩

theorem role_wrong_length_outcome : classifyCaptureBytes CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role roleExpected.body.frame { roleEnvelope with byteLength := 1849 } = .invalidEnvelope := by

  apply (invalid_envelope_outcome_exact CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role roleExpected.body.frame { roleEnvelope with byteLength := 1849 }).mpr
  intro meaning
  have impossible := meaning.length
  change 1849 = 1848 at impossible
  omega

theorem role_old_AST_interface_accepts_unparsed_bytes : CandidateBindingCapture.prepare CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role roleExpected.body.frame { roleEnvelope with content := [1,2],byteLength := 2 } roleAst = some { rolePrepared with envelope := { roleEnvelope with content := [1,2],byteLength := 2 } } := by

  decide

theorem role_new_byte_interface_refuses_unparsed_bytes : prepareBytes CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role roleExpected.body.frame { roleEnvelope with content := [1,2],byteLength := 2 } = none := by

  rfl

theorem role_unsupported_scalar_outcome : classifyRecordBytes CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role [34,92,117,100,56,48,48,34] = .unsupportedScalar (.string [55296]) := by

  simp only [classifyRecordBytes,CandidateScalarConversion.escaped_unpaired_is_unsupported]

theorem role_malformed_UTF8_outcome : classifyRecordBytes CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role [34,255,34] = .invalidSyntax := by

  simp only [classifyRecordBytes,CandidateScalarConversion.malformed_utf8_is_invalid]

theorem role_supported_null_is_invalid_record : classifyRecordBytes CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role [110,117,108,108] = .invalidRecord .null := by

  have parsed : CandidateJsonParser.parseDocumentBytes [110,117,108,108] = some CandidateJsonBytes.RawValue.null := by rfl
  simp only [classifyRecordBytes,CandidateScalarConversion.classifyBytes,parsed,CandidateScalarConversion.convertValue]
  rfl

#print axioms resolution_original_capture_accepts

#print axioms resolution_original_capture_outcome

#print axioms resolution_original_entry_bytes_retained

#print axioms resolution_original_catalog_accepts

#print axioms resolution_stale_frame_outcome

#print axioms resolution_wrong_length_outcome

#print axioms resolution_old_AST_interface_accepts_unparsed_bytes

#print axioms resolution_new_byte_interface_refuses_unparsed_bytes

#print axioms resolution_unsupported_scalar_outcome

#print axioms resolution_malformed_UTF8_outcome

#print axioms resolution_supported_null_is_invalid_record

#print axioms role_original_capture_accepts

#print axioms role_original_capture_outcome

#print axioms role_original_entry_bytes_retained

#print axioms role_original_catalog_accepts

#print axioms role_stale_frame_outcome

#print axioms role_wrong_length_outcome

#print axioms role_old_AST_interface_accepts_unparsed_bytes

#print axioms role_new_byte_interface_refuses_unparsed_bytes

#print axioms role_unsupported_scalar_outcome

#print axioms role_malformed_UTF8_outcome

#print axioms role_supported_null_is_invalid_record

end RelationalSuccessor.CandidateBindingBytes.Controls
