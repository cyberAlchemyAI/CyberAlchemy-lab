#!/usr/bin/env python3
"""Preflight or atomically apply the exact Decision 0070 admission bundle."""
from __future__ import annotations
import argparse,hashlib,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;LAB=HERE.parents[2];PROPOSAL=HERE/'proposal';AUTH=HERE/'authorization.json';FINAL_BUNDLE=LAB/'authority/admissions/definition-complete-lab-model/v1';DECISION_ID='CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION'
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n',encoding='utf-8')
def verify_proposal():
 r=subprocess.run([sys.executable,str(PROPOSAL/'validate.py')],cwd=LAB);assert r.returncode==0,'proposal validation failed';v=load(PROPOSAL/'validation.json');assert v['result']=='PASS';p=load(PROPOSAL/'proposal.json');assert p['decision_id']==DECISION_ID and p['authority_effect']=='none';return p,v
def verify_authorization(proposal):
 if not AUTH.is_file():raise RuntimeError('authorization.json is absent; exact owner authorization is required')
 a=load(AUTH);required={'schema_version':'cyberalchemy-lab-owner-authorization/v1','decision_id':DECISION_ID,'authorized':True,'proposal_path':str((PROPOSAL/'proposal.json').relative_to(LAB)),'proposal_sha256':sha(PROPOSAL/'proposal.json')}
 for k,v in required.items():
  if a.get(k)!=v:raise RuntimeError(f'authorization mismatch at {k}: expected {v!r}')
 if not a.get('verbatim_user_authorization','').strip():raise RuntimeError('verbatim user authorization is empty')
 if a.get('verbatim_user_authorization','').startswith('REPLACE '):raise RuntimeError('authorization template was not resolved')
 return a
def build_stage(stage,proposal,authorization):
 am=load(PROPOSAL/'artifact-type-admission-manifest.json');rm=load(LAB/proposal['inputs']['relation_kind_manifest']['path']);ar=load(PROPOSAL/'artifact-type-registry-postimage.json');rr=load(PROPOSAL/'relation-kind-registry-postimage.json');ep=load(PROPOSAL/'endpoint-inventory-postimage.json');gm=load(PROPOSAL/'governed-model-instance-postimage.json')
 artifact_admission={'schema_version':'cyberalchemy-lab-collective-artifact-type-admission/v1','decision_id':DECISION_ID,'status':'owner-admitted','authority_effect':'artifact-type-admission-only','count':93,'predecessors_transitioned_to_historical':9,'entries':am['entries'],'ordinary_instances_admitted':0,'claim_ceiling':'Admits only the 93 exact Artifact Type contracts bound here and transitions the nine exact admitted predecessors. It activates nothing.'}
 relation_admission={'schema_version':'cyberalchemy-lab-collective-relation-kind-admission/v1','decision_id':DECISION_ID,'status':'owner-admitted','authority_effect':'relation-kind-admission-only','count':40,'entries':rm['entries'],'typed_relation_instances_admitted':0,'claim_ceiling':'Admits only the 40 exact Relation Kind records bound here. It creates no Typed Relation.'}
 model_admission={'schema_version':'cyberalchemy-lab-governed-model-admission/v1','decision_id':DECISION_ID,'status':'owner-admitted','authority_effect':'integrated-model-contract-admission-only','count':1,'effective_state':gm,'runtime_activations':0,'typed_relation_instances_admitted':0,'claim_ceiling':gm['claim_ceiling']}
 dump(stage/'artifact-type-admission.json',artifact_admission);dump(stage/'relation-kind-admission.json',relation_admission);dump(stage/'governed-model-admission.json',model_admission);dump(stage/'artifact-type-registry.json',ar);dump(stage/'relation-kind-registry.json',rr);dump(stage/'endpoint-inventory.json',ep)
 files=[]
 for name in ('artifact-type-admission.json','relation-kind-admission.json','governed-model-admission.json','artifact-type-registry.json','relation-kind-registry.json','endpoint-inventory.json'):files.append({'path':name,'sha256':sha(stage/name)})
 bundle={'schema_version':'cyberalchemy-lab-definition-complete-admission-bundle/v2','bundle_id':'CAL-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION-BUNDLE-0070','decision_id':DECISION_ID,'status':'owner-admitted','authority_effect':'artifact-type-relation-kind-and-integrated-model-admission','authorization':{'path':str(AUTH.relative_to(LAB)),'sha256':sha(AUTH)},'proposal':{'path':str((PROPOSAL/'proposal.json').relative_to(LAB)),'sha256':sha(PROPOSAL/'proposal.json')},'files':files,'counts':{'artifact_types_admitted':93,'artifact_type_predecessors_historical':9,'relation_kinds_admitted':40,'resolved_endpoint_kinds':101,'governed_model_instances_admitted':1,'ordinary_instances_admitted':1,'typed_relation_instances_admitted':0,'runtime_activations':0},'excluded_effects':proposal['excluded_effects'],'claim_ceiling':'This atomic bundle admits the exact Artifact Type contracts, Relation Kind records, and one integrated Governed Model instance declared by Decision 0070. It activates no runtime.'};dump(stage/'bundle.json',bundle)
 return bundle
def decision_payload(bundle,proposal,authorization):
 return {'schema_version':'cyberalchemy-lab-definition-complete-model-admission-decision/v2','decision_id':DECISION_ID,'title':proposal['title'],'status':'owner-admitted','authority_effect':'artifact-type-relation-kind-and-integrated-model-admission','decision_source':{'kind':'explicit-user-authorization','verbatim':authorization['verbatim_user_authorization'],'owner_ref':authorization['owner_ref']},'authorization':{'path':str(AUTH.relative_to(LAB)),'sha256':sha(AUTH)},'proposal':{'path':str((PROPOSAL/'proposal.json').relative_to(LAB)),'sha256':sha(PROPOSAL/'proposal.json')},'admission_bundle':{'path':str((FINAL_BUNDLE/'bundle.json').relative_to(LAB)),'sha256':sha(FINAL_BUNDLE/'bundle.json')},'effects':proposal['proposed_effects'],'excluded_effects':proposal['excluded_effects'],'transaction':proposal['transaction'],'claim_ceiling':'Decision 0070 admits the exact 93 Artifact Type contracts, 40 Relation Kind records, and one integrated Governed Model instance. It admits no Typed Relation and activates no consumer or runtime.'}
def render(d):
 e=d['effects'];return '\n'.join(['<!-- GENERATED FILE: canonical data is decision.json. -->','','# Decision 0070: definition-complete Lab model admission','',f"- Status: `{d['status']}`",f"- Artifact Types admitted: `{e['artifact_types_admitted']}`",f"- Relation Kinds admitted: `{e['relation_kinds_admitted']}`",f"- Governed Model instances admitted: `{e['governed_model_instances_admitted']}`",f"- Typed Relations admitted: `{e['typed_relation_instances_admitted']}`",f"- Runtime activations: `{e['runtime_activations']}`",'','## Claim ceiling','',d['claim_ceiling'],''])
def preflight():
 p,v=verify_proposal();assert p['proposed_effects']['artifact_types_admitted']==93 and p['proposed_effects']['relation_kinds_admitted']==40 and p['proposed_effects']['governed_model_instances_admitted']==1;assert not (HERE/'decision.json').exists() and not FINAL_BUNDLE.exists();print(json.dumps({'result':'PASS','proposal_sha256':sha(PROPOSAL/'proposal.json'),'artifact_types':93,'relation_kinds':40,'governed_model_instances':1,'authorization_present':AUTH.is_file(),'application_state':'not-applied'},sort_keys=True))
def apply():
 p,v=verify_proposal();a=verify_authorization(p)
 if (HERE/'decision.json').exists() or FINAL_BUNDLE.exists():raise RuntimeError('Decision 0070 or its admission bundle already exists; refusing duplicate application')
 temp=Path(tempfile.mkdtemp(prefix='.decision-0070-',dir=str(LAB)));stage=temp/'bundle';stage.mkdir();created=[]
 try:
  build_stage(stage,p,a);FINAL_BUNDLE.parent.mkdir(parents=True,exist_ok=True);os.replace(stage,FINAL_BUNDLE);created.append(FINAL_BUNDLE)
  d=decision_payload(load(FINAL_BUNDLE/'bundle.json'),p,a);dump(HERE/'decision.json',d);created.append(HERE/'decision.json');(HERE/'DECISION.md').write_text(render(d),encoding='utf-8');created.append(HERE/'DECISION.md')
  receipt={'schema_version':'cyberalchemy-lab-definition-complete-model-application-receipt/v1','result':'PASS','decision_id':DECISION_ID,'authority_effect':d['authority_effect'],'materials':{'decision_sha256':sha(HERE/'decision.json'),'bundle_sha256':sha(FINAL_BUNDLE/'bundle.json'),'authorization_sha256':sha(AUTH),'proposal_sha256':sha(PROPOSAL/'proposal.json')},'counts':load(FINAL_BUNDLE/'bundle.json')['counts']};dump(HERE/'receipts/application.json',receipt);created.append(HERE/'receipts/application.json')
  r=subprocess.run([sys.executable,str(HERE/'validate-decision.py')],cwd=LAB);assert r.returncode==0,'post-application validation failed';print(json.dumps({'result':'APPLIED','decision_id':DECISION_ID,'decision_sha256':sha(HERE/'decision.json'),'bundle_sha256':sha(FINAL_BUNDLE/'bundle.json')},sort_keys=True))
 except Exception:
  for path in reversed(created):
   if path.is_dir():shutil.rmtree(path,ignore_errors=True)
   elif path.exists():path.unlink()
  raise
 finally:shutil.rmtree(temp,ignore_errors=True)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--preflight',action='store_true');args=ap.parse_args();preflight() if args.preflight else apply()
if __name__=='__main__':main()
