from pathlib import Path
import subprocess,sys,json
root=Path.cwd();p=Path(__file__).resolve().parent;unit=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.canonical-package-manifest';stem=sys.argv[1];script={'profile':'verify_authority_profile.py','reuse':'verify_static_snapshot_reuse.py','dependency':'verify_dependencies.py','inventory':'verify_current_inventory.py'}[stem];argv=[sys.executable,'-B',str(unit/script),'--write'];r=subprocess.run(argv,cwd=root,capture_output=True)
for k,raw in [('stdout',r.stdout),('stderr',r.stderr)]:
 with (unit/(stem+'-'+k+'.txt')).open('xb') as f:f.write(raw)
with (unit/(stem+'-command-result.json')).open('x') as f:json.dump({'argv':argv,'exit_code':r.returncode,'stdout':stem+'-stdout.txt','stderr':stem+'-stderr.txt'},f,indent=2);f.write('\n')
if stem=='dependency' and r.returncode==0:
 x=json.loads(r.stdout);print(json.dumps({k:v for k,v in x.items() if k not in ['missing_dependency_packets','cycles']},indent=2));print(json.dumps({'missing_packets':len(x['missing_dependency_packets']),'unclassified_cycles':len(x['cycles'])}))
else:print(r.stdout.decode(),end='')
print(r.stderr.decode(),end='',file=sys.stderr);raise SystemExit(r.returncode)
