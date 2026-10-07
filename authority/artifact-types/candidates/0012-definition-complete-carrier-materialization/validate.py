#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
import jsonschema
ROOT=Path(__file__).resolve().parent;LAB=ROOT.parents[3]
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n',encoding='utf-8')
def main():
 subprocess.run([sys.executable,str(ROOT/'build.py')],check=True);m=load(ROOT/'carrier-postimages.json');n=load(ROOT/'noncarrier-realizations.json');checks=[]
 def ck(i,o,d):checks.append({'check_id':i,'result':'PASS' if o else 'BLOCK','detail':d})
 canonical=[ROOT/'carrier-postimages.json',ROOT/'noncarrier-realizations.json',ROOT/'runtime/session-memory.schema.json',ROOT/'REVIEW.md']
 for x in m['entries']:canonical += [LAB/x['artifact_path'],LAB/x['schema_path'],LAB/x['fixture_path']]
 before={str(p):sha(p) for p in canonical};subprocess.run([sys.executable,str(ROOT/'build.py')],check=True);after={str(p):sha(p) for p in canonical};ck('deterministic-materialization',before==after,{'files':len(before),'manifest_sha256':sha(ROOT/'carrier-postimages.json')})
 results=[]
 for x in m['entries']:
  root=(LAB/x['artifact_path']).parent;r=subprocess.run([sys.executable,str(root/'validate.py')],text=True,capture_output=True);receipt=load(root/'receipts/validation.json');results.append({'artifact_type_ref':x['artifact_type_ref'],'exit':r.returncode,'result':receipt['result'],'artifact_current':sha(root/'artifact.json')==x['artifact_sha256'],'schema_current':sha(root/'schema.json')==x['schema_sha256'],'fixture_current':sha(root/'fixtures/valid/record.json')==x['fixture_sha256']})
 ck('34-carriers-pass',len(results)==34 and all(all(v in (0,'PASS',True) for k,v in x.items() if k!='artifact_type_ref') for x in results),results)
 coverage=load(LAB/m['coverage_audit']['path']);ck('exact-coverage-actions',m['count']==34 and {x['artifact_type_ref'] for x in m['entries']}=={x['artifact_type_ref'] for x in coverage['required_actions']} and m['coverage_audit']['sha256']==sha(LAB/m['coverage_audit']['path']),{'manifest':m['count'],'actions':len(coverage['required_actions'])})
 relation=load(LAB/m['relation_model']['path']);rr=load((LAB/m['relation_model']['path']).parent/'receipts/validation.json');ck('relation-model-pass-current',m['relation_model']['sha256']==sha(LAB/m['relation_model']['path']) and relation['counts']['active_relation_kinds']==40 and rr['result']=='PASS',{'model':relation['model_id'],'result':rr['result']})
 names={x['definition_ref'].split('@')[0].removeprefix('cal.definition.') for x in n['entries']};ck('six-noncarrier-realizations',names=={'actor','agent','session-memory','operational-learning-cycle','classification','failure'} and n['authority_effect']=='none',sorted(names))
 sm=n['session_memory_schema'];schema=load(LAB/sm['path']);good=load(LAB/sm['positive_witness']);bad=load(LAB/sm['negative_witness']);ge=list(jsonschema.Draft202012Validator(schema).iter_errors(good));be=list(jsonschema.Draft202012Validator(schema).iter_errors(bad));ck('ephemeral-session-memory-enforced',not ge and bool(be) and good['expires_with_session'] is True and good['persistence_allowed'] is False,{'valid_errors':[e.message for e in ge],'invalid_errors':[e.message for e in be]})
 artifacts=[load(LAB/x['artifact_path']) for x in m['entries']];ck('candidate-no-authority-effect',all(x['status']=='candidate-unadmitted' and x['authority_effect']=='none' for x in artifacts) and m['authority_effect']=='none',{'count':len(artifacts)})
 result='PASS' if all(x['result']=='PASS' for x in checks) else 'BLOCK';r={'schema_version':'cyberalchemy-lab-definition-complete-carrier-materialization-validation/v1','result':result,'authority_effect':'none','checks':checks,'materials':{'carrier_manifest_sha256':sha(ROOT/'carrier-postimages.json'),'noncarrier_manifest_sha256':sha(ROOT/'noncarrier-realizations.json'),'session_memory_schema_sha256':sha(ROOT/'runtime/session-memory.schema.json'),'review_sha256':sha(ROOT/'REVIEW.md')},'claim_ceiling':'PASS proves 34 exact candidate carrier packages and six explicit noncarrier realizations, including ephemeral Session Memory. It admits no type, instance, relation, consumer, or runtime.'};dump(ROOT/'receipts/validation.json',r);print(json.dumps({'result':result,'checks':len(checks),**r['materials']},sort_keys=True));return 0 if result=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
