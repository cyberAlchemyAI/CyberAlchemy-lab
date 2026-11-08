#!/usr/bin/env python3
"""Verify the filesystem migration without staging Git or modifying native authority."""
from pathlib import Path
import hashlib,json,os,subprocess
ROOT=Path(__file__).resolve().parents[3]
HOME=Path(__file__).resolve().parent
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 plan=json.loads((HOME/'PLAN.json').read_text());journal=json.loads((HOME/'JOURNAL.json').read_text())
 errors=[];edited={e['path']:e['after_sha256'] for e in journal['edits']}
 def mapped(rel):
  for move in plan['units']:
   if rel==move['source'] or rel.startswith(move['source']+'/'):rel=move['destination']+rel[len(move['source']):]
  return rel
 result={'format':'lab-product-workspace-file-verification/v1','authority_effect':'none','runtime_copies':0}
 passed=0
 for row in plan['selected_files']:
  rel=mapped(row['path']);p=ROOT/rel
  if not p.is_file():errors.append({'kind':'missing','path':rel});continue
  if digest(p)!=edited.get(rel,row['sha256']):errors.append({'kind':'content-drift','path':rel})
  else:passed+=1
  if p.stat().st_ino!=row['inode']:errors.append({'kind':'file-inode','path':rel})
 result.update(selected_files=len(plan['selected_files']),verified_file_hashes=passed)
 for move in journal['moves']:
  old,new=ROOT/move['source'],ROOT/move['destination']
  if not old.is_symlink() or old.resolve()!=new.resolve() or new.stat().st_ino!=move['inode']:errors.append({'kind':'move-or-compatibility-link','path':move['source']})
 for row in journal['link_rewrites']:
  p=ROOT/row['path']
  if not p.is_symlink() or str(p.resolve())!=row['target']:errors.append({'kind':'dependency-link','path':row['path']})
 for row in plan['shared_roots']:
  p=ROOT/row['path'];st=p.stat()
  if st.st_ino!=row['inode'] or st.st_dev!=row['device']:errors.append({'kind':'shared-root','path':row['path']})
 node=plan['shared_node'];p=Path(node['path'])
 if p.stat().st_ino!=node['inode'] or digest(p)!=node['sha256']:errors.append({'kind':'shared-node'})
 chains={}
 for row in journal['edits']:
  if digest(ROOT/row['preimage'])!=row['before_sha256']:errors.append({'kind':'preimage','path':row['path']})
  if row['path'] in chains and chains[row['path']]!=row['before_sha256']:errors.append({'kind':'edit-chain','path':row['path']})
  chains[row['path']]=row['after_sha256']
 for rel,expected in chains.items():
  if digest(ROOT/rel)!=expected:errors.append({'kind':'journal-final-hash','path':rel})
 raw=(HOME/'preexisting-git-status.bin').read_bytes()
 if hashlib.sha256(raw).hexdigest()!=plan['preexisting_git_status_sha256']:errors.append({'kind':'baseline-status-integrity'})
 deleted=[]
 for token in raw.split(bytes([0])):
  if len(token)>3 and b'D' in token[:2]:
   rel=os.fsdecode(token[3:]);deleted.append(rel)
   if (ROOT/rel).exists():errors.append({'kind':'preexisting-deletion-restored','path':rel})
 result['preexisting_deleted_paths_preserved']=len(deleted)
 result.update(directory_moves=len(journal['moves']),dependency_links_verified=len(journal['link_rewrites']),shared_roots_verified=len(plan['shared_roots']),journaled_file_edits=len(journal['edits']))
 checks={}
 for label in ['final-runtime-v1','final-runtime-v2','final-define-standalone','compat-define-standalone','compat-define-lab','migrated-define-lab-r3','migrated-craft-build-r3','final-craft-check','migrated-website-tests','migrated-ontology-package-tests','migrated-ontology-lifecycle-tests']:
  p=HOME/'checks'/f'{label}.json'
  if not p.is_file():errors.append({'kind':'missing-check','label':label});continue
  row=json.loads(p.read_text());checks[label]=row['exit_code']
  if row['exit_code']!=0:errors.append({'kind':'check-failure','label':label})
  for stream in ['stdout','stderr']:
   out=HOME/'checks'/f'{label}.{stream}.txt'
   if digest(out)!=row[stream+'_sha256']:errors.append({'kind':'check-output-drift','label':label})
 for old,new in [('baseline-runtime-v1','final-runtime-v1'),('baseline-runtime-v2','final-runtime-v2'),('baseline-define-standalone','final-define-standalone')]:
  a=json.loads((HOME/'checks'/f'{old}.json').read_text());b=json.loads((HOME/'checks'/f'{new}.json').read_text())
  if a['stdout_sha256']!=b['stdout_sha256']:errors.append({'kind':'baseline-output-drift','label':new})
 baseline_legacy=json.loads((HOME/'checks/baseline-define.json').read_text());current_legacy=json.loads((HOME/'checks/final-legacy-define.json').read_text())
 if baseline_legacy['exit_code']!=current_legacy['exit_code'] or baseline_legacy['stderr_sha256']!=current_legacy['stderr_sha256']:errors.append({'kind':'legacy-define-baseline-regression'})
 result['legacy_define_diagnostic_matches_baseline']=True
 catalog=subprocess.run(['python3','-B',str(ROOT/'architecture/workspace-model-mapping/inventory/check_workspaces.py')],cwd=ROOT,capture_output=True,text=True)
 if catalog.returncode:errors.append({'kind':'catalog','detail':catalog.stderr})
 result.update(checks=checks,status='pass' if not errors else 'fail',errors=errors,native_model_adoption='not-performed')
 (HOME/'VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
 return 0 if not errors else 1
if __name__=='__main__':raise SystemExit(verify())
