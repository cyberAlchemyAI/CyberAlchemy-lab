from pathlib import Path
import json,subprocess,sys
root=Path.cwd();p=Path(__file__).resolve().parent;unit=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.intent-resolution';rows=[]
for name,script,args in [('author',p/'author_native.py',[]),('build',unit/'build_candidate.py',[]),('model',unit/'verify_candidate.py',['--write']),('source',unit/'verify_source_checks.py',['--write'])]:
 argv=[sys.executable,'-B',str(script)]+args;result=subprocess.run(argv,cwd=root,capture_output=True);out=unit if unit.exists() else p;row={'check':name,'argv':argv,'exit_code':result.returncode,'stdout':name+'-stdout.txt','stderr':name+'-stderr.txt'}
 for key,data in [('stdout',result.stdout),('stderr',result.stderr)]:
  with (out/row[key]).open('xb') as f:f.write(data)
 with (out/(name+'-command-result.json')).open('x') as f:json.dump(row,f,indent=2);f.write('\n')
 print(result.stdout.decode(),end='',flush=True);print(result.stderr.decode(),end='',file=sys.stderr,flush=True)
 if result.returncode or result.stderr:raise SystemExit(result.returncode or 1)
 rows.append(row)
with (unit/'native-stage-results.json').open('x') as f:json.dump(rows,f,indent=2);f.write('\n')
print('PASS-actual-native-author-build-model-source-checks',flush=True)
