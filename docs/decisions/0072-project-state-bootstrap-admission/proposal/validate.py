#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;HERE=ROOT.parent;LAB=HERE.parents[2];C=LAB/'authority/project-state-transitions/candidates/0001-decision-0071-bootstrap';POST=ROOT/'bundle-postimage'
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def snap():
 ps=[ROOT/'proposal.json',ROOT/'PROPOSAL.md']+sorted(x for x in POST.rglob('*') if x.is_file());return {str(x.relative_to(ROOT)):sha(x) for x in ps}
def main():
 checks=[]
 def ck(i,o,d):checks.append({'check_id':i,'result':'PASS' if o else 'FAIL','detail':d})
 r=subprocess.run([sys.executable,str(C/'validate.py')],cwd=LAB,text=True,capture_output=True);vr=load(C/'receipts/validation.json');ck('candidate-pass',r.returncode==0 and vr['result']=='PASS',{'returncode':r.returncode,'stdout':r.stdout.strip()})
 before=snap();r=subprocess.run([sys.executable,str(ROOT/'build.py')],cwd=LAB,text=True,capture_output=True);after=snap();ck('deterministic-proposal',r.returncode==0 and before==after,{'returncode':r.returncode,'changed':sorted(set(before)|set(after)) if before!=after else []})
 p=load(ROOT/'proposal.json');b=load(POST/'bundle.json');files=[{'path':x['path'],'match':sha(POST/x['path'])==x['sha256']} for x in b['files']];ck('bundle-closure',all(x['match'] for x in files),files)
 counts={'definitions_admitted':2,'artifact_types_admitted':2,'artifact_instances_admitted':3,'typed_relation_instances_admitted':2,'semantic_events_admitted':1,'governance_events_admitted':1,'predecessor_project_states_historical':1,'runtime_activations':0};ck('exact-effects',p['proposed_effects']==b['counts']==counts and p['authority_effect']=='none' and not p['authorization_present'],p['proposed_effects'])
 dr=load(POST/'registries/definition-registry.json');ar=load(POST/'registries/artifact-type-registry.json');ck('registry-postimages',len(dr['entries'])==188 and len(dr['current_lookup'])==182 and ar['inventory']['admitted_contract_count']==129 and ar['inventory']['admitted_current_count']==115,{'definitions':[len(dr['entries']),len(dr['current_lookup'])],'artifact_types':ar['inventory']})
 ck('proposal-binding',p['postimage']['sha256']==sha(POST/'bundle.json') and sha(LAB/p['inputs']['transition']['path'])==p['inputs']['transition']['sha256'] and sha(LAB/p['inputs']['validation']['path'])==p['inputs']['validation']['sha256'],p['postimage'])
 result='PASS' if all(x['result']=='PASS' for x in checks) else 'FAIL';out={'schema_version':'cyberalchemy-lab-project-state-bootstrap-proposal-validation/v1','result':result,'authority_effect':'none','checks':checks,'materials':{'proposal_sha256':sha(ROOT/'proposal.json'),'bundle_sha256':sha(POST/'bundle.json'),'candidate_validation_sha256':sha(C/'receipts/validation.json')},'claim_ceiling':'PASS proves the exact proposal and postimage; it does not apply Decision 0072.'};dump(ROOT/'validation.json',out);print(json.dumps({'result':result,'checks':len(checks),**out['materials']},sort_keys=True));return 0 if result=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
