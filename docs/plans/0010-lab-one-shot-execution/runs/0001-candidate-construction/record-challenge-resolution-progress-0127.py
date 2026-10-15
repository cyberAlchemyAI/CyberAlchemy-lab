"""Record current metrics explicitly; historical receipts do not grant new proof."""
import hashlib
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';API=BASE/'api-v86'


def bind(path):return {'path':path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def load(path):return json.loads(path.read_bytes())


def main():
    predecessor=BASE/'api-v85/receipts/R03-0126.json';old=load(predecessor)
    source_path,profile_path=API/'source-manifest.json',API/'contract-profile.json'
    source,profile=load(source_path),load(profile_path)
    component=RUN/'challenge-resolution-contracts-0001.json';controls=RUN/'API86-source-controls-0002.json'
    q,c=load(component),load(controls)
    assert q['result']==c['result']=='PASS' and q['actual_cases']==15 and c['actual_cases']==7
    assert q['failures']==q['errors']==c['failures']==c['errors']==0
    assert not q['public_handler_qualified'] and not c['challenge_resolution_actual_runtime_qualified']
    catalog=load(ROOT/'docs/proposals/0008-lab-api-contracts/api-contracts.json')
    missing=[row['operation'] for row in catalog['operations'] if row['operation'] not in profile['implemented_operations']]
    assert len(catalog['operations'])==34 and len(profile['implemented_operations'])==24 and len(missing)==10
    rows={row['path']:row for row in old['files']}
    for row in [*source['files'],*q['files'],*c['files']]:
        assert rows.get(row['path'],row)==row,row['path'];rows[row['path']]=row
    for path in (predecessor,source_path,profile_path,component,controls,
                 RUN/'API86-source-controls-0001.json',RUN/'qualify-API86-controls-0001.py',
                 RUN/'qualify-API86-controls-0002.py',Path(__file__).resolve()):rows[bind(path)['path']]=bind(path)
    for row in rows.values():assert bind(ROOT/row['path'])==row,row['path']
    value={'schema_version':'lab-current-api-progress/v2-candidate','result':'PASS',
        'task':'R03','files':[rows[key] for key in sorted(rows)],'historical_progress_binding':bind(predecessor),
        'source_binding':bind(source_path),'profile_binding':bind(profile_path),
        'authored_public_handlers':24,'original_public_operation_count':34,
        'remaining_unimplemented_operations':missing,'unimplemented_public_operation_count':10,
        'original_API_test_methods_retained':323,'unchanged_method_ASTs':320,
        'explicit_registry_count_expectation_revisions':source['binding_only_revised_methods'],
        'isolated_resolution_contract_qualification_binding':bind(component),'actual_isolated_resolution_cases':15,
        'source_control_qualification_binding':bind(controls),'actual_source_control_cases':7,
        'preserved_source_control_failure_binding':bind(RUN/'API86-source-controls-0001.json'),
        'source_control_fixture_corrections':c['explicit_fixture_input_corrections'],
        'same_predecessor_live_jobs':[{'tool_session_id':21646,'API':85,'purpose':'original14Machine+6termination',
            'selection_binding':bind(RUN/'API85-independent-selection-0001.json')}],
        'current_Machine_qualified':False,'challenge_resolution_public_handler_qualified':False,'whole_API_qualified':False,
        'runtime_qualification_transferred':False,'actual_owner_outcome':None,'canonical_admissions':0,
        'authority_effect':'none','task_complete':False,'goal_complete':False,
        'remaining_obligations':[
            'Observe the same original API85 full20case job21646 through actual terminal; do not transfer predecessor qualification to API86.',
            'Construct a freshly owned signed source containing exact recognized owner/Challenge/Contract/Decision/Effect/Decision Scope/evidence records, then qualify positive challenge.resolve through actual channel, native validator and original journal/retry/deadline.',
            'Correct the explicitly observed inherited Product.version_ref fixture in a future frozen successor; preserve its failed original receipt and all original assertions. The external control correction is scoped evidence only.',
            *old['remaining_obligations'][1:4],
            'Implement all10 original missing operations: '+','.join(missing)+'.',
            'Complete all original R03 affected public selections, R05 journeys, R06 privacy, R07 acceptance and S02 exact complete package before sole actual R08 owner response; preserve A01-A04 scope.'],
        'change':'Authored and froze API86 challenge.resolve preparation: independently signed exact development gate, current original records, Contract response obligations, distinct semantic/governance proposals and Effect/target/Scope mapping.15actual isolated component cases passed.7source/schema/control cases passed after an explicit external Product fixture correction; the original1failure is retained. No positive public resolution, canonical owner outcome or wholeAPI qualification.',
        'claim_ceiling':'24authored handlers; actual15isolated and7bounded control cases only. All34operations/46tasks retained; no canonical admission, live effects or complete Lab.'}
    output=API/'receipts/R03-0127.json';output.parent.mkdir(mode=0o700,exist_ok=True)
    with output.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':'PASS','progress_binding':bind(output),'bound_files':len(rows),
                      'authored_handlers':24,'missing_operations':10,'task_complete':False}),flush=True)


if __name__=='__main__':main()
