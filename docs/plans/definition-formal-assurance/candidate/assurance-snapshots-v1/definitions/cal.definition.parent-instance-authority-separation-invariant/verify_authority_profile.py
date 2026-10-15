"""Qualified Parent-Instance lifecycle/record hypotheses and actual catalog/prototype/Definition-shape observations."""
import copy,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
AXES=['identity','kind','carrier','owner_scope','sources','parent','instance','snapshot','claims','contract','extension_scope','project','registration','routes']
FORBIDDEN=['folder_proves_authority','name_proves_identity','repository_permission_proves_authority','project_membership_proves_authority','decision_token_proves_adoption','evidence_token_proves_conformance','route_proves_owner_acknowledgment','stop_token_proves_termination','inheritance_proves_canonicality','source_local_means_authenticated','path_proves_completed_absorption']
def envelope():return {n:'hyp:'+n for n in AXES}
def qualify(before,after,flags):return ['binding-changed:'+n for n in AXES if before[n]!=after[n]]+['forbidden-inference:'+n for n in FORBIDDEN if flags[n]]
def profiles():
 rows=[];base=envelope();flags={n:False for n in FORBIDDEN}
 def add(id,after,f,expected):
  errors=qualify(base,after,f);assert bool(errors)==expected;rows.append({'case_id':id,'before':base,'after':after,'flags':f,'errors':errors,'expected_rejection':expected,'actual_runtime_execution':False,'actual_binding_authority_conformance_or_transition_verified':False,'source_fidelity_accepted':False})
 add('exact-qualified-hypothesis',copy.deepcopy(base),copy.deepcopy(flags),False);add('declared-binding-with-independent-no-actual-authority-or-transition-claim',copy.deepcopy(base),copy.deepcopy(flags),False)
 for n in AXES:a=copy.deepcopy(base);a[n]='hyp:changed';add('changed-'+n,a,copy.deepcopy(flags),True)
 for n in FORBIDDEN:f=copy.deepcopy(flags);f[n]=True;add('forbidden-'+n,copy.deepcopy(base),f,True)
 return rows
def frames():
 base={'before':envelope(),'after':envelope(),'exact_snapshot':True,'snapshot_mode':'version','parent_claim_subject_matches':True,'instance_claim_subject_matches':True,'distinct_claims':True,'same_principal':True,'inherited_contract_matches_snapshot':True,'inherited_behavior_allowed':True,'specialization_scope_permits':True,'registration_fields_bound':True,'change_kind':'shared','parent_route_matches':True,'instance_route_matches':True,'applicable_path_declared':True,'actual_outcome_claim':False,'stop_as_termination_proof':False};rows=[]
 def add(id,mutate,expected):
  x=copy.deepcopy(base);mutate(x);errors=[]
  if x['before']!=x['after']:errors.append('qualified-binding-change-needs-independent-review')
  for n in ['exact_snapshot','parent_claim_subject_matches','instance_claim_subject_matches','distinct_claims','inherited_contract_matches_snapshot','inherited_behavior_allowed','specialization_scope_permits','registration_fields_bound']:
   if not x[n]:errors.append('missing-'+n)
  if x['snapshot_mode'] not in ['version','state']:errors.append('not-exact-version-or-state')
  if x['change_kind']=='shared' and not x['parent_route_matches']:errors.append('shared-change-needs-parent-route')
  if x['change_kind'] in ['local','absorb'] and not x['instance_route_matches']:errors.append('local-or-absorb-needs-instance-route')
  if x['change_kind']=='absorb' and not x['applicable_path_declared']:errors.append('absorb-needs-applicable-promotion-or-adoption-path')
  if x['actual_outcome_claim']:errors.append('declarations-not-actual-authority-conformance-or-execution')
  if x['stop_as_termination_proof']:errors.append('stop-token-not-well-foundedness-or-termination')
  assert bool(errors)==expected;rows.append({'case_id':id,'frame':x,'errors':errors,'expected_rejection':expected,'actual_runtime_execution':False,'universal_frame_record_authority_or_independence_proof':False})
 add('exact-version-shared-principal-distinct-claims',lambda x:None,False)
 add('exact-state-binding',lambda x:x.update(snapshot_mode='state'),False)
 add('separate-principals-permitted',lambda x:x.update(same_principal=False),False)
 add('local-change-instance-route',lambda x:x.update(change_kind='local',parent_route_matches=False),False)
 add('absorption-qualified-path-without-completion-claim',lambda x:x.update(change_kind='absorb',parent_route_matches=False),False)
 add('shared-change-does-not-require-instance-route',lambda x:x.update(instance_route_matches=False),False)
 for n in ['parent','instance','snapshot','claims','contract','extension_scope','project','registration','routes']:add('changed-'+n,lambda x,n=n:x['after'].update({n:'hyp:changed'}),True)
 for n in ['exact_snapshot','parent_claim_subject_matches','instance_claim_subject_matches','distinct_claims','inherited_contract_matches_snapshot','inherited_behavior_allowed','specialization_scope_permits','registration_fields_bound']:add('missing-'+n,lambda x,n=n:x.update({n:False}),True)
 add('latest-label-not-exact-mode',lambda x:x.update(snapshot_mode='latest'),True)
 add('shared-wrong-parent-route',lambda x:x.update(parent_route_matches=False),True)
 add('local-wrong-instance-route',lambda x:x.update(change_kind='local',instance_route_matches=False),True)
 add('absorb-wrong-instance-route',lambda x:x.update(change_kind='absorb',instance_route_matches=False),True)
 add('absorb-missing-applicable-path',lambda x:x.update(change_kind='absorb',applicable_path_declared=False),True)
 add('declaration-as-actual-outcome',lambda x:x.update(actual_outcome_claim=True),True)
 add('registered-stop-as-termination-proof',lambda x:x.update(stop_as_termination_proof=True),True)
 return rows
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();source=load('t.json')['payload']['source'];paths={'registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json','prototype':b.ROOT/'evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/semantic/semantic-parent-instance-authority-separation-invariant/v1/artifact.json','Definition_schema':b.ROOT/'authority/artifact-types/definition/v1/schema.json','current_Definition_schema':b.ROOT/'authority/artifact-types/definition/v2/schema.json','source':b.ROOT/source['path'],'binding_artifact':b.ROOT/'authority/artifact-types/model-instance-binding/v1/artifact.json','binding_schema':b.ROOT/'authority/artifact-types/model-instance-binding/v1/schema.json','binding_fixture':b.ROOT/'authority/artifact-types/model-instance-binding/v1/fixtures/valid/record.json','checker':b.UNIT/'verify_authority_profile.py'};refs={k:b.ref(p) for k,p in paths.items()};docs={k:json.loads(p.read_bytes()) for k,p in paths.items() if p.suffix=='.json'};rows=docs['registry']['admitted_contracts'];current=[x for x in rows if x['lifecycle_state']=='admitted-current'];direct=[x for x in current if source['version_ref'] in x['semantic_definition_refs']];generic=[x for x in current if x['artifact_type_ref']=='cal.artifact-type.definition/v2'];proto=docs['prototype'];schema=docs['Definition_schema'];b.c.Draft202012Validator.check_schema(schema);validator=b.c.Draft202012Validator(schema);current_validator=b.c.Draft202012Validator(docs['current_Definition_schema']);checks=[]
 def ck(id,ok):checks.append({'check_id':id,'result':bool(ok)})
 ck('registry143rows121current',len(rows)==143 and len(current)==121)
 ck('no-admitted-direct-Parent-Instance-invariant-type',not direct)
 ck('no-current-generic-invariant-carrier',not any(x['semantic_kind']=='invariant' for x in current))
 ck('current-generic-Definition-v2',len(generic)==1 and generic[0]['admission_decision_ref']=='CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION')
 ck('generic-Definition-binds-current-Definition-meaning',generic[0]['semantic_definition_refs']==[b.source_ref(snap,'cal.definition.definition')['version_ref']])
 ck('historical-generic-Definition-v1-retained',any(x['artifact_type_ref']=='cal.artifact-type.definition/v1' and x['lifecycle_state']=='admitted-historical' for x in rows))
 ck('prototype-remains-prototype-scaffold',proto['status']=='prototype-scaffold')
 ck('prototype-authority-effect-none',proto['authority_effect']=='none')
 ck('prototype-exact-normalized-identity',proto['normalized_contract']['concept_id']==proto['target_id']=='semantic.parent-instance-authority-separation-invariant')
 ck('prototype-independent-kind-carrier-owner-axes',proto['normalized_contract']['semantic_kind']=='invariant' and proto['normalized_contract']['carrier_ref']=='type.invariant' and proto['normalized_contract']['owner_scope']=='scope.shared-authority')
 ck('prototype-no-admitted-lifecycle-transition-schema',proto['four_facets']['schema']['admitted_schema_ref'] is None and proto['four_facets']['schema']['schema_state']=='definition-voice-shape-prototyped')
 observed=load('source-checks.json')['selected_source_sections']
 for label,sr,section in zip(['D64'],proto['source_refs'],observed):
  ck('prototype-'+label+'-selector-and-digest',sr['selector']==section['source_ref']['selector'] and sr['section_sha256']==section['sha256'])
 ck('prototype-D64-split-disposition',[(x['legacy_id'],x['decision']) for x in proto['accepted_source_decisions']]==[('CAV2-D64','split')])
 ck('prototype-normalization-owner-decision-not-governance-execution',proto['owner_decision_ref']=='CAL-DECISION-0012-NORMALIZE-01-DEFAULTS' and proto['normalization_ref']=='CAL-NORMALIZE-01')
 ck('family-specific-admitted-type-gap-preserved',any('family-specific admitted Artifact Type' in x for x in proto['gaps']))
 ck('selected-Definition-v1-shape-valid',not list(validator.iter_errors(docs['source'])) and docs['source']['classification']['artifact_type_ref']=='cal.artifact-type.definition/v1')
 ck('historical-body-and-C53-overlay-separate',all(x['admission_posture']=='candidate-unadmitted' for x in docs['source']['source_refs']) and load('source-checks.json')['current_registry_entry_lifecycle']=='admitted')
 neighbor=[x for x in current if x['artifact_type_ref']=='cal.artifact-type.model-instance-binding/v1'];artifact=docs['binding_artifact'];binding_schema=docs['binding_schema'];b.c.Draft202012Validator.check_schema(binding_schema);binding_validator=b.c.Draft202012Validator(binding_schema)
 ck('neighboring-ModelInstanceBinding-current-C70',len(neighbor)==1 and neighbor[0]['admission_decision_ref']=='CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION')
 ck('neighboring-binding-exact-artifact-and-schema',neighbor[0]['artifact_path']==refs['binding_artifact']['path'] and neighbor[0]['artifact_sha256']==refs['binding_artifact']['sha256'] and neighbor[0]['schema_path']==refs['binding_schema']['path'] and neighbor[0]['schema_sha256']==refs['binding_schema']['sha256'])
 ck('neighboring-binding-has-separate-current-meaning',neighbor[0]['semantic_definition_refs']==[b.source_ref(snap,'cal.definition.model-instance-binding')['version_ref']] and source['version_ref'] not in neighbor[0]['semantic_definition_refs'])
 ck('neighboring-binding-retained-candidate-body-independent-of-current-overlay',artifact['status']=='candidate-unadmitted' and artifact['authority_effect']=='none')
 ck('neighboring-binding-closed-22-root-shape',binding_schema['additionalProperties'] is False and len(binding_schema['required'])==22)
 ck('neighboring-binding-valid-source-fixture-shape',not list(binding_validator.iter_errors(docs['binding_fixture'])))
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 probes=[]
 def probe(id,doc,expected):
  errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in validator.iter_errors(doc)];accepted=not errors
  if accepted!=expected:raise ValueError('Wrong authored Definition-shape probe '+id+' '+str(errors))
  probes.append({'case_id':id,'schema_accepted':accepted,'errors':errors,'actual_binding_authority_conformance_or_transition_verified':False,'scope':'Definition/v1 shape only;no executable lifecycle or transition carrier'})
 original=docs['source'];probe('selected-exact-Definition-shape',copy.deepcopy(original),True)
 for n in schema['required']:
  d=copy.deepcopy(original);d.pop(n);probe('missing-required-root-'+n,d,False)
 for n in ['parent_model_ref','instance_ref','recursive_stop','parent_owner_route']:
  d=copy.deepcopy(original);d[n]='hyp:claimed';probe('binding-field-not-in-Definition-schema-'+n,d,False)
 for n in ['definition_id','term','semantic_owner_ref']:
  d=copy.deepcopy(original);d[n]='hyp:unresolved';probe('shape-does-not-resolve-'+n,d,True)
 d=copy.deepcopy(original);d['voices']['scientific_formal']['normative_statement']='hyp:parent binding grants canonical authority';probe('shape-valid-overclaimed-normative-text',d,True)
 errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in current_validator.iter_errors(original)]
 binding_probes=[]
 def binding_probe(id,doc,expected):
  errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in binding_validator.iter_errors(doc)];accepted=not errors
  if accepted!=expected:raise ValueError('Wrong neighboring binding shape probe '+id+' '+str(errors))
  binding_probes.append({'case_id':id,'schema_accepted':accepted,'errors':errors,'actual_binding_authority_conformance_or_transition_verified':False,'scope':'ModelInstanceBinding/v1 neighboring shape only;no source-fidelity or live-consumer acceptance'})
 fixture=docs['binding_fixture'];binding_probe('exact-neighbor-source-fixture-shape',copy.deepcopy(fixture),True)
 for n in binding_schema['required']:
  d=copy.deepcopy(fixture);d.pop(n);binding_probe('missing-required-root-'+n,d,False)
 for n in ['parent_model_ref','parent_model_version_ref','instance_ref','parent_owner_route','instance_owner_route']:
  d=copy.deepcopy(fixture);d[n]='hyp:unresolved';binding_probe('shape-does-not-resolve-'+n,d,True)
 d=copy.deepcopy(fixture);d.update(binding_state='active');binding_probe('active-state-label-without-activation-proof',d,True)
 d=copy.deepcopy(fixture);d['instance_owner_route']=d['parent_owner_route'];d['instance_authority_scope']=d['parent_authority_scope'];binding_probe('equal-route-and-scope-labels-not-semantic-collapse-proof',d,True)
 d=copy.deepcopy(fixture);d['inherited_contract_refs']=[];binding_probe('empty-inherited-contract-rejected',d,False)
 d=copy.deepcopy(fixture);d['conformance_refs']=[];binding_probe('empty-conformance-refs-do-not-prove-conformance',d,True)
 d=copy.deepcopy(fixture);d['claim_ceiling']='hyp:adoption authority and termination verified';binding_probe('shape-valid-overclaimed-outcome-text',d,True)
 d=copy.deepcopy(fixture);d['authority_effect']='canonical';binding_probe('claimed-authority-effect-rejected',d,False)
 d=copy.deepcopy(fixture);d['recursive_stop']='hyp:stop';binding_probe('extra-recursive-stop-field-rejected',d,False)
 inputs=[b.ref(b.UNIT/n) for n in ['t.json','source-checks.json','comparison-selection.json']];bindings=[b.ref(p) for p in [b.UNIT/'verify_authority_profile.py',b.IMPL/'contracts.py',b.IMPL/'ir.py',b.IMPL/'verifier.py']];report={'schema_version':'definition-assurance-PIAS-profile/v1-candidate','status':'PASS-for-qualified-governance-hypotheses-and-actual-catalog-prototype-observations','authority_effect':'none','checker_bindings':bindings,'input_refs':inputs,'runtime_bindings':runtime,'selected_inputs':refs,'profiles':profiles(),'finite_governance_frames':frames(),'actual_checks':checks,'actual_check_count':len(checks),'current_type_registry_rows':len(rows),'admitted_current_type_rows':len(current),'direct_current_definition_binding_types':[x['artifact_type_ref'] for x in direct],'generic_Definition_current_type_ref':generic[0]['artifact_type_ref'],'generic_Definition_semantic_ref':generic[0]['semantic_definition_refs'][0],'prototype_status':proto['status'],'prototype_authority_effect':proto['authority_effect'],'admitted_lifecycle_transition_schema_ref':None,'schema_probe_surface':'selected Definition/v1 shape;generic Definition/v2 is not an executable lifecycle or transition adapter','schema_probes':probes,'neighboring_binding_type_ref':neighbor[0]['artifact_type_ref'],'neighboring_binding_semantic_ref':neighbor[0]['semantic_definition_refs'][0],'neighboring_binding_schema_probes':binding_probes,'neighboring_binding_consumer_alignment_accepted':False,'historical_source_current_definition_shape':{'errors':errors,'exact_source_admission_invalidated':False,'semantic_epoch_mismatch_claimed':False},'bound_package_validator_executed':False,'generator_module_or_materialization_writer_executed':False,'native_or_live_consumer_executed':False,'actual_governance_record_authority_or_transition_created':False,'generic_carrier_or_consumer_alignment_accepted':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Qualified authored parent/instance binding hypotheses plus actual registry,prototype,D64 and Definition/neighboring ModelInstanceBinding shape observations. ModelInstanceBinding/v1 is admitted-current for its separate meaning;its retained body is candidate-unadmitted. No direct invariant carrier,accepted cross-definition adapter,actual grants,conformance,adoption,recomposition,termination,execution or owner fidelity.'}
 b.unchanged(list(refs.values())+inputs+bindings+context['sources']);b.external_current(context);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh profile observations differ')
 return report
def main():
 r=verify('--write' in b.sys.argv);print(json.dumps({'status':r['status'],'profiles':len(r['profiles']),'rejected_profiles':sum(x['expected_rejection'] for x in r['profiles']),'frames':len(r['finite_governance_frames']),'rejected_frames':sum(x['expected_rejection'] for x in r['finite_governance_frames']),'catalog_checks':r['actual_check_count'],'neighbor_binding_probes':len(r['neighboring_binding_schema_probes']),'neighbor_binding_acceptances':sum(x['schema_accepted'] for x in r['neighboring_binding_schema_probes']),'Definition_schema_probes':len(r['schema_probes']),'schema_acceptances':sum(x['schema_accepted'] for x in r['schema_probes']),'direct_current_definition_binding_types':r['direct_current_definition_binding_types']},indent=2))
if __name__=='__main__':main()
