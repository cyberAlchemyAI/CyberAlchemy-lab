"""Actual original test methods selected against an explicit successor source family.
No clock, assertion, source, permission or runtime callbacks are monkeypatched.
Diagnostic local exception events capture only public fixed require reasons.
"""
import hashlib,importlib.util,json,sys,time,unittest,argparse,inspect
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');I=ROOT/'product/lab/release-candidates/v1/interface';API=I/'api-session-source-v3-action-0148';OUT=Path('/tmp/cal-session-diagnostic-action-0148')
p=argparse.ArgumentParser();p.add_argument('--case',choices=['expiry','safety'],required=True);a=p.parse_args();case=a.case
receipt=OUT/('union-'+case+'-v3-qualification-0001');receipt.mkdir(mode=0o700)
start=time.monotonic();events=receipt/'events.jsonl'
def emit(v):
 with events.open('a') as f:f.write(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-start,**v},sort_keys=True)+'\n');f.flush()
def raised(code,offset,error):
 reason=str(error) if code.co_name=='require' and isinstance(error,(ValueError,AssertionError)) else None
 emit({'phase':'local-exception','file':str(Path(code.co_filename).relative_to(ROOT)),'function':code.co_name,'exception_type':type(error).__name__,'fixed_require_reason':reason})
TOOL=3
# No global monitoring: CPython3.14 disallows local RAISE event selection.
try:
 n='_cal_qualified_union_api_session_action_0148';s=importlib.util.spec_from_file_location(n,API/'__init__.py',submodule_search_locations=[str(API)]);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m)
 g=__import__(n+'.guard',fromlist=['verify']);source=hashlib.sha256((API/'source-manifest.json').read_bytes()).hexdigest();profile=hashlib.sha256((API/'contract-profile.json').read_bytes()).hexdigest();emit({'phase':'entry-history-guard','source_sha256':source,'profile_sha256':profile});g.verify(source)
 tests=__import__(n+'.run_session_checks',fromlist=['Sessions']);tests.PROFILE=profile;tests.SOURCE=source
 # Monitor actual require and selected API preflight functions only, avoiding
 # millions of unrelated schema engine exceptions. No frame locals recorded.
 codes=set()
 for mod in list(sys.modules.values()):
  path=getattr(mod,'__file__',None)
  if not path or not str(path).startswith(str(ROOT)):continue
  for obj in vars(mod).values():
   objects=[obj,*vars(obj).values()] if inspect.isclass(obj) else [obj]
   for value in objects:
    if inspect.isfunction(value) and value.__name__ in ('require','_start','_finish','open_plan','_open_plan','_call') and str(value.__code__.co_filename).startswith(str(ROOT)):codes.add(value.__code__)
 # Actual uninstrumented original methods preserve qualification timing.
 names=['test_27_actual_expiry_timer_disposes'] if case=='expiry' else ['test_24_captured_source_corruption_disposes_on_inspection','test_26_private_policy_revocation_disposes','test_28_no_short_memory_in_any_recorded_reply','test_29_source_and_period_unchanged','test_31_frozen_producer_modules_retain_original_origins']
 # The original tests stay byte-identical. New family has extra actual class
 # witnesses in its constructor; original helper origins remain exact v4.
 emit({'phase':'actual-methods-start','methods':names,'instrumented_code_objects':0,'original_method_bodies_changed':False})
 with (receipt/'tests.log').open('x') as f:result=unittest.TextTestRunner(stream=f,verbosity=2).run(unittest.TestSuite([tests.Sessions(name) for name in names]))
 emit({'phase':'exit-history-guard'});g.verify(source)
 wire=tests.Sessions.events;(receipt/'wire.json').write_text(json.dumps(wire,indent=2,sort_keys=True)+'\n')
 report={'result':'PASS' if result.wasSuccessful() and result.testsRun==len(names) else 'FAIL','actual_methods':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'original_assertions_clocks_callbacks_changed':False,'original_request_deadline_seconds':70,'actual_public_calls':len(wire),'source_sha256':source,'profile_sha256':profile,'full_history_source_entry_exit_passed':True,'test_log_sha256':hashlib.sha256((receipt/'tests.log').read_bytes()).hexdigest(),'wire_sha256':hashlib.sha256((receipt/'wire.json').read_bytes()).hexdigest(),'events_sha256':hashlib.sha256(events.read_bytes()).hexdigest(),'elapsed_seconds':time.monotonic()-start,'authority_effect':'none','actual_owner_outcome':None,'claim_ceiling':'Focused original methods on separately selected source union; no full Product completion.'}
 (receipt/'qualification.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(json.dumps(report),flush=True)
finally:pass
