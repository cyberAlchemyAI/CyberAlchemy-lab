from pathlib import Path
import json,subprocess,sys
p=Path(__file__).resolve().parent;root=Path.cwd();u=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.artifact-type-registry';stem=sys.argv[1];script={'freeze':'close_types_logic_stage.py','audit':'check_types_logic_stage.py'}[stem];argv=[sys.executable,'-B',str(u/script)];r=subprocess.run(argv,cwd=root,capture_output=True);paths={k:p/('typed-stage-'+stem+'-'+k+'.txt') for k in ['stdout','stderr']}
for k,raw in [('stdout',r.stdout),('stderr',r.stderr)]:
 with paths[k].open('xb') as f:f.write(raw)
with (p/('typed-stage-'+stem+'-command-result.json')).open('x') as f:json.dump({'argv':argv,'exit_code':r.returncode,**{k:str(v) for k,v in paths.items()}},f,indent=2);f.write('\n')
print(r.stdout.decode(),end='');print(r.stderr.decode(),end='',file=sys.stderr);raise SystemExit(r.returncode)
