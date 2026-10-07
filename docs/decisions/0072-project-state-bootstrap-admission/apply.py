#!/usr/bin/env python3
"""Preflight or atomically apply Decision 0072."""
from __future__ import annotations
import argparse,hashlib,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;LAB=HERE.parents[2];P=HERE/'proposal';AUTH=HERE/'authorization.json';FINAL=LAB/'authority/admissions/project-state-bootstrap/v1';DECISION='CAL-DECISION-0072-PROJECT-STATE-BOOTSTRAP-ADMISSION';DREG=LAB/'authority/definitions/registry.json';DINDEX=LAB/'authority/definitions/DEFINITIONS-INDEX.md'
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def verify():
 r=subprocess.run([sys.executable,str(P/'validate.py')],cwd=LAB);assert r.returncode==0,'proposal validation failed';v=load(P/'validation.json');p=load(P/'proposal.json');a=load(AUTH)
 if v['result']!='PASS' or v['materials']['proposal_sha256']!=sha(P/'proposal.json'):raise RuntimeError('proposal validation stale')
 req={'schema_version':'cyberalchemy-lab-owner-authorization/v1','decision_id':DECISION,'authorized':True,'proposal_path':str((P/'proposal.json').relative_to(LAB)),'proposal_sha256':sha(P/'proposal.json')}
 for k,x in req.items():
  if a.get(k)!=x:raise RuntimeError(f'authorization mismatch at {k}')
 if a['interpreted_scope']!=p['proposed_effects'] or not a.get('verbatim_user_authorization','').strip():raise RuntimeError('authorization scope mismatch')
 return p,a
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');args=ap.parse_args();p,a=verify()
 if not args.apply:print(json.dumps({'result':'PASS','mode':'preflight','proposal_sha256':sha(P/'proposal.json'),'bundle_sha256':sha(P/'bundle-postimage/bundle.json')},sort_keys=True));return 0
 old_reg=DREG.read_bytes();old_index=DINDEX.read_bytes();created=False
 try:
  if FINAL.exists():
   if sha(FINAL/'bundle.json')!=p['postimage']['sha256']:raise RuntimeError('different final bundle exists')
  else:
   FINAL.parent.mkdir(parents=True,exist_ok=True);stage_root=Path(tempfile.mkdtemp(prefix='.decision-0072-',dir=FINAL.parent));stage=stage_root/'v1';shutil.copytree(P/'bundle-postimage',stage)
   if sha(stage/'bundle.json')!=p['postimage']['sha256']:raise RuntimeError('staged bundle mismatch')
   os.replace(stage,FINAL);shutil.rmtree(stage_root,ignore_errors=True);created=True
  os.replace(FINAL/'registries/definition-registry.json',DREG)
  shutil.copyfile(P/'bundle-postimage/registries/definition-registry.json',FINAL/'registries/definition-registry.json')
  os.replace(FINAL/'registries/DEFINITIONS-INDEX.md',DINDEX)
  shutil.copyfile(P/'bundle-postimage/registries/DEFINITIONS-INDEX.md',FINAL/'registries/DEFINITIONS-INDEX.md')
  decision={'schema_version':'cyberalchemy-lab-project-state-bootstrap-decision/v1','decision_id':DECISION,'title':'Admit the Decision 0071 Project State bootstrap','status':'owner-admitted','decided_at':'2026-10-06','owner_ref':'role:repository-owner','authority_effect':'project-state-bootstrap-admission-only','authorization':{'path':str(AUTH.relative_to(LAB)),'sha256':sha(AUTH),'verbatim_user_authorization':a['verbatim_user_authorization']},'proposal':{'path':str((P/'proposal.json').relative_to(LAB)),'sha256':sha(P/'proposal.json')},'admission_bundle':{'path':str((FINAL/'bundle.json').relative_to(LAB)),'sha256':sha(FINAL/'bundle.json')},'effects':p['proposed_effects'],'effective_registries':{'definitions':{'path':str(DREG.relative_to(LAB)),'sha256':sha(DREG)},'artifact_types':{'path':str((FINAL/'registries/artifact-type-registry.json').relative_to(LAB)),'sha256':sha(FINAL/'registries/artifact-type-registry.json')}},'current_project_state_ref':'project-state:cyberalchemy-v2-to-lab-migration:decision-0071','historical_project_state_ref':'project-state:cyberalchemy-v2-to-lab-migration:decision-0070','next_successor_obligation':'Decision 0072 and this bundle enter the next Project State successor through semantic and governance events; the Decision 0071 state remains immutable.','excluded_effects':p['excluded_effects'],'claim_ceiling':'Decision 0072 closes the first Project State bootstrap only. It creates no Agent session, evidence claim, ontology projection, implementation adoption, or runtime activation.'};dump(HERE/'decision.json',decision)
  (HERE/'DECISION.md').write_text(f"# Decision 0072: Project State bootstrap admission\n\nStatus: **owner-admitted**\n\nCurrent Project State: `project-state:cyberalchemy-v2-to-lab-migration:decision-0071`\n\n- Definitions admitted: `2`\n- Artifact Types admitted: `2`\n- Artifact instances admitted: `3`\n- Typed Relations admitted: `2`\n- Semantic events admitted: `1`\n- Governance events admitted: `1`\n- Runtime activations: `0`\n\nThe Decision 0070 state is historical. Decision 0072 belongs in the next immutable successor.\n\n## Claim ceiling\n\n{decision['claim_ceiling']}\n")
  receipt={'schema_version':'cyberalchemy-lab-project-state-bootstrap-application-receipt/v1','decision_id':DECISION,'result':'PASS','applied_at':'2026-10-06','effects':p['proposed_effects'],'materials':{'decision_sha256':sha(HERE/'decision.json'),'bundle_sha256':sha(FINAL/'bundle.json'),'authorization_sha256':sha(AUTH),'proposal_sha256':sha(P/'proposal.json'),'definition_registry_sha256':sha(DREG),'definition_index_sha256':sha(DINDEX)},'claim_ceiling':decision['claim_ceiling']};dump(HERE/'receipts/application.json',receipt);print(json.dumps({'result':'PASS','mode':'applied',**receipt['materials'],**p['proposed_effects']},sort_keys=True));return 0
 except Exception:
  DREG.write_bytes(old_reg);DINDEX.write_bytes(old_index)
  if created:shutil.rmtree(FINAL,ignore_errors=True)
  raise
if __name__=='__main__':raise SystemExit(main())
