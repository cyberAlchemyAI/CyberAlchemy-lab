"""Fallback only after a second actual interrupted inventory capture.

Launcher exit zero means only that a separate process was started. Completion
still requires that process's actual command-result file, stdout parity, and
all six native command records. Do not run while the current process is live.
"""
from pathlib import Path
import json,os,subprocess,sys
root=Path.cwd();p=Path(__file__).resolve().parent
u=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/CAV2-D60'
for pid in [461904,461905,461906]:
 path=Path('/proc')/str(pid)/'cmdline'
 if path.exists() and path.read_bytes():
  raise RuntimeError('Current independent inventory process stilllive;fallback prohibited.')
second=p/'retained-interrupted-full-replay-2/interruption-observation.json'
if not second.is_file():raise RuntimeError('Second actual interruption evidence missing;fallback prohibited.')
record=json.loads(second.read_bytes())
assert record['actual_tool_capture_exit_code']==143
assert not(u/'fresh-inventory-command-result.json').exists()
assert not(p/'fresh-delivery-command-result.json').exists()
argv=[sys.executable,'-B',str(p/'capture_resumed_delivery.py')]
with (p/'detached-inventory-supervisor-stdout.txt').open('xb') as stdout, (p/'detached-inventory-supervisor-stderr.txt').open('xb') as stderr:
 child=subprocess.Popen(argv,cwd=root,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,start_new_session=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
 report={'schema_version':'Project-detached-inventory-launch/v1-candidate','launch_pid':child.pid,'argv':argv,'new_session':True,'process_liveness_requires_current_procfs':True,'actual_check_completed':False,'terminal_evidence_required':'fresh-delivery-command-result.json','stdout':'detached-inventory-supervisor-stdout.txt','stderr':'detached-inventory-supervisor-stderr.txt','authority_effect':'none','goal_status':'active'}
 with (p/'detached-inventory-launch.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
 print(json.dumps({'launched_pid':child.pid,'actual_check_completed':False,'goal_status':'active'}))

