"""Close the CLI unit while all whole-source semantic gates remain unresolved."""
import hashlib
import json
import sys
from pathlib import Path
UNIT=Path(__file__).resolve().parent;ROOT=UNIT.parents[6];BASE=UNIT.parents[1]
IMPL=ROOT/'craft/formalization/candidates/definition-assurance-v1';sys.path.insert(0,str(IMPL))
import reports
import resolver as r
import verifier as v

def ref(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def load(name):return r.parse((UNIT/name).read_bytes(),name)
def unchanged(refs):
    for item in refs:
        if ref(ROOT/item['path'])!=item:raise ValueError('Changed bound bytes: '+item['path'])
def put(name,value):
    with (UNIT/name).open('x') as out:json.dump(value,out,indent=2,sort_keys=True);out.write('\n')
def audit():
    context=load('context.json');unchanged(context['sources'])
    predecessor=BASE/'definitions/cal.definition.semantic-primitive/delivery-manifest.json'
    prior=r.parse(predecessor.read_bytes(),str(predecessor));unchanged(prior['files'])
    if len(prior['files'])!=1134:raise ValueError('Wrong predecessor denominator')
    for name in ['I03','E04','A10']:
        rec=r.parse((BASE/f'units/{name}/receipt.json').read_bytes(),name)
        if not rec['task_result'].startswith('PASS'):raise ValueError('Prerequisite not complete: '+name)
        unchanged(rec['inputs']+rec['outputs'])
    report=reports.coverage(ROOT,ref(BASE/'current-snapshot.json'),ref(predecessor))
    if not r.same_json(report,load('coverage-report.json')):raise ValueError('Recorded report differs from fresh inspection')
    expected={'current_definitions':183,'admitted_source_versions':189,'per_definition_partial_drafts':8,'owner_accepted_whole_translations':0,'whole_definition_proofs':0,'manifest_file_count':1134}
    if any(report[k]!=n for k,n in expected.items()) or report['semantic_ready'] is not False:raise ValueError('Wrong whole-source denominator or readiness')
    if len(report['whole_definition_missing_drafts'])!=175 or report['projection']['identity_count']!=7 or report['projection']['whole_definition_credit']!=0 or len(report['recorded_failures_or_unresolved_queries'])!=1:raise ValueError('Projection confused with whole translations or failure omitted')
    if (UNIT/'coverage-report-human.txt').read_text()!=reports.human(report)+'\n':raise ValueError('Human view differs from exact JSON')
    test=load('test-result.json');log=(UNIT/'test-stderr.txt').read_text()
    if test['exit_code']!=0 or test['tests_run']!=9 or any(test[x] for x in ['failures','errors','skips']) or 'Ran 9 tests in ' not in log or not log.endswith('\nOK\n'):raise ValueError('Required end-to-end tests incomplete')
    commands=load('command-results.json')
    if len(commands)!=5 or any(x['exit_code']!=0 or (UNIT/x['stderr']).read_bytes() for x in commands):raise ValueError('Actual CLI command failed')
    capture=load('capture.json')
    if not r.same_json(capture['snapshot'],r.parse((BASE/'current-snapshot.json').read_bytes(),'snapshot')) or capture['semantic_ready'] is not False:raise ValueError('Capture changed selection or promoted readiness')
    typed=load('typed-check.json');diff=load('revision-diff.json')
    if typed['status']!='typed-candidate-interpretation' or typed['source_fidelity']!='pending' or typed['semantic_ready'] is not False:raise ValueError('Typing mistaken for accepted meaning')
    if diff['status']!='candidate-revision-generated' or diff['result']['evidence_verified'] is not False or diff['semantic_ready'] is not False:raise ValueError('Diff mistaken for evidence acceptance')
    if not (UNIT/'REVIEW.md').is_file():raise ValueError('Detailed review missing')
    return context,report
def main():
    context,report=audit()
    bindings=[ref(path) for path in [IMPL/'cli.py',IMPL/'reports.py',IMPL/'tests/test_I04.py',UNIT/'finalize.py',UNIT/'check_delivery.py']]
    put('episode-status.json',{'authority_effect':'none','goal_status':'active','latest_completed_unit':'I04.1','current_definitions':183,'admitted_source_versions':189,
         'per_definition_T_candidate_drafts':8,'remaining_current_identities_without_per_definition_T_draft':175,
         'source_owner_accepted_whole_translations':0,'whole_definition_proofs':0,'foundations_family_result':'PARTIAL','foundations_joint_review_exit':'not-ready',
         'projection_identities':7,'projection_whole_definition_credit':0,'semantic_ready':False,'next_independent_unit':'I05.1','full_project_completion':'not-established'})
    outputs=[ref(path) for path in sorted(UNIT.rglob('*')) if path.is_file() and '__pycache__' not in path.parts and path.suffix!='.pyc']
    outputs += [ref(IMPL/'cli.py'),ref(IMPL/'reports.py'),ref(IMPL/'tests/test_I04.py')]
    put('receipt.json',{'schema_version':'definition-assurance-unit-receipt/v1-candidate','unit_id':'I04.1','authority_effect':'none','goal_status':'active',
         'task_result':'PASS for stdout-only candidate CLI, all183-identity coverage, separate seven-source projection and explicit pending/failure outcomes',
         'inputs':context['sources'],'outputs':sorted(outputs,key=lambda x:x['path']),'checker_bindings':bindings,'runtime_bindings':v.f.current_bindings(),
         'criterion_results':[{'criterion':'capture/check/verify/diff/report with JSON and readable views','result':'PASS','evidence':'Five actual repository command invocations plus actual temporary-bundle independent verification in the nine-test suite.'},
           {'criterion':'unreviewed or missing translations prevent readiness','result':'PASS','evidence':'183 rows;8 partial drafts,175 missing,0 accepted whole translations,0 whole proofs; forged readiness and omitted failure rejected.'},
           {'criterion':'exact whole-definition versus projection coverage, remaining premises, failures and next unit','result':'PASS','evidence':'Distinct8-draft/7-projection inventories, selected premise accounts, deferred obligations, exact bounded-failure ledger and candidate I05.1 prerequisites.'},
           {'criterion':'output inventory and preservation; no admissions/registry mutation','result':'PASS','evidence':'Creation limited to declared four target areas;1134 preceding candidate files and201 captured source files rechecked; stdout-only CLI.'}],
         'validation':{'tests_run':9,'failures':0,'errors':0,'skips':0,'actual_repository_command_runs':5,'prior_candidate_files_preserved':1134,'source_files_current':201},
         'preserved_attempts':[{'path':'attempt-001-archival-draft-selection','result':'superseded-selection-failure'}, {'path':'attempt-002-fixture-publication','result':'superseded-test-fixture-failure'}],
         'review_disposition':{'kind':'candidate-agent-self-review','result':'CLI implementation criteria verified; source-owner fidelity and full episode remain pending.'},
         'semantic_ready':False,'mechanized_proof':False,'source_fidelity':'pending','whole_definition_translation':'pending',
         'coverage_report_ref':ref(UNIT/'coverage-report.json'),'next_ready_unit':'I05.1','full_project_completion':'not-established'})
    files=[ref(path) for folder in [BASE,IMPL] for path in sorted(folder.rglob('*')) if path.is_file() and '__pycache__' not in path.parts and path.suffix!='.pyc']
    put('delivery-manifest.json',{'schema_version':'definition-assurance-delivery-manifest/v1-candidate','authority_effect':'none','files':sorted(files,key=lambda x:x['path']),
         'claim_ceiling':'Exact preserved candidate bytes and tested stdout-only CLI. Whole-source fidelity, semantic closure, meaning alignment, all183 translations/proofs and complete episode review remain unresolved.'})
    print(json.dumps({'result':'PASS-for-I04.1-read-only-CLI','candidate_files':len(files),'prior_candidate_files_preserved':1134,'source_files_current':201,'tests_run':9,
                      'per_definition_partial_drafts':8,'missing_per_definition_drafts':175,'projection_identities':7,'whole_translations':0,'whole_proofs':0,'goal_status':'active','next_ready_unit':'I05.1'},indent=2,sort_keys=True))
if __name__=='__main__':main()
