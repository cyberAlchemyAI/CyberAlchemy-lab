from pathlib import Path
import sys,subprocess,json
p=Path(__file__).resolve().parent;root=Path.cwd();u=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.artifact-type-registry';stem=sys.argv[1];script={'seal':'finalize.py','audit':'check_delivery.py'}[stem];argv=[sys.executable,'-B',str(u/script)];r=subprocess.run(argv,cwd=root,capture_output=True);paths={k:p/('full-delivery-'+stem+'-'+k+'.txt') for k in ['stdout','stderr']}
for k,raw in [('stdout',r.stdout),('stderr',r.stderr)]:
 with paths[k].open('xb') as f:f.write(raw)
with (p/('full-delivery-'+stem+'-command-result.json')).open('x') as f:json.dump({'argv':argv,'exit_code':r.returncode,**{k:str(v) for k,v in paths.items()}},f,indent=2);f.write('\n')
print(r.stdout.decode(),end='');print(r.stderr.decode(),end='',file=sys.stderr);raise SystemExit(r.returncode)
