"""Verify exact fixture binding revision and record current candidate progress."""
import ast
import hashlib
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
OLD,API=BASE/'api-v84',BASE/'api-v85'


def bind(path):return {'path':path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def load(path):return json.loads(path.read_bytes())


def methods(text):
    return {node.name:ast.dump(node,include_attributes=False) for node in ast.walk(ast.parse(text))
            if isinstance(node,ast.FunctionDef) and node.name.startswith('test_')}


def main():
    parent_path=OLD/'receipts/R03-0123.json';parent=load(parent_path)
    unchanged=[];revised=[]
    for old in OLD.glob('*.py'):
        before=old.read_text();after=(API/old.name).read_text()
        expected=before
        if old.name=='test_machine_transport.py':
            expected=before.replace("        request=self.inspection(context['session_ref'])",
                                    "        request=self.inspection(context['session_ref'])\n        request['caller_context_ref']=context['context_ref']",1)
        assert methods(expected)==methods(after),old.name
        for name,value in methods(before).items():
            (unchanged if methods(after)[name]==value else revised).append(old.name+':'+name)
    assert len(unchanged)==322 and revised==['test_machine_transport.py:test_02_all_seven_public_read_operations_with_actual_Actor']
    for name in ('machine_transport.py','auth.py','service.py','custody_context_sessions.py','protocol.py','workspace.py','guarded_reads.py','guarded_candidate.py'):
        assert (OLD/name).read_bytes()==(API/name).read_bytes(),name
    case_path=RUN/'API84-Machine-seven-read-observation-0002.json';case=load(case_path)
    assert case['result']=='FAIL' and case['actual_cases']==1
    assert next(row for row in case['actual_calls'] if row['operation']=='context.get')['kind']=='result'
    inspected=next(row for row in case['actual_calls'] if row['operation']=='session.inspect')
    assert inspected['code']=='unauthorized' and not inspected['peer_closed'] and not inspected['observed_after_actual_Session_expiry']
    rows={row['path']:row for row in parent['files']}
    for row in load(API/'source-manifest.json')['files']:
        assert rows.get(row['path'],row)==row,row['path'];rows[row['path']]=row
    paths=[API/'source-manifest.json',API/'contract-profile.json',parent_path,case_path,
           RUN/'qualify-API85-Machine-seven-read-observation-0001.py',Path(__file__).resolve()]
    for path in paths:rows[bind(path)['path']]=bind(path)
    for row in rows.values():assert bind(ROOT/row['path'])==row,row['path']
    actual_path=RUN/'API85-Machine-seven-read-observation-0001.json'
    actual=load(actual_path) if actual_path.exists() else None
    if actual is not None:
        for row in actual['files']:rows[row['path']]=row
        rows[bind(actual_path)['path']]=bind(actual_path)
    value={**parent,'files':[rows[key] for key in sorted(rows)],'parent_progress_binding':bind(parent_path),
           'current_API_version':85,'source_binding':bind(API/'source-manifest.json'),'profile_binding':bind(API/'contract-profile.json'),
           'unchanged_method_ASTs':322,'exact_fixture_binding_revisions':1,'fixture_binding_revised_methods':revised,
           'exact_fixture_binding_checks':'PASS','production_auth_clock_permission_and_dispatch_bytes_unchanged':True,
           'API84_actual_Machine_context_get_passed':True,'API84_actual_case_binding':bind(case_path),
           'actual_Machine_observation_job':78380,'actual_Machine_repair_case_binding':bind(actual_path) if actual is not None else None,
           'actual_Machine_repair_case_posture':actual['result'] if actual is not None else 'running',
           'remaining_obligations':[
               'Observe the same actual API85 seven-read job78380 with exact source/profile assertions. Candidate84 Context read passed; its inspection correctly rejected the fixture stale parent opaque context. Candidate85 corrects that single control input and retains all original assertions.',
               *parent['remaining_obligations'][1:]],
           'change':'API84 actual Machine Context repair returned an original domain result with live unexpired peer; subsequent inspection rejected the fixture parent opaque context reference. API85 adds actualMachinecaller_context_ref in that exact original fixture method. All323methods retained,322ASTs unchanged,1declared exact connection-binding correction; original assertions and production transport/auth/permission/clock/service/custodian/protocol/vault/guards byte-identical to84. Corrected original case78380runs with exact candidate source/profile. Real4body3relation learning candidate remains unadmitted/unapplied.23handlers/11missing,36/46tasksclosed remain.',
           'current_Machine_qualified':False,'whole_API_qualified':False,'task_complete':False,'goal_complete':False,
           'claim_ceiling':'Actual Machine Context repaired read, exact fixture connection correction and unadmitted learning records only. Complete original Machine/fullAPI/application/outcome and owner admission remain.'}
    output=API/'receipts/R03-0124.json';output.parent.mkdir(exist_ok=True)
    with output.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':'PASS','binding':bind(output),'bound_files':len(rows),
                      'unchanged_methods':322,'exact_fixture_revisions':1,'actual_repaired_case_posture':value['actual_Machine_repair_case_posture']}),flush=True)


if __name__=='__main__':main()
