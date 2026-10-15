from pathlib import Path
import json,subprocess,sys
p=Path(__file__).resolve().parent;unit=Path.cwd()/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.implementation';kind=sys.argv[1];assert kind in ['freeze','audit']
script='close_types_logic_stage.py' if kind=='freeze' else 'check_types_logic_stage.py';argv=[sys.executable,'-B',str(unit/script)];result=subprocess.run(argv,cwd=Path.cwd(),capture_output=True);stem='typed-stage-'+kind
for suffix,data in [('stdout.txt',result.stdout),('stderr.txt',result.stderr),('command-result.json',(json.dumps({'argv':argv,'exit_code':result.returncode,'stdout':stem+'-stdout.txt','stderr':stem+'-stderr.txt'},indent=2)+'\n').encode())]:
 with (p/(stem+'-'+suffix)).open('xb') as f:f.write(data)
print(result.stdout.decode(),end='');print(result.stderr.decode(),end='',file=sys.stderr);raise SystemExit(result.returncode)
