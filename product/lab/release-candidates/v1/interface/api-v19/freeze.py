"""Freeze retained declaration/raw-source successor before owned API effects."""
import ast,hashlib,importlib.metadata,json,platform
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5];RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p.read_bytes())}
def put(p,v):p.open('x').write(json.dumps(v,indent=2,sort_keys=True)+'\n')
def methods(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(p.read_bytes())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def main():
 assert not (HERE/'source-manifest.json').exists();parent=HERE.parent/'api-v18';old=json.loads((parent/'source-manifest.json').read_bytes())
 assert bind(parent/'source-manifest.json')['sha256']=='07a14881e21fe3c0db88ff55e0b3b982de05959cbd68a931efa89a2c3368e445'
 terminal=json.loads((RUN/'custody-api-diagnostic-terminal-0002.json').read_bytes());diagnostic=json.loads((RUN/'custody-api-diagnostic-result-0002.json').read_bytes())
 assert terminal['exit_code']==0 and terminal['result_binding']==bind(RUN/'custody-api-diagnostic-result-0002.json') and terminal['log_binding']==bind(RUN/'custody-api-diagnostic-0002.log')
 assert diagnostic['owned_resources_closed'] and diagnostic['projection']['result']=='FAIL'
 failures=[e for e in diagnostic['events'] if e['result']=='FAIL'];assert failures and {e['category'] for e in failures}=={'definition'}
 assert len(diagnostic['events'])==582
 previous=json.loads((parent/'contract-profile.json').read_bytes());profile={**previous,'files':[]}
 for row in previous['files']:
  p=ROOT/row['path'];profile['files'].append(bind(HERE/p.relative_to(parent) if p.is_relative_to(parent) else p))
 assert len(profile['implemented_operations'])==12;assert len({r['path'] for r in profile['files']})==len(profile['files'])
 profile['claim_ceiling']='Twelve existing candidate handlers; raw original instance bytes, explicit Definition/RelationKind declaration representations, complete disposable SQL and ephemeral Session custody. Full129 verification and independent audit pending;22 APIs remain.'
 put(HERE/'contract-profile.json',profile)
 rows={r['path']:r for r in old['files']}
 def add(b):assert rows.get(b['path'],b)==b,b['path'];rows[b['path']]=b
 add(bind(parent/'source-manifest.json'))
 for p in [RUN/'context-R03-custody-api-0004.json',RUN/'derive-R03-custody-api-0003.py',RUN/'custody-api-terminal-0001.json',RUN/'custody-api-failure-analysis-0002.json',parent.parent/'api-v17/checks-0001.log',parent.parent/'api-v17/receipts/checks.json',parent.parent/'api-v17/receipts/wire-observations.json',RUN/'context-R03-custody-api-diagnostic-0002.json',RUN/'diagnose-R03-custody-api-0002.py',RUN/'custody-api-diagnostic-source-0002.json',RUN/'custody-api-diagnostic-terminal-0002.json',RUN/'custody-api-diagnostic-result-0002.json',RUN/'custody-api-diagnostic-0002.log']:add(bind(p))
 deltas={}
 for n in ['test_preparation.py','test_preparation_corrected.py','run_session_checks.py','test_custody_sessions.py','test_custody_api.py']:
  assert methods(HERE/n)==methods(parent/n);deltas[n]={'methods':len(methods(HERE/n)),'changed_test_method_ASTs':[]}
 for p in HERE.rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts:
   if p.suffix=='.py':ast.parse(p.read_bytes())
   add(bind(p))
 for row in rows.values():assert bind(ROOT/row['path'])==row
 env={'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')};assert env==old['environment']
 put(HERE/'source-manifest.json',{'schema_version':'lab-original-source-API-source/v1-candidate','files':sorted(rows.values(),key=lambda r:r['path']),'environment':env,'parent_source_binding':bind(parent/'source-manifest.json'),'profile_binding':bind(HERE/'contract-profile.json'),'correction_context_binding':bind(RUN/'context-R03-custody-api-0004.json'),'terminal_diagnostic_binding':bind(RUN/'custody-api-diagnostic-terminal-0002.json'),'original_test_method_derivation':deltas,'expected_full_test_methods':129,'full_parent_suite_pending_at_freeze':True,'final_independent_audit_requires_complete_parent_terminal_and_retained_failure_outputs':True,'original_operations':34,'implemented_operations':12,'remaining_operations':22,'frozen_before_owned_API_effects':True,'authority_effect':'none','actual_owner_outcome':None,'task_complete':False})
 print(json.dumps({'result':'FROZEN','files':len(rows),'source_binding':bind(HERE/'source-manifest.json'),'profile_binding':bind(HERE/'contract-profile.json'),'expected_tests':129}),flush=True)
if __name__=='__main__':main()
