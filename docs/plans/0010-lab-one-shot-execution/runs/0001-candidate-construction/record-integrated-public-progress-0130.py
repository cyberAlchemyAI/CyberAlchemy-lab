"""Record actual full cold-source qualification and evidenced public closure gaps."""
import base64
import hashlib
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';API=BASE/'api-v87'


def bind(path):return {'path':path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def load(path):return json.loads(path.read_bytes())


def main():
    parent=BASE/'api-v86/receipts/R03-0129.json';value=load(parent);rows={row['path']:row for row in value['files']}
    cold=RUN/'integrated-source-qualification-0008.json';c=load(cold)
    assert c['result']=='PASS' and c['actual_cases']==23 and c['failures']==c['errors']==0 and c['source_guarded_exit_completed']
    failed=RUN/'API87-integrated-resolution-0001.json';f=load(failed)
    diagnosis=RUN/'API87-integrated-resolution-diagnosis-0002.json';d=load(diagnosis)
    assert f['result']=='FAIL' and d['result']=='PASS' and d['expected_domain_conflict_observed']
    assert len(d['failure_evidence_originals'])==18 and d['fixture_removed'] and not d['public_resolution_qualified']
    observations=[]
    for row in d['failure_evidence_originals']:
        raw=base64.b64decode(row['base64_original_bytes'],validate=True)
        assert hashlib.sha256(raw).hexdigest()==row['binding']['sha256']
        record=json.loads(raw)
        if record.get('schema_version')=='lab-validation-report/v1-candidate':
            observations.append({'result':record['result'],'unresolved_reference_checks':[check for check in record['reference_checks'] if check['posture']!='resolved'],
                                 'gaps':record['gaps']})
    assert len(observations)==3 and all(item['result']=='not-evaluable' for item in observations)
    paths=[parent,cold,failed,diagnosis,Path(__file__).resolve(),RUN/'qualify-API87-integrated-resolution-0001.py',
           RUN/'diagnose-API87-integrated-resolution-0002.py',RUN/'freeze-API87-integrated-resolution-0001.py',
           API/'source-manifest.json',API/'contract-profile.json']
    source=load(API/'source-manifest.json')
    for row in [*source['files'],*c['files'],*f['files'],*d['files'],*[bind(path) for path in paths]]:
        assert rows.get(row['path'],row)==row,row['path'];rows[row['path']]=row
    for row in rows.values():assert bind(ROOT/row['path'])==row,row['path']
    value.update(files=[rows[key] for key in sorted(rows)],historical_progress_binding=bind(parent),
        source_binding=bind(API/'source-manifest.json'),profile_binding=bind(API/'contract-profile.json'),
        integrated_source_qualified=True,integrated_source_full_cold_qualification_binding=bind(cold),integrated_source_full_cold_cases=23,
        integrated_public_resolution_failed_binding=bind(failed),integrated_public_resolution_diagnosis_binding=bind(diagnosis),
        integrated_public_source_owner_authentication_verified=True,integrated_public_resolution_qualified=False,
        actual_retained_public_validation_evidence_objects=18,actual_public_reference_validation_results=observations,
        same_live_jobs=[],original_API_test_methods_retained=323,unchanged_method_ASTs=322,
        explicit_fixture_input_corrections=['test_current_controls.py:test_07_exact_new_episode_Work_Product_and_ten_relations'],
        current_Machine_qualified=False,whole_API_qualified=False,task_complete=False,goal_complete=False,
        remaining_obligations=[
            'Implement independently selected exact reference roles for Work expected output declarations; preserve their distinction from observed outputs and do not fabricate completed Context delivery or Work satisfaction.',
            'Implement a full scoped Challenge Event resolver for exact Contract/challenger/subject/evidence/Decision/residue references, including retained exact challenged-version history after prospective Work revision; validate without granting current participation or effect authority from historical sources.',
            'Wire these declarations/resolvers through a frozen successor and execute actual public resolution, exact retry, changed-source/policy, schema/signature/core failure, deadline and pure-scope refusal cases. Preserve API87failed case and18original evidence objects.',
            *value['remaining_obligations'][1:]],
        change='Source8 full23actual cold/native/gate cases PASS:all105originals,63explicit typed relations, native current/historical compatibility, independent signatures/refusals, actual transaction tampering, exact retries and cleanup. API87frozen integratedSource8/Reader7 public policy retains323methods with1explicit Product fixture correction. Actual public call authenticated the controlled owner and source but correctly returned conflict for not-evaluable semantic references. A second actual diagnostic retained18original evidence objects and identified Workfuture output declaration, missing ChallengeEventresolver, and historical challenged Workversion closure after prospective revision. No native validator weakened or unknown reference promoted to success.',
        claim_ceiling='Actual Source8 full23cold/native/gate and current public source/owner authentication with diagnosed semantic closure refusal only; positive public resolution, inherited API/adapter, mapped AgentContext, learning application and completeLab remain unqualified.')
    output=API/'receipts/R03-0130.json';output.parent.mkdir(mode=0o700,exist_ok=True)
    with output.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':'PASS','progress_binding':bind(output),'bound_files':len(rows),'actual_cold_cases':23,
                      'retained_public_evidence_objects':18,'public_resolution_qualified':False}),flush=True)


if __name__=='__main__':main()
