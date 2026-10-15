"""Record API51 construction and complete API50 scoped suites without reuse claims."""
import hashlib
import json
from pathlib import Path
RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'


def load(p):return json.loads(p.read_bytes())


def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}


def main():
    parent=BASE/'api-v50/receipts/R03-0089.json'
    old=load(parent)
    source=BASE/'api-v51/source-manifest.json';profile=BASE/'api-v51/contract-profile.json'
    manifest=load(source)
    assert bind(source)['sha256']=='7444cec4a6d58c5cb851b876de79d4c52c2d392c55b53e64e1eb214788b2cf3c'
    assert bind(profile)['sha256']=='49468dfe1ed356bc800681197f39f2b91acfdf7c951367c5b465f6d48eb1530b'
    assert manifest['unchanged_inherited_method_count']==293
    authored=load(profile)['implemented_operations'];assert len(authored)==18 and 'lesson.select' in authored
    catalog=load(ROOT/'docs/proposals/0008-lab-api-contracts/api-contracts.json')
    missing=sorted({row['operation'] for row in catalog['operations']}-set(authored));assert len(missing)==16
    rules=BASE/'lesson-selection-rules-v2'
    proof=load(rules/'receipts/checks-0001.json')
    assert proof['result']=='PASS' and proof['pure_cases']==61 and proof['pure_failures']==proof['pure_errors']==0
    assert proof['original_W06_cases']==53 and proof['original_W06_full_suite_completed']
    assert load(RUN/'lesson-query-rules-terminal-0002.json')['actual_exit_code']==0
    rows={row['path']:row for row in old['files']}
    for row in manifest['files']+load(rules/'source-manifest.json')['files']+load(rules/'source-manifest.json')['input_bindings']+proof['files']:
        rows[row['path']]=row
    completed=[]
    for label,count in [('typed10',10),('failure18',18),('controls11',11)]:
        terminal_path=RUN/('API50-'+label+'-terminal-0001.json');terminal=load(terminal_path)
        assert terminal['actual_exit_code']==0 and terminal['actual_cases']==count and terminal['full_selected_suite_completed']
        assert terminal['errors']==terminal['failures']==0
        for key in ['report_binding','log_binding']:
            row=terminal[key];assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'];rows[row['path']]=row
        row=bind(terminal_path);rows[row['path']]=row;completed.append(row)
    for p in [parent,source,profile,rules/'source-manifest.json',rules/'receipts/checks-0001.json',
              RUN/'lesson-query-rules-terminal-0002.json',RUN/'API51-lesson3-started-0001.json',Path(__file__).resolve()]:
        row=bind(p);rows[row['path']]=row
    for row in rows.values():assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],row['path']
    value={**old,'files':[rows[k] for k in sorted(rows)],'parent_progress_binding':bind(parent),
        'source_binding':bind(source),'profile_binding':bind(profile),
        'change':'Constructed/froze API51 lesson host and declared read policy;18 handlers/16 missing. Actual host/Machine/Session source and original eligibility joins implemented; all34 public contracts and293 inherited methods retained. Query exclusions precede conflict formation;61 pure cases and53 unchanged W06 tests PASS. API50 typed10/failure18/controls11 complete PASS39; same driver now running full146. API51 actual lesson3 runner started; no terminal result yet.',
        'implemented_public_handlers':18,'unimplemented_public_operation_count':16,'unimplemented_public_operations':missing,
        'lesson_selection_rules_source_sha256':proof['source_sha256'],'lesson_selection_rules_report_binding':bind(rules/'receipts/checks-0001.json'),
        'lesson_selection_rules_terminal_binding':bind(RUN/'lesson-query-rules-terminal-0002.json'),
        'lesson_selection_pure_rule_cases':61,'lesson_selection_retained_W06_cases':53,
        'lesson_selection_public_handler_integrated':True,'lesson_selection_actual_live_Session_qualified':False,
        'lesson_selection_nonempty_signed_source_qualified':False,'lesson_selection_public_suite_verdict':None,
        'lesson_selection_public_runner_start_binding':bind(RUN/'API51-lesson3-started-0001.json'),
        'lesson_selection_actual_public_calls':None,
        'API50_completed_scope_terminal_bindings':completed,'API50_completed_selected_cases':39,'API50_remaining_selected_cases':413,
        'API50_typed_operator_runtime_qualified':True,'API50_failure_assessment_scope_qualified':True,'API50_controls_scope_qualified':True,
        'API50_typed_qualification_source_sha256':'3e46a5bef724a601d3f465841205f8c73a7723637538fd738cdd2ef7a85dcd64',
        'API50_typed_qualification_profile_sha256':'6cb5e2461cdc6442384821c4e01df3c117b61166856e3e69731b051ae01b65d5',
        'current_selected_completed_cases':None,'current_selected_remaining_cases':None,
        'current_full_suite_selected_cases':None,'current_full_suites':None,
        'current_serialized_public_driver_binding':None,'current_public_suite_observation_binding':None,
        'current_full_public_suite_verdict':None,'current_control_successor_suite_executed':False,
        'current_typed_operator_runtime_qualified':False,'typed_operator_public_qualified':False,
        'API51_full_public_runtime_qualified':False,'current_complete_public_API_qualification':False,
        'superseded_obligations_preserved_in_parent':old['remaining_obligations'],
        'remaining_obligations':[
            'Observe the same API51 lesson3 actual runner18103/PID35000; bind complete actual report and terminal before any transport qualification. Never restart because an observation times out.',
            'Qualify actual signed nonempty Lesson inventory. The current source has no Lessons and its original Context/Ontology delivery refuses nonempty catalogs; a governed source/context/ontology successor is required, not fabricated objects or altered guards.',
            'Qualify all API51 original suites under its exact source/profile; preserve legacy policy sets, inherited293 assertions and declaration of18-handler count successors.',
            'Complete the same API50 serialized452-case run;39 full selected cases completed,413 remain. Source-specific historical qualification does not qualify API51.',
            'Complete all16 missing public operations, assigned Machine typed participation, governed internal endpoint and specialized canonical authority resolvers.',
            'Preserve API47 actual exit143, API48 unknown exit and all failed/interrupted evidence; no old claim, key, memory or fixture restoration.',
            'Complete genuine R05 participant evidence, genuinely reviewed model changes where required, R06/R07 and all-member S02 before sole actual R08.',
            'Actual owner outcomes and independently scoped authorization remain required before A01-A04 effects.'
        ],
        'claim_ceiling':'Frozen API51 source implementation plus61 synthetic rule cases/53 original W06 checks; actual public host tests remain running.39 complete API50 selected cases are scoped to API50 only. No nonempty source qualification, assigned typed Agent grant, genuine review/use, admission, full API or plan completion.',
        'whole_API_qualified':False,'task_complete':False,'goal_complete':False}
    p=BASE/'api-v51/receipts/R03-0090.json'
    with p.open('x') as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps({'result':'PASS','progress_binding':bind(p),'bound_files':len(rows),'handlers':18,'missing':16,'task_complete':False}),flush=True)


if __name__=='__main__':main()
