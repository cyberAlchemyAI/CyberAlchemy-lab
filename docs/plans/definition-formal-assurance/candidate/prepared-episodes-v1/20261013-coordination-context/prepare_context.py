"""Exact source/admission/projection and predecessor checks before the prepared builder."""
from pathlib import Path
import ast,hashlib,json,re,sys
root=Path.cwd();p=Path(__file__).resolve().parent;prepared=p/'prepared';sys.path.insert(0,str(prepared));import build_candidate as b
prev=b.BASE/'definitions/cal.definition.capability-realization-binding';prior=json.loads((prev/'delivery-manifest.json').read_bytes());b.unchanged(prior['files']);assert len(prior['files'])==10389
priorprep=p.parent/'20261012-capability-realization-binding';audit=json.loads((priorprep/'full-delivery-audit-command-result.json').read_bytes());assert audit['exit_code']==0 and not(priorprep/audit['stderr']).read_bytes()
snapshot=b.snapshot();assert b.r.verify(snapshot,root)['files']==201
source=b.source_ref(snapshot,'cal.definition.coordination-context');assert source['sha256']=='547a714a9552f83985de78b2ce228421f5102c40cacf8c1edfb48ef46366a8aa'
doc=json.loads((root/source['path']).read_bytes());decisionpath=root/'docs/decisions/0018-definition-and-ctx00-promotion/decision.json';decision=json.loads(decisionpath.read_bytes());assert decision['status']=='owner-admitted' and len(decision['admitted_definitions'])==8
assert any(x['definition_id']==source['definition_id'] and x['sha256']==source['sha256'] for x in decision['admitted_definitions'])
c17path=root/'docs/decisions/0017-ctx00-source-admission/decision.json';c17=json.loads(c17path.read_bytes());assert c17['status']=='owner-admitted'
admissionspath=root/'authority/decisions/source-admission/ctx00-context-metamodel/v1/admissions.json';admissions=json.loads(admissionspath.read_bytes());assert len(admissions['admissions'])==7 and admissions['status']=='candidate-unadmitted'
external=json.loads((p/'external-source-inspection.json').read_bytes())
for row,reference in zip(external,doc['source_refs']):
 data=Path(row['absolute_path']).read_bytes();assert hashlib.sha256(data).hexdigest()==row['sha256']
 if row['selector']=='CAV2-D66':
  lines=data.splitlines(keepends=True);start=next(i for i,line in enumerate(lines) if line.startswith(b'## CAV2-D66:'));end=next((i for i in range(start+1,len(lines)) if lines[i].startswith(b'## ')),len(lines));selected=b''.join(lines[start:end])
 else:selected=data
 assert hashlib.sha256(selected).hexdigest()==row['selected_sha256']==reference['content_sha256']
 admission=next(x for x in admissions['admissions'] if x['admission_id']==reference['source_ref']);assert admission['selected_sha256']==row['selected_sha256'] and admission['non_effects']
 assert reference['source_admission_ref']==c17['decision_id'] and row['original_declared_absolute_path']!=row['absolute_path']
generatorpath=root/'authority/artifact-types/definition/v1/generator.py';schema=root/'authority/artifact-types/definition/v1/schema.json';namespace={}
nodes=[n for n in ast.parse(generatorpath.read_bytes()).body if isinstance(n,ast.FunctionDef) and n.name in ['esc','bullets','render']];exec(compile(ast.Module(body=nodes,type_ignores=[]),str(generatorpath),'exec'),namespace)
projection=(root/source['path']).with_name('DEFINITION.md');assert namespace['render'](doc).encode()==projection.read_bytes();assert not list(b.c.Draft202012Validator(json.loads(schema.read_bytes())).iter_errors(doc))
workpath=root/'docs/plans/definition-formal-assurance/candidate/foundations-first-v1/swu-manifest.json';work=json.loads(workpath.read_bytes());swu=next(x for x in work['units'] if x['id']=='F08-T.cal.definition.coordination-context');assert swu['inputs'][:2]==[source['path'],source['sha256']] and swu['depends_on_tasks']==['A04','C01','E02']
names=['cal.definition.'+name for name in ['definition','artifact','artifact-type','evidence','validation','validation-receipt','provenance','source','role','principal','principal-reference','decision','authority','policy','intent','work','product','identity-relation','identity-carrier','parent-instance-authority-separation-invariant','root-axis-independence-invariant','canonical-representation-invariant','bounded-context','context-lineage-record','context-view','context-request']]+['CAV2-D59','CAV2-D60']
for name in names:b.source_ref(snapshot,name)
assert len(names)==len(set(names))
paths=[root/source['path'],projection,generatorpath,schema,decisionpath,c17path,admissionspath,root/'authority/definitions/registry.json',b.BASE/'current-snapshot.json',prev/'receipt.json',prev/'delivery-manifest.json',workpath,workpath.with_name('dag.json'),priorprep/'full-delivery-audit-command-result.json',priorprep/audit['stdout'],priorprep/audit['stderr']]+[p/name for name in ['ARE-evidence.json','ARE-prepared-model-boundary.json','CONTEXT.md','external-source-inspection.json','builder_header.py','theory_body.py','builder_main.py','model_body.py','model_verify_tail.py','assemble_prepared.py','prepare_context.py','run_prepared.py']]+[prepared/name for name in ['build_candidate.py','verify_candidate.py']]
refs=[b.ref(path) for path in paths];b.unchanged(refs)
prerequisites=json.loads((prev/'context.json').read_bytes())['prerequisite_receipts']
for binding in prerequisites:
 b.unchanged([binding['receipt_ref']]);assert binding['result'].startswith('PASS') and json.loads((root/binding['receipt_ref']['path']).read_bytes())['task_result']==binding['result']
assert not(b.BASE/'definitions/cal.definition.coordination-context').exists()
context={'unit_id':swu['id'],'source_selection':source,'sources':refs,'external_sources':external,'prerequisite_receipts':prerequisites,'write_scope':swu['write_scope'],'direct_dependency_names':names,'authority_effect':'none','source_fidelity':'pending','semantic_ready':False,'pre_execution_check':{'native_output_absent':True,'source_files_current':201,'prior_candidate_files_preserved':10389,'previous_separate_delivery_audit_exit_code':0},'session_scope':{'kind':'local-native-SWU','blocking_user_decisions':[],'handoff':'none','experiment_harness':'not-applicable','deferred_meaning_decisions':['Owner and reference resolution','Materiality and desired-anchor correspondence','Independent boundary ownership','Actual identity, lifecycle, permission, source fidelity and whole proof']},'current_admission_ref':decision['decision_id'],'source_units_observed':len(b.co.inventory(doc)),'projection_bytes':len(projection.read_bytes()),'constraints':['Preserve 10389 predecessor files, 201 sources and original T/O/E/R/J scope.','Fourteen coordinates; one Product, optional Project and Goal, zero or more explicit independently owned boundary versions.','Materiality is separate from anchor difference; desired state is separate from successor reference.','No actual outcomes or target assumptions; no whole prior theory imports.']}
with (prepared/'context.json').open('x') as f:json.dump(context,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps({'result':'PASS-exact-C18-C17-CoordinationContext-prepared-source-context','source_units':len(b.co.inventory(doc)),'direct_dependencies':len(names),'prior_files':10389,'native_unit_created':False},indent=2))
