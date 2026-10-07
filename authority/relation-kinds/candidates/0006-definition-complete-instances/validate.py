#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
import jsonschema
ROOT=Path(__file__).resolve().parent;LAB=ROOT.parents[3];RK=LAB/'authority/artifact-types/relation-kind/v2';TR=LAB/'authority/artifact-types/typed-relation/v2'
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n',encoding='utf-8')
def package(root):
 s=load(root/'schema.json');a=load(root/'artifact.json');v=load(root/'fixtures/valid/record.json');val=jsonschema.Draft202012Validator(s);checks=[]
 def ck(i,o,d):checks.append({'check_id':i,'result':'PASS' if o else 'BLOCK','detail':d})
 es=[e.message for e in val.iter_errors(v)];ck('valid-fixture',not es,es);neg=[]
 for p in sorted((root/'fixtures/invalid').glob('*.json')):
  er=[e.message for e in val.iter_errors(load(p))];neg.append({'path':str(p.relative_to(root)),'rejected':bool(er),'errors':er})
 ck('four-hostile-rejections',len(neg)==4 and all(x['rejected'] for x in neg),neg);ck('closed-current-schema',s.get('additionalProperties') is False and a['schema_digest']==sha(root/'schema.json'),a['schema_digest']);ck('candidate-no-effect',a['status']=='candidate-unadmitted' and a['authority_effect']=='none',{'status':a['status'],'effect':a['authority_effect']})
 result='PASS' if all(x['result']=='PASS' for x in checks) else 'BLOCK';r={'schema_version':'cyberalchemy-lab-definition-complete-relation-carrier-validation/v1','result':result,'authority_effect':'none','checks':checks,'materials':{'artifact_sha256':sha(root/'artifact.json'),'schema_sha256':sha(root/'schema.json'),'fixture_sha256':sha(root/'fixtures/valid/record.json')}};dump(root/'receipts/validation.json',r);print(json.dumps({'artifact_type_ref':a['artifact_type_ref'],'result':result,'checks':len(checks)},sort_keys=True));return 0 if result=='PASS' else 1
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--package',type=Path);args=ap.parse_args();
 if args.package:return package(args.package.resolve())
 subprocess.run([sys.executable,str(ROOT/'build.py')],check=True);rc1=package(RK);rc2=package(TR);model=load(LAB/'authority/relation-kinds/candidates/0005-definition-complete-extension/model.json');rk=load(ROOT/'relation-kind-instances.json');tr=load(ROOT/'typed-relation-examples.json');manifest=load(ROOT/'relation-kind-admission-manifest.json');rs=load(RK/'schema.json');ts=load(TR/'schema.json');checks=[]
 def ck(i,o,d):checks.append({'check_id':i,'result':'PASS' if o else 'BLOCK','detail':d})
 re=[]
 for x in rk['entries']:re.append({'id':x['payload']['relation_kind_id'],'errors':[e.message for e in jsonschema.Draft202012Validator(rs).iter_errors(x)]})
 te=[]
 for x in tr['entries']:te.append({'id':x['payload']['relation_kind_ref'],'errors':[e.message for e in jsonschema.Draft202012Validator(ts).iter_errors(x)]})
 ck('all-40-relation-kind-records-valid',len(re)==40 and all(not x['errors'] for x in re),re);ck('all-40-typed-relation-examples-valid',len(te)==40 and all(not x['errors'] for x in te),te)
 by={x['payload']['relation_kind_id']:x['payload'] for x in rk['entries']};sem=[]
 for e in model['entries']:
  p=by[e['relation_kind_id']];sem.append({'id':e['relation_kind_id'],'axis':p['axis_id']==e['axis_id'],'question':p['unique_question']==e['unique_question'],'effect':p['operational_effect']==e['operational_effect'],'pairs':p['allowed_endpoint_pairs']==e['allowed_endpoint_pairs'],'qualifiers':p['qualifier_contract']['required_axes']==e['required_qualifier_axes'],'forbidden':p['forbidden_inferences']==e['forbidden_inferences']})
 ck('complete-model-semantics-retained',all(all(v for k,v in x.items() if k!='id') for x in sem),sem);pc=sum(len(x['payload']['allowed_endpoint_pairs']) for x in rk['entries']);ck('closed-pair-universe',pc==model['counts']['declared_endpoint_pairs'] and all('*' not in (p['source_kind'],p['target_kind']) for x in rk['entries'] for p in x['payload']['allowed_endpoint_pairs']),{'pairs':pc,'wildcards':0})
 mr=[]
 for x in manifest['entries']:
  p=LAB/x['instance_path'];mr.append({'id':x['relation_kind_id'],'current':sha(p)==x['instance_sha256'],'typed_example_excluded':x['typed_relation_example_admission']=='excluded'})
 ck('exact-40-admission-manifest',manifest['count']==40 and manifest['typed_relation_instances_to_admit']==0 and all(all(v for k,v in x.items() if k!='id') for x in mr),mr);ck('carrier-receipts-pass',rc1==rc2==0 and load(RK/'receipts/validation.json')['result']==load(TR/'receipts/validation.json')['result']=='PASS',{'relation-kind':rc1,'typed-relation':rc2});ck('candidate-no-effect',rk['authority_effect']==tr['authority_effect']==manifest['authority_effect']=='none',{'relation-kind':rk['authority_effect'],'typed-relation':tr['authority_effect']})
 names=('candidate.json','carrier-postimages.json','relation-kind-instances.json','typed-relation-examples.json','relation-kind-admission-manifest.json','RELATION-KINDS.md');before=[(ROOT/x).read_bytes() for x in names];subprocess.run([sys.executable,str(ROOT/'build.py')],check=True);after=[(ROOT/x).read_bytes() for x in names];ck('deterministic',before==after,{'manifest_sha256':sha(ROOT/'relation-kind-admission-manifest.json')})
 result='PASS' if all(x['result']=='PASS' for x in checks) else 'BLOCK';r={'schema_version':'cyberalchemy-lab-definition-complete-relation-materialization-validation/v1','result':result,'authority_effect':'none','checks':checks,'materials':{'candidate_sha256':sha(ROOT/'candidate.json'),'carrier_postimages_sha256':sha(ROOT/'carrier-postimages.json'),'relation_kind_instances_sha256':sha(ROOT/'relation-kind-instances.json'),'typed_relation_examples_sha256':sha(ROOT/'typed-relation-examples.json'),'admission_manifest_sha256':sha(ROOT/'relation-kind-admission-manifest.json'),'review_sha256':sha(ROOT/'RELATION-KINDS.md')},'claim_ceiling':'PASS proves two current carrier schemas, 40 exact Relation Kind candidates, and 40 excluded Typed Relation examples. It admits nothing.'};dump(ROOT/'receipts/validation.json',r);print(json.dumps({'result':result,'checks':len(checks),**r['materials']},sort_keys=True));return 0 if result=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
