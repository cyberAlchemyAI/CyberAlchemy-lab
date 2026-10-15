"""Record the policy composition repair without closing runtime obligations."""
import hashlib
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
API=BASE/'api-v83'


def load(path):return json.loads(path.read_bytes())


def bind(path):
    return {'path':path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    parent_path=BASE/'api-v82/receipts/R03-0118.json'
    parent=load(parent_path)
    manifest=load(API/'source-manifest.json')
    checked_path=RUN/'API83-live-application-authoring-checks-0001.json'
    checked=load(checked_path)
    assert checked['result']=='PASS' and checked['original_inherited_methods']==323
    assert checked['unchanged_method_ASTs']==323 and not checked['actual_runtime_qualified']
    rows={row['path']:row for row in parent['files']}
    for row in manifest['files']+checked['files']:
        assert rows.get(row['path'],row)==row,row['path']
        rows[row['path']]=row
    paths=[API/'source-manifest.json',API/'contract-profile.json',parent_path,checked_path,
           RUN/'qualify-API83-live-application-composition-0001.py',
           RUN/'API83-live-application-composition-0001.json',
           RUN/'qualify-API83-live-application-composition-0002.py',Path(__file__).resolve()]
    for path in paths:rows[bind(path)['path']]=bind(path)
    actual_path=RUN/'API83-live-application-composition-0002.json'
    actual=load(actual_path) if actual_path.exists() else None
    if actual is not None:
        rows[bind(actual_path)['path']]=bind(actual_path)
        for row in actual['files']:rows[row['path']]=row
    for row in rows.values():assert bind(ROOT/row['path'])==row,row['path']
    value={**parent,'result':'PASS','files':[rows[key] for key in sorted(rows)],
           'parent_progress_binding':bind(parent_path),'current_API_version':83,
           'source_binding':bind(API/'source-manifest.json'),'profile_binding':bind(API/'contract-profile.json'),
           'retained_predecessor_methods':323,'unchanged_method_ASTs':323,
           'exact_handler_count_expectation_revisions':0,
           'lesson_application_authoring_checks_binding':bind(checked_path),
           'lesson_application_live_composition_repaired_in_source':True,
           'actual_composition_qualification_binding':bind(actual_path) if actual is not None else None,
           'actual_composition_qualification_posture':actual['result'] if actual is not None else 'running',
           'actual_composition_job':51955,
           'lesson_apply_actual_runtime_qualified':False,'lesson_assess_actual_runtime_qualified':False,
           'remaining_obligations':[
               'Bind the same actual API83 composition job51955 result; first attempt0001 has0cases after missing test-profile configuration and remains preserved. Successor0002 supplies exact original profile binding.',
               'Observe same actual API79 job35646 and API80 job19391 full original20 cases; preserve actual terminal outcomes and safe exception frames.',
               'Create actual current controlled lesson/application/evidence episode; qualify positive lesson.apply and lesson.assess, conflicts, overrides, stale Session/source and original guards.',
               'Implement all11 remaining original public operations: '+','.join(parent['remaining_unimplemented_operations'])+'.',
               'Complete original R03,R05,R06,R07 and S02 exact whole package before sole actual R08 owner response; preserve separately scoped A01-A04.'],
           'change':'Repaired the intrinsic API82 null-Session application-policy incompatibility in API83/lesson-application-v2. A separate current-participation policy composes original source period, actual operator, original Session eligibility and exact application method. One pair of future private identifiers permits prospective content; declarations allocate no resources. Actual opening reserves identifiers outside pure facts before RAM creation, refuses durable reuse and preserves real900second ceiling and original closing.23handlers/11missing unchanged;all323testASTs unchanged.7structural/source checks pass. Actual opening/closing diagnostic remains separately qualified; positive application and complete API remain unqualified.',
           'whole_API_qualified':False,'task_complete':False,'goal_complete':False,
           'claim_ceiling':'Source composition repair and exact structural checks only, plus separately recorded actual scoped episode when complete. No positive application, outcome, complete API, owner decision or admission inferred.'}
    output=API/'receipts/R03-0119.json'
    output.parent.mkdir(exist_ok=True)
    with output.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':'PASS','binding':bind(output),'bound_files':len(rows),'authored_handlers':23,
                      'remaining_handlers':11,'composition_qualification':value['actual_composition_qualification_posture']}),flush=True)


if __name__=='__main__':main()
