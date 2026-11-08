"""Native CI author after Project full audit and exact assembled semantic precheck."""
from pathlib import Path
import hashlib,json,shutil,sys
root=Path.cwd();base=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1'
prev=base/'definitions/CAV2-D60';unit=base/'definitions/cal.definition.capability-instance'
prepared=Path(__file__).resolve().parent;p=prepared.parent
priorprep=p.parent/'20261012-project'
sys.path.insert(0,str(prev));import build_candidate as b
audit=json.loads((priorprep/'full-delivery-audit-command-result.json').read_bytes())
assert audit['exit_code']==0 and str(prev/'check_delivery.py') in audit['argv']
err=Path(audit['stderr']);assert not err.read_bytes()
snap=b.snapshot();checked=b.r.verify(snap,root);prior=json.loads((prev/'delivery-manifest.json').read_bytes())
b.unchanged(prior['files'])
assert len(prior['files'])==10188 and not unit.exists() and len(list((base/'definitions').glob('*/t.json')))==108
source=b.source_ref(snap,'cal.definition.capability-instance')
assert source['sha256']=='d1e0140d47887b3f8c49334e81c33bd105edaecaf02f3df3df841885340505a5'
receipts=json.loads((prev/'context.json').read_bytes())['prerequisite_receipts']
b.unchanged([x['receipt_ref'] for x in receipts])
assert all(json.loads((root/x['receipt_ref']['path']).read_bytes())['task_result']==x['result'] for x in receipts)
manifest=root/'docs/plans/definition-formal-assurance/candidate/foundations-first-v1/swu-manifest.json'
work=json.loads(manifest.read_bytes());swu=next(x for x in work['units'] if x['id']=='F08-T.cal.definition.capability-instance')
assert swu['inputs'][:2]==[source['path'],source['sha256']] and swu['depends_on_tasks']==['A04','C01','E02']
assert swu['outputs']==[(unit/'t.json').relative_to(root).as_posix()] and swu['write_scope']==[unit.relative_to(root).as_posix()+'/']
nextprep=prev/'next-unit-preparation';planned=json.loads((nextprep/'manifest.json').read_bytes());b.unchanged(planned['files'])
inspection=json.loads((nextprep/'source-inspection.json').read_bytes())
assert inspection['source']==source and len(inspection['checks'])==27 and all(x['result'] for x in inspection['checks'])
assert inspection['source_units']==20 and inspection['projection_bytes']==4095 and len(inspection['external_file_refs'])==2
precheck=json.loads((p/'assembled-check-command-result.json').read_bytes());observed=json.loads((p/'assembled-check-stdout.txt').read_bytes())
assert precheck['exit_code']==0 and not(p/'assembled-check-stderr.txt').read_bytes()
assert (observed['source_units'],observed['mapped_source_clauses'],observed['encoded_source_clauses'],observed['declarations'],observed['required_populations'],observed['controls'],observed['countermodel_queries'],observed['conditioned_queries'],observed['maximum_steps'])==(20,20,12,171,18,186,28,2,30041)
assert observed['native_unit_created'] is False
gate=json.loads((p/'ARE-evidence.json').read_bytes())
assert all(gate[n]['ok'] is True and gate[n]['kind']=='gate' and gate[n]['authority_effect']=='none' for n in ['route','context','effect'])
names=['cal.definition.'+n for n in ['definition','artifact','artifact-type','evidence','validation','validation-receipt','provenance','source','role','principal','principal-reference','decision','authority','policy','intent','work','product','identity-relation','identity-carrier','parent-instance-authority-separation-invariant','root-axis-independence-invariant','canonical-representation-invariant','product-capability','bounded-context','coordination-context','conformance','cyberalchemy-construction-method','contract']]+['CAV2-D59','CAV2-D60']
assert len(names)==len(set(names))==30
for n in names:b.source_ref(snap,n)
nexts=[x for x in work['units'] if x['kind']=='definition-T' and x['definition_id']!=source['definition_id'] and not(base/'definitions'/x['definition_id']/'t.json').exists()]
assert nexts[0]['id']=='F08-T.cal.definition.capability-realization-binding'
old=priorprep/'capability-instance-preparation'
failed=[b.ref(q) for q in sorted((old/'retained-failed-syntax-1').rglob('*')) if q.is_file()]
corrected=[b.ref(q) for q in sorted((old/'retained-before-module-file-binding').rglob('*')) if q.is_file()]
assert len(failed)==len(corrected)==5
paths=[root/source['path'],base/'current-snapshot.json',prev/'delivery-manifest.json',prev/'receipt.json',manifest,manifest.parent/'dag.json',nextprep/'manifest.json',nextprep/'source-inspection.json']+[root/x['path'] for x in inspection['selected_inputs'].values()]
paths += [p/n for n in ['CONTEXT.md','ARE-evidence.json','builder_header.py','theory_body.py','builder_main.py','model_body.py','model_verify_tail.py','verify_source_checks.py','check_assembled_prepared.py','assembled-check-command-result.json','assembled-check-stdout.txt','assembled-check-stderr.txt','prepared-check-command-result.json','prepared-check-stdout.txt','prepared-check-stderr.txt']]
paths += [prepared/n for n in ['author_candidate.py','build_candidate.py','verify_candidate.py','verify_source_checks.py']]
refs=[b.ref(q) for q in dict.fromkeys(paths)];b.unchanged(refs+failed+corrected)
external=[]
for item in inspection['external_file_refs']:
 q=Path(item['absolute_path']);raw=q.read_bytes()
 assert b.r.digest(raw)==item['sha256'] and not Path(item['original_declared_absolute_path']).exists()
 selected=b''.join(raw.splitlines(keepends=True)[item['observed_start_line']-1:item['observed_end_line']])
 assert b.r.digest(selected)==item['selected_sha256']
 if q not in external:external.append(q)
external += [priorprep/'full-delivery-audit-command-result.json',priorprep/'full-delivery-audit-stdout.txt',priorprep/'full-delivery-audit-stderr.txt']
ext=[{'absolute_path':str(q),'sha256':b.r.digest(q.read_bytes())} for q in external]
context={'authority_effect':'none','unit_id':swu['id'],'source_selection':source,'sources':refs,'external_sources':ext,'prerequisite_receipts':receipts,'write_scope':swu['write_scope'],
'pre_execution_check':{'output_absent_before_creation':True,'prior_candidate_files_preserved':10188,'source_files_current':checked['files'],'previous_separate_delivery_audit_exit_code':0,'prepared_source_and_model_check_exit_code':0},
'retained_preparation_failure_refs':failed,'retained_successful_preparation_refs':corrected+[b.ref(p/n) for n in ['check_assembled_prepared.py','assembled-check-command-result.json','assembled-check-stdout.txt','assembled-check-stderr.txt']],
'retained_successful_native_stage_refs':[],'direct_dependency_names':names,
'unavailable_requested_dependency_labels':['capability-version-reference','local-owner-interpretation','parent-and-instance-authority-lane-map','extension-scope-contract','D65-construction-binding-map','conformance-reference-collection','lifecycle-interpretation','recursion-budget-or-stop-contract','terminal-handoff-contract'],
'next_definition_priority':nexts[0]['id'],
'session_scope':{'kind':'local-native-SWU','blocking_user_decisions':[],'handoff':'none','experiment_harness':'not-applicable','deferred_meaning_decisions':['Owner locality andcandidate semantic-context membership','Exact parent/version/identity andclaim-lane consumer maps','Adoption/construction/conformance/lifecycle/recursion/handoff evidence','Actual authority,fidelity,shared interpretation andwhole proof'],'routing_posture':{'selected':'CA2-ROUTE-GOVERNANCE','write_ceiling':'candidate evidence only','authority_effect':'none','enforcement_runtime_admitted':False}},
'constraints':['Preserve10188sealedpredecessorfiles201sources/original183identities189versions121tasks511edges797SWUs36frontiers.',
'Retainowner-local version-exact realizationORspecialization positivegenus and16coordinates;owner issource-backed companion,notcanonical tuplechange.',
'Explicitcoordination/semanticcontext nominations,oneexactparentversion andsharedidentityinequality;no accepted wholeprior theory imported.',
'Parent/instanceclaimlanes separated oncommoncandidateclaimcarrier;no required differentprincipals,strengthlabels orclaimcontent.',
'RecursionbudgetORstop inclusively withrecomposition/handoff;no actualtermination/fixedpoint orruntime compliance inferred.',
'Conformance andparentauthority conditionedcountermodels havetrueantecedents;no instanceauthority inferred andindependent actualauthority remainspossible.',
'ExactC18positiveDefinition/C17scopedD64/D67sourceuses andrelocatedselectedbytes preserved;no unselectedlegacysemantics orprivate authority imported.',
'One Python syntaxpreparation failure retained beforecorrection;no semanticprecheckfailure orweakenedlimits.']}
unit.mkdir()
with (unit/'context.json').open('x') as f:json.dump(context,f,indent=2,sort_keys=True);f.write('\n')
for name in ['author_candidate.py','build_candidate.py','verify_candidate.py','verify_source_checks.py']:shutil.copyfile(prepared/name,unit/name)
b.unchanged(prior['files']+refs+failed+corrected);b.external_current(context)
assert b.r.verify(snap,root)['files']==201
print(json.dumps({'result':'PASS-exact-C18-CapabilityInstance-native-preflight','prior_candidate_files_preserved':10188,'source_files_current':201,'direct_semantic_uses':30,'retained_prepared_syntax_failure':1,'retained_prepared_semantic_failures':0,'actual_Instance_created_or_adopted':False,'next_definition_priority':nexts[0]['id']},indent=2))

