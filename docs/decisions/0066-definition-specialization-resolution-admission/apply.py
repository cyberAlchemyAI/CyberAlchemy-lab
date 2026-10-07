#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,os,subprocess,sys,tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any
LAB=Path(__file__).resolve().parents[3]; ROOT=Path(__file__).resolve().parent
CROOT=LAB/'authority/definitions/candidates/0014-definition-specialization-resolution'; CANDIDATE=CROOT/'candidate.json'; RESOLUTION=CROOT/'resolution.json'; SOURCE_RECEIPT=CROOT/'receipts/validation.json'
REGISTRY=LAB/'authority/definitions/registry.json'; INDEX=LAB/'authority/definitions/DEFINITIONS-INDEX.md'; DRIFT=LAB/'authority/definitions/drift-audit.json'; DRIFT_MD=LAB/'authority/definitions/DEFINITION-DRIFT-AUDIT.md'
DECISION_ID='CAL-DECISION-0066-DEFINITION-SPECIALIZATION-RESOLUTION-ADMISSION'
EXPECTED={'candidate':'a01c9560d410dfc21b64fca92946923e073176746254128bd49c6ce4c4ab8646','resolution':'943d86c6abb23e08475f44138601d46a196ded35595acfabc81d28823e81cb25','receipt':'d051c8fd65a1f107784db4215149871ddc08009604ff7bcff4fb609fcdcbbe4a','registry':'129fbb8c13250a0afd4b8a8bbcd189998137a062c15590cee6ce390433699b3a'}
def load(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def enc(v): return (json.dumps(v,indent=2,sort_keys=True)+'\n').encode()
def rel(p): return str(p.relative_to(LAB))
def exact(p): return {'path':rel(p),'sha256':sha(p)}
def atomic(p,b):
 p.parent.mkdir(parents=True,exist_ok=True); fd,n=tempfile.mkstemp(prefix='.'+p.name+'.',dir=p.parent)
 try:
  with os.fdopen(fd,'wb') as h: h.write(b); h.flush(); os.fsync(h.fileno())
  os.replace(n,p)
 finally:
  if os.path.exists(n): os.unlink(n)
def render_index(r):
 lines=['<!-- GENERATED FILE: edit machine sources and run the bound admission builder. -->','','# CyberAlchemy Lab Definition Index','',f"- Status: `{r['status']}`",f"- Admission decision: `{r['admission_decision_ref']}`",'','| ID | Version | Term | Lifecycle | Path |','| --- | --- | --- | --- | --- |']
 for x in r['entries']: lines.append(f"| `{x['definition_id']}` | `{x['version']}` | {x['term']} | `{x['lifecycle_state']}` | `{x['path']}` |")
 lines += ['','## Current lookup','']+[f'- `{k}` -> `{v}`' for k,v in r['current_lookup'].items()]+['','## Claim ceiling','',r['claim_ceiling']]
 return '\n'.join(lines).rstrip()+'\n'
def render_drift(d):
 lines=['<!-- GENERATED FILE: edit drift-audit.json through its bound admission builder. -->','','# Definition Drift Audit','', '> Post-admission explanatory projection; machine JSON is canonical.','']
 for x in d['findings']: lines += [f"## {x['finding_id']} — {x['status']}",'',x['condition'],'',f"Remediation: {x['remediation']}",'']
 return '\n'.join(lines+['## Claim ceiling','',d['claim_ceiling']]).rstrip()+'\n'
def main():
 c=load(CANDIDATE); r=load(RESOLUTION); sr=load(SOURCE_RECEIPT); live=load(REGISTRY)
 actual={'candidate':sha(CANDIDATE),'resolution':sha(RESOLUTION),'receipt':sha(SOURCE_RECEIPT),'registry':sha(REGISTRY)}
 if actual!=EXPECTED: raise RuntimeError(f'reviewed admission envelope changed: {actual}')
 if sr.get('result')!='PASS' or sr.get('summary')!={'failed':0,'passed':20,'total':20}: raise RuntimeError('Step 3 validation must pass 20/20')
 if len(c['definitions'])!=7 or len({x['definition_id'] for x in c['definitions']})!=7: raise RuntimeError('approval binds exactly seven Definitions')
 digest_map=sr['materials']['definition_digests']; records=[]
 for x in c['definitions']:
  p=LAB/x['path']; d=load(p)
  if d['definition_id']!=x['definition_id'] or d['version']!=x['version'] or sha(p)!=digest_map.get(d['definition_id']): raise RuntimeError('Definition identity or digest changed: '+x['definition_id'])
  records.append((d,p))
 ids={d['definition_id'] for d,_ in records}; existing=[x for x in live['entries'] if x['definition_id'] in ids]
 if existing:
  if len(existing)==7 and all(x.get('admission_decision_ref')==DECISION_ID and x['lifecycle_state']=='admitted' for x in existing): return subprocess.run([sys.executable,str(ROOT/'validate.py')],cwd=LAB).returncode
  raise RuntimeError('one or more Step 3 Definition identities already exist')
 if len(live['entries'])!=179 or len(live['current_lookup'])!=173: raise RuntimeError('registry preimage counts changed')
 auth={'schema_version':'cyberalchemy-lab-definition-resolution-admission-authorization/v1','authorization_id':'CAL-AUTHORIZATION-0066-DEFINITION-SPECIALIZATION-RESOLUTION','recorded_on':'2026-10-06','principal_id':'person:<vrondelli>','selected_role':'definition-owner','user_instruction_verbatim':'Admit','interpreted_scope':'Admit the exact Step 3 candidate: seven positive Definitions plus the digest-bound workflow, Ledger, Withdrawal Record, and Project Identity resolutions.','authorized_effect':'Admit seven exact Definition versions and make the exact resolution.json a canonical decision overlay.','candidate':exact(CANDIDATE),'resolution_overlay':exact(RESOLUTION),'validation_receipt':exact(SOURCE_RECEIPT),'registry_preimage':exact(REGISTRY),'definition_digests':digest_map,'excluded_effects':['No Artifact Type or instance is admitted or rebound.','No workflow consumer is activated and no existing Definition identity is superseded.','No Ledger carrier is created and no identifier is withdrawn.','Project Identity/v1 remains candidate-unadmitted.','No Relation Kind, endpoint pair, qualifier, runtime, publication, release, or deployment is admitted or activated.']}
 atomic(ROOT/'authorization.json',enc(auth))
 post=deepcopy(live)
 for d,p in records:
  post['entries'].append({'admission_decision_ref':DECISION_ID,'definition_id':d['definition_id'],'lifecycle_state':'admitted','path':rel(p),'sha256':sha(p),'term':d['term'],'version':d['version']}); post['current_lookup'][d['definition_id']]=f"{d['definition_id']}@{d['version']}"
 post['entries'].sort(key=lambda x:(x['definition_id'],x['version'])); post['current_lookup']=dict(sorted(post['current_lookup'].items())); post['status']='owner-admitted'; post['authority_effect']='one-hundred-eighty-six-exact-definition-versions-canonical'; post['admission_decision_ref']=DECISION_ID; post['predecessor']={'path':rel(REGISTRY),'sha256':sha(REGISTRY),'entry_count':179,'current_count':173,'admission_decision_ref':live['admission_decision_ref']}; post['source_direction']={'canonical':'registry.json','human_projection':'DEFINITIONS-INDEX.md','projection_policy':'generated-only','generator_ref':'cal.generator.definition-specialization-resolution-admission/v1'}; post['claim_ceiling']='This registry contains 186 admitted Definition versions and selects 180 current identities. CAL-DECISION-0066 also admits the exact specialization resolution overlay. It does not admit or rebind Artifact Types, instances, relations, qualifiers, Project Identity, workflows, runtimes, or consumers.'
 drift=deepcopy(load(DRIFT)); drift['admission_decision_ref']=DECISION_ID; drift['record_id']='CAL-DEFINITION-DRIFT-AUDIT-POST-SPECIALIZATION-RESOLUTION-V1'; drift['findings'].append({'finding_id':'STEP3-SPECIALIZATION-RESOLUTION-POST-001','severity':'resolved','status':'admitted','condition':'Seven positive Definitions are admitted; three Craft workflow meanings specialize their generic cal.* meanings; Ledger and Withdrawal Record are resolved; Project Identity remains v1.','target':DECISION_ID,'remediation':'Rebind affected Artifact Type candidates through their owner route and generate the effective-state registry before carrier admission.'}); drift['summary'].update({'current_definition_terms':180,'definition_versions':186,'new_definition_identities':148,'new_definition_versions_admitted':152,'generic_ledger_primitive':'admitted-current','definition_specialization_resolution':'admitted-overlay','workflow_specialization_overlaps':'3-resolved','project_identity_epoch':'retain-v1'}); drift['source_direction']={'canonical':'drift-audit.json','human_projection':'DEFINITION-DRIFT-AUDIT.md','projection_policy':'generated-only','generator_ref':'cal.generator.definition-specialization-resolution-admission/v1'}; drift['claim_ceiling']='This audit establishes the exact Step 3 Definition and resolution overlay admission. It does not establish Artifact Type rebinding, carrier admission, relation, qualifier, runtime, or consumer conformance.'
 backups={p:p.read_bytes() for p in [REGISTRY,INDEX,DRIFT,DRIFT_MD]}; created=[ROOT/x for x in ['authorization.json','decision.json','DECISION.md','receipts/validation.json']]
 try:
  atomic(REGISTRY,enc(post)); atomic(INDEX,render_index(post).encode()); drift['registry_sha256']=sha(REGISTRY); atomic(DRIFT,enc(drift)); atomic(DRIFT_MD,render_drift(drift).encode())
  decision={'schema_version':'cyberalchemy-lab-definition-resolution-admission-decision/v1','decision_id':DECISION_ID,'title':'Definition specialization and identity resolution admission','status':'owner-admitted','authority_effect':'seven-definitions-and-exact-resolution-overlay-admitted','authorization':exact(ROOT/'authorization.json'),'admitted_definitions':[{'definition_ref':f"{d['definition_id']}@{d['version']}",'path':rel(p),'sha256':sha(p)} for d,p in records],'resolution_overlay':exact(RESOLUTION),'resolution_effects':{'positive_definition_bindings':5,'ledger':'positive-abstract-definition','withdrawal_record':'positive-definition','workflow_specializations':3,'workflow_successions':0,'project_identity_epoch':'retain-v1'},'registry_postimage':exact(REGISTRY),'index_postimage':exact(INDEX),'drift_audit_postimage':exact(DRIFT),'admission_result':{'definitions_admitted':7,'canonical_definition_versions':186,'current_definition_identities':180,'resolution_overlays_admitted':1,'artifact_types_admitted':0,'artifact_types_rebound':0,'relation_kinds_admitted':0,'consumer_activations':0,'result':'complete'},'excluded_effects':auth['excluded_effects'],'claim_ceiling':post['claim_ceiling'],'source_direction':{'canonical':'decision.json','human_projection':'DECISION.md','projection_policy':'generated-only','generator':'apply.py'}}
  atomic(ROOT/'decision.json',enc(decision)); atomic(ROOT/'DECISION.md',('\n'.join(['<!-- GENERATED FILE: canonical data is decision.json. -->','','# Definition specialization and identity resolution admission','',f'- Decision: `{DECISION_ID}`','- Status: `owner-admitted`','- Definitions admitted: `7`','- Resolution overlays admitted: `1`','- Workflow specialization pairs: `3`','- Project Identity epoch: `retain-v1`','- Artifact Types admitted or rebound: `0`','','## Claim ceiling','',post['claim_ceiling'],''])).encode())
  rc=subprocess.run([sys.executable,str(ROOT/'validate.py')],cwd=LAB).returncode
  if rc: raise RuntimeError('post-admission validation failed')
 except Exception:
  for p,b in backups.items(): atomic(p,b)
  for p in created: p.unlink(missing_ok=True)
  raise
 return 0
if __name__=='__main__': raise SystemExit(main())
