"""Computed byte digests are oracle fixtures; identity/review/profile roots are synthetic."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[9]
def b(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def run():
 rows=[];defs=['import DigestCaptureCatalog','import ByteCaptureControls','import DigestControls',
 'set_option autoImplicit false','set_option maxRecDepth 65536','set_option maxHeartbeats 10000000',
 'namespace RelationalSuccessor.CandidateDigestCapture.Controls',
 'open CandidateBindingBytes.Controls (resolutionBytes resolutionExpected roleBytes roleExpected)',
 'def profile : CandidateDigest.Profile := ⟨resolutionExpected.ownerReview,"sha256-fips1804-2015","lowerhex64"⟩']
 for kind in ['resolution','role']:
  original=HERE.parent/'K02-pipeline/schemas'/f'{kind}-binding.fixture.json';data=original.read_bytes();digest=hashlib.sha256(data).hexdigest()
  rows.append({'kind':kind,'original_bytes':b(original),'byte_count':len(data),'computed_sha256':digest})
  defs += [f'def {kind}Capture : CandidateBindingCapture.Envelope := ⟨{kind}Bytes,{len(data)},profile.ref,{json.dumps(digest)}⟩',
   f'def {kind}Frame : Frame := {kind}Expected.body.frame']
 # These closed controls stop at explicit pre-parsing guards; positive complete paths are runtime controls.
 names=[]
 for kind in ['resolution','role']:
  version='CandidateBindingRecords.'+kind+'Version';recordkind='CandidateBindingRecords.'+kind+'Kind';target='CandidateBindingAst.'+kind;frame=kind+'Frame';capture=kind+'Capture';n=next(r['byte_count'] for r in rows if r['kind']==kind)
  for name,cap,budget,result in [
   ('wrong_count',f'{{{capture} with byteLength:={n+1}}}',n,'invalidEnvelope'),
   ('wrong_profile',f'{{{capture} with digestProfile:={{profile.ref with digest:="other"}}}}',n,'digestRefused .unsupportedProfile'),
   ('budget',capture,n-1,'digestRefused .byteBudgetExceeded')]:
   theorem=kind+'_'+name+'_refused';names.append(theorem)
   args=f'profile {budget} {version} {recordkind} {target} {frame} {cap}'
   if name=='wrong_count':proof=f'by\n  apply (checked_invalid_envelope_exact {args}).mpr\n  rw [←CandidateBindingCapture.envelope_check_exact]\n  decide'
   elif name=='wrong_profile':proof=f'by\n  apply (checked_profile_refusal_exact {args}).mpr\n  exact ⟨(CandidateBindingCapture.envelope_check_exact _).mp (by decide),by decide⟩'
   else:proof=f'by\n  apply (checked_budget_refusal_exact {args}).mpr\n  exact ⟨(CandidateBindingCapture.envelope_check_exact _).mp (by decide),by decide,by decide,by decide⟩'
   defs.append(f'theorem {theorem} : classifyCheckedCapture {args}=.{result} := {proof}')
  theorem=kind+'_aggregate_budget_refused';names.append(theorem)
  defs.append(f'theorem {theorem} : prepare{kind.title()}CatalogDigest profile ⟨{n},{2*n-1},2⟩ {frame} [{capture}] [{capture}]=none := by decide')
  theorem=kind+'_count_budget_refused';names.append(theorem)
  defs.append(f'theorem {theorem} : prepare{kind.title()}CatalogDigest profile ⟨{n},{2*n},1⟩ {frame} [{capture}] [{capture}]=none := by decide')
 names.append('unsupported_empty_catalog_refused')
 defs.append('theorem unsupported_empty_catalog_refused : prepareRoleCatalogDigest {profile with algorithm:="sha1"} ⟨0,0,0⟩ roleFrame [] []=none := by decide')
 names.append('valid_digest_does_not_make_empty_bytes_a_record')
 defs += ['def emptyCapture : CandidateBindingCapture.Envelope := ⟨[],0,profile.ref,CandidateDigest.Controls.emptyDigest⟩',
 '''theorem valid_digest_does_not_make_empty_bytes_a_record :
    classifyCheckedCapture profile 0 CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind
      CandidateBindingAst.role roleFrame emptyCapture=.byteStage (.recordRefused .invalidSyntax) := by
  apply (checked_syntax_exact profile 0 _ _ _ roleFrame emptyCapture).mpr
  refine ⟨(CandidateBindingCapture.envelope_check_exact emptyCapture).mp (by decide),?_,?_⟩
  · exact ⟨by decide,by decide,by decide,CandidateDigest.Controls.empty_vector_meaning⟩
  · exact (CandidateJsonCompleteness.byte_document_none_iff_no_meaning []).mp rfl''']
 defs += ['#print axioms '+name for name in names]+['end RelationalSuccessor.CandidateDigestCapture.Controls']
 (HERE/'DigestCaptureControls.lean').write_text('\n'.join(defs)+'\n')
 lines=['import DigestCaptureControls','open RelationalSuccessor.CandidateDigestCapture','open RelationalSuccessor.CandidateDigestCapture.Controls',
 'set_option maxRecDepth 65536','set_option maxHeartbeats 10000000',
 'namespace RelationalSuccessor',
 'def outcomeTag {α : Type} : CaptureOutcome α → String\n  | .invalidEnvelope => "invalid-envelope"\n  | .digestRefused reason => "digest:" ++ reprStr reason\n  | .byteStage reason => match reason with\n    | .invalidEnvelope => "unreachable-byte-envelope"\n    | .recordRefused rec => match rec with\n      | .invalidSyntax => "invalid-syntax"\n      | .unsupportedScalar _ => "unsupported-scalar"\n      | .invalidRecord _ => "invalid-record"\n      | .decoded _ => "unreachable-decoded-refusal"\n    | .staleFrame _ => "stale-frame"\n    | .prepared _ => "prepared"']
 cases=[]
 def emit(name,expr,expected):cases.append({'name':name,'expression':expr,'expected_json':json.dumps(expected)});lines.append('#eval '+expr)
 prefix='digest:RelationalSuccessor.CandidateDigest.Outcome.'
 for row in rows:
  kind=row['kind'];n=row['byte_count'];capture=kind+'Capture';frame=kind+'Frame'
  def classify(cap,fr=frame,budget=n):return f'outcomeTag (classifyCheckedCapture profile {budget} CandidateBindingRecords.{kind}Version CandidateBindingRecords.{kind}Kind CandidateBindingAst.{kind} {fr} {cap})'
  emit(kind+'-original',classify(capture),'prepared')
  emit(kind+'-entrypoint',f'(prepare{kind.title()}Digest profile {n} {frame} {capture}).isSome',True)
  emit(kind+'-wrong-count',classify(f'{{{capture} with byteLength:={n+1}}}'),'invalid-envelope')
  emit(kind+'-old-uncomputed-digest',classify(f'{{{capture} with digest:="uncomputed fixture digest"}}'),prefix+'malformedDigest')
  emit(kind+'-wrong-full-profile',classify(f'{{{capture} with digestProfile:={{profile.ref with digest:="other"}}}}'),prefix+'unsupportedProfile')
  emit(kind+'-per-capture-budget',classify(capture,budget=n-1),prefix+'byteBudgetExceeded')
  emit(kind+'-stale-frame',classify(capture,fr=f'{{{frame} with epoch:=43}}'),'stale-frame')
  emit(kind+'-same-count-byte-change',classify(f'{{{capture} with content:=0::{capture}.content.drop 1}}'),prefix+'digestMismatch')
  emit(kind+'-truncated',classify(f'{{{capture} with content:={capture}.content.take {n-1},byteLength:={n-1}}}'),prefix+'digestMismatch')
  emit(kind+'-appended',classify(f'{{{capture} with content:={capture}.content++[32],byteLength:={n+1}}}',budget=n+1),prefix+'digestMismatch')
  limits=f'⟨{n},{2*n},2⟩';catalog=f'prepare{kind.title()}CatalogDigest profile'
  emit(kind+'-full-catalog',f'({catalog} {limits} {frame} [{capture}] [{capture}]).isSome',True)
  emit(kind+'-catalog-count-guard',f'({catalog} ⟨{n},{2*n},1⟩ {frame} [{capture}] [{capture}]).isSome',False)
  emit(kind+'-catalog-total-byte-guard',f'({catalog} ⟨{n},{2*n-1},2⟩ {frame} [{capture}] [{capture}]).isSome',False)
  bad=f'{{{capture} with digestProfile:={{profile.ref with digest:="other"}}}}'
  emit(kind+'-unused-bad-root-not-skipped',f'({catalog} ⟨{n},{3*n},3⟩ {frame} [{capture}] [{capture},{bad}]).isSome',False)
  emit(kind+'-retained-catalog-original-bytes',f'(({catalog} {limits} {frame} [{capture}] [{capture}]).map fun stage => (stage.records.map (fun output=>output.envelope))==[{capture}]).getD false',True)
 emit('valid-hash-empty-content-invalid-json','outcomeTag (classifyCheckedCapture profile 0 CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role roleFrame emptyCapture)','invalid-syntax')
 # Correct hashes of unsupported/raw malformed data must proceed to interpretation and refuse there.
 for name,data,expected in [('malformed-utf8',bytes([0xc0,0x80]),'invalid-syntax'),('unpaired-json-scalar',b'"\\uD800"','unsupported-scalar'),('json-null-not-a-binding',b'null','invalid-record')]:
  digest=hashlib.sha256(data).hexdigest();cap=f'(CandidateBindingCapture.Envelope.mk [{",".join(map(str,data))}] {len(data)} profile.ref {json.dumps(digest)})'
  emit('valid-hash-'+name,f'outcomeTag (classifyCheckedCapture profile {len(data)} CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role roleFrame {cap})',expected)
 index={'task':'N01','unit':'K02-digest-capture','original_fixtures':rows,'kernel_control_declarations':names,'runtime_cases':cases,
  'computed_digest_oracle':'Python hashlib; independent proof checker not run','original_positive_kernel_hash_controls':False,
  'profile_and_owner_review_roots_synthetic':True,'authenticated_capture_proved':False,'inherited_discharges':0,'authority_effect':'none'}
 (HERE/'control-index.json').write_text(json.dumps(index,indent=2)+'\n')
 (HERE/'DigestCaptureRuntimeControls.lean').write_text('\n'.join(lines)+'\nend RelationalSuccessor\n')
 print({'kernel_controls':len(names),'runtime_cases':len(cases)})
if __name__=='__main__':run()
