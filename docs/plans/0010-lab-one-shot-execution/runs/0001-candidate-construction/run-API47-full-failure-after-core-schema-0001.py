"""Run the complete original failure suite after the same owned predecessor check."""
import json,subprocess,sys,time
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
TERMINAL=RUN/'API46-core-schema-focused-terminal-0001.json'
PRIOR_PID=351852
EXPECTED=(RUN/'run-API46-core-schema-after-diagnostic-0001.py').as_posix().encode()
SOURCE='666fcd2bc4f0e77b257a26915d26aab8083a8ac6c252dd9bc0f259a7ede80c62'
PROFILE='754aee27b34b334f67e4143dd9ab7826dcab7047ba40a2cb68461d2da457aa13'
def identity():
 try:raw=(Path('/proc')/str(PRIOR_PID)/'cmdline').read_bytes()
 except FileNotFoundError:return False
 return EXPECTED in raw.split(b'\0')
def main():
 if not TERMINAL.exists():
  assert identity(),'inspect missing predecessor process/terminal before successor suite'
  print(json.dumps({'phase':'WAITING-FOR-SAME-CORE-SCHEMA-CHECK','session_id':37740,'owned_driver_PID':PRIOR_PID,'new_successor_fixture_effects_started':False}),flush=True)
 while not TERMINAL.exists():
  time.sleep(5)
  if not identity() and not TERMINAL.exists():
   time.sleep(5);assert TERMINAL.exists(),'owned predecessor ended without terminal; never restart from a timeout'
 previous=json.loads(TERMINAL.read_bytes());assert previous['actual_exit_code'] in [0,1]
 report=json.loads((RUN/'API46-core-schema-focused-0001.json').read_bytes())
 assert report['actual_tests']==2 and report['errors']==0 and report['original_reader_entry_exit_and_source_guards_completed'],'inspect anomalous predecessor before full suite'
 # Preserve either actual predecessor assertion result. The frozen successor
 # receives the full original suite rather than replacing failed expectations.
 cmd=[sys.executable,'-B',str(ROOT/'product/lab/release-candidates/v1/interface/api-v47/checks_failure.py'),'--source-sha256',SOURCE,'--profile-sha256',PROFILE]
 print(json.dumps({'phase':'STARTING-FULL-ORIGINAL-FAILURE18','predecessor_actual_result':report['result'],'source_sha256':SOURCE,'profile_sha256':PROFILE,'original_900_second_bound_unchanged':True}),flush=True)
 result=subprocess.run(cmd)
 print(json.dumps({'phase':'FULL-ORIGINAL-FAILURE18-TERMINAL','actual_exit_code':result.returncode}),flush=True)
 return result.returncode
if __name__=='__main__':raise SystemExit(main())
