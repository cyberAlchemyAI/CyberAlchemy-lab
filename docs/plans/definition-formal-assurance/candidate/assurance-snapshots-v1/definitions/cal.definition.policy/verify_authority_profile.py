"""Qualified Policy hypotheses and actual direct Policy/v2 shape/role observations; no writer."""
import ast,copy,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
AXES=['identity','kind','carrier','owner_scope','sources','rule_set','version','issuer','governed_scope','rules','targets','exception_route','effective_period','relations']
FORBIDDEN=['issuer_label_proves_grant','scope_label_proves_containment','rule_ref_proves_truth','schema_proves_execution','record_proves_compliance','policy_replaces_decision','evidence_proves_adoption','relation_proves_authority','active_label_proves_activation','source_admission_proves_fidelity','nonentailment_means_all_effects_impossible']
def envelope():return {n:'hyp:'+n for n in AXES}
def profiles():
 rows=[];base=envelope();flags={n:False for n in FORBIDDEN}
 def add(id,after,f,expected):
  errors=['binding-changed:'+n for n in AXES if base[n]!=after[n]]+['forbidden-inference:'+n for n in FORBIDDEN if f[n]];assert bool(errors)==expected;rows.append({'case_id':id,'before':base,'after':after,'flags':f,'errors':errors,'expected_rejection':expected,'actual_runtime_execution':False,'actual_issuer_authority_issuance_compliance_verified':False,'source_fidelity_accepted':False})
 add('exact-qualified-policy-hypothesis',copy.deepcopy(base),copy.deepcopy(flags),False)
 add('declared-policy-with-independent-actual-outcome-obligations',copy.deepcopy(base),copy.deepcopy(flags),False)
 for n in AXES:
  after=copy.deepcopy(base);after[n]='hyp:changed';add('changed-'+n,after,copy.deepcopy(flags),True)
 for n in FORBIDDEN:
  f=copy.deepcopy(flags);f[n]=True;add('forbidden-'+n,copy.deepcopy(base),f,True)
 return rows
def frames():
 base={'before':envelope(),'after':envelope(),'version_bound':True,'issuer_declared':True,'scope_within_issuer_declared':True,'rule_within_policy_scope_declared':True,'target_within_policy_scope_declared':True,'rule_in_bound_set':True,'target_categories':['decision'],'constrains':True,'requires':False,'actual_outcome_claim':False,'denies_all_independently_authorized_effects':False};rows=[]
 def add(id,mutate,expected):
  x=copy.deepcopy(base);mutate(x);errors=[]
  if x['before']!=x['after']:errors.append('qualified-binding-change-needs-independent-review')
  for n in ['version_bound','issuer_declared','scope_within_issuer_declared','rule_within_policy_scope_declared','target_within_policy_scope_declared','rule_in_bound_set']:
   if not x[n]:errors.append('missing-'+n)
  if not x['target_categories'] or any(n not in ['decision','action','lifecycle-transition','evidence','handling'] for n in x['target_categories']):errors.append('target-category-needs-source-map')
  if not (x['constrains'] or x['requires']):errors.append('neither-constrain-nor-require')
  if x['actual_outcome_claim']:errors.append('declaration-not-actual-issuance-authority-compliance')
  if x['denies_all_independently_authorized_effects']:errors.append('nonentailment-is-not-universal-negative-effect')
  assert bool(errors)==expected;rows.append({'case_id':id,'frame':x,'errors':errors,'expected_rejection':expected,'actual_runtime_execution':False,'actual_issuer_authority_issuance_compliance_verified':False})
 add('constrain-without-require',lambda x:None,False)
 add('require-without-constrain',lambda x:x.update(constrains=False,requires=True),False)
 add('both-modalities-permitted',lambda x:x.update(requires=True),False)
 add('overlapping-target-categories-permitted',lambda x:x.update(target_categories=['decision','evidence']),False)
 add('declared-narrower-target-scope-without-grant-claim',lambda x:None,False)
 for n in ['rule_set','version','issuer','governed_scope','rules','targets','exception_route','effective_period','relations']:add('changed-'+n,lambda x,n=n:x['after'].update({n:'hyp:changed'}),True)
 for n in ['version_bound','issuer_declared','scope_within_issuer_declared','rule_within_policy_scope_declared','target_within_policy_scope_declared','rule_in_bound_set']:add('missing-'+n,lambda x,n=n:x.update({n:False}),True)
 add('target-without-category',lambda x:x.update(target_categories=[]),True)
 add('target-with-unmapped-category',lambda x:x.update(target_categories=['unmapped']),True)
 add('neither-modality',lambda x:x.update(constrains=False),True)
 add('declared-policy-as-actual-outcome',lambda x:x.update(actual_outcome_claim=True),True)
 add('nonentailment-as-universal-effect-denial',lambda x:x.update(denies_all_independently_authorized_effects=True),True)
 return rows
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();source=load('t.json')['payload']['source'];registry_path=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json';registry=json.loads(registry_path.read_bytes());rows=registry['admitted_contracts'];current=[x for x in rows if x['lifecycle_state']=='admitted-current'];direct=[x for x in current if source['version_ref'] in x['semantic_definition_refs']];assert len(direct)==1;carrier=direct[0];artifact_path=b.ROOT/carrier['artifact_path'];artifact=json.loads(artifact_path.read_bytes());paths={'registry':registry_path,'source':b.ROOT/source['path'],'Definition_schema':b.ROOT/'authority/artifact-types/definition/v1/schema.json','current_Definition_schema':b.ROOT/'authority/artifact-types/definition/v2/schema.json','direct_artifact':artifact_path,'direct_schema':b.ROOT/carrier['schema_path'],'direct_fixture':artifact_path.parent/artifact['validation_contract']['positive_witness'],'relation_model':b.ROOT/artifact['relation_model_binding']['path'],'role_observer_source':b.ROOT/artifact['validation_contract']['shared_validator_path'],'checker':b.UNIT/'verify_authority_profile.py'}
 for i,n in enumerate(artifact['validation_contract']['negative_witnesses']):paths['hostile_'+str(i)]=artifact_path.parent/n
 refs={k:b.ref(p) for k,p in paths.items()};docs={k:json.loads(p.read_bytes()) for k,p in paths.items() if p.suffix=='.json'};definition_schema=docs['Definition_schema'];schema=docs['direct_schema'];b.c.Draft202012Validator.check_schema(definition_schema);b.c.Draft202012Validator.check_schema(schema);dv=b.c.Draft202012Validator(definition_schema);pv=b.c.Draft202012Validator(schema);generic=[x for x in current if x['artifact_type_ref']=='cal.artifact-type.definition/v2'];checks=[]
 def ck(id,ok):checks.append({'check_id':id,'result':bool(ok)})
 ck('registry143rows121current',len(rows)==143 and len(current)==121)
 ck('direct-current-Policy-v2-C74A',carrier['artifact_type_ref']=='cal.artifact-type.policy/v2' and carrier['admission_decision_ref']=='CAL-DECISION-0074A-GOVERNANCE-CARRIER-ADMISSION')
 ck('direct-exact-current-Policy-meaning',carrier['semantic_definition_refs']==[source['version_ref']] and artifact['semantic_definition_refs']==[source['version_ref']])
 ck('direct-artifact-schema-bytes-current',refs['direct_artifact']['sha256']==carrier['artifact_sha256'] and refs['direct_schema']['sha256']==carrier['schema_sha256']==artifact['schema_digest'])
 ck('direct-retained-body-candidate-no-effect',artifact['status']=='candidate-unadmitted' and artifact['authority_effect']=='none')
 ck('direct-Definition-binding-current',artifact['semantic_definition_bindings'][0]['path']==source['path'] and artifact['semantic_definition_bindings'][0]['sha256']==source['sha256'] and artifact['semantic_definition_bindings'][0]['definition_ref']==source['version_ref'])
 ck('closed14root5payload-shape',schema['additionalProperties'] is False and len(schema['required'])==14 and schema['properties']['payload']['additionalProperties'] is False and len(schema['properties']['payload']['required'])==5)
 ck('direct-discriminator-exact',schema['properties']['schema_version']['const']==carrier['instance_discriminator']['value']=='cyberalchemy-lab-policy/v2')
 ck('current-generic-Definition-meaning',len(generic)==1 and generic[0]['semantic_definition_refs']==[b.source_ref(snap,'cal.definition.definition')['version_ref']])
 ck('historical-Definition-v1-retained',any(x['artifact_type_ref']=='cal.artifact-type.definition/v1' and x['lifecycle_state']=='admitted-historical' for x in rows))
 ck('selected-Definition-v1-shape-valid',not list(dv.iter_errors(docs['source'])))
 ck('historical-source-and-C65-overlay-separate',all(x['admission_posture']=='candidate-unadmitted' for x in docs['source']['source_refs']) and load('source-checks.json')['current_registry_admission_ref']=='CAL-DECISION-0065-INTEGRATED-LAB-DEFINITION-MODEL-ADMISSION')
 ck('relation-model-bytes-bound',refs['relation_model']['sha256']==artifact['relation_model_binding']['sha256'])
 ck('pure-role-observer-source-bound',refs['role_observer_source']['sha256']==artifact['validation_contract']['shared_validator_sha256'])
 nodes=[x for x in ast.parse(paths['role_observer_source'].read_bytes()).body if isinstance(x,ast.FunctionDef) and x.name=='roles_for'];assert len(nodes)==1;ns={};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(paths['role_observer_source']),'exec'),ns);expected_roles=ns['roles_for']('policy',docs['relation_model']);allowed={(x['relation_kind_ref'],x['direction'],k) for x in expected_roles for k in x['counterpart_kinds']}
 ck('pure-observed-role-surface-exact',artifact['relation_roles']==expected_roles and artifact['allowed_relation_kinds']==sorted({x['relation_kind_ref'] for x in expected_roles}))
 ck('four-carrier-orthogonality-rules',len(artifact['orthogonality_rules'])==4 and artifact['hostile_non_collapse']==['constitution','contract'])
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 definition_probes=[];policy_probes=[]
 def probe(bucket,id,doc,validator,expected):
  errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in validator.iter_errors(doc)];accepted=not errors
  if accepted!=expected:raise ValueError('Wrong authored shape probe '+id+' '+str(errors))
  item={'case_id':id,'schema_accepted':accepted,'errors':errors,'actual_issuer_authority_issuance_compliance_verified':False}
  if bucket is policy_probes:item['declared_roles_satisfied']=all((x.get('relation_kind_ref'),x.get('direction'),x.get('counterpart_kind')) in allowed for x in doc.get('relation_refs',[]))
  bucket.append(item)
 original=docs['source'];probe(definition_probes,'selected-exact-Definition-shape',copy.deepcopy(original),dv,True)
 for n in definition_schema['required']:
  d=copy.deepcopy(original);d.pop(n);probe(definition_probes,'missing-root-'+n,d,dv,False)
 for n in ['issuer_ref','rule_refs','exception_route','effective_period']:
  d=copy.deepcopy(original);d[n]='hyp:claimed';probe(definition_probes,'instance-field-not-in-Definition-'+n,d,dv,False)
 for n in ['definition_id','term','semantic_owner_ref']:
  d=copy.deepcopy(original);d[n]='hyp:unresolved';probe(definition_probes,'Definition-shape-does-not-resolve-'+n,d,dv,True)
 d=copy.deepcopy(original);d['voices']['scientific_formal']['normative_statement']='hyp:policy proves compliance and grants authority';probe(definition_probes,'Definition-shape-valid-overclaimed-text',d,dv,True)
 fixture=docs['direct_fixture'];probe(policy_probes,'exact-current-direct-fixture-shape',copy.deepcopy(fixture),pv,True)
 for n in schema['required']:
  d=copy.deepcopy(fixture);d.pop(n);probe(policy_probes,'missing-root-'+n,d,pv,False)
 for n in schema['properties']['payload']['required']:
  d=copy.deepcopy(fixture);d['payload'].pop(n);probe(policy_probes,'missing-payload-'+n,d,pv,False)
 for n in ['issuer_ref','governed_scope_ref','exception_route','effective_period']:
  d=copy.deepcopy(fixture);d['payload'][n]='hyp:unresolved';probe(policy_probes,'shape-does-not-resolve-'+n,d,pv,True)
 d=copy.deepcopy(fixture);d['payload']['rule_refs']=['hyp:unresolved-rule'];probe(policy_probes,'shape-does-not-resolve-rule',d,pv,True)
 d=copy.deepcopy(fixture);d['payload']['rule_refs']=[];probe(policy_probes,'empty-rule-refs-rejected',d,pv,False)
 for location in ['root','payload']:
  d=copy.deepcopy(fixture);(d if location=='root' else d['payload'])['implicit_grant']='hyp:authority';probe(policy_probes,'extra-'+location+'-field-rejected',d,pv,False)
 d=copy.deepcopy(fixture);d['authority_effect']='canonical';probe(policy_probes,'actual-authority-effect-rejected',d,pv,False)
 d=copy.deepcopy(fixture);d['schema_version']='cyberalchemy-lab-policy/v1';probe(policy_probes,'wrong-discriminator-rejected',d,pv,False)
 d=copy.deepcopy(fixture);d['kind']='constitution';probe(policy_probes,'neighbor-kind-rejected',d,pv,False)
 d=copy.deepcopy(fixture);d['lifecycle_state']='active';probe(policy_probes,'active-label-without-activation-proof',d,pv,True)
 d=copy.deepcopy(fixture);d['evidence_refs']=[];probe(policy_probes,'empty-evidence-does-not-prove-compliance',d,pv,True)
 d=copy.deepcopy(fixture);d['claim_ceiling']='hyp:issuer authority execution and compliance verified';probe(policy_probes,'shape-valid-overclaimed-text',d,pv,True)
 d=copy.deepcopy(fixture);d['payload']['effective_period']='   ';probe(policy_probes,'nonempty-whitespace-period-has-no-temporal-meaning',d,pv,True)
 d=copy.deepcopy(fixture);d['relation_refs']=[];probe(policy_probes,'empty-relations-rejected',d,pv,False)
 for id,kind,direction,counterpart in [('declared-successor-role','relation.successor-of','target','policy'),('schema-product-challenges-wrong-role','relation.challenges','source','admission-transaction'),('schema-product-violates-wrong-role','relation.violates','source','policy')]:
  d=copy.deepcopy(fixture);d['relation_refs'][0].update(relation_kind_ref=kind,direction=direction,counterpart_kind=counterpart);probe(policy_probes,id,d,pv,True)
 for i in range(5):probe(policy_probes,'retained-hostile-source-'+str(i),docs['hostile_'+str(i)],pv,False)
 assert sum(x['schema_accepted'] and not x['declared_roles_satisfied'] for x in policy_probes)==2
 current_errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in b.c.Draft202012Validator(docs['current_Definition_schema']).iter_errors(original)]
 inputs=[b.ref(b.UNIT/n) for n in ['t.json','source-checks.json','comparison-selection.json']];bindings=[b.ref(p) for p in [b.UNIT/'verify_authority_profile.py',b.IMPL/'contracts.py',b.IMPL/'ir.py',b.IMPL/'verifier.py']]
 report={'schema_version':'definition-assurance-Policy-profile/v1-candidate','status':'PASS-for-qualified-Policy-hypotheses-and-actual-direct-carrier-observations','authority_effect':'none','checker_bindings':bindings,'input_refs':inputs,'runtime_bindings':runtime,'selected_inputs':refs,'profiles':profiles(),'finite_policy_frames':frames(),'actual_checks':checks,'actual_check_count':len(checks),'current_type_registry_rows':len(rows),'admitted_current_type_rows':len(current),'direct_current_definition_binding_types':[x['artifact_type_ref'] for x in direct],'direct_Policy_admission_ref':carrier['admission_decision_ref'],'direct_Policy_semantic_ref':carrier['semantic_definition_refs'][0],'generic_Definition_current_type_ref':generic[0]['artifact_type_ref'],'generic_Definition_semantic_ref':generic[0]['semantic_definition_refs'][0],'Definition_schema_probes':definition_probes,'direct_Policy_schema_probes':policy_probes,'schema_accepted_but_role_invalid_cases':2,'pure_role_surface_observer_executed':True,'historical_source_current_Definition_shape':{'errors':current_errors,'exact_source_admission_invalidated':False},'bound_package_validator_executed':False,'generator_module_or_materialization_writer_executed':False,'native_or_live_consumer_executed':False,'actual_policy_authority_issuance_compliance_created':False,'direct_carrier_or_consumer_alignment_accepted':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Qualified declared Policy hypotheses and actual C74A direct Policy/v2/Definition shape observations. Two accepted enum-product relation shapes fail exact declared role membership. Pure AST-extracted role observer only;no package validator,writer,instance grant,issuer authentication,effective rules,execution,compliance,owner fidelity or consumer proof.'}
 b.unchanged(list(refs.values())+inputs+bindings+context['sources']);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh profile differs')
 return report
def main():
 r=verify('--write' in b.sys.argv);print(json.dumps({'status':r['status'],'profiles':len(r['profiles']),'rejected_profiles':sum(x['expected_rejection'] for x in r['profiles']),'frames':len(r['finite_policy_frames']),'rejected_frames':sum(x['expected_rejection'] for x in r['finite_policy_frames']),'catalog_checks':r['actual_check_count'],'Definition_probes':len(r['Definition_schema_probes']),'Definition_acceptances':sum(x['schema_accepted'] for x in r['Definition_schema_probes']),'Policy_probes':len(r['direct_Policy_schema_probes']),'Policy_acceptances':sum(x['schema_accepted'] for x in r['direct_Policy_schema_probes']),'schema_accepted_but_role_invalid_cases':r['schema_accepted_but_role_invalid_cases']},indent=2))
if __name__=='__main__':main()
