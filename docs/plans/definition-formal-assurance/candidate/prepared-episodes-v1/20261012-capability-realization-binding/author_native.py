"""Native source-bound authoring only after actual prepared model success and CI full audit0."""
from pathlib import Path
import hashlib,json,shutil,sys
root=Path.cwd();p=Path(__file__).resolve().parent;prepared=p/'prepared';base=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1';prev=base/'definitions/cal.definition.capability-instance';unit=base/'definitions/cal.definition.capability-realization-binding'
sys.path.insert(0,str(prev));import build_candidate as b
prior=json.loads((prev/'delivery-manifest.json').read_bytes());b.unchanged(prior['files']);assert len(prior['files'])==10287 and not unit.exists()
audit_path=p.parent/'20261012-capability-instance/full-delivery-audit-command-result.json';audit=json.loads(audit_path.read_bytes());assert audit['exit_code']==0 and not(audit_path.parent/audit['stderr']).read_bytes()
results=json.loads((p/'prepared-check-results.json').read_bytes());assert [x['check'] for x in results]==['context','build','model'] and all(x['exit_code']==0 and not(p/x['stderr']).read_bytes() for x in results)
control=json.loads((prepared/'model-controls.json').read_bytes());assert control['control_count']==201 and len(control['nonentailment_countermodels'])==33
snapshot=b.snapshot();assert b.r.verify(snapshot,root)['files']==201 and len(list((base/'definitions').glob('*/t.json')))==109
context=json.loads((prepared/'context.json').read_bytes());b.unchanged(context['sources']);source=b.source_ref(snapshot,'cal.definition.capability-realization-binding');assert source==context['source_selection']
work=json.loads((root/'docs/plans/definition-formal-assurance/candidate/foundations-first-v1/swu-manifest.json').read_bytes());swu=next(x for x in work['units'] if x['id']==context['unit_id']);assert swu['outputs']==[(unit/'t.json').relative_to(root).as_posix()] and swu['write_scope']==context['write_scope']
for binding in context['prerequisite_receipts']:
 b.unchanged([binding['receipt_ref']]);assert json.loads((root/binding['receipt_ref']['path']).read_bytes())['task_result']==binding['result'] and binding['result'].startswith('PASS')
failed=[b.ref(q) for q in sorted((p/'retained-prepared-model-construction-1').rglob('*')) if q.is_file()];assert len(failed)==26
assert json.loads((p/'retained-prepared-model-construction-1/observation.json').read_bytes())['actual_model_exit']==1
successful=[b.ref(q) for q in sorted(prepared.iterdir()) if q.is_file()]+[b.ref(p/'prepared-check-results.json')]+[b.ref(p/x[n]) for x in results for n in ['stdout','stderr']]+[b.ref(p/('prepared-'+x['check']+'-command-result.json')) for x in results]
context['sources'] += [b.ref(p/'author_native.py'),b.ref(prepared/'verify_source_checks.py'),b.ref(p/'prepared-check-results.json')]
context['retained_preparation_failure_refs']=failed;context['retained_successful_preparation_refs']=successful;context['retained_successful_native_stage_refs']=[]
context['pre_execution_check'].update({'output_absent_before_creation':True,'prepared_source_and_model_check_exit_code':0,'prior_candidate_files_preserved':10287})
remaining=[x for x in work['units'] if x['kind']=='definition-T' and x['definition_id']!=source['definition_id'] and not(base/'definitions'/x['definition_id']/'t.json').exists()];context['next_definition_priority']=remaining[0]['id']
unit.mkdir()
with (unit/'context.json').open('x') as f:json.dump(context,f,indent=2,sort_keys=True);f.write('\n')
for name in ['build_candidate.py','verify_candidate.py','verify_source_checks.py']:
 with (unit/name).open('xb') as f:f.write((prepared/name).read_bytes())
with (unit/'author_candidate.py').open('xb') as f:f.write(Path(__file__).read_bytes())
b.unchanged(prior['files']+context['sources']+failed+successful)
print(json.dumps({'result':'PASS-exact-C66-CRB-native-author','prior_files':10287,'source_files':201,'prepared_controls':201,'queries':33,'retained_failed_prepared_model_construction':1,'actual_instance_created':False,'next_definition_priority':remaining[0]['id']},indent=2))
