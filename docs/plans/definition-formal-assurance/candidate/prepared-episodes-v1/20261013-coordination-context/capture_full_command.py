from pathlib import Path
import json,subprocess,sys
root=Path.cwd();p=Path(__file__).resolve().parent;unit=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.coordination-context';name,script=sys.argv[1:3];args=sys.argv[3:];assert '/' not in name and script.endswith('.py')
argv=[sys.executable,'-B',str(unit/script)]+args;result=subprocess.run(argv,cwd=root,capture_output=True);stem=name;out=p if name.startswith('full-delivery') else unit
row={'check':name,'argv':argv,'exit_code':result.returncode,'stdout':stem+'-stdout.txt','stderr':stem+'-stderr.txt'}
for key,data in [('stdout',result.stdout),('stderr',result.stderr)]:
 with (out/row[key]).open('xb') as f:f.write(data)
with (out/(stem+'-command-result.json')).open('x') as f:json.dump(row,f,indent=2);f.write('\n')
print(result.stdout.decode(),end='',flush=True);print(result.stderr.decode(),end='',file=sys.stderr,flush=True);raise SystemExit(result.returncode or bool(result.stderr))
