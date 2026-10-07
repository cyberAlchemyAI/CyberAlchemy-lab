#!/usr/bin/env python3
"""Build the exact Decision 0072 Project State bootstrap admission postimage."""
from __future__ import annotations
import hashlib,json,shutil
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parent;HERE=ROOT.parent;LAB=HERE.parents[2]
CANDIDATE=LAB/'authority/project-state-transitions/candidates/0001-decision-0071-bootstrap'
POST=ROOT/'bundle-postimage';DECISION='CAL-DECISION-0072-PROJECT-STATE-BOOTSTRAP-ADMISSION'
FINAL='authority/admissions/project-state-bootstrap/v1'
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def dump(p,v):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def cp(src,dst):Path(dst).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)

def main():
 m=load(CANDIDATE/'transition.json');v=load(CANDIDATE/'receipts/validation.json')
 if v['result']!='PASS' or v['materials']['transition_sha256']!=sha(CANDIDATE/'transition.json'):raise RuntimeError('candidate validation is stale')
 if POST.exists():shutil.rmtree(POST)
 cp(CANDIDATE/'transition.json',POST/'source-transition.json');cp(CANDIDATE/'TRANSITION.md',POST/'TRANSITION.md');cp(CANDIDATE/'receipts/validation.json',POST/'receipts/candidate-validation.json')
 cp(CANDIDATE/'definition-registry-postimage.json',POST/'registries/definition-registry.json');cp(CANDIDATE/'DEFINITIONS-INDEX-postimage.md',POST/'registries/DEFINITIONS-INDEX.md');cp(CANDIDATE/'artifact-type-registry-postimage.json',POST/'registries/artifact-type-registry.json')
 for item in m['definitions']:
  src=LAB/item['path'];base=POST/'definitions'/Path(item['path']).parent.parent.name
  cp(src,base/'definition.json');cp(src.with_name('DEFINITION.md'),base/'DEFINITION.md')
 for item in m['artifact_types']:
  base=(LAB/item['artifact_path']).parent;dst=POST/'artifact-types'/item['semantic_kind']
  for rel in ['artifact.json','schema.json','ARTIFACT.md','fixtures/valid/record.json','fixtures/valid/RECORD.md','fixtures/invalid/authority.json','fixtures/invalid/extra-field.json']:cp(base/rel,dst/rel)
 for item in m['artifact_instances']:
  src=LAB/item['path'];cp(src,POST/'instances/artifacts'/src.name)
 for item in m['typed_relations']:
  src=LAB/item['path'];cp(src,POST/'instances/typed-relations'/src.name)
 dump(POST/'definition-admission.json',{'schema_version':'cyberalchemy-lab-definition-admission/v1','decision_id':DECISION,'status':'owner-admitted-postimage','authority_effect':'two-definition-admission-only','count':2,'entries':m['definitions'],'claim_ceiling':'Admits only the two exact Project event history Definitions.'})
 dump(POST/'artifact-type-admission.json',{'schema_version':'cyberalchemy-lab-artifact-type-admission/v1','decision_id':DECISION,'status':'owner-admitted-postimage','authority_effect':'two-artifact-type-admission-only','count':2,'entries':m['artifact_types'],'relation_endpoint_pairs_admitted':0,'runtime_activations':0,'claim_ceiling':'Admits only the two exact Project event history Artifact Types; no Relation Kind or endpoint extension is added.'})
 instance_entries=[]
 for item in m['artifact_instances']:
  src=LAB/item['path'];instance_entries.append({**item,'admitted_instance_path':f"{FINAL}/instances/artifacts/{src.name}",'lifecycle_state':'admitted-current','admission_decision_ref':DECISION})
 dump(POST/'artifact-instance-admission.json',{'schema_version':'cyberalchemy-lab-artifact-instance-admission/v1','decision_id':DECISION,'status':'owner-admitted-postimage','authority_effect':'project-state-bootstrap-instance-admission-only','count':3,'predecessor_transition':{'identity_ref':m['predecessor_state_ref'],'from':'admitted-current','to':'admitted-historical','bytes_preserved':True},'entries':instance_entries,'runtime_activations':0,'claim_ceiling':'Admits two histories and the Decision 0071 successor Project State; the initial Project State becomes historical without byte mutation.'})
 rel_entries=[]
 for item in m['typed_relations']:
  src=LAB/item['path'];rel_entries.append({**item,'admitted_instance_path':f"{FINAL}/instances/typed-relations/{src.name}",'lifecycle_state':'admitted-current','admission_decision_ref':DECISION})
 dump(POST/'typed-relation-admission.json',{'schema_version':'cyberalchemy-lab-typed-relation-instance-admission/v1','decision_id':DECISION,'status':'owner-admitted-postimage','authority_effect':'two-typed-relation-instance-admission-only','count':2,'entries':rel_entries,'relation_kinds_admitted':0,'claim_ceiling':'Admits only the exact successor-of and member-of relation instances.'})
 files=[]
 for p in sorted(x for x in POST.rglob('*') if x.is_file() and x.name!='bundle.json'):files.append({'path':str(p.relative_to(POST)),'sha256':sha(p)})
 counts={'definitions_admitted':2,'artifact_types_admitted':2,'artifact_instances_admitted':3,'typed_relation_instances_admitted':2,'semantic_events_admitted':1,'governance_events_admitted':1,'predecessor_project_states_historical':1,'runtime_activations':0}
 bundle={'schema_version':'cyberalchemy-lab-project-state-bootstrap-admission-bundle/v1','bundle_id':'CAL-PROJECT-STATE-BOOTSTRAP-BUNDLE-0072','decision_id':DECISION,'status':'owner-admitted-postimage','authority_effect':'project-state-bootstrap-admission-only','counts':counts,'integrity':m['integrity'],'files':files,'excluded_effects':m['excluded_effects'],'claim_ceiling':'Immutable Decision 0072 postimage. It takes effect only after exact authorization and atomic application.'};dump(POST/'bundle.json',bundle)
 proposal={'schema_version':'cyberalchemy-lab-project-state-bootstrap-admission-proposal/v1','decision_id':DECISION,'title':'Decision 0071 Project State bootstrap atomic admission','status':'candidate-awaiting-owner-authorization','authority_effect':'none','authorization_present':False,'inputs':{'transition':{'path':str((CANDIDATE/'transition.json').relative_to(LAB)),'sha256':sha(CANDIDATE/'transition.json')},'validation':{'path':str((CANDIDATE/'receipts/validation.json').relative_to(LAB)),'sha256':sha(CANDIDATE/'receipts/validation.json'),'result':'PASS'}},'postimage':{'path':str((POST/'bundle.json').relative_to(LAB)),'sha256':sha(POST/'bundle.json'),'final_path':FINAL},'proposed_effects':counts,'atomic_transaction':['Verify candidate and proposal','Verify owner authorization','Install immutable bundle','Advance the live Definition registry and generated index','Write Decision 0072 and receipts'],'excluded_effects':m['excluded_effects'],'claim_ceiling':'Proposal only; it has no authority effect before atomic application.'};dump(ROOT/'proposal.json',proposal)
 (ROOT/'PROPOSAL.md').write_text(f"# Decision 0072 proposal\n\n- Definitions: `2`\n- Artifact Types: `2`\n- Artifact instances: `3`\n- Typed Relations: `2`\n- Semantic events: `1`\n- Governance events: `1`\n- Runtime activations: `0`\n\nBundle: `{proposal['postimage']['sha256']}`\n\n{proposal['claim_ceiling']}\n")
 print(json.dumps({'bundle_sha256':proposal['postimage']['sha256'],**counts},sort_keys=True))
if __name__=='__main__':main()
