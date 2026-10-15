"""Close all original candidate O07 obligations only from current actual proof."""
import re,unittest
from base import *

def run(pin):
 source_guard(pin);files={};checks=[]
 def capture(b):
  bound(b,external=True);require(b['path'] not in files or files[b['path']]==b['sha256'],'evidence epoch mismatch');files[b['path']]=b['sha256']
 def check(name,x):require(x,name);checks.append({'test':name,'result':'PASS'})
 capture(binding(HERE/'manifest.json'))
 for b in load(HERE/'manifest.json')['files']:capture(b)
 import test_audit,test_native
 declared=set()
 for cls in [test_audit.CoherenceGuards,test_native.NativeCoherenceGuards]:
  declared.update(t.id().split('.')[-1] for t in unittest.defaultTestLoader.loadTestsFromTestCase(cls))
 log=(HERE/'proof/guards.stderr').read_text();observed=re.findall(r'^(test_\S+) \([^\n]+\) \.\.\. ok$',log,re.M)
 check('every declared no-collapse/native guard actually passed',len(declared)==len(observed) and set(observed)==declared and re.search(r'Ran '+str(len(declared))+r' tests in [0-9.]+s\n\nOK\s*$',log) is not None)
 terminal=load(HERE/'proof/terminal-observations.json');check('all six producer processes terminal successful',terminal['exit_codes']=={k:0 for k in ['guards','rebuild-warm','rebuild-cold','audit-warm','audit-cold','queries']})
 rebuilt=[load(HERE/'proof'/('rebuild-'+n)/'result.json') for n in ['warm','cold']]
 check('two actual independent complete original-source constructions',all(r['result']=='PASS' and r['files_compared']==225 and r['same_original_bytes'] and r['source_construction']['carriers_checked']==220 and r['source_construction']['items_reconciled']==140 and r['source_construction']['blocked_revisions']==9 for r in rebuilt))
 for name in ['warm','cold']:
  original_files={p.relative_to(ORIGINAL).as_posix():p.read_bytes() for p in ORIGINAL.rglob('*') if p.is_file()}
  output=HERE/'proof'/('rebuild-'+name)/'package';actual={p.relative_to(output).as_posix():p.read_bytes() for p in output.rglob('*') if p.is_file()}
  check(name+' original-byte 225 file parity',actual==original_files and len(actual)==225)
 check('two cold native replay parity and exact separate cursors',all(r['native_checkpoint_parity']=='PASS' and r['semantic_cursor']==r['governance_cursor']==88 and r['owned_native_stores_removed'] and not r['execution_locator_relocation']['original_scope_changed'] for r in rebuilt))
 audits=[load(HERE/'proof'/('audit-'+n+'.json')) for n in ['warm','cold']]
 check('fresh repeated 31-check diagnostic joins equal',audits[0]==audits[1] and audits[0]['result']=='PASS' and len(audits[0]['checks'])==31)
 queries=load(HERE/'proof/queries/result.json');check('six fresh query processes and ten original question answers',queries['result']=='PASS' and queries['actual_fresh_processes']==6 and len(queries['processes'])==6 and queries['written_question_count']==5 and queries['answer_materializations']==10 and queries['same_original_answers'] and queries['same_independent_warm_cold_answers'])
 for row in queries['processes']:
  current=original(row['current_result_binding']);prior=original(row['original_result_binding'])
  for name,q in current['questions'].items():check(row['repetition']+' '+row['scope']+' '+name+' actual answer bytes identical',bound(q['response_binding'])==bound(prior['questions'][name]['response_binding']))
 check('source execution activation and current permission excluded',all(r['source_execution'] is False and r['canonical_effects_applied']==0 and r['actual_owner_outcome'] is None for r in rebuilt) and not queries['current_action_permission'] and not queries['runtime_activation'] and not queries['Session_memory_restored'])
 for folder in [HERE/'proof',COVERAGE]:
  for p in folder.rglob('*'):
   if p.is_file():capture(binding(p))
 capture(original(CONTEXT)['execution_locator_binding'])
 source_guard(pin)
 receipt={'schema_version':'lab-O07-selected-candidate-coherence/v1-candidate','task':'O07','result':'PASS','task_complete':True,'completion_mode':'candidate-implementation-verified',
  'authority_effect':'none','actual_owner_outcome':None,'canonical_effects_applied':0,'runtime_activation':False,'source_retirements':0,
  'admitted_coherence':False,'original_operational_owner_obligation_route':'A03','tests':len(declared),'guard_checks':[{'test':name,'result':'PASS'} for name in observed],
  'join_checks':audits[0]['checks'],'validation_checks':checks,'counts':audits[0]['counts'],'source_manifest_binding':binding(HERE/'manifest.json'),
  'actual_independent_source_rebuilds':2,'files_compared_per_rebuild':225,'actual_fresh_query_processes':6,'original_question_count':5,'answer_materializations':10,
  'files':[{'path':p,'sha256':h} for p,h in sorted(files.items())],'source_bindings':original(CONTEXT)['source_bindings'],'source_drift':[],
  'remaining_obligations':[],'final_owner_binding_residue':original(CONTEXT)['final_owner_binding_residue'],
  'downstream_obligations':['Complete final S02 registry/owner/implementation/environment/entrypoint/postimage/Decision core closure before actual R08 response.','Apply exact positive R08 members only in A01; admitted operational coherence remains A03.','Complete remaining 30 API handlers and operator/client/packaging/acceptance criteria; no whole-plan or owner usability claim.'],
  'claim_ceiling':'Original selected candidate O07 reconstruction/parity/coverage/freshness and source accounting only; all missing/excluded/deferred and query gaps remain explicit. No source meaning/body import/execution, private/public export, current operation or Lesson permission, new global relation, actual owner outcome/adoption/admitted coherence, activation, retirement, human pilot or complete-repository closure.'}
 emit(ONTOLOGY/'receipts/coherence-closure.json',receipt)
 print(json.dumps({'result':'PASS','tests':len(declared),'join_checks':len(audits[0]['checks']),'validation_checks':len(checks),'files':len(files),'receipt_binding':binding(ONTOLOGY/'receipts/coherence-closure.json')}))

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--manifest-sha256',required=True);a=p.parse_args();run(a.manifest_sha256)
