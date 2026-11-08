from pathlib import Path
import json,subprocess,sys
root=Path.cwd();p=Path(__file__).resolve().parent;rows=[]
for name,script,args in [('context',p/'prepare_context.py',[]),('build',p/'prepared/build_candidate.py',[]),('model',p/'prepared/verify_candidate.py',['--write'])]:
 argv=[sys.executable,'-B',str(script)]+args;r=subprocess.run(argv,cwd=root,capture_output=True)
 row={'check':name,'argv':argv,'exit_code':r.returncode,'stdout':'prepared-'+name+'-stdout.txt','stderr':'prepared-'+name+'-stderr.txt'}
 for suffix,data in [('stdout',r.stdout),('stderr',r.stderr)]:
  with (p/row[suffix]).open('xb') as f:f.write(data)
 with (p/('prepared-'+name+'-command-result.json')).open('x') as f:json.dump(row,f,indent=2);f.write('\n')
 print(r.stdout.decode(),end='',flush=True);print(r.stderr.decode(),end='',file=sys.stderr,flush=True)
 if r.returncode or r.stderr:raise SystemExit(r.returncode or 1)
 rows.append(row)
with (p/'prepared-check-results.json').open('x') as f:json.dump(rows,f,indent=2);f.write('\n')
print('PASS-actual-prepared-source-build-and-finite-model-checks',flush=True)
