"""Create the native candidate only after four actual prepared checks and predecessor audit."""
from pathlib import Path
import json,sys
root=Path.cwd();p=Path(__file__).resolve().parent;prepared=p/'prepared';base=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1';prev=base/'definitions/cal.definition.capability-realization-binding';unit=base/'definitions/cal.definition.coordination-context'
sys.path.insert(0,str(prepared));import build_candidate as b
prior=json.loads((prev/'delivery-manifest.json').read_bytes());b.unchanged(prior['files']);assert len(prior['files'])==10389 and not unit.exists()
auditpath=p.parent/'20261012-capability-realization-binding/full-delivery-audit-command-result.json';audit=json.loads(auditpath.read_bytes());assert audit['exit_code']==0 and not(auditpath.parent/audit['stderr']).read_bytes()
results=json.loads((p/'prepared-check-results.json').read_bytes())+[json.loads((p/'prepared-source-command-result.json').read_bytes())];assert [row['check'] for row in results]==['context','build','model','source'] and all(row['exit_code']==0 and not(p/row['stderr']).read_bytes() for row in results)
controls=json.loads((prepared/'model-controls.json').read_bytes());assert controls['control_count']==198 and len(controls['nonentailment_countermodels'])==32
sourcecheck=json.loads((prepared/'source-checks.json').read_bytes());assert len(sourcecheck['checks'])==86 and sourcecheck['source_query_obligations']==74
snapshot=b.snapshot();assert b.r.verify(snapshot,root)['files']==201 and len(list((base/'definitions').glob('*/t.json')))==110
context=json.loads((prepared/'context.json').read_bytes());b.unchanged(context['sources']);assert context['source_selection']==b.source_ref(snapshot,'cal.definition.coordination-context')
work=json.loads((root/'docs/plans/definition-formal-assurance/candidate/foundations-first-v1/swu-manifest.json').read_bytes());swu=next(row for row in work['units'] if row['id']==context['unit_id']);assert swu['outputs']==[(unit/'t.json').relative_to(root).as_posix()] and swu['write_scope']==context['write_scope']
for binding in context['prerequisite_receipts']:
 b.unchanged([binding['receipt_ref']]);assert binding['result'].startswith('PASS') and json.loads((root/binding['receipt_ref']['path']).read_bytes())['task_result']==binding['result']
failed=[b.ref(path) for folder in ['retained-prepared-assembly-1','retained-prepared-model-construction-2'] for path in sorted((p/folder).rglob('*')) if path.is_file()]
assert len(failed)==42
assert json.loads((p/'retained-prepared-assembly-1/observation.json').read_bytes())['assembly_exit_code']==1 and json.loads((p/'retained-prepared-model-construction-2/observation.json').read_bytes())['actual_model_exit']==1
successful=[b.ref(path) for path in sorted(prepared.iterdir()) if path.is_file()]+[b.ref(p/'prepared-check-results.json')]+[b.ref(p/row[key]) for row in results for key in ['stdout','stderr']]+[b.ref(p/('prepared-'+row['check']+'-command-result.json')) for row in results]
dirtypath=p.parent/'20261012-project/unrelated-tracked-work.json';dirty=json.loads(dirtypath.read_bytes());b.unchanged(dirty['refs']);assert len(dirty['refs'])==30
context['sources']+=[b.ref(Path(__file__)),b.ref(prepared/'verify_source_checks.py'),b.ref(p/'prepared-check-results.json'),b.ref(p/'prepared-source-command-result.json'),b.ref(p/'ARE-native-types-boundary.json'),b.ref(dirtypath)]
context['retained_preparation_failure_refs']=failed;context['retained_successful_preparation_refs']=successful;context['retained_successful_native_stage_refs']=[]
context['pre_execution_check'].update({'output_absent_before_creation':True,'prepared_source_and_model_check_exit_code':0,'prepared_independent_source_check_exit_code':0,'prior_candidate_files_preserved':10389})
remaining=[row for row in work['units'] if row['kind']=='definition-T' and row['definition_id']!=context['source_selection']['definition_id'] and not(base/'definitions'/row['definition_id']/'t.json').exists()];context['next_definition_priority']=remaining[0]['id']
unit.mkdir()
with (unit/'context.json').open('x') as f:json.dump(context,f,indent=2,sort_keys=True);f.write('\n')
for name in ['build_candidate.py','verify_candidate.py','verify_source_checks.py']:
 with (unit/name).open('xb') as f:f.write((prepared/name).read_bytes())
with (unit/'author_candidate.py').open('xb') as f:f.write(Path(__file__).read_bytes())
b.unchanged(prior['files']+context['sources']+failed+successful+dirty['refs']);b.external_current(context)
print(json.dumps({'result':'PASS-exact-C18-C17-CoordinationContext-native-author','prior_files':10389,'source_files':201,'prepared_controls':198,'queries':32,'retained_failed_preparation_attempts':2,'actual_instance_created':False,'next_definition_priority':remaining[0]['id']},indent=2))
