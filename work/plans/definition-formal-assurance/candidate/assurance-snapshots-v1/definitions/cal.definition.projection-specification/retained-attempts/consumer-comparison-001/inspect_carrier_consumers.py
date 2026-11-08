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
 audit=b.ROOT/'docs/plans/definition-formal-assurance/candidate/prepared-episodes-v1/20261011-projection-specification/typed-stage-audit-command-result.json';assert json.loads(audit.read_bytes())['exit_code']==0 and not audit.with_name('typed-stage-audit-stderr.txt').read_bytes()
 rp=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json';registry=json.loads(rp.read_bytes());current=[x for x in registry['admitted_contracts'] if x['lifecycle_state']=='admitted-current'];direct=[x for x in current if context['source_selection']['version_ref'] in x['semantic_definition_refs']];generic=next(x for x in current if x['artifact_type_ref']=='cal.artifact-type.definition/v2');generated=next(x for x in current if x['artifact_type_ref']=='cal.artifact-type.generated-output/v2');receipt_direct=[x for x in current if b.source_ref(snap,'cal.definition.validation-receipt')['version_ref'] in x['semantic_definition_refs']]
 comparison_contracts=[next(x for x in current if x['artifact_type_ref']==n) for n in ['cal.artifact-type.context-view/v1','cal.artifact-type.ontology-view/v1']]
 paths={'registry':rp,'source':b.ROOT/context['source_selection']['path'],'Definition_schema':b.ROOT/'authority/artifact-types/definition/v1/schema.json','Definition_generator':b.ROOT/'authority/artifact-types/definition/v1/generator.py','current_Definition_schema':b.ROOT/generic['schema_path'],'current_GeneratedOutput_schema':b.ROOT/generated['schema_path'],'current_GeneratedOutput_type_artifact':b.ROOT/generated['artifact_path'],'typed_receipt':b.UNIT/'types-logic-receipt.json','typed_separate_audit':audit,'checker':b.UNIT/'inspect_carrier_consumers.py','prior_CPRI_profile':b.BASE/'definitions/cal.definition.canonical-representation-invariant/authority-profile-checks.json','prior_ValidationReceipt_profile':b.BASE/'definitions/cal.definition.validation-receipt/authority-profile-checks.json'}
 selections=[b.source_ref(snap,'cal.definition.'+n) for n in ['projection-specification','context-view','ontology-view','source','provenance','generated-output','definition','authority']]
 for selected in selections:
  key=selected['definition_id'];q=b.ROOT/selected['path'];paths[key]=q;paths[key+'-projection']=q.with_name('DEFINITION.md')
 for contract in comparison_contracts:
  paths[contract['artifact_type_ref']+'-schema']=b.ROOT/contract['schema_path'];paths[contract['artifact_type_ref']+'-artifact']=b.ROOT/contract['artifact_path']
 refs={key:b.ref(q) for key,q in paths.items()};docs={key:json.loads(q.read_bytes()) for key,q in paths.items() if q.suffix=='.json'};checks=[]
 def ck(name,ok):
  assert ok,name;checks.append({'check_id':name,'result':True})
 ck('frozen16-stage-separate-audit0',typed['result']=='PASS-for-typed-candidate-stage-only' and len(typed['inputs'])==16 and typed['full_delivery_sealed'] is False)
 ck('catalog143rows121current',len(registry['admitted_contracts'])==143 and len(current)==121)
 ck('no-current-direct-ProjectionSpecification-definition-contract',direct==[])
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
 dr=docs['cal.definition.projection-specification'];source=load('source-checks.json');cv=docs['cal.artifact-type.context-view/v1-schema'];ov=docs['cal.artifact-type.ontology-view/v1-schema']
 ck('C53-overlay-and-D44-source-retained',source['current_registry_admission_ref']=='CAL-DECISION-0053-FULL-DEFINITION-QUEUE-ADMISSION' and source['external_source_observations'][0]['current_selection_sha256']=='b90efb80d4f8a497b49168a3db804626ecf52e3524141c98aa42725c9f52897c')
 ck('no-listed-primary-consumer-is-bounded-source-observation',dr['primary_consumer_refs']==[])
 consumer_labels=[]
 for contract,label in zip(comparison_contracts,['context-view','ontology-view']):
  ck(label+'-C70-own-meaning-binding',contract['admission_decision_ref']=='CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION' and contract['semantic_definition_refs']==[b.source_ref(snap,'cal.definition.'+label)['version_ref']])
 ck('ContextView-closed20fields-none-candidate',len(cv['required'])==20 and cv['additionalProperties'] is False and cv['properties']['authority_effect']=={'const':'none'} and cv['properties']['status']=={'const':'candidate-unadmitted'})
 ck('OntologyView-closed13root15payloadfields-none',len(ov['required'])==13 and len(ov['properties']['payload']['required'])==15 and ov['additionalProperties'] is False and ov['properties']['payload']['additionalProperties'] is False and ov['properties']['authority_effect']=={'const':'none'})
 view_fields=['allowed_readings','forbidden_authority_moves','distinct_evidence','lifecycle_posture_needed','reuse_surface','view_bearing','governed_view_needed','ordinary_narrative_unsafe']
 ck('view-contracts-have-no-D44-threshold-reading-move-fields',not any(n in cv['properties'] or n in ov['properties']['payload']['properties'] for n in view_fields))
 ck('ContextView-date-pattern-and-inclusion-no-uniqueness',cv['properties']['generated_at'].get('format') is None and cv['properties']['included_material'].get('uniqueItems') is None)
 ck('OntologyView-no-date-format-replay-false',ov['properties']['payload']['properties']['freshness_at']=={'minLength':1,'type':'string'} and ov['properties']['payload']['properties']['replay_source']=={'const':False})
 probes=[]
 def probe(name,mutate,expected):
  doc=copy.deepcopy(dr);mutate(doc);before=copy.deepcopy(doc);errors=sorted('/'+('/'.join(map(str,e.absolute_path)))+': '+e.message for e in validator.iter_errors(doc));accepted=not errors;assert accepted==expected,(name,errors);one=gen['render'](doc).encode() if accepted else None;two=gen['render'](doc).encode() if accepted else None;assert one==two and before==doc;probes.append({'case_id':name,'schema_accepted':accepted,'expected_schema_acceptance':expected,'schema_errors':errors,'two_generated_projections_equal':True if accepted else None,'fixture_digest':b.ir.digest(doc),'actual_semantic_obligations_enforced':False,'accepted_semantic_map':False})
 probe('exact-selected-Definition',lambda x:None,True)
 for field in schema['required']:probe('missing-required-'+field,lambda x,field=field:x.pop(field),False)
 for field in ['definition_id','semantic_owner_ref','term']:probe('unresolved-nonempty-'+field,lambda x,field=field:x.update({field:'hyp:unresolved'}),True)
 for field in view_fields+['evidence_ref','lifecycle_ref']:probe('view-instance-field-not-Definition-'+field,lambda x,field=field:x.update({field:'hyp:unaccepted-map'}),False)
 probe('empty-source-selection-shape-valid',lambda x:x.update(source_refs=[]),True);probe('empty-consumer-list-shape-valid',lambda x:x.update(primary_consumer_refs=[]),True)
 for name,text in [('every-term-view','hyp:every term requires a new tree'),('all-six-preservation-roles','hyp:every view must preserve all six roles'),('view-grants-authority','hyp:view fields grant instance authority'),('missing-fields-complete','hyp:missing allowed readings means complete view')]:probe(name,lambda x,text=text:x['voices']['scientific_formal'].update(normative_statement=text),True)
 cf={n:'hyp:'+n for n in cv['required']};cf.update(authority_effect='none',kind='context-view',status='candidate-unadmitted',generated_at='2026-10-11T10:00:00Z',expires_at='2026-10-12T10:00:00Z',included_material=[{'source_ref':'hyp:source','selector':'hyp:selector','sha256':'0'*64}],excluded_material=[],lineage_refs=['hyp:lineage'],limitations=['Hypothetical probe only'])
 of={n:'hyp:'+n for n in ov['required']};of.update(schema_version='cyberalchemy-lab-ontology-view/v1',kind='ontology-view',record_state='candidate',authority_effect='none',evidence_refs=[],successor_refs=[],payload={n:'hyp:'+n for n in ov['properties']['payload']['required']});of['payload'].update(cut_digest='0'*64,selected_node_refs=['hyp:node'],selected_edge_refs=[],exclusions=[],freshness_at='2026-10-11T10:00:00Z',expires_at='2026-10-12T10:00:00Z',source_event_set_digest='1'*64,semantic_cursor=1,replay_source=False)
 view_probes=[]
 def vp(label,name,schema,fixture,mutate,expected):
  doc=copy.deepcopy(fixture);mutate(doc);errors=sorted('/'+('/'.join(map(str,e.absolute_path)))+': '+e.message for e in b.c.Draft202012Validator(schema).iter_errors(doc));assert (not errors)==expected,(label,name,errors);view_probes.append({'carrier':label,'case_id':name,'whole_hypothetical_fixture_shape_validated':True,'schema_accepted':not errors,'schema_errors':errors,'fixture_digest':b.ir.digest(doc),'actual_view_created':False,'actual_D44_conditions_enforced':False,'accepted_semantic_map':False})
 def cp(name,mutate,expected):vp('ContextView/v1',name,cv,cf,mutate,expected)
 def op(name,mutate,expected):vp('OntologyView/v1',name,ov,of,mutate,expected)
 cp('baseline-opaque-refs-and-uncomputed-hash',lambda x:None,True)
 for n in cv['required']:cp('missing-root-'+n,lambda x,n=n:x.pop(n),False)
 for n in view_fields:cp('extra-D44-field-'+n,lambda x,n=n:x.update({n:'hyp:unaccepted-map'}),False)
 cp('promotion-effect',lambda x:x.update(authority_effect='promotion'),False);cp('asserted-admitted-status',lambda x:x.update(status='admitted'),False)
 cp('unresolved-owner',lambda x:x.update(owner_ref='hyp:unresolved'),True);cp('other-uncomputed-hash',lambda x:x['included_material'][0].update(sha256='1'*64),True)
 cp('overclaim-text',lambda x:x.update(claim_ceiling='hyp:actual evidence independence and authority proven'),True)
 cp('impossible-calendar-date',lambda x:x.update(generated_at='2026-99-99T99:99:99Z'),True);cp('expiry-before-generation',lambda x:x.update(expires_at='2025-10-11T10:00:00Z'),True)
 cp('duplicate-included-material',lambda x:x['included_material'].append(copy.deepcopy(x['included_material'][0])),True);cp('empty-exclusions',lambda x:x.update(excluded_material=[]),True)
 cp('empty-inclusions',lambda x:x.update(included_material=[]),False);cp('invalid-inclusion-hash',lambda x:x['included_material'][0].update(sha256='invalid'),False)
 op('baseline-opaque-refs-and-uncomputed-hashes',lambda x:None,True)
 for n in ov['required']:op('missing-root-'+n,lambda x,n=n:x.pop(n),False)
 for n in ov['properties']['payload']['required']:op('missing-payload-'+n,lambda x,n=n:x['payload'].pop(n),False)
 for n in view_fields:op('extra-D44-payload-'+n,lambda x,n=n:x['payload'].update({n:'hyp:unaccepted-map'}),False)
 op('unresolved-owner',lambda x:x.update(owner_ref='hyp:unresolved'),True);op('uncomputed-cut-hash',lambda x:x['payload'].update(cut_digest='2'*64),True)
 op('non-date-freshness',lambda x:x['payload'].update(freshness_at='not-a-date',expires_at='not-an-expiry'),True);op('expiry-before-freshness',lambda x:x['payload'].update(expires_at='2025-10-11T10:00:00Z'),True)
 op('asserted-admitted-record',lambda x:x.update(record_state='admitted'),True);op('empty-selection-and-evidence',lambda x:x['payload'].update(selected_node_refs=[],selected_edge_refs=[]),True)
 op('overclaim-text',lambda x:x.update(claim_ceiling='hyp:authentic complete governed view and instance authority proven'),True)
 op('replay-source-true',lambda x:x['payload'].update(replay_source=True),False);op('semantic-cursor-zero',lambda x:x['payload'].update(semantic_cursor=0),False);op('promotion-effect',lambda x:x.update(authority_effect='promotion'),False);op('invalid-cut-hash',lambda x:x['payload'].update(cut_digest='invalid'),False)
 comparison=[];core=load('t.json')['payload'];compiled=load('static-ir.json');ids={x['symbol_id']:b.ir.qualified(core['source'],core['scope'],x['symbol_id']) for x in core['declarations']}
 def compare(name,mutate,expected):
  m=a.base_model();mutate(m);model=a.qualify(m,ids);e=v.Denotation(compiled['declarations'],model);tc=[{'clause_id':x['clause_id'],'truth':e.truth(x['formal_statement'])} for x in compiled['clauses'] if x['disposition']=='encoded'];pc=[{'population_id':x['population_id'],'truth':e.truth(x['statement'])} for x in compiled['populations'] if x['requirement']=='required'];T=all(x['truth'] for x in tc);I=all(x['truth'] for x in pc);assert (T,I)==expected,(name,T,I);comparison.append({'case_id':name,'model':model,'model_sha256':b.ir.digest(model),'T':T,'I':I,'clause_results':tc,'population_results':pc,'accepted_ProjectionSpecification_carrier_map':False,'whole_upstream_theories_imported':False})
 compare('view-bearing-and-ordinary-concepts',lambda m:None,(True,True))
 compare('explicit-empty-allowed-reading-members',lambda m:m['predicates'].update(AllowedReadingMemberDeclared=[]),(True,False))
 compare('explicit-empty-forbidden-move-members',lambda m:m['predicates'].update(ForbiddenMoveMemberDeclared=[]),(True,False))
 def one_role(m):
  for n in b.PRESERVES:m['predicates']['ViewHelpsPreserve'+n+'Declared']=[['v0'],['v1'],['vExtra']] if n=='Evidence' else []
 compare('one-preservation-role-suffices',one_role,(True,False))
 compare('missing-explicit-nominated-readings',lambda m:m['predicates']['AllowedReadingsExplicitDeclared'].remove(['v0']),(False,False))
 issues=[
 'C53 D44 View-Bearing Concept source meaning and normalized Projection Specification label require an accepted role map. There is no direct current registry Definition binding; C70 ContextView and OntologyView each bind their own separate Definition.',
 'Definition shape and pure text projection accept unsupported every-term-tree, all-six-preservation, view-authority and missing-field-completeness wording; they do not enforce D44 conditions.',
 'ContextView shape lacks D44 allowed readings, forbidden authority moves and five-condition semantics. Uncomputed hashes, opaque owners, impossible dates, reversed expiry, repeated included material and overclaim text remain shape-valid.',
 'OntologyView shape lacks D44 threshold and reading/move sets. Uncomputed cut/event hashes, non-date freshness, reversed expiry, empty selections and asserted admitted record state do not establish preservation, authentic replay or authority.',
 'PS-only comparison models distinguish explicitly empty sets from absent declarations and six-role inclusive disjunction from all-six requirements. Declaration satisfaction is not actual helpfulness, inspectability or preservation.',
 'Concept/view universes, external source authenticity, owner routes, sibling field maps, exact consumer selection and shared consistency remain unaccepted. No view/tree writer, consumer effect or whole upstream theory is executed or imported.'
 ]
 findings=[{'finding_id':'PS-CONSUMER-FINDING-'+str(i+1).zfill(3),'issue':x,'status':'unresolved','accepted_map_refs':[]} for i,x in enumerate(issues)]
 prior=load('../cal.definition.generated-output/delivery-manifest.json');b.unchanged(prior['files']+typed['inputs']+list(refs.values()));b.external_current(context)
 report={'schema_version':'definition-assurance-ProjectionSpecification-carrier-consumer-inspection/v1-candidate','result':'PASS-exact-D44-meaning-and-separately-bound-view-shapes','authority_effect':'none','source':context['source_selection'],'checks':checks,'check_count':len(checks),'selected_inputs':refs,'external_file_refs':source['external_file_refs'],'external_context_sections':source['external_source_observations'],'current_registry_contracts':len(registry['admitted_contracts']),'admitted_current_contracts':len(current),'direct_current_definition_binding_types':[],'direct_current_ValidationReceipt_binding_types':[x['artifact_type_ref'] for x in receipt_direct],'generic_current_Definition_ref':generic['artifact_type_ref'],'current_GeneratedOutput_type_ref':generated['artifact_type_ref'],'meaning_observations':observations,'consumer_label_observations':consumer_labels,'shape_probes':probes,'shape_probe_count':len(probes),'shape_acceptances':sum(x['schema_accepted'] for x in probes),'view_shape_probes':view_probes,'view_shape_probe_count':len(view_probes),'view_shape_acceptances':sum(x['schema_accepted'] for x in view_probes),'separately_bound_comparison_contracts':comparison_contracts,'typed_comparison_models':comparison,'typed_comparison_count':len(comparison),'accepted_semantic_map_refs':[],'unresolved_consumer_findings':findings,'isolated_pure_Definition_helpers_executed':True,'canonical_or_candidate_carrier_writer_executed':False,'native_or_live_consumer_executed':False,'real_view_helpfulness_preservation_or_authority_created':False,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_inventory_refresh_complete':False,'claim_ceiling':'Exact eight selected meanings, current catalog and hypothetical Definition/ContextView/OntologyView shape probes; pure text projections and five supplied PS-only models. No real governed view, actual preservation, accepted source role/consumer map, source fidelity or whole proof.'}
 if write:b.put('carrier-consumer-inspection.json',report)
 elif not b.r.same_json(report,load('carrier-consumer-inspection.json')):raise ValueError('Fresh PS consumer observations differ')
 return report
if __name__=='__main__':
 x=inspect('--write' in b.sys.argv);print(json.dumps({key:x[key] for key in ['result','check_count','shape_probe_count','shape_acceptances','view_shape_probe_count','view_shape_acceptances','typed_comparison_count','current_registry_contracts','admitted_current_contracts','direct_current_definition_binding_types','semantic_ready']},indent=2))
