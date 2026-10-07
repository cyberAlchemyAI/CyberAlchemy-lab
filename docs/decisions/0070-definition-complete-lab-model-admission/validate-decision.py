#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;LAB=HERE.parents[2];BUNDLE=LAB/'authority/admissions/definition-complete-lab-model/v1'
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 required=[HERE/'authorization.json',HERE/'decision.json',HERE/'receipts/application.json',BUNDLE/'bundle.json'];missing=[str(x.relative_to(LAB)) for x in required if not x.is_file()]
 if missing:print(json.dumps({'result':'BLOCK','missing':missing},sort_keys=True));return 1
 d=load(HERE/'decision.json');b=load(BUNDLE/'bundle.json');a=load(HERE/'authorization.json');r=load(HERE/'receipts/application.json');checks=[]
 def ck(i,o,d):checks.append({'check_id':i,'result':'PASS' if o else 'BLOCK','detail':d})
 ck('authorization-exact',a['authorized'] is True and a['decision_id']==d['decision_id'] and a['proposal_sha256']==sha(HERE/'proposal/proposal.json'),a)
 ck('decision-bundle-bound',d['admission_bundle']['sha256']==sha(BUNDLE/'bundle.json') and b['decision_id']==d['decision_id'],d['admission_bundle'])
 files=[]
 for x in b['files']:files.append({'path':x['path'],'current':sha(BUNDLE/x['path'])==x['sha256']})
 ck('bundle-files-current',all(x['current'] for x in files),files);ck('exact-effects',b['counts']=={'artifact_types_admitted':93,'artifact_type_predecessors_historical':9,'relation_kinds_admitted':40,'resolved_endpoint_kinds':101,'governed_model_instances_admitted':1,'ordinary_instances_admitted':1,'typed_relation_instances_admitted':0,'runtime_activations':0},b['counts'])
 at=load(BUNDLE/'artifact-type-admission.json');rk=load(BUNDLE/'relation-kind-admission.json');gm=load(BUNDLE/'governed-model-admission.json');ck('exact-admissions',at['count']==len(at['entries'])==93 and rk['count']==len(rk['entries'])==40 and gm['count']==1 and gm['effective_state']['record_id']=='cal.governed-model.definition-complete-lab/v1' and at['ordinary_instances_admitted']==rk['typed_relation_instances_admitted']==gm['typed_relation_instances_admitted']==gm['runtime_activations']==0,{'artifact-types':at['count'],'relation-kinds':rk['count'],'governed-models':gm['count']})
 ck('application-receipt-current',r['result']=='PASS' and r['materials']['decision_sha256']==sha(HERE/'decision.json') and r['materials']['bundle_sha256']==sha(BUNDLE/'bundle.json'),r['materials'])
 result='PASS' if all(x['result']=='PASS' for x in checks) else 'BLOCK';out={'schema_version':'cyberalchemy-lab-definition-complete-model-decision-validation/v2','result':result,'checks':checks,'materials':{'decision_sha256':sha(HERE/'decision.json'),'bundle_sha256':sha(BUNDLE/'bundle.json')}};(HERE/'receipts').mkdir(exist_ok=True);(HERE/'receipts/decision-validation.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'result':result,'checks':len(checks),**out['materials']},sort_keys=True));return 0 if result=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
