from pathlib import Path
import subprocess,sys,json
u=Path(__file__).resolve().parent;argv=[sys.executable,str(u/'verify_source_checks.py'),'--write'];p=subprocess.run(argv,capture_output=True)
for suffix,data in [('stdout',p.stdout),('stderr',p.stderr)]:
 with (u/('source-'+suffix+'.txt')).open('xb') as out:out.write(data)
with (u/'source-command-result.json').open('x') as out:json.dump({'argv':argv,'exit_code':p.returncode,'stdout':'source-stdout.txt','stderr':'source-stderr.txt'},out,indent=2);out.write('\n')
print(p.stdout.decode(),end='');print(p.stderr.decode(),end='',file=sys.stderr);print(json.dumps({'producer':'source','exit_code':p.returncode}));raise SystemExit(p.returncode)
