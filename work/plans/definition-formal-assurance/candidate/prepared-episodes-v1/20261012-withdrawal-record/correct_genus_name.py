"""Retain prepared JSON contract failure; keep repository BASE and genus formula distinct."""
from pathlib import Path
import json,hashlib,shutil,ast
p=Path(__file__).resolve().parent;a=p/'retained-attempts/001-genus-shadowed-repository-base';a.mkdir(parents=True)
names=['prepare_typed.py','prepare_model.py','check_prepared.py','capture_precheck.py','prepared/build_candidate.py','prepared/verify_candidate.py','prepared-check-command-result.json','prepared-check-stdout.txt','prepared-check-stderr.txt'];refs=[]
for n in names:
 target=a/n;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p/n,target);refs.append({'path':n,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
with (a/'attempt.json').open('x') as f:json.dump({'status':'retained-actual-prepared-contract-failure','exit_code':json.loads((a/'prepared-check-command-result.json').read_text())['exit_code'],'reason':'Genus BASE variable shadowed repository BASE path; precheck restored helper BASE path and exposed non-JSON formula','files':refs,'correction':'Alpha-rename genus formula to GENUS; keep repository path BASE unchanged','semantic_theory_change':'none','checker_limits_changed':False,'native_unit_created':False},f,indent=2);f.write('\n')
for q in [p/'prepare_typed.py',p/'prepared/build_candidate.py']:
 s=q.read_text().replace('BASE=selected(', 'GENUS=selected(').replace("'genus':BASE", "'genus':GENUS").replace("'/scope/applicability':(BASE", "'/scope/applicability':(GENUS").replace("'/voices/scientific_formal/testable_conditions/0':(BASE", "'/voices/scientific_formal/testable_conditions/0':(GENUS");ast.parse(s);q.write_text(s)
for n in ['prepared-check-command-result.json','prepared-check-stdout.txt','prepared-check-stderr.txt']:(p/n).unlink()
print('Retained prepared contract failure; genus/repository symbols separated without changing formulas.')
