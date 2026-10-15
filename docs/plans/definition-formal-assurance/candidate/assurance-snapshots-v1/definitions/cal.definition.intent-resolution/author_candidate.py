"""Author the native candidate only after actual prepared source/model checks."""
from pathlib import Path
import json,sys
root=Path.cwd();p=Path(__file__).resolve().parent;prepared=p/'prepared';sys.path.insert(0,str(prepared));import build_candidate as b
unit=b.BASE/'definitions/cal.definition.intent-resolution';prior=json.loads((b.BASE/'definitions/cal.definition.intent/delivery-manifest.json').read_bytes());b.unchanged(prior['files']);assert len(prior['files'])==10703 and not unit.exists()
previous=p.parent/'20261013-intent';audit=json.loads((previous/'full-delivery-audit-command-result.json').read_bytes());assert audit['exit_code']==0 and not(previous/audit['stderr']).read_bytes()
results=json.loads((p/'prepared-check-results.json').read_bytes());assert [r['check'] for r in results]==['context','build','model','source'] and all(r['exit_code']==0 and not(p/r['stderr']).read_bytes() for r in results)
controls=json.loads((prepared/'model-controls.json').read_bytes());sourcechecks=json.loads((prepared/'source-checks.json').read_bytes());assert controls['control_count']==183 and len(controls['nonentailment_countermodels'])==35 and len(sourcechecks['checks'])==97 and sourcechecks['source_query_obligations']==111
snap=b.snapshot();assert b.r.verify(snap,root)['files']==201 and len(list((b.BASE/'definitions').glob('*/t.json')))==113
context=json.loads((prepared/'context.json').read_bytes());b.unchanged(context['sources']);assert context['source_selection']==b.source_ref(snap,'cal.definition.intent-resolution')
workpath=root/'docs/plans/definition-formal-assurance/candidate/foundations-first-v1/swu-manifest.json';work=json.loads(workpath.read_bytes());swu=next(r for r in work['units'] if r['id']==context['unit_id']);assert swu['outputs']==[(unit/'t.json').relative_to(root).as_posix()] and swu['write_scope']==context['write_scope']
for binding in context['prerequisite_receipts']:b.unchanged([binding['receipt_ref']]);assert binding['result'].startswith('PASS') and json.loads((root/binding['receipt_ref']['path']).read_bytes())['task_result']==binding['result']
successful=[b.ref(path) for path in sorted(prepared.iterdir()) if path.is_file()]+[b.ref(p/'prepared-check-results.json')]+[b.ref(p/r[key]) for r in results for key in ['stdout','stderr']]+[b.ref(p/('prepared-'+r['check']+'-command-result.json')) for r in results]
dirtypath=p.parent/'20261012-project/unrelated-tracked-work.json';dirty=json.loads(dirtypath.read_bytes());assert len(dirty['refs'])==30;b.unchanged(dirty['refs'])
context['sources']+=[b.ref(Path(__file__)),b.ref(p/'prepared-check-results.json'),b.ref(dirtypath)];context['retained_preparation_failure_refs']=[];context['retained_successful_preparation_refs']=successful;context['retained_successful_native_stage_refs']=[];context['pre_execution_check'].update({'output_absent_before_creation':True,'prepared_source_and_model_check_exit_code':0,'prepared_independent_source_check_exit_code':0,'prior_candidate_files_preserved':10703})
remaining=[r for r in work['units'] if r['kind']=='definition-T' and r['definition_id']!=context['source_selection']['definition_id'] and not(b.BASE/'definitions'/r['definition_id']/'t.json').exists()];context['next_definition_priority']=remaining[0]['id']
unit.mkdir()
with(unit/'context.json').open('x') as f:json.dump(context,f,indent=2,sort_keys=True);f.write('\n')
for name in ['build_candidate.py','verify_candidate.py','verify_source_checks.py']:
    with(unit/name).open('xb') as f:f.write((prepared/name).read_bytes())
with(unit/'author_candidate.py').open('xb') as f:f.write(Path(__file__).read_bytes())
b.unchanged(prior['files']+context['sources']+successful+dirty['refs'])
print(json.dumps({'result':'PASS-exact-C65-IntentResolution-native-author','prior_files':10703,'source_files':201,'prepared_controls':183,'queries':35,'retained_failed_preparation_attempts':0,'actual_resolution_effect_created':False,'next_definition_priority':remaining[0]['id']}))
