"""Prepare exact SEI consumer observations without changing frozen typed inputs."""
from pathlib import Path
import ast
p=Path(__file__).resolve().parent
u=Path('docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.schema-evolution-invariant')
s='''"""Exact current invariant, symbolic consumers and separate generic Schema shape."""
import ast,copy,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def pure(path,names):
 nodes=[x for x in ast.parse(path.read_bytes()).body if isinstance(x,ast.FunctionDef) and x.name in names];assert {x.name for x in nodes}==set(names);ns={};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),ns);return ns
def inspect(write=False):
 context=load('context.json');typed=load('types-logic-receipt.json');b.unchanged(typed['inputs']+typed['producer_results']+context['sources']);b.external_current(context);snap=b.snapshot();assert b.r.verify(snap,b.ROOT)['files']==201
 audit=b.ROOT/'docs/plans/definition-formal-assurance/candidate/prepared-episodes-v1/20261011-schema-evolution-invariant/typed-stage-audit-command-result.json';assert json.loads(audit.read_bytes())['exit_code']==0 and not audit.with_name('typed-stage-audit-stderr.txt').read_bytes()
 rp=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json';registry=json.loads(rp.read_bytes());current=[x for x in registry['admitted_contracts'] if x['lifecycle_state']=='admitted-current'];direct=[x for x in current if context['source_selection']['version_ref'] in x['semantic_definition_refs']];generic=next(x for x in current if x['artifact_type_ref']=='cal.artifact-type.definition/v2');schema_contract=next(x for x in current if x['artifact_type_ref']=='cal.artifact-type.schema/v1');receipt_direct=[x for x in current if b.source_ref(snap,'cal.definition.validation-receipt')['version_ref'] in x['semantic_definition_refs']]
 paths={'registry':rp,'source':b.ROOT/context['source_selection']['path'],'Definition_schema':b.ROOT/'authority/artifact-types/definition/v1/schema.json','Definition_generator':b.ROOT/'authority/artifact-types/definition/v1/generator.py','current_Definition_schema':b.ROOT/generic['schema_path'],'current_Schema_schema':b.ROOT/schema_contract['schema_path'],'current_Schema_type_artifact':b.ROOT/schema_contract['artifact_path'],'Schema_fixture':b.ROOT/'authority/artifact-types/schema/v1/fixtures/valid/record.json','Schema_validator':b.ROOT/'authority/artifact-types/schema/v1/validate.py','shared_Schema_validator':b.ROOT/'tooling/validators/endpoint_carrier.py','normalization_registry':b.ROOT/'evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/registry.json','typed_receipt':b.UNIT/'types-logic-receipt.json','typed_separate_audit':audit,'checker':b.UNIT/'inspect_carrier_consumers.py'}
 selections=load('comparison-selection.json')['separate_qualified_sources']
 for selected in selections:
  key=selected['definition_id'];q=b.ROOT/selected['path'];paths[key]=q;paths[key+'-projection']=q.with_name('DEFINITION.md')
 refs={key:b.ref(q) for key,q in paths.items()};docs={key:json.loads(q.read_bytes()) for key,q in paths.items() if q.suffix=='.json'};checks=[]
 def ck(name,ok):
  assert ok,name;checks.append({'check_id':name,'result':True})
 ck('frozen16-stage-separate-audit0',typed['result']=='PASS-for-typed-candidate-stage-only' and len(typed['inputs'])==16 and typed['full_delivery_sealed'] is False)
 ck('catalog143rows121current',len(registry['admitted_contracts'])==143 and len(current)==121)
 ck('no-current-direct-SEI-definition-contract',direct==[])
 ck('Definition-v2-own-meaning',generic['semantic_definition_refs']==[b.source_ref(snap,'cal.definition.definition')['version_ref']] and generic['schema_sha256']==refs['current_Definition_schema']['sha256'])
 ck('Schema-v1-exact-C70-own-meaning',schema_contract['admission_decision_ref']=='CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION' and schema_contract['schema_sha256']==refs['current_Schema_schema']['sha256'] and schema_contract['artifact_sha256']==refs['current_Schema_type_artifact']['sha256'] and schema_contract['semantic_definition_refs']==[b.source_ref(snap,'cal.definition.schema')['version_ref']])
 ck('no-current-ValidationReceipt-definition-contract-binding',receipt_direct==[])
 schema=docs['Definition_schema'];validator=b.c.Draft202012Validator(schema);gen=pure(paths['Definition_generator'],['esc','bullets','render']);observations=[]
 for selected in selections:
  key=selected['definition_id'];doc=docs[key];row=next(x for x in snap['current_entries'] if x['definition_id']==key)
  ck(key+'-exact-current-source',refs[key]=={'path':selected['path'],'sha256':selected['sha256']} and row['effective_state']=='admitted-current')
  ck(key+'-Definition-v1-valid',not list(validator.iter_errors(doc)))
  before=copy.deepcopy(doc);one=gen['render'](before).encode();two=gen['render'](before).encode();ck(key+'-two-pure-Definition-projections',one==two==paths[key+'-projection'].read_bytes() and before==doc)
  observations.append({'source':selected,'outer_Definition_classification':doc['classification'],'admission_decision_ref':row['admission_decision_ref'],'first_render_sha256':b.r.digest(one),'second_render_sha256':b.r.digest(two),'accepted_semantic_map_refs':[],'native_or_live_consumer_executed':False})
 dr=docs['source'];source=load('source-checks.json');ss=docs['current_Schema_schema'];artifact=docs['current_Schema_type_artifact'];nr=docs['normalization_registry']
 ck('C53-admission-retains-body-ceiling',source['current_registry_admission_ref']=='CAL-DECISION-0053-FULL-DEFINITION-QUEUE-ADMISSION' and 'It is not admitted' in dr['claim_ceiling'] and dr['source_refs'][0]['admission_posture']=='candidate-unadmitted' and 'prototype meaning' in dr['voices']['domain_context']['explanation'])
 ck('two-symbolic-primary-consumer-labels',dr['primary_consumer_refs']==['semantic.governance-axis-independence-invariant','semantic.schema'])
 consumer_labels=[]
 for label in dr['primary_consumer_refs']:
  row=next(x for x in nr['entries'] if x['target_id']==label);selected=b.source_ref(snap,row['definition_ref'].split('@')[0]);ck(label+'-exact-normalized-record',row['definition_ref']==selected['version_ref'] and row['path']==selected['path'] and row['sha256']==selected['sha256']);consumer_labels.append({'label':label,'normalization_entry':row,'current_Definition':selected,'source_label_is_filesystem_path':False,'current_admission_inferred_from_embedded_posture':False,'accepted_map':False,'native_or_live_consumer_executed':False})
 ck('Schema-closed14root5payload-fields',len(ss['required'])==14 and len(ss['properties']['payload']['required'])==5 and ss['additionalProperties'] is False and ss['properties']['payload']['additionalProperties'] is False and ss['properties']['authority_effect']=={'const':'none'})
 amendment_fields=['shape_change_ref','before_shape_ref','after_shape_ref','amendment_ref','reason_ref','compatibility_ref','witness_ref','witness_kind','witness_evidence_ref','residue_ref','residue_owner_ref','residue_effect_ref','rollout_ref','rollback_ref','enforcement_path','residue_path']
 ck('Schema-content-contract-not-amendment-record',not any(n in ss['properties'] or n in ss['properties']['payload']['properties'] for n in amendment_fields))
 ck('Schema-body-candidate-under-current-C70-overlay',artifact['status']=='candidate-unadmitted' and artifact['semantic_definition_refs']==schema_contract['semantic_definition_refs'])
 ck('Schema-fixture-valid-current-comparison-shape',not list(b.c.Draft202012Validator(ss).iter_errors(docs['Schema_fixture'])))
 validator_text=paths['shared_Schema_validator'].read_text();ck('Schema-validator-source-read-only', 'def ' in validator_text and 'semantic_definition_bindings' in validator_text)
 actual_observations=[{'source_ref':refs['Schema_fixture'],'comparison_schema_accepted':True,'fixture_is_actual_amendment':False,'accepted_SEI_consumer_map':False},{'source_ref':refs['Schema_validator'],'shared_source_ref':refs['shared_Schema_validator'],'inspection':'Scoped source read only; no carrier validator or writer executed','accepted_SEI_consumer_map':False}]
 probes=[]
 def probe(name,mutate,expected):
  doc=copy.deepcopy(dr);mutate(doc);before=copy.deepcopy(doc);errors=sorted('/'+('/'.join(map(str,e.absolute_path)))+': '+e.message for e in validator.iter_errors(doc));assert (not errors)==expected,(name,errors);one=gen['render'](doc).encode() if expected else None;two=gen['render'](doc).encode() if expected else None;assert one==two and before==doc;probes.append({'case_id':name,'schema_accepted':not errors,'expected_schema_acceptance':expected,'schema_errors':errors,'two_generated_projections_equal':True if expected else None,'fixture_digest':b.ir.digest(doc),'actual_semantic_obligations_enforced':False,'accepted_semantic_map':False})
 probe('exact-selected-SEI-Definition',lambda x:None,True)
 for n in schema['required']:probe('missing-required-'+n,lambda x,n=n:x.pop(n),False)
 for n in ['definition_id','semantic_owner_ref','term']:probe('unresolved-label-'+n,lambda x,n=n:x.update({n:'hyp:unresolved'}),True)
 for n in amendment_fields:probe('amendment-instance-field-not-Definition-'+n,lambda x,n=n:x.update({n:'hyp:unaccepted-map'}),False)
 probe('empty-source-selection',lambda x:x.update(source_refs=[]),True);probe('empty-consumer-list',lambda x:x.update(primary_consumer_refs=[]),True)
 for name,text in [('review-forbidden','hyp:every change requires an automated validator and review witnesses are forbidden'),('unowned-absence','hyp:absence without any residue owner or effect completes the amendment'),('witness-ref-proves-enforcement','hyp:a witness reference proves successful actual enforcement'),('amendment-grants-authority','hyp:an amendment grants publication and execution authority')]:probe(name,lambda x,text=text:x['voices']['scientific_formal'].update(normative_statement=text),True)
 carrier_probes=[];fixture=docs['Schema_fixture']
 def cp(name,mutate,expected):
  doc=copy.deepcopy(fixture);mutate(doc);errors=sorted('/'+('/'.join(map(str,e.absolute_path)))+': '+e.message for e in b.c.Draft202012Validator(ss).iter_errors(doc));assert (not errors)==expected,(name,errors);carrier_probes.append({'carrier':'Schema/v1','case_id':name,'whole_hypothetical_fixture_shape_validated':True,'schema_accepted':not errors,'schema_errors':errors,'fixture_digest':b.ir.digest(doc),'actual_amendment_created':False,'actual_SEI_semantics_enforced':False,'accepted_semantic_map':False})
 cp('unchanged-whole-Schema-fixture',lambda x:None,True)
 for n in ss['required']:cp('missing-root-'+n,lambda x,n=n:x.pop(n),False)
 for n in ss['properties']['payload']['required']:cp('missing-payload-'+n,lambda x,n=n:x['payload'].pop(n),False)
 for n in amendment_fields:cp('unsupported-amendment-field-'+n,lambda x,n=n:x.update({n:'hyp:unaccepted-map'}),False)
 cp('effect-promotion',lambda x:x.update(authority_effect='promotion'),False);cp('unrecognized-witness-kind-field',lambda x:x.update(witness_kind='absent'),False)
 for n in ['owner_ref','scope_ref','challenge_route']:cp('opaque-'+n,lambda x,n=n:x.update({n:'hyp:unresolved'}),True)
 for n in ss['properties']['payload']['required']:cp('unresolved-payload-'+n,lambda x,n=n:x['payload'].update({n:'hyp:uncomputed-or-unresolved'}),True)
 cp('empty-evidence',lambda x:x.update(evidence_refs=[]),True)
 cp('opaque-evidence',lambda x:x.update(evidence_refs=['hyp:not-observed']),True)
 cp('same-ID-changed-schema-content',lambda x:x['payload'].update(schema_ref='hyp:new-content',content_digest='hyp:not-a-hash'),True)
 cp('same-ID-changed-scope',lambda x:x.update(scope_ref='hyp:different-scope'),True)
 cp('overclaim-enforcement',lambda x:x.update(claim_ceiling='hyp:actual enforcement and owned absence proved'),True)
 cp('empty-relations',lambda x:x.update(relation_refs=[]),False)
 cp('invalid-relation-kind',lambda x:x['relation_refs'][0].update(relation_kind_ref='relation.hyp'),False)
 cp('allowed-components-unsupported-relation-role',lambda x:x['relation_refs'][0].update(direction='source'),True)
 comparison=[];compiled=load('static-ir.json');controls=load('model-controls.json')['results']
 wanted=[('exact-amendment-witness-and-owned-absence-records',(True,True)),('no-selected-changes',(True,False)),('only-first-change-selected',(True,False)),('independent-authority-not-supplied',(True,False)),('all-actual-outcomes-independently-supplied',(True,False)),('hybrid-one-named-check-cardinality-not-inferred',(True,False)),('non-governing-present-review-with-no-path',(True,True)),('independently-supported-actual-Enforcement',(True,True)),('wrong-normalized-meaning-meaningIdentity',(False,True)),('downstream-shape-without-enforcement-or-residue',(False,True))]
 for name,expected in wanted:
  row=next(x for x in controls if x['case_id']==name);model=copy.deepcopy(row['model']);e=v.Denotation(compiled['declarations'],model);tc=[{'clause_id':x['clause_id'],'truth':e.truth(x['formal_statement'])} for x in compiled['clauses'] if x['disposition']=='encoded'];pc=[{'population_id':x['population_id'],'truth':e.truth(x['statement'])} for x in compiled['populations'] if x['requirement']=='required'];T=all(x['truth'] for x in tc);I=all(x['truth'] for x in pc);assert (T,I)==expected and b.ir.digest(model)==row['model_sha256'],name;comparison.append({'case_id':name,'model':model,'model_sha256':b.ir.digest(model),'T':T,'I':I,'clause_results':tc,'population_results':pc,'accepted_SEI_carrier_map':False,'whole_upstream_theories_imported':False})
 issues=[
 'C53 current admission binds the exact Definition and D25 source, while embedded candidate/prototype metadata and source posture remain unchanged. No current contract directly binds the invariant; current Schema/v1 binds generic Schema D56 only.',
 'Generic Definition validation and exact pure projections accept normative prose forbidding review, allowing unowned witness absence, inferring enforcement from references or granting authority from amendments. Shape and repeatable rendering do not enforce amendment semantics.',
 'Schema/v1 requires typed content references, owner and scope but no amendment, reason, before/after, compatibility, witness, owned residue or rollout/rollback tuple. Missing amendment fields cannot be repaired by assuming Schema content is a change record.',
 'Whole Schema fixtures accept opaque or uncomputed content digests, unresolved owners and check profiles, absent evidence and changed schema content/scope under one ID. Allowed relation components do not alone enforce the exact role combination; the bound validator was read only, not executed.',
 'The two primary consumer labels resolve to exact normalization registry entries and current Definitions for Governance Axis Independence and Schema. Embedded candidate posture does not replace current admission; semantic references do not identify a filesystem consumer or establish an operational map.',
 'Witness kind and record universes, owned absence/effect fidelity, compatibility and executable rollout/rollback, enforcement paths, consumer denotations and independent authority need owner-reviewed maps. Ten independently evaluated SEI-only models keep T and I separate and import no whole upstream theories.'
 ]
 findings=[{'finding_id':'SEI-CONSUMER-FINDING-'+str(i+1).zfill(3),'issue':x,'status':'unresolved','accepted_map_refs':[]} for i,x in enumerate(issues)]
 prior=load('../cal.definition.representation-revision/delivery-manifest.json');b.unchanged(prior['files']+typed['inputs']+list(refs.values()));b.external_current(context)
 report={'schema_version':'definition-assurance-SchemaEvolutionInvariant-carrier-consumer-inspection/v1-candidate','result':'PASS-exact-SEI-meaning-symbolic-consumers-and-separate-Schema-shape','authority_effect':'none','source':context['source_selection'],'checks':checks,'check_count':len(checks),'selected_inputs':refs,'external_file_refs':source['external_file_refs'],'external_context_sections':source['external_source_observations'],'current_registry_contracts':len(registry['admitted_contracts']),'admitted_current_contracts':len(current),'direct_current_definition_binding_types':[x['artifact_type_ref'] for x in direct],'direct_current_ValidationReceipt_binding_types':[x['artifact_type_ref'] for x in receipt_direct],'generic_current_Definition_ref':generic['artifact_type_ref'],'current_Schema_type_ref':schema_contract['artifact_type_ref'],'meaning_observations':observations,'consumer_label_observations':consumer_labels,'selected_actual_consumer_observations':actual_observations,'shape_probes':probes,'shape_probe_count':len(probes),'shape_acceptances':sum(x['schema_accepted'] for x in probes),'carrier_shape_probes':carrier_probes,'carrier_shape_probe_count':len(carrier_probes),'carrier_shape_acceptances':sum(x['schema_accepted'] for x in carrier_probes),'separately_bound_comparison_contracts':[schema_contract],'typed_comparison_models':comparison,'typed_comparison_count':len(comparison),'accepted_semantic_map_refs':[],'unresolved_consumer_findings':findings,'isolated_pure_Definition_helpers_executed':True,'canonical_or_candidate_carrier_writer_executed':False,'native_or_live_consumer_executed':False,'real_amendment_enforcement_compatibility_or_authority_created':False,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_inventory_refresh_complete':False,'claim_ceiling':'Exact eighteen selected meanings, current catalog and two symbolic consumer resolutions, whole hypothetical Definition/Schema probes and ten fresh SEI-only model evaluations. No actual amendment, enforcement, accepted map or authority.'}
 if write:b.put('carrier-consumer-inspection.json',report)
 elif not b.r.same_json(report,load('carrier-consumer-inspection.json')):raise ValueError('Fresh SEI consumer observations differ')
 return report
if __name__=='__main__':
 x=inspect('--write' in b.sys.argv);print(json.dumps({k:x[k] for k in ['result','check_count','shape_probe_count','shape_acceptances','carrier_shape_probe_count','carrier_shape_acceptances','typed_comparison_count','current_registry_contracts','admitted_current_contracts','direct_current_definition_binding_types','semantic_ready']},indent=2))
'''
ast.parse(s)
with (u/'inspect_carrier_consumers.py').open('x') as f:f.write(s)
prev=p.with_name('20261011-representation-revision')
for n in ['capture_consumer.py','capture_delivery_checks.py']:
 s=(prev/n).read_text().replace('cal.definition.representation-revision','cal.definition.schema-evolution-invariant');ast.parse(s)
 with (p/n).open('x') as f:f.write(s)
print('Prepared exact SEI consumer comparison.')
