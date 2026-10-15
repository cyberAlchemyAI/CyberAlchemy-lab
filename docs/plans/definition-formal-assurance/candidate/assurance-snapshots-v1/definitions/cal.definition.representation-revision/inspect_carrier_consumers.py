"""Current Definition and Generated Output shapes;no actual refresh or accepted maps."""
import ast,copy,json
from pathlib import Path
import build_candidate as b
import verify_candidate as a
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def pure(path,names):
 nodes=[x for x in ast.parse(path.read_bytes()).body if isinstance(x,ast.FunctionDef) and x.name in names];assert {x.name for x in nodes}==set(names);ns={};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),ns);return ns
def inspect(write=False):
 context=load('context.json');typed=load('types-logic-receipt.json');b.unchanged(typed['inputs']+typed['producer_results']+typed['retained_preparation_failure_refs']+context['sources']);b.external_current(context);snap=b.snapshot();assert b.r.verify(snap,b.ROOT)['files']==201
 audit=b.ROOT/'docs/plans/definition-formal-assurance/candidate/prepared-episodes-v1/20261011-representation-revision/typed-stage-audit-command-result.json';assert json.loads(audit.read_bytes())['exit_code']==0 and not audit.with_name('typed-stage-audit-stderr.txt').read_bytes()
 rp=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json';registry=json.loads(rp.read_bytes());current=[x for x in registry['admitted_contracts'] if x['lifecycle_state']=='admitted-current'];direct=[x for x in current if context['source_selection']['version_ref'] in x['semantic_definition_refs']];generic=next(x for x in current if x['artifact_type_ref']=='cal.artifact-type.definition/v2');generated=next(x for x in current if x['artifact_type_ref']=='cal.artifact-type.generated-output/v2');receipt_direct=[x for x in current if b.source_ref(snap,'cal.definition.validation-receipt')['version_ref'] in x['semantic_definition_refs']]
 comparison_contracts=[next(x for x in current if x['artifact_type_ref']==n) for n in ['cal.artifact-type.context-migration-manifest/v2','cal.artifact-type.bounded-context/v3']]
 paths={'registry':rp,'source':b.ROOT/context['source_selection']['path'],'Definition_schema':b.ROOT/'authority/artifact-types/definition/v1/schema.json','Definition_generator':b.ROOT/'authority/artifact-types/definition/v1/generator.py','current_Definition_schema':b.ROOT/generic['schema_path'],'current_GeneratedOutput_schema':b.ROOT/generated['schema_path'],'current_GeneratedOutput_type_artifact':b.ROOT/generated['artifact_path'],'typed_receipt':b.UNIT/'types-logic-receipt.json','typed_separate_audit':audit,'checker':b.UNIT/'inspect_carrier_consumers.py','prior_CPRI_profile':b.BASE/'definitions/cal.definition.canonical-representation-invariant/authority-profile-checks.json','prior_ValidationReceipt_profile':b.BASE/'definitions/cal.definition.validation-receipt/authority-profile-checks.json'}
 selections=[b.source_ref(snap,'cal.definition.'+n) for n in ['representation-revision','semantic-epoch','derived-refresh','canonical-representation-invariant','definition','bounded-context','context-migration-manifest','validation']]
 for selected in selections:
  key=selected['definition_id'];q=b.ROOT/selected['path'];paths[key]=q;paths[key+'-projection']=q.with_name('DEFINITION.md')
 for contract in comparison_contracts:
  paths[contract['artifact_type_ref']+'-schema']=b.ROOT/contract['schema_path'];paths[contract['artifact_type_ref']+'-artifact']=b.ROOT/contract['artifact_path']
 refs={key:b.ref(q) for key,q in paths.items()};docs={key:json.loads(q.read_bytes()) for key,q in paths.items() if q.suffix=='.json'};checks=[]
 def ck(name,ok):
  assert ok,name;checks.append({'check_id':name,'result':True})
 ck('frozen16-stage-separate-audit0',typed['result']=='PASS-for-typed-candidate-stage-only' and len(typed['inputs'])==16 and typed['full_delivery_sealed'] is False)
 ck('catalog143rows121current',len(registry['admitted_contracts'])==143 and len(current)==121)
 ck('no-current-direct-RepresentationRevision-definition-contract',direct==[])
 ck('generic-Definition-v2-not-refresh-instance',generic['semantic_definition_refs']==[b.source_ref(snap,'cal.definition.definition')['version_ref']] and generic['schema_sha256']==refs['current_Definition_schema']['sha256'])
 ck('generated-output-v2-exact-current-C74A',generated['admission_decision_ref']=='CAL-DECISION-0074A-GOVERNANCE-CARRIER-ADMISSION' and generated['schema_sha256']==refs['current_GeneratedOutput_schema']['sha256'] and generated['artifact_sha256']==refs['current_GeneratedOutput_type_artifact']['sha256'] and generated['semantic_definition_refs']==[b.source_ref(snap,'cal.definition.generated-output')['version_ref']])
 ck('no-current-ValidationReceipt-definition-contract-binding',receipt_direct==[])
 for contract in comparison_contracts:
  ck(contract['artifact_type_ref']+'-exact-current-schema-artifact',refs[contract['artifact_type_ref']+'-schema']['sha256']==contract['schema_sha256'] and refs[contract['artifact_type_ref']+'-artifact']['sha256']==contract['artifact_sha256'])
 schema=docs['Definition_schema'];validator=b.c.Draft202012Validator(schema);gen=pure(paths['Definition_generator'],['esc','bullets','render']);observations=[]
 for selected in selections:
  key=selected['definition_id'];doc=docs[key];row=next(x for x in snap['current_entries'] if x['definition_id']==key)
  ck(key+'-exact-current-source',refs[key]=={'path':selected['path'],'sha256':selected['sha256']} and row['effective_state']=='admitted-current')
  ck(key+'-Definition-v1-valid',not list(validator.iter_errors(doc)))
  before=copy.deepcopy(doc);one=gen['render'](before).encode();two=gen['render'](before).encode();ck(key+'-two-pure-Definition-projections',one==two==paths[key+'-projection'].read_bytes() and before==doc)
  observations.append({'source':selected,'outer_Definition_classification':doc['classification'],'admission_decision_ref':row['admission_decision_ref'],'first_render_sha256':b.r.digest(one),'second_render_sha256':b.r.digest(two),'accepted_semantic_map_refs':[],'native_or_live_consumer_executed':False})
 dr=docs['cal.definition.representation-revision'];source=load('source-checks.json');ms=docs['cal.artifact-type.context-migration-manifest/v2-schema'];bs=docs['cal.artifact-type.bounded-context/v3-schema']
 ck('C28-admission-retains-body-and-residue-ceilings',source['current_registry_admission_ref']=='CAL-DECISION-0028-CRAFT-FOUNDATION-V1' and 'does not reclassify, replace, mutate, or admit any CTX08 artifact' in dr['claim_ceiling'] and dr['residue_refs']==['definition-owner-admission-required','representation-revision-artifact-type-not-yet-authored','CTX08-replacement-not-authorized'])
 ck('four-primary-consumer-directory-labels',dr['primary_consumer_refs']==['contexts/migrations','contexts/governance','contexts/ontology-lifecycle','tooling/validators'])
 consumer_labels=[]
 for label in dr['primary_consumer_refs']:
  directory=b.ROOT/label;files=sorted(x for x in directory.rglob('*') if x.is_file() and '__pycache__' not in x.parts and x.suffix!='.pyc');selected=[b.ref(x) for x in files]
  ck(label+'-bounded-current-directory-membership',directory.is_dir() and bool(files));consumer_labels.append({'label':label,'path_exists':True,'directory_membership_refs':selected,'accepted_map':False,'native_or_live_consumer_executed':False});refs.update({label+':'+str(i):x for i,x in enumerate(selected)})
 for contract,label in zip(comparison_contracts,['context-migration-manifest','bounded-context']):
  ck(label+'-C70-separate-own-meaning',contract['admission_decision_ref']=='CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION' and contract['semantic_definition_refs']==[b.source_ref(snap,'cal.definition.'+label)['version_ref']])
 mp=ms['$defs']['contextMigrationManifest']['allOf'][1];bp=bs['$defs']['boundedContext']['allOf'][1]
 ck('MigrationManifest-v2-closed24-required-none-no-execution',len(ms['$defs']['base']['required'])+len(mp['required'])==24 and ms['$defs']['contextMigrationManifest']['unevaluatedProperties'] is False and mp['properties']['immutable']=={'const':True} and mp['properties']['execution_authority']=={'const':False} and ms['$defs']['base']['properties']['authority_effect']=={'const':'none'})
 ck('BoundedContext-v3-closed16-required-retains-v2-type-label',len(bs['$defs']['base']['required'])+len(bp['required'])==16 and bs['$defs']['boundedContext']['unevaluatedProperties'] is False and bp['properties']['classification']['properties']['artifact_type_ref']=={'const':'cal.artifact-type.bounded-context/v2'})
 revision_fields=['representation_revision_id','semantic_epoch_ref','preimage_digest','postimage_digest','representation_delta_ref','equivalence_evidence_ref','validation_ref','owner_selection_ref','rollback_ref','no_semantic_successor_lineage']
 ck('comparison-contracts-have-no-full-RR-record-fields',not any(n in mp['properties'] or n in bp['properties'] for n in revision_fields))
 raw_paths={'migration':'contexts/migrations/governance-ontology-lifecycle-v1-to-v2/v1/migration.json','governance':'contexts/governance/v3/context.json','ontology':'contexts/ontology-lifecycle/v3/context.json','migration_validator':'tooling/validators/migration_contracts.py'}
 actual_observations=[]
 for label,path in raw_paths.items():
  q=b.ROOT/path;refs['selected-consumer-'+label]=b.ref(q)
  if q.suffix=='.json':
   doc=json.loads(q.read_bytes());chosen=ms if label=='migration' else bs;errors=sorted('/'+('/'.join(map(str,e.absolute_path)))+': '+e.message for e in b.c.Draft202012Validator(chosen).iter_errors(doc))
   ck(label+'-observed-local-version-not-current-comparison-schema',bool(errors) and doc['schema_version']!=chosen['$defs'][chosen['$ref'].split('/')[-1]]['allOf'][1]['properties']['schema_version']['const'])
   actual_observations.append({'label':label,'source_ref':refs['selected-consumer-'+label],'observed_schema_version':doc['schema_version'],'comparison_schema_accepted':not errors,'schema_errors':errors,'current_admission_or_RR_alignment_inferred':False})
  else:
   text=q.read_text();ck('migration-validator-read-only-scope-and-no-action-authority',"action_authorized" in text and 'Admission scope mismatch' in text and 'def resolve(' in text);actual_observations.append({'label':label,'source_ref':refs['selected-consumer-'+label],'inspection':'Scoped source read; no function or CLI execution','accepted_RR_consumer_map':False})
 probes=[]
 def probe(name,mutate,expected):
  doc=copy.deepcopy(dr);mutate(doc);before=copy.deepcopy(doc);errors=sorted('/'+('/'.join(map(str,e.absolute_path)))+': '+e.message for e in validator.iter_errors(doc));assert (not errors)==expected,(name,errors);one=gen['render'](doc).encode() if expected else None;two=gen['render'](doc).encode() if expected else None;assert one==two and before==doc;probes.append({'case_id':name,'schema_accepted':not errors,'expected_schema_acceptance':expected,'schema_errors':errors,'two_generated_projections_equal':True if expected else None,'fixture_digest':b.ir.digest(doc),'actual_semantic_obligations_enforced':False,'accepted_semantic_map':False})
 probe('exact-selected-RR-Definition',lambda x:None,True)
 for n in schema['required']:probe('missing-required-'+n,lambda x,n=n:x.pop(n),False)
 for n in ['definition_id','semantic_owner_ref','term']:probe('unresolved-label-'+n,lambda x,n=n:x.update({n:'hyp:unresolved'}),True)
 for n in revision_fields:probe('revision-instance-field-not-Definition-'+n,lambda x,n=n:x.update({n:'hyp:unaccepted-map'}),False)
 probe('empty-source-selection',lambda x:x.update(source_refs=[]),True);probe('empty-consumer-list',lambda x:x.update(primary_consumer_refs=[]),True)
 for name,text in [('labels-prove-equivalence','hyp:matching labels prove meaning preservation'),('revision-creates-semantic-successor','hyp:every encoding revision creates a semantic successor'),('validation-ref-proves-PASS','hyp:a validation reference proves execution PASS'),('rollback-ref-authorizes-effect','hyp:a rollback reference grants execution authority')]:probe(name,lambda x,text=text:x['voices']['scientific_formal'].update(normative_statement=text),True)
 mf=json.loads((b.ROOT/raw_paths['migration']).read_bytes());mf['schema_version']='cyberalchemy-lab-context-migration-manifest/v2'
 bf=json.loads((b.ROOT/raw_paths['governance']).read_bytes());bf['schema_version']='cyberalchemy-lab-bounded-context/v3'
 carrier_probes=[]
 def cp(label,name,chosen,fixture,mutate,expected):
  doc=copy.deepcopy(fixture);mutate(doc);errors=sorted('/'+('/'.join(map(str,e.absolute_path)))+': '+e.message for e in b.c.Draft202012Validator(chosen).iter_errors(doc));assert (not errors)==expected,(label,name,errors);carrier_probes.append({'carrier':label,'case_id':name,'whole_hypothetical_fixture_shape_validated':True,'schema_accepted':not errors,'schema_errors':errors,'fixture_digest':b.ir.digest(doc),'actual_revision_created':False,'actual_RR_semantics_enforced':False,'accepted_semantic_map':False})
 def m(name,mutate,expected):cp('ContextMigrationManifest/v2',name,ms,mf,mutate,expected)
 def c(name,mutate,expected):cp('BoundedContext/v3',name,bs,bf,mutate,expected)
 for label,chosen,fixture,fn,part in [('migration',ms,mf,m,mp),('bounded',bs,bf,c,bp)]:
  fn('adapted-version-whole-hypothetical-baseline',lambda x:None,True)
  for n in chosen['$defs']['base']['required']+part['required']:fn('missing-'+n,lambda x,n=n:x.pop(n),False)
  for n in revision_fields:fn('unsupported-RR-field-'+n,lambda x,n=n:x.update({n:'hyp:unaccepted-map'}),False)
  fn('effect-promotion',lambda x:x.update(authority_effect='promotion'),False);fn('asserted-admitted-status',lambda x:x.update(status='admitted'),False)
  fn('unresolved-owner',lambda x,label=label:x.update({('owner_ref' if label=='migration' else 'semantic_owner_ref'):'hyp:unresolved'}),True)
  fn('overclaim-text',lambda x:x.update(claim_ceiling='hyp:actual semantic equivalence, authenticated immutable history and rollback proven'),True)
 m('uncomputed-preimage-hash',lambda x:x['preimages'][0].update(sha256='0'*64),True)
 m('invalid-preimage-hash',lambda x:x['preimages'][0].update(sha256='invalid'),False)
 m('no-expected-postimage-digest-required',lambda x:x['expected_postimages'][0].update(expected_condition='hyp:any output'),True)
 m('changed-meaning-as-revise-disposition',lambda x:x['dispositions'][0].update(disposition='revise',destination_ref='hyp:changed-meaning'),True)
 m('opaque-validation-obligation',lambda x:x.update(validation_obligations=['hyp:no-run']),True)
 m('opaque-owner-gate',lambda x:x.update(owner_gates=[{'role_ref':'hyp:unresolved','effect':'hyp:unexecuted'}]),True)
 m('opaque-rollback-boundary',lambda x:x.update(rollback_boundary='hyp:no-executable-route'),True)
 m('immutable-false',lambda x:x.update(immutable=False),False);m('execution-authority-true',lambda x:x.update(execution_authority=True),False)
 c('same-label-changed-owned-model',lambda x:x.update(domain_model_ref='hyp:new-meaning'),True)
 c('same-label-changed-scope',lambda x:x['scope'].update(statement='hyp:new-scope'),True)
 c('changed-semantic-version',lambda x:x.update(version='3.0.0-candidate.1'),True)
 c('unresolved-contracts',lambda x:x.update(contract_refs=['hyp:unresolved']),True)
 c('map-backreference-forbidden',lambda x:x.update(context_map_refs=['hyp:map']),False)
 comparison=[];compiled=load('static-ir.json');controls=load('model-controls.json')['results']
 wanted=[('exact-representation-revisions',(True,True)),('no-selected-revisions',(True,False)),('only-first-revision-selected',(True,False)),('duplicate-declared-revision-identity-not-forced-injective',(True,True)),('independent-authority-not-supplied',(True,False)),('all-actual-outcomes-independently-supplied',(True,False)),('independently-supported-actual-MeaningEquivalence',(True,True)),('changed-meaning-with-same-label',(False,True)),('missing-posture-OwnerSelectionRecordedDeclared-selection0',(False,True))]
 for name,expected in wanted:
  row=next(x for x in controls if x['case_id']==name);model=copy.deepcopy(row['model']);e=v.Denotation(compiled['declarations'],model);tc=[{'clause_id':x['clause_id'],'truth':e.truth(x['formal_statement'])} for x in compiled['clauses'] if x['disposition']=='encoded'];pc=[{'population_id':x['population_id'],'truth':e.truth(x['statement'])} for x in compiled['populations'] if x['requirement']=='required'];T=all(x['truth'] for x in tc);I=all(x['truth'] for x in pc);assert (T,I)==expected and b.ir.digest(model)==row['model_sha256'],name;comparison.append({'case_id':name,'model':model,'model_sha256':b.ir.digest(model),'T':T,'I':I,'clause_results':tc,'population_results':pc,'accepted_RepresentationRevision_carrier_map':False,'whole_upstream_theories_imported':False})
 issues=[
 'C28 admits the positive Representation Revision Definition while the selected body retains carrier-not-authored and CTX08-no-replacement residues. No current registry contract directly binds this meaning; C70 Context Migration Manifest and Bounded Context each bind separate own meanings.',
 'Generic Definition shape and pure text projection accept unsupported label-equivalence, semantic-successor, validation-PASS and rollback-authority wording. Neither enforces the positive RR logical obligations.',
 'Context Migration Manifest requires preimages, expected conditions, validation obligations, owner gates, immutability and a rollback boundary. Its shape does not bind preserved epoch/identity/meaning, distinct exact postimage digests or authenticated equivalence and successful rollback.',
 'Bounded Context shape retains context identity, owner, model, language, scope and contract refs but accepts changed model/scope/version under the same ID. Embedded v2 Artifact Type label and v3 schema need explicit correspondence; neither becomes an RR record.',
 'The three selected local consumer documents use earlier schema-version labels than the current comparison contracts and are shape-rejected by those contracts. This scoped observation does not revoke an earlier admission or establish an authorized replacement. Migration validator is read only, not executed.',
 'Exact revision/support-record universes, digest content maps, semantic equivalence, typed history, four change dimensions, current consumer selection, owner routes and independent effect authorization remain unaccepted. Nine independently evaluated RR-only models do not import whole upstream theories or prove common meanings.'
 ]
 findings=[{'finding_id':'RR-CONSUMER-FINDING-'+str(i+1).zfill(3),'issue':x,'status':'unresolved','accepted_map_refs':[]} for i,x in enumerate(issues)]
 prior=load('../cal.definition.projection-specification/delivery-manifest.json');b.unchanged(prior['files']+typed['inputs']+list(refs.values()));b.external_current(context)
 report={'schema_version':'definition-assurance-RepresentationRevision-carrier-consumer-inspection/v1-candidate','result':'PASS-exact-RR-meaning-and-separate-migration-context-shapes','authority_effect':'none','source':context['source_selection'],'checks':checks,'check_count':len(checks),'selected_inputs':refs,'external_file_refs':source['external_file_refs'],'external_context_sections':source['external_source_observations'],'current_registry_contracts':len(registry['admitted_contracts']),'admitted_current_contracts':len(current),'direct_current_definition_binding_types':[],'direct_current_ValidationReceipt_binding_types':[x['artifact_type_ref'] for x in receipt_direct],'generic_current_Definition_ref':generic['artifact_type_ref'],'current_GeneratedOutput_type_ref':generated['artifact_type_ref'],'meaning_observations':observations,'consumer_label_observations':consumer_labels,'selected_actual_consumer_observations':actual_observations,'shape_probes':probes,'shape_probe_count':len(probes),'shape_acceptances':sum(x['schema_accepted'] for x in probes),'carrier_shape_probes':carrier_probes,'carrier_shape_probe_count':len(carrier_probes),'carrier_shape_acceptances':sum(x['schema_accepted'] for x in carrier_probes),'separately_bound_comparison_contracts':comparison_contracts,'typed_comparison_models':comparison,'typed_comparison_count':len(comparison),'accepted_semantic_map_refs':[],'unresolved_consumer_findings':findings,'isolated_pure_Definition_helpers_executed':True,'canonical_or_candidate_carrier_writer_executed':False,'native_or_live_consumer_executed':False,'real_revision_equivalence_rollback_or_authority_created':False,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_inventory_refresh_complete':False,'claim_ceiling':'Exact eight selected meanings, current catalog, four consumer directories and selected local schema/validator observations, hypothetical whole Definition/migration/context schema probes and nine fresh RR-only model evaluations. No actual revision, equivalence proof, rollback, accepted source/consumer map or authority.'}
 if write:b.put('carrier-consumer-inspection.json',report)
 elif not b.r.same_json(report,load('carrier-consumer-inspection.json')):raise ValueError('Fresh RR consumer observations differ')
 return report
if __name__=='__main__':
 x=inspect('--write' in b.sys.argv);print(json.dumps({k:x[k] for k in ['result','check_count','shape_probe_count','shape_acceptances','carrier_shape_probe_count','carrier_shape_acceptances','typed_comparison_count','current_registry_contracts','admitted_current_contracts','direct_current_definition_binding_types','semantic_ready']},indent=2))
