"""Typed row controls are data-only; byte-source controls compute original content digests."""
from pathlib import Path
import copy,hashlib,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[9]
def b(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def run():
 lines=['import ProfileSelectionEvidence','import DigestCaptureControls','set_option autoImplicit false','set_option maxRecDepth 65536','set_option maxHeartbeats 10000000',
 'namespace RelationalSuccessor.CandidateProfileSelection.Controls',
 'def frame : Frame := CandidateBindingBytes.Controls.roleExpected.body.frame',
 'def issuer : RevisionRef := ⟨⟨"fixture","principal","1"⟩,"uncomputed-fixture-principal"⟩',
 'def declaration : Declaration := ⟨⟨declarationVersion,⟨"fixture","digest-profile","1"⟩,declarationKind,⟨"declare-profile",⟨"sha256-fips1804-2015","lowerhex64",issuer,.accepted,.clear,100⟩,frame⟩,issuer⟩,⟨[1],1,issuer,"uncomputed-typed-row-digest"⟩⟩',
 'def selection : SelectionRecord := ⟨⟨selectionVersion,⟨"fixture","profile-selection","1"⟩,selectionKind,⟨"select-profile",⟨declaration.entry.ref,issuer,.accepted,.clear,100⟩,frame⟩,issuer⟩,⟨[2],1,issuer,"uncomputed-typed-row-digest"⟩⟩']
 controls=[]
 def emit(name,decls,sels,result='none'):
  controls.append(name);lines.append(f'theorem {name} : selectProfileRows frame {decls} {sels}={result} := by decide')
 emit('typed_data_positive','[declaration]','[selection]','some (declaredProfile declaration)')
 emit('typed_identical_duplicates','[declaration,declaration]','[selection,selection]','some (declaredProfile declaration)')
 emit('missing_selection','[declaration]','[]');emit('missing_declaration','[]','[selection]')
 for subject,payload in [('declaration','declaration'),('selection','selection')]:
  for field,value in [('review','.missing'),('review','.rejected'),('revocation','.unknown'),('revocation','.revoked'),('expiry','42')]:
   name=subject+'_'+field+'_'+value.replace('.','');expr=f'{{{subject} with record:={{{subject}.record with body:={{{subject}.record.body with target:={{{subject}.record.body.target with {field}:={value}}}}}}}}}'
   emit(name,'['+(expr if subject=='declaration' else 'declaration')+']','['+(expr if subject=='selection' else 'selection')+']')
  expr=f'{{{subject} with record:={{{subject}.record with body:={{{subject}.record.body with frame:={{frame with epoch:=43}}}}}}}}'
  emit(subject+'_wrong_frame','['+(expr if subject=='declaration' else 'declaration')+']','['+(expr if subject=='selection' else 'selection')+']')
  expr=f'{{{subject} with record:={{{subject}.record with body:={{{subject}.record.body with token:="other"}}}}}}'
  emit(subject+'_wrong_token','['+(expr if subject=='declaration' else 'declaration')+']','['+(expr if subject=='selection' else 'selection')+']')
 for field,value in [('algorithm','sha1'),('encoding','upperhex64')]:
  expr=f'{{declaration with record:={{declaration.record with body:={{declaration.record.body with target:={{declaration.record.body.target with {field}:="{value}"}}}}}}}}'
  emit('unsupported_'+field,'['+expr+']','[selection]')
 changed='{selection with record:={selection.record with body:={selection.record.body with target:={selection.record.body.target with declaration:=issuer}}}}'
 emit('wrong_complete_declaration_ref','[declaration]','['+changed+']')
 emit('selection_conflict_forward','[declaration]','[selection,'+changed+']')
 emit('selection_conflict_reverse','[declaration]','['+changed+',selection]')
 changed='{declaration with record:={declaration.record with ownerReview:={issuer with digest:="other"}}}'
 emit('unused_declaration_key_conflict','[declaration,'+changed+']','[selection]')
 lines+=['#print axioms '+name for name in controls]+['end RelationalSuccessor.CandidateProfileSelection.Controls']
 (HERE/'ProfileSelectionControls.lean').write_text('\n'.join(lines)+'\n')
 original=HERE.parent/'K02-pipeline/schemas/role-binding.fixture.json';base=json.loads(original.read_text());frameJSON=base['body']['frame'];issuerJSON={'key':{'owner':'fixture','artifact':'principal','revision':'1'},'digest':'uncomputed-fixture-principal'}
 declarationJSON={'schema_version':'cyberalchemy-lab-digest-profile-declaration/candidate-v1','binding_revision_key':{'owner':'fixture','artifact':'digest-profile','revision':'1'},'kind':'digest-profile-declaration','body':{'token':'declare-profile','target':{'algorithm':'sha256-fips1804-2015','encoding':'lowerhex64','issuer':issuerJSON,'review_posture':'accepted','revocation_posture':'clear','expiry_epoch':100},'frame':frameJSON},'owner_review_ref':issuerJSON}
 def encoded(obj):return (json.dumps(obj,indent=2)+'\n').encode()
 def ref_for(obj):return {'key':obj['binding_revision_key'],'digest':hashlib.sha256(encoded(obj)).hexdigest()}
 declarationRef=ref_for(declarationJSON)
 selectionJSON={'schema_version':'cyberalchemy-lab-digest-profile-selection/candidate-v1','binding_revision_key':{'owner':'fixture','artifact':'profile-selection','revision':'1'},'kind':'digest-profile-selection','body':{'token':'select-profile','target':{'declaration_ref':declarationRef,'issuer':issuerJSON,'review_posture':'accepted','revocation_posture':'clear','expiry_epoch':100},'frame':frameJSON},'owner_review_ref':issuerJSON}
 fixtureDir=HERE/'fixtures';fixtureDir.mkdir(exist_ok=True)
 fixtures=[];runtime=['import ProfileSelectionControls','set_option maxRecDepth 65536','set_option maxHeartbeats 10000000','namespace RelationalSuccessor.CandidateProfileSelection.RuntimeControls','open Controls (frame)','def bootstrap : CandidateDigest.Profile := CandidateDigestCapture.Controls.profile','def limits : CandidateDigestCapture.Limits := ⟨10000,100000,100⟩']
 caseRows=[];num=0
 def env(obj,name,bytes_override=None,digest_override=None):
  nonlocal num
  data=encoded(obj) if bytes_override is None else bytes_override;digest=hashlib.sha256(data).hexdigest() if digest_override is None else digest_override
  path=fixtureDir/f'{name}.json';path.write_bytes(data)
  row={'name':name,'original_bytes':b(path),'byte_count':len(data),'submitted_digest':digest,'computed_digest':hashlib.sha256(data).hexdigest()};fixtures.append(row)
  var='capture'+str(num);num+=1;runtime.append(f'def {var} : CandidateBindingCapture.Envelope := ⟨[{",".join(map(str,data))}],{len(data)},bootstrap.ref,{json.dumps(digest)}⟩');return var
 d=env(declarationJSON,'declaration');s=env(selectionJSON,'selection')
 def case(name,ds,ss,expected=True,frameExpr='frame',limitExpr='limits',extract=False):
  expression=f'prepareSelectedProfile bootstrap {limitExpr} {frameExpr} {ds} {ss}'
  if extract:expression=f'(({expression}).map fun stage=>stage.profile.ref.digest).getD "REFUSED"'
  else:expression=f'({expression}).isSome'
  caseRows.append({'name':name,'expression':expression,'expected_json':json.dumps(expected)});runtime.append('#eval '+expression)
 case('captured-positive',f'[{d}]',f'[{s}]');case('derived-original-content-digest',f'[{d}]',f'[{s}]',declarationRef['digest'],extract=True)
 case('captured-identical-duplicates',f'[{d},{d}]',f'[{s},{s}]')
 case('missing-selection',f'[{d}]','[]',False);case('missing-declaration','[]',f'[{s}]',False)
 for subject,originalObj in [('declaration',declarationJSON),('selection',selectionJSON)]:
  for field,value in [('review_posture','missing'),('review_posture','rejected'),('revocation_posture','unknown'),('revocation_posture','revoked'),('expiry_epoch',42)]:
   obj=copy.deepcopy(originalObj);obj['body']['target'][field]=value;changed=env(obj,subject+'-'+field+'-'+str(value))
   if subject=='declaration':
    choice=copy.deepcopy(selectionJSON);choice['body']['target']['declaration_ref']=ref_for(obj);choiceCap=env(choice,subject+'-'+field+'-'+str(value)+'-matching-selection');case(subject+'-'+field+'-'+str(value),f'[{changed}]',f'[{choiceCap}]',False)
   else:case(subject+'-'+field+'-'+str(value),f'[{d}]',f'[{changed}]',False)
 for field,value in [('algorithm','sha1'),('encoding','upperhex64')]:
  obj=copy.deepcopy(declarationJSON);obj['body']['target'][field]=value;changed=env(obj,'unsupported-'+field)
  choice=copy.deepcopy(selectionJSON);choice['body']['target']['declaration_ref']=ref_for(obj);choiceCap=env(choice,'unsupported-'+field+'-selection');case('unsupported-'+field,f'[{changed}]',f'[{choiceCap}]',False)
 wrong=copy.deepcopy(selectionJSON);wrong['body']['target']['declaration_ref']['digest']='other';other=env(wrong,'wrong-complete-ref')
 case('wrong-complete-ref',f'[{d}]',f'[{other}]',False)
 case('conflict-forward',f'[{d}]',f'[{s},{other}]',False);case('conflict-reverse',f'[{d}]',f'[{other},{s}]',False)
 changed=copy.deepcopy(declarationJSON);changed['owner_review_ref']['digest']='other';unused=env(changed,'unused-declaration-key-conflict');case('unused-declaration-key-conflict',f'[{d},{unused}]',f'[{s}]',False)
 case('wrong-full-frame',f'[{d}]',f'[{s}]',False,frameExpr='{frame with epoch:=43}')
 altered=env(declarationJSON,'same-count-declaration-byte-change',bytes_override=b'\x00'+encoded(declarationJSON)[1:],digest_override=declarationRef['digest']);case('same-count-byte-change',f'[{altered}]',f'[{s}]',False)
 case('capture-count-budget',f'[{d}]',f'[{s}]',False,limitExpr='⟨10000,100000,1⟩')
 case('total-byte-budget',f'[{d}]',f'[{s}]',False,limitExpr='⟨10000,1,100⟩')
 case('per-capture-budget',f'[{d}]',f'[{s}]',False,limitExpr='⟨1,100000,100⟩')
 runtime.append('end RelationalSuccessor.CandidateProfileSelection.RuntimeControls');(HERE/'ProfileSelectionRuntimeControls.lean').write_text('\n'.join(runtime)+'\n')
 index={'task':'N01','unit':'K02-profile-selection','kernel_control_declarations':controls,'kernel_controls_are_typed_data_only':True,
  'runtime_cases':caseRows,'fixtures':fixtures,'frame_source':b(original),'profile_principal_bootstrap_review_roots_synthetic':True,
  'authentic_evidence_provider_realized':False,'inherited_discharges':0,'authority_effect':'none'}
 (HERE/'control-index.json').write_text(json.dumps(index,indent=2)+'\n');print({'kernel_controls':len(controls),'runtime_cases':len(caseRows),'source_fixtures':len(fixtures)})
if __name__=='__main__':run()
