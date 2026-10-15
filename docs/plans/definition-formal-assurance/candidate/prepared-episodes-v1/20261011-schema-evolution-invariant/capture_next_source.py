from pathlib import Path
import sys,json,subprocess
p=Path(__file__).resolve().parent;root=Path.cwd();u=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.schema-evolution-invariant/next-unit-preparation';argv=[sys.executable,'-B',str(u/'inspect_source.py'),'--write'];r=subprocess.run(argv,cwd=root,capture_output=True)
for k,raw in [('stdout',r.stdout),('stderr',r.stderr)]:
 with (u/('source-inspection-'+k+'.txt')).open('xb') as f:f.write(raw)
with (u/'source-inspection-command-result.json').open('x') as f:json.dump({'argv':argv,'exit_code':r.returncode,'stdout':'source-inspection-stdout.txt','stderr':'source-inspection-stderr.txt'},f,indent=2);f.write('\n')
if r.returncode==0:
 import hashlib
 report=json.loads((u/'source-inspection.json').read_bytes());files=[{'path':q.relative_to(root).as_posix(),'sha256':hashlib.sha256(q.read_bytes()).hexdigest()} for q in sorted(u.iterdir()) if q.is_file()];m={'schema_version':'definition-assurance-next-source-manifest/v1-candidate','authority_effect':'none','source':report['source'],'next_definition_priority':'F04-T.cal.definition.semantic-epoch','files':files,'owner_acceptance_ref':None,'actual_next_unit_created':False,'typed_interpretation_or_models_created':False,'semantic_ready':False,'mechanized_proof':False,'requires_SchemaEvolutionInvariant_full_delivery_audit_first':True}
 with (u/'manifest.json').open('x') as f:json.dump(m,f,indent=2);f.write('\n')
print(r.stdout.decode(),end='');print(r.stderr.decode(),end='',file=sys.stderr);raise SystemExit(r.returncode)
