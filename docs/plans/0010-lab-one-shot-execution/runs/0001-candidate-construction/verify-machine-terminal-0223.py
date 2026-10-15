"""Independently recover original completed methods; retain caller serialization failure."""
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[5]
RUN=Path(__file__).resolve().parent
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v12'
SOURCE='5c7f5c69d5795f5a5c0cb8b67c52a47621f8eab746c6afd70d42f06177ddc6ae'
PLAN='25d0b54f0c9110d9ae25d66d93e3825b5e2714310c6bb7682c92a4f8e5c124d4'

def bind(p):
    return {'path':str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}

def main():
    out=RUN/'machine-terminal-recovery-0223.json';assert not out.exists()
    paths=[RUN/'final-api-regression-fixture-recovery-plan-0215.json',
           RUN/'final-api-regression-fixture-recovery-0215.py',
           RUN/'final-api-regression-0173-0215.worker-machine.events.jsonl',
           RUN/'final-api-regression-0173-0215-worker-machine.log']
    before=list(map(bind,paths));assert before[0]['sha256']==PLAN
    plan=json.loads(paths[0].read_text());assert before[1]==plan['recovery_caller_binding']
    assert Path('/tmp/cal-final-fixture-recovery-0215/qualify.py').read_bytes()==paths[1].read_bytes()
    events=[json.loads(x) for x in paths[2].read_text().splitlines()]
    assert events[0]['phase']=='starting' and events[0]['source_pin']==SOURCE
    assert any(x['phase']=='full-history-entry-guard-passed' for x in events)
    cases=[{k:v for k,v in x.items() if k not in ('at','phase')} for x in events if x['phase']=='case-completed']
    wanted=plan['workers']['machine'];assert len(cases)==len(wanted)==14
    assert len({x['declared_method'] for x in cases})==14 and {x['declared_method'] for x in cases}==set(wanted)
    assert all(x['result']=='PASS' for x in cases)
    assert events[-1]['phase']=='terminal' and events[-1]['result']=='PASS'
    assert events[-1]['actual_methods']==14 and events[-1]['exact_method_accounting'] and events[-1]['full_history_exit_guard_passed']
    log=paths[3].read_text();assert 'Ran 14 tests' in log and '\nOK\n' in log
    assert "is not in the subpath of '/home/vlad_/projects/CyberAlchemy-lab'" in log
    assert not (RUN/'final-api-regression-0173-0215.worker-machine.json').exists()
    spec=importlib.util.spec_from_file_location('_recovered_machine_guard',API/'guard.py')
    guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
    guard.verify(SOURCE)
    spec=importlib.util.spec_from_file_location('_recovered_machine_inventory',RUN/'final-api-regression-map-0173.py')
    inventory=importlib.util.module_from_spec(spec);spec.loader.exec_module(inventory)
    assert inventory.discover(API)==plan['method_inventory']
    guard.verify(SOURCE);assert before==list(map(bind,paths))
    value={'schema_version':'lab-original-method-terminal-recovery/v1-candidate',
           'result':'PASS-method-observation-recovery','actual_methods':14,'cases':cases,
           'original_actual_process_exit_code':1,'original_process_result_serialization_failed':True,
           'original_event_terminal_binding':before[2],'original_log_binding':before[3],
           'original_full_history_entry_exit_events_verified':True,
           'original_unittest_cleanup_completed':True,'original_report_exists':False,
           'fresh_source_entry_exit_guards':True,'unchanged_original_method_and_fixture_ASTs':True,
           'fixture_defining_module_SOURCE_PROFILE_injection_only':True,
           'files':before,'checked_at':datetime.now(timezone.utc).isoformat(),
           'native_methods_reexecuted':False,'authority_effect':'none','actual_owner_outcome':None,
           'whole_API_qualified':False,'goal_complete':False}
    with out.open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'result':value['result'],'actual_methods':14,'binding':bind(out)}),flush=True)

if __name__=='__main__':main()
