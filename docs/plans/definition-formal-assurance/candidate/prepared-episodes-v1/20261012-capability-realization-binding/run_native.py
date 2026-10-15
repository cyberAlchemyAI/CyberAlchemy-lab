from pathlib import Path
import json,subprocess,sys
root=Path.cwd();p=Path(__file__).resolve().parent;u=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.capability-realization-binding'
for name,script,args in [('author',p/'author_native.py',[]),('build',u/'build_candidate.py',[]),('model',u/'verify_candidate.py',['--write']),('source',u/'verify_source_checks.py',['--write'])]:
 argv=[sys.executable,'-B',str(script)]+args;r=subprocess.run(argv,cwd=root,capture_output=True);row={'check':name,'argv':argv,'exit_code':r.returncode,'stdout':name+'-stdout.txt','stderr':name+'-stderr.txt'}
 for folder in [p,u] if u.exists() else [p]:
  for suffix,data in [('stdout.txt',r.stdout),('stderr.txt',r.stderr),('command-result.json',(json.dumps(row,indent=2)+'\n').encode())]:
   with (folder/(name+'-'+suffix)).open('xb') as f:f.write(data)
 print(r.stdout.decode(),end='',flush=True);print(r.stderr.decode(),end='',file=sys.stderr,flush=True)
 if r.returncode or r.stderr:raise SystemExit(r.returncode or 1)
