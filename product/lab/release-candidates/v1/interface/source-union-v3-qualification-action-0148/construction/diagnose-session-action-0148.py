"""Exception-only CPython monitoring of an unchanged original Session70 test.
No frame locals, signing keys, caller input bodies or Session RAM are captured.
"""
import argparse,hashlib,importlib.util,json,os,sys,time,unittest
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');OUT=Path('/tmp/cal-session-diagnostic-action-0148')
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v7'
SOURCE='c373b7b65c381b97f3016192d74a21b6d13463ef8f6fdbd0938c1260dd828707'
PROFILE=hashlib.sha256((API/'contract-profile.json').read_bytes()).hexdigest()
start=time.monotonic();events=OUT/'exception-events.jsonl';counts={};call_stacks={}
def emit(value):
 with events.open('a') as stream:stream.write(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-start,**value},sort_keys=True)+'\n');stream.flush()
def raised(code,offset,error):
 path=Path(code.co_filename)
 if not path.is_absolute() or not path.is_relative_to(ROOT):return
 if code.co_name not in ('require','guard','policy_guard','_start','_finish','open_plan','_open_plan','_call','open','original','resolve'):return
 reason=str(error)[:1000] if code.co_name=='require' and isinstance(error,(ValueError,AssertionError)) else None
 emit({'phase':'actual-exception','file':path.relative_to(ROOT).as_posix(),'function':code.co_name,'instruction_offset':offset,'exception_type':type(error).__name__,'fixed_require_reason':reason})
TOOL=3;sys.monitoring.use_tool_id(TOOL,'exception-only-session-action-0148');sys.monitoring.register_callback(TOOL,sys.monitoring.events.RAISE,raised);sys.monitoring.set_events(TOOL,sys.monitoring.events.RAISE)
try:
 emit({'phase':'starting','source_sha256':SOURCE,'profile_sha256':PROFILE,'original_clocks_callbacks_assertions_changed':False,'captured_frame_locals':False})
 n='_cal_original_api7_session_exception_action_0148';spec=importlib.util.spec_from_file_location(n,API/'__init__.py',submodule_search_locations=[str(API)]);m=importlib.util.module_from_spec(spec);sys.modules[n]=m;spec.loader.exec_module(m)
 guard=__import__(n+'.guard',fromlist=['verify']);guard.verify(SOURCE)
 tests=__import__(n+'.run_session_checks',fromlist=['Sessions']);tests.PROFILE=PROFILE;tests.SOURCE=SOURCE
 emit({'phase':'suite-selected','original_test':'Sessions.test_27_actual_expiry_timer_disposes'})
 suite=unittest.TestSuite([tests.Sessions('test_27_actual_expiry_timer_disposes')])
 with (OUT/'original-test.log').open('x') as stream:result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
 guard.verify(SOURCE)
 report={'result':'PASS' if result.wasSuccessful() and result.testsRun==1 else 'FAIL','actual_methods':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'source_sha256':SOURCE,'profile_sha256':PROFILE,'exception_events_sha256':hashlib.sha256(events.read_bytes()).hexdigest(),'original_clock_callbacks_assertions_changed':False,'captured_frame_locals':False,'authority_effect':'none','actual_owner_outcome':None,'scope':'Diagnostic monitoring only; not transferred qualification.'}
 (OUT/'diagnostic.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');emit({'phase':'terminal','result':report['result'],'actual_methods':result.testsRun});print(json.dumps(report),flush=True)
finally:sys.monitoring.set_events(TOOL,0);sys.monitoring.free_tool_id(TOOL)
