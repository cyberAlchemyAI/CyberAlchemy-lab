"""Generate byte capture/catalog regressions from kernel-checked original fixture results."""
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent

def run():
 lines=['import OriginalByteControls','import ScalarConversionControls','set_option autoImplicit false','set_option maxRecDepth 65536','set_option maxHeartbeats 10000000','namespace RelationalSuccessor.CandidateBindingBytes.Controls'];names=[]
 def theorem(name,statement,proof):
  names.append(name);lines.extend([f'theorem {name} : {statement} := by',proof])
 for kind,typ in [('resolution','CandidateIntentAddressing.Resolution'),('role','CandidateIntentAddressing.Role')]:
  k=kind;cap='CandidateBindingCapture';rec='CandidateBindingRecords';ast='CandidateBindingAst';version=f'{rec}.{k}Version';relation=f'{rec}.{k}Kind';target=f'{ast}.{k}';args=f'{version} {relation} {target}';frame=f'{k}Expected.body.frame';fixture=HERE.parent/f'K02-pipeline/schemas/{k}-binding.fixture.json';length=len(fixture.read_bytes())
  lines.extend([f'def {k}Envelope : {cap}.Envelope := ⟨{k}Bytes,{length},{k}Expected.ownerReview,"uncomputed fixture digest"⟩',f'def {k}Prepared : {cap}.Prepared {typ} := ⟨{k}Expected,{k}Envelope⟩',f'def {k}Stage : {cap}.CatalogStage {typ} := ⟨{frame},{k}Envelope.digestProfile,[{k}Prepared],[{k}Prepared]⟩'])
  theorem(k+'_original_capture_accepts',f'prepareBytes {args} {frame} {k}Envelope = some {k}Prepared',f'''  apply (prepare_bytes_exact {args} {frame} {k}Envelope {k}Prepared).mpr
  apply (prepared_bytes_components {args} {frame} {k}Envelope {k}Prepared).mpr
  exact ⟨({cap}.envelope_check_exact {k}Envelope).mp (by decide),
    (record_bytes_exact {args} {k}Bytes {k}Expected).mp original_{k}_bytes_accept,rfl,rfl⟩''')
  theorem(k+'_original_capture_outcome',f'classifyCaptureBytes {args} {frame} {k}Envelope = .prepared {k}Prepared',f'  exact (prepared_outcome_matches_entrypoint {args} {frame} {k}Envelope {k}Prepared).mpr {k}_original_capture_accepts')
  theorem(k+'_original_entry_bytes_retained',f'{k}Prepared.entry.content = {k}Bytes', '  rfl')
  theorem(k+'_original_catalog_accepts',f'prepareCatalogBytes {args} (fun value => value.ref.key) {frame} {k}Envelope.digestProfile [{k}Envelope] [{k}Envelope] = some {k}Stage',f'''  simp only [prepareCatalogBytes,prepareManyBytes,{k}_original_capture_accepts]
  decide''')
  theorem(k+'_stale_frame_outcome',f'classifyCaptureBytes {args} {{ {frame} with epoch := 43 }} {k}Envelope = .staleFrame {k}Expected',f'''  apply (stale_frame_outcome_exact {args} {{ {frame} with epoch := 43 }} {k}Envelope {k}Expected).mpr
  exact ⟨({cap}.envelope_check_exact {k}Envelope).mp (by decide),
    (record_bytes_exact {args} {k}Bytes {k}Expected).mp original_{k}_bytes_accept,by decide⟩''')
  theorem(k+'_wrong_length_outcome',f'classifyCaptureBytes {args} {frame} {{ {k}Envelope with byteLength := {length+1} }} = .invalidEnvelope',f'''  apply (invalid_envelope_outcome_exact {args} {frame} {{ {k}Envelope with byteLength := {length+1} }}).mpr
  intro meaning
  have impossible := meaning.length
  change {length+1} = {length} at impossible
  omega''')
  theorem(k+'_old_AST_interface_accepts_unparsed_bytes',f'{cap}.prepare {args} {frame} {{ {k}Envelope with content := [1,2],byteLength := 2 }} {k}Ast = some {{ {k}Prepared with envelope := {{ {k}Envelope with content := [1,2],byteLength := 2 }} }}','  decide')
  theorem(k+'_new_byte_interface_refuses_unparsed_bytes',f'prepareBytes {args} {frame} {{ {k}Envelope with content := [1,2],byteLength := 2 }} = none','  rfl')
  theorem(k+'_unsupported_scalar_outcome',f'classifyRecordBytes {args} [34,92,117,100,56,48,48,34] = .unsupportedScalar (.string [55296])',f'  simp only [classifyRecordBytes,CandidateScalarConversion.escaped_unpaired_is_unsupported]')
  theorem(k+'_malformed_UTF8_outcome',f'classifyRecordBytes {args} [34,255,34] = .invalidSyntax',f'  simp only [classifyRecordBytes,CandidateScalarConversion.malformed_utf8_is_invalid]')
  theorem(k+'_supported_null_is_invalid_record',f'classifyRecordBytes {args} [110,117,108,108] = .invalidRecord .null',f'''  have parsed : CandidateJsonParser.parseDocumentBytes [110,117,108,108] = some CandidateJsonBytes.RawValue.null := by rfl
  simp only [classifyRecordBytes,CandidateScalarConversion.classifyBytes,parsed,CandidateScalarConversion.convertValue]
  rfl''')
 lines += ['#print axioms '+name for name in names]+['end RelationalSuccessor.CandidateBindingBytes.Controls']
 (HERE/'ByteCaptureControls.lean').write_text('\n\n'.join(lines)+'\n')
 (HERE/'capture-control-index.json').write_text(json.dumps({'worked_control_declarations':len(names),'names':names,'method':'Kernel-checked exact original byte decode results, generic refinement application, explicit old-versus-new AST/byte regression and representation refusals','digest_labels_uncomputed':True,'profile_and_review_roots_synthetic':True,'authenticated_capture_proved':False,'inherited_discharges':0},indent=2)+'\n')
 print('Generated',len(names),'capture/catalog and refusal controls.')
if __name__=='__main__':run()
