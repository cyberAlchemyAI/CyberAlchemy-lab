from pathlib import Path
import sys,subprocess,json,hashlib
p=Path(__file__).resolve().parent;root=Path.cwd();u=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.principal-reference/next-unit-preparation';argv=[sys.executable,'-B',str(u/'inspect_source.py'),'--write'];r=subprocess.run(argv,cwd=root,capture_output=True)
for k,raw in [('stdout',r.stdout),('stderr',r.stderr)]:
 with (u/('source-inspection-'+k+'.txt')).open('xb') as f:f.write(raw)
with (u/'source-inspection-command-result.json').open('x') as f:json.dump({'argv':argv,'exit_code':r.returncode,'stdout':'source-inspection-stdout.txt','stderr':'source-inspection-stderr.txt'},f,indent=2)
print(r.stdout.decode(),end='');print(r.stderr.decode(),end='',file=sys.stderr)
if r.returncode:raise SystemExit(r.returncode)
with (u/'CONTEXT.md').open('x') as f:f.write('Exact C53 source-only preparation. No next native T or model created. Upstream CAV2-D28 bytes and source-owner interpretation remain pending. The watch guard distinguishes value constraints,cycle permission,explicit acyclicity and recorded reviewed exceptions;not a contextuality theorem or a ban on harmless cyclic/non-value or acyclic/value edges. Next native definition requires Principal Reference full seal and separate actual audit0. Original183/189/201scope and prior9364sealedfiles preserved;goalactive.')
files=[{'path':str(f.relative_to(root)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted(u.iterdir()) if f.is_file()];assert len(files)==6
source=json.loads((u/'source-inspection.json').read_bytes())['source']
with (u/'manifest.json').open('x') as f:json.dump({'source':source,'files':files,'authority_effect':'none','next_definition_priority':'F07-T.cal.definition.constraint-cycle-safety-invariant','actual_next_unit_created':False,'typed_interpretation_or_models_created':False,'owner_acceptance_ref':None,'semantic_ready':False,'mechanized_proof':False},f,indent=2)

