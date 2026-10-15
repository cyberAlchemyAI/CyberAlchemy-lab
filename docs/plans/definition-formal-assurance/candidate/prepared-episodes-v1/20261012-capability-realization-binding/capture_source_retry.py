from pathlib import Path
import json,subprocess,sys
p=Path(__file__).resolve().parent;u=Path.cwd()/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.capability-realization-binding'
argv=[sys.executable,'-B',str(u/'verify_source_checks.py'),'--write'];r=subprocess.run(argv,cwd=Path.cwd(),capture_output=True)
for folder,stem in [(p,'source-retry-1'),(u,'source')]:
 row={'check':'source','argv':argv,'exit_code':r.returncode,'stdout':stem+'-stdout.txt','stderr':stem+'-stderr.txt'}
 for suffix,data in [('stdout.txt',r.stdout),('stderr.txt',r.stderr),('command-result.json',(json.dumps(row,indent=2)+'\n').encode())]:
  with (folder/(stem+'-'+suffix)).open('xb') as f:f.write(data)
print(r.stdout.decode(),end='');print(r.stderr.decode(),end='',file=sys.stderr);raise SystemExit(r.returncode)
