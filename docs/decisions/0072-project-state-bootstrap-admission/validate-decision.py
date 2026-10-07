#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;LAB=HERE.parents[2];FINAL=LAB/'authority/admissions/project-state-bootstrap/v1';DREG=LAB/'authority/definitions/registry.json';DINDEX=LAB/'authority/definitions/DEFINITIONS-INDEX.md'
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def dump(p,v):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def main():
 checks=[]
 def ck(i,o,d):checks.append({'check_id':i,'result':'PASS' if o else 'FAIL','detail':d})
 req=[HERE/'authorization.json',HERE/'decision.json',HERE/'receipts/application.json',FINAL/'bundle.json'];missing=[str(x.relative_to(LAB)) for x in req if not x.is_file()]
 if missing:print(json.dumps({'result':'FAIL','missing':missing}));return 1
 a=load(HERE/'authorization.json');d=load(HERE/'decision.json');r=load(HERE/'receipts/application.json');b=load(FINAL/'bundle.json');p=load(HERE/'proposal/proposal.json')
 ck('authorization-exact',a['authorized'] and a['decision_id']==d['decision_id'] and a['proposal_sha256']==sha(HERE/'proposal/proposal.json'),a)
 ck('decision-bundle-binding',d['admission_bundle']['sha256']==sha(FINAL/'bundle.json')==p['postimage']['sha256'] and b['decision_id']==d['decision_id'],d['admission_bundle'])
 files=[{'path':x['path'],'current':sha(FINAL/x['path'])==x['sha256']} for x in b['files']];ck('immutable-bundle-closure',all(x['current'] for x in files),files)
 bundled_reg=FINAL/'registries/definition-registry.json';bundled_index=FINAL/'registries/DEFINITIONS-INDEX.md';ck('live-definition-registry',sha(DREG)==sha(bundled_reg)==d['effective_registries']['definitions']['sha256'] and sha(DINDEX)==sha(bundled_index),{'registry':sha(DREG),'index':sha(DINDEX)})
 dr=load(DREG);ar=load(FINAL/'registries/artifact-type-registry.json');ck('effective-registry-counts',len(dr['entries'])==188 and len(dr['current_lookup'])==182 and ar['inventory']['admitted_contract_count']==129 and ar['inventory']['admitted_current_count']==115,{'definitions':[len(dr['entries']),len(dr['current_lookup'])],'artifact_types':ar['inventory']})
 sem=load(FINAL/'instances/artifacts/project-semantic-event-history.json');gov=load(FINAL/'instances/artifacts/project-governance-event-history.json');state=load(FINAL/'instances/artifacts/project-state.json');se=sem['payload']['events'][0];ge=gov['payload']['events'][0];ck('event-chain-integrity',se['event_digest']==digest({k:v for k,v in se.items() if k!='event_digest'}) and sem['payload']['chain_digest']==digest([se['event_digest']]) and ge['event_digest']==digest({k:v for k,v in ge.items() if k!='event_digest'}) and gov['payload']['chain_digest']==digest([ge['event_digest']]) and ge['semantic_event_ref']['semantic_event_digest']==se['event_digest'],{'semantic':se['event_digest'],'governance':ge['event_digest']})
 materials=[{'path':x,'sha256':sha(LAB/x)} for x in state['payload']['artifact_refs']];expected='sha256:'+digest(materials);ck('successor-state-current',state['node_id']==d['current_project_state_ref'] and state['payload']['cursor']=='decision:0071' and state['payload']['state_digest']==expected==se['resulting_state_digest'] and d['historical_project_state_ref']==se['predecessor_state_ref'],{'state_ref':state['node_id'],'digest':state['payload']['state_digest'],'expected':expected})
 counts={'definitions_admitted':2,'artifact_types_admitted':2,'artifact_instances_admitted':3,'typed_relation_instances_admitted':2,'semantic_events_admitted':1,'governance_events_admitted':1,'predecessor_project_states_historical':1,'runtime_activations':0};ck('exact-effects',b['counts']==d['effects']==r['effects']==counts,b['counts'])
 ck('application-receipt-current',r['result']=='PASS' and r['materials']['decision_sha256']==sha(HERE/'decision.json') and r['materials']['bundle_sha256']==sha(FINAL/'bundle.json') and r['materials']['definition_registry_sha256']==sha(DREG),r['materials'])
 result='PASS' if all(x['result']=='PASS' for x in checks) else 'FAIL';out={'schema_version':'cyberalchemy-lab-project-state-bootstrap-decision-validation/v1','result':result,'checks':checks,'materials':{'decision_sha256':sha(HERE/'decision.json'),'bundle_sha256':sha(FINAL/'bundle.json'),'definition_registry_sha256':sha(DREG)},'claim_ceiling':'PASS proves Decision 0072, its event chains, successor Project State, registries, and immutable bundle remain exact. It does not establish a runtime or later generated records.'};dump(HERE/'receipts/decision-validation.json',out);print(json.dumps({'result':result,'checks':len(checks),**out['materials']},sort_keys=True));return 0 if result=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
