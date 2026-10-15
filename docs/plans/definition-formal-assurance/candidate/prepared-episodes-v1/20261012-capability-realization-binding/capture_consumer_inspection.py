from pathlib import Path
import json,subprocess,sys
root=Path.cwd();p=Path(__file__).resolve().parent;u=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.capability-realization-binding';replay='--replay' in sys.argv
argv=[sys.executable,'-B',str(u/'inspect_carrier_consumers.py')]+([] if replay else ['--write']);r=subprocess.run(argv,cwd=root,capture_output=True);stem='carrier-inspection-replay' if replay else 'carrier-inspection';record={'argv':argv,'exit_code':r.returncode,'stdout':stem+'-stdout.txt','stderr':stem+'-stderr.txt'}
for folder in [p] if replay else [p,u]:
 for suffix,data in [('stdout.txt',r.stdout),('stderr.txt',r.stderr),('command-result.json',(json.dumps(record,indent=2)+'\n').encode())]:
  with (folder/(stem+'-'+suffix)).open('xb') as f:f.write(data)
print(r.stdout.decode(),end='');print(r.stderr.decode(),end='',file=sys.stderr);raise SystemExit(r.returncode)
