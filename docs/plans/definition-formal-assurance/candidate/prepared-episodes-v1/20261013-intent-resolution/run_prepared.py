from pathlib import Path
import json,subprocess,sys
root=Path.cwd();p=Path(__file__).resolve().parent;rows=[]
for name,script,args in [('context',p/'prepare_context.py',[]),('build',p/'prepared/build_candidate.py',[]),('model',p/'prepared/verify_candidate.py',['--write']),('source',p/'prepared/verify_source_checks.py',['--write'])]:
 argv=[sys.executable,'-B',str(script)]+args;result=subprocess.run(argv,cwd=root,capture_output=True);row={'check':name,'argv':argv,'exit_code':result.returncode,'stdout':'prepared-'+name+'-stdout.txt','stderr':'prepared-'+name+'-stderr.txt'}
 for key,data in [('stdout',result.stdout),('stderr',result.stderr)]:
  with (p/row[key]).open('xb') as f:f.write(data)
 with (p/('prepared-'+name+'-command-result.json')).open('x') as f:json.dump(row,f,indent=2);f.write('\n')
 print(result.stdout.decode(),end='',flush=True);print(result.stderr.decode(),end='',file=sys.stderr,flush=True)
 if result.returncode or result.stderr:raise SystemExit(result.returncode or 1)
 rows.append(row)
with (p/'prepared-check-results.json').open('x') as f:json.dump(rows,f,indent=2);f.write('\n')
print('PASS-actual-prepared-source-build-and-finite-model-checks',flush=True)
