"""Serialize original successor cases behind the same verified owned diagnostic.

A transient observation timeout never starts a replacement diagnostic. Stop on
missing process/terminal evidence rather than infer completion or restart it.
"""
import json,os,subprocess,sys,time
from pathlib import Path
RUN=Path(__file__).resolve().parent
DIAGNOSTIC_PID=342334
TERMINAL=RUN/'API45-failure12-cpu-measurement-terminal-0001.json'
EXPECTED_RUNNER=(RUN/'profile-API45-failure12-0001.py').as_posix().encode()
def identity():
 p=Path('/proc')/str(DIAGNOSTIC_PID)/'cmdline'
 try:raw=p.read_bytes()
 except FileNotFoundError:return False
 return EXPECTED_RUNNER in raw.split(b'\0')
def main():
 if not TERMINAL.exists():
  assert identity(),'expected owned diagnostic is not live; inspect missing terminal'
  print(json.dumps({'phase':'WAITING-FOR-SAME-DIAGNOSTIC','session_id':43273,'owned_PID':DIAGNOSTIC_PID,'new_owned_fixture_effects_started':False}),flush=True)
 while not TERMINAL.exists():
  time.sleep(5)
  if not identity() and not TERMINAL.exists():
   # Allow the original child wrapper to publish its terminal record.
   time.sleep(5)
   assert TERMINAL.exists(),'diagnostic process ended without authoritative terminal; inspect before successor fixtures'
 value=json.loads(TERMINAL.read_bytes());assert value['actual_exit_code']==0
 report=json.loads((RUN/'API45-failure12-cpu-measurement-0001.json').read_bytes())
 assert report['result']=='MEASURED' and report['actual_tests']==1 and report['errors']==0,'inspect anomalous diagnostic before original cases'
 cmd=[sys.executable,'-B',str(RUN/'verify-API46-core-schema-original-cases-0001.py')]
 print(json.dumps({'phase':'STARTING-UNCHANGED-ORIGINAL-CASES','ordered_original_methods':['test_14_uncertain_core_failure_stays_pending','test_15_invalid_schema_is_never_assessed'],'profiling_enabled':False}),flush=True)
 result=subprocess.run(cmd)
 print(json.dumps({'phase':'ORIGINAL-CASES-TERMINAL','actual_exit_code':result.returncode}),flush=True)
 return result.returncode
if __name__=='__main__':raise SystemExit(main())
