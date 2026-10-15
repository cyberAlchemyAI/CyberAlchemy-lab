from pathlib import Path
import subprocess,sys,json
p=Path(__file__).resolve().parent;root=Path.cwd();u=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.withdrawal-record/next-unit-preparation';argv=[sys.executable,'-B',str(u/'inspect_source.py'),'--write'];r=subprocess.run(argv,cwd=root,capture_output=True)
for k,raw in [('stdout',r.stdout),('stderr',r.stderr)]:
 with (u/('source-inspection-'+k+'.txt')).open('xb') as f:f.write(raw)
with (u/'source-inspection-command-result.json').open('x') as f:json.dump({'argv':argv,'exit_code':r.returncode,'stdout':'source-inspection-stdout.txt','stderr':'source-inspection-stderr.txt'},f,indent=2);f.write('\n')
if r.returncode==0:
 sys.path.insert(0,str(u.parent));import build_candidate as b
 observed=json.loads((u/'source-inspection.json').read_bytes());files=[b.ref(x) for x in sorted(u.iterdir()) if x.is_file() and x.name!='manifest.json'];assert len(files)==6
 with (u/'manifest.json').open('x') as f:json.dump({'schema_version':'definition-assurance-next-unit-source-manifest/v1-candidate','authority_effect':'none','source':observed['source'],'next_definition_priority':'F05-T.cal.definition.actor','files':files,'actual_next_unit_created':False,'typed_interpretation_or_models_created':False,'owner_acceptance_ref':None,'semantic_ready':False,'mechanized_proof':False},f,indent=2,sort_keys=True);f.write('\n')
print(r.stdout.decode(),end='');print(r.stderr.decode(),end='',file=sys.stderr);raise SystemExit(r.returncode)
