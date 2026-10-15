from pathlib import Path
import json,subprocess,sys
p=Path(__file__).resolve().parent;u=Path.cwd()/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.capability-realization-binding';replay='--replay' in sys.argv
argv=[sys.executable,'-B',str(u/'verify_authority_profile.py')]+([] if replay else ['--write']);r=subprocess.run(argv,cwd=Path.cwd(),capture_output=True);stem='profile-replay' if replay else 'profile';record={'argv':argv,'exit_code':r.returncode,'stdout':stem+'-stdout.txt','stderr':stem+'-stderr.txt'}
for folder in [p] if replay else [p,u]:
 for suffix,data in [('stdout.txt',r.stdout),('stderr.txt',r.stderr),('command-result.json',(json.dumps(record,indent=2)+'\n').encode())]:
  with (folder/(stem+'-'+suffix)).open('xb') as f:f.write(data)
print(r.stdout.decode(),end='');print(r.stderr.decode(),end='',file=sys.stderr);raise SystemExit(r.returncode)
