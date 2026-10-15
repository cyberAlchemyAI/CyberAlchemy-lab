"""Prepare source-only Semantic Epoch checks; no next native theory."""
from pathlib import Path
import ast
p=Path(__file__).resolve().parent;u=Path('docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.schema-evolution-invariant');n=u/'next-unit-preparation';n.mkdir()
prev=u.with_name('cal.definition.projection-specification')/'next-unit-preparation/inspect_source.py';s=prev.read_text().replace('cal.definition.representation-revision','cal.definition.semantic-epoch').replace('5bb818e70b0281dc14edcd4dade418335f50df93bc30c607823ecce5b3349850','e138c57bf7a69f958ca966690428bde166ff9d2137f557a14e153e94028272e3')
i=s.index("f=doc['voices'");j=s.index('observations=[]',i)
s=s[:i]+'''f=doc['voices']['scientific_formal'];expr=f['formal_expression'];norm=f['normative_statement']
ck('immutable-owner-selected-meaning-genus',all(x in norm for x in ['one immutable owner-selected version',"artifact's normative meaning"]))
ck('successor-owner-determines-material-change',all(x in norm for x in ['successor Semantic Epoch is required exactly when','owner determines','identity-preserving normative meaning, scope, exclusions, owned model, or semantic contracts materially changed']))
ck('representation-and-derived-refresh-do-not-create-epochs','Representation-only revisions and derived refreshes do not create Semantic Epochs.' in norm)
ck('formal-material-meaning-iff', 'NewSemanticEpoch(a_before,a_after) iff MaterialNormativeMeaning(a_before) != MaterialNormativeMeaning(a_after)' in expr)
ck('representation-change-not-sufficient','RepresentationChanged and MeaningEqual does not imply NewSemanticEpoch.' in expr)
ck('byte-label-and-equivalence-boundaries',all(x in f['boundary_conditions'] for x in ['A byte change alone does not prove semantic change.','A claim that meaning is preserved is reviewable evidence, not automatic equivalence.','A semantic successor requires explicit owner selection and applicable lineage.']))
ck('three-exclusions-three-boundaries-three-tests-two-notations',len(doc['scope']['exclusions'])==3 and len(doc['boundaries'])==3 and len(f['testable_conditions'])==3 and len(f['notation'])==2)
ck('positive-predecessor-delta-and-negative-representation-tests',all(x in f['testable_conditions'] for x in ['The change assessment separates semantic fields from representation fields.','Every new epoch identifies its predecessor and material meaning delta.','No representation-only change is classified as semantic lineage.']))
ck('source-body-does-not-select-existing-successor','does not classify any existing artifact, create lineage, or select a successor' in doc['claim_ceiling'])
'''+s[j:]
s=s.replace('requires_ProjectionSpecification_full_delivery_audit_first','requires_SchemaEvolutionInvariant_full_delivery_audit_first').replace('PASS-next-RepresentationRevision-source-only','PASS-next-SemanticEpoch-source-only')
i=s.index("with (P/'source-inspection.json').open('x')");j=s.index("print(json.dumps",i)
s=s[:i]+'''if '--write' in sys.argv:
 with (P/'source-inspection.json').open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\\n')
else:assert b.r.same_json(report,json.loads((P/'source-inspection.json').read_bytes()))
'''+s[j:]
ast.parse(s)
with (n/'inspect_source.py').open('x') as f:f.write(s)
with (n/'README.md').open('x') as f:f.write('''# Semantic Epoch source-only preparation

Exact C28 current Definition and two selected local upstream source versions are inspected before any native Semantic Epoch directory is created. Immutable owner-selected normative meaning and successor material-change assessment remain distinct from representation revision and derived refresh. The richer owner/lineage obligations and the short material-meaning iff require explicit source precedence in the next typed candidate. No existing artifact is classified and no actual successor or lineage is created. Next native work requires Schema Evolution Invariant full delivery seal and separate actual audit. Source fidelity, owner acceptance and whole proof remain pending.
''')
s='''from pathlib import Path
import sys,json,subprocess
p=Path(__file__).resolve().parent;root=Path.cwd();u=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.schema-evolution-invariant/next-unit-preparation';argv=[sys.executable,'-B',str(u/'inspect_source.py'),'--write'];r=subprocess.run(argv,cwd=root,capture_output=True)
for k,raw in [('stdout',r.stdout),('stderr',r.stderr)]:
 with (u/('source-inspection-'+k+'.txt')).open('xb') as f:f.write(raw)
with (u/'source-inspection-command-result.json').open('x') as f:json.dump({'argv':argv,'exit_code':r.returncode,'stdout':'source-inspection-stdout.txt','stderr':'source-inspection-stderr.txt'},f,indent=2);f.write('\\n')
if r.returncode==0:
 import hashlib
 report=json.loads((u/'source-inspection.json').read_bytes());files=[{'path':q.relative_to(root).as_posix(),'sha256':hashlib.sha256(q.read_bytes()).hexdigest()} for q in sorted(u.iterdir()) if q.is_file()];m={'schema_version':'definition-assurance-next-source-manifest/v1-candidate','authority_effect':'none','source':report['source'],'next_definition_priority':'F04-T.cal.definition.semantic-epoch','files':files,'owner_acceptance_ref':None,'actual_next_unit_created':False,'typed_interpretation_or_models_created':False,'semantic_ready':False,'mechanized_proof':False,'requires_SchemaEvolutionInvariant_full_delivery_audit_first':True}
 with (u/'manifest.json').open('x') as f:json.dump(m,f,indent=2);f.write('\\n')
print(r.stdout.decode(),end='');print(r.stderr.decode(),end='',file=sys.stderr);raise SystemExit(r.returncode)
'''
ast.parse(s)
with (p/'capture_next_source.py').open('x') as f:f.write(s)
print('Prepared source-only Semantic Epoch inspection.')
