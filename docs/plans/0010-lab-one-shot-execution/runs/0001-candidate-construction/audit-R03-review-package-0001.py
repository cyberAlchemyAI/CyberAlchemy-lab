"""Independent original-byte candidate preview; no publicAPI or owner proof."""
import argparse,base64,hashlib,importlib.util,json,os,sys
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];K=ROOT/'product/lab/release-candidates/v1/interface/review-package-v2';PIN='0c78b7951d9ac21a8cac03021bc7c5ed6df31c80ffa281e87fd7df5edd073d6a'
def sha(b):return hashlib.sha256(b).hexdigest()
def guard(pin):
 p=HERE/'review-package-audit-source-0001.json';assert sha(p.read_bytes())==pin
 for r in json.loads(p.read_bytes())['files']:
  p=ROOT/r['path'];assert p.is_file() and not p.is_symlink() and sha(p.read_bytes())==r['sha256'],r['path']
def emit(path,value):
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'w') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
def main():
 p=argparse.ArgumentParser();p.add_argument('--source-sha256',required=True);a=p.parse_args();guard(a.source_sha256)
 name='_cal_exact_review_independent';spec=importlib.util.spec_from_file_location(name,K/'__init__.py',submodule_search_locations=[str(K)]);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
 B=__import__(name+'.base',fromlist=['*']);F=__import__(name+'.fixtures',fromlist=['*']);B.guard(PIN);cases=[];examples=[]
 def check(ok,label):assert ok,label;cases.append(label)
 for source_name in ['reference-corrected','custody-participation']:
  print(json.dumps({'source_name':source_name,'phase':'actual-owned-preview'}),flush=True)
  with F.example(PIN,source_name=source_name,multiple_voices=True) as (builder,review,witness):
   package,evidence=builder.build(review,B.P.compact(review));manifest=B.P.frame_parse(builder.vault.object_read(package['manifest_binding']))
   check(builder.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:review-package:v1-candidate',package),source_name+':originalpackage-schema')
   proof=witness['signed_nonce_proof'];check(proof['challenge']==witness['nonce_challenge'],source_name+':actualnonce')
   Ed25519PublicKey.from_public_bytes(base64.b64decode(witness['public_policy']['reader_public_key'])).verify(base64.b64decode(proof['signature']),B.P.compact(proof['challenge']))
   check(True,source_name+':independentEd25519signature')
   check(len(manifest['targets'])==2 and len(manifest['ordered_required_owner_responses'])==4,source_name+':twoindependentcores-fourvoices')
   check(package['human_checkpoint_count']==1 and package['atomicity_requirement']=='all-or-nothing' and manifest['all_targets_materialized'],source_name+':singlependingcheckpoint')
   check(manifest['original_semantic_and_operational_gaps']==review['gaps'] and manifest['input_posture']==review['posture'],source_name+':actualgapsretained')
   check(manifest['actual_owner_outcome'] is None and manifest['current_owner_authority_verified'] is False and not manifest['preference_current_admission_claimed'] and not manifest['workflow_protocol_is_WorkflowRun_artifact'],source_name+':noinventedauthority')
   snapshots={}
   def capture(binding,raw,role):
    check(sha(raw)==binding['sha256'],source_name+':'+role+':originalSHA');value=B.P.frame_parse(raw);B.W.privacy(value)
    old=snapshots.get(binding['ref']);entry={'binding':binding,'roles':[role],'original_bytes_base64':base64.b64encode(raw).decode(),'decoded_body':value}
    if old:
     check(old['binding']==binding and old['original_bytes_base64']==entry['original_bytes_base64'],source_name+':duplicatebyteparity');old['roles'].append(role)
    else:snapshots[binding['ref']]=entry
    return value
   proposal_raw=builder.vault.object_read(review['proposal_binding']);proposal=capture(review['proposal_binding'],proposal_raw,'original-proposal')
   for i,row in enumerate(manifest['targets']):
    target=row['target'];raw=builder.vault.material(row['original_content_binding']);body=capture(row['original_content_binding'],raw,'target:'+str(i))
    check(sha(raw)==target['artifact']['byte_sha256'] and len(raw)==target['content']['size_bytes'],source_name+':target-header-size:'+str(i))
    builder.view.handle.operations.validate_record(body,target['artifact']['carrier_ref'],builder.view.data['projection']);check(True,source_name+':target-carrierschema:'+str(i))
    core=capture(row['core_binding'],builder.vault.material(row['core_binding']),'stable-core:'+str(i))
    meta=capture(target['candidate_binding'],builder.vault.material(target['candidate_binding']),'target-metadata:'+str(i))
    runtime_target={'category':meta['category'],'operation':target['operation'],'version_ref':target['artifact']['version_ref'],'carrier_ref':target['artifact']['carrier_ref'],'record':body,'predecessor_ref':None if target['predecessor'] is None else target['predecessor']['version_ref'],'decision_ref':meta['decision_ref'],'contract':meta['contract']}
    if source_name=='custody-participation':runtime_target['content']=builder.view.handle.custody.content_entry(raw)
    expected={'decision_ref':meta['decision_ref'],'category':meta['category'],'operation':target['operation'],'version_ref':target['artifact']['version_ref'],'target_digest':builder.view.handle.common.digest(runtime_target)}
    check(core==expected and package['ordered_core_bindings'][i]==row['core_binding'],source_name+':independent-full-runtime-core:'+str(i))
    contract=builder.view.data['projection']['contracts'][target['artifact']['carrier_ref']];b={'ref':contract['schema_path'],'sha256':contract['schema_sha256']};capture(b,B.P.source.original({'path':b['ref'],'sha256':b['sha256']}),'target-exact-schema:'+str(i))
   all_objects=[package['manifest_binding'],review['validation_report_binding'],*review['example_bindings'],*review['declared_consequence_bindings'],review['private_public_review_binding'],manifest['original_review_binding'],*[r['object_binding'] for r in manifest['generated_carriers']]]
   for binding in all_objects:capture(binding,builder.vault.object_read(binding),'generated-or-evidence-object')
   for generated in manifest['generated_carriers']:
    raw=builder.vault.object_read(generated['object_binding']);body=B.P.frame_parse(raw);check(sha(raw)==generated['artifact']['byte_sha256'],source_name+':generatedheader')
    builder.view.handle.operations.validate_record(body,generated['artifact']['carrier_ref'],builder.view.data['projection']);check(True,source_name+':generatedoriginalschema')
    if body['kind']=='decision-bundle':check(len(body['payload']['ordered_decisions'])==2 and all(d['selected_outcome'] is None for d in body['payload']['ordered_decisions']),source_name+':individualpendingdecisions')
    else:check(body['payload']['presentation_state']=='pending' and body['payload']['closed_at'] is None,source_name+':checkpointpending')
   for ref in [builder.routing['workflow_decision_profile'],builder.routing['accountable_owner'],*[v['role_declaration'] for route in builder.routing['members'] for v in route['required_owner_voices']]]:
    s=builder.service.handlers.resolve_exact(ref);raw=B.M.record_bytes(builder.view,s)[0];capture({'ref':ref['version_ref'],'sha256':ref['byte_sha256']},raw,'selected-current-routing-declaration')
   capture(manifest['routing_original_binding'],B.W.read_private(builder.path),'independent-routing-original')
   archive={'schema_version':'lab-original-candidate-review-archive/v1-candidate','source_name':source_name,'review_package':package,'materialization_manifest':manifest,'original_objects':list(snapshots.values()),'public_witness':witness,'actual_owner_outcome':None,'authority_effect':'none','current_authority_claimed':False,'claim_ceiling':'Historical isolated preview after cleanup. Declared roles do not prove governing role completeness or current authority; public API13 remains pending.'}
   B.W.privacy(archive);root=Path(witness['root'])
  check(not root.exists(),source_name+':host-key-workspace-removed');examples.append(archive);print(json.dumps({'source_name':source_name,'original_objects':len(snapshots),'owned_host_removed':True}),flush=True)
 B.guard(PIN);guard(a.source_sha256)
 out=K/'receipts/independent-originals-0001.json';emit(out,examples)
 emit(K/'receipts/independent-audit-0001.json',{'schema_version':'lab-review-kernel-independent-audit/v1-candidate','result':'PASS','checks':len(cases),'cases':cases,'source_binding':{'path':str((HERE/'review-package-audit-source-0001.json').relative_to(ROOT)),'sha256':a.source_sha256},'originals_binding':{'path':str(out.relative_to(ROOT)),'sha256':sha(out.read_bytes())},'original20tests_retained':True,'actual_public_API_operations':12,'original_operations':34,'remaining_public_API_operations':22,'public_review_adapter_implemented':False,'required_owner_role_coverage_verified':False,'actual_owner_outcome':None,'authority_effect':'none','task_complete':False})
 print(json.dumps({'result':'PASS','checks':len(cases),'source_previews':2,'public_review_adapter_implemented':False}),flush=True)
if __name__=='__main__':main()
