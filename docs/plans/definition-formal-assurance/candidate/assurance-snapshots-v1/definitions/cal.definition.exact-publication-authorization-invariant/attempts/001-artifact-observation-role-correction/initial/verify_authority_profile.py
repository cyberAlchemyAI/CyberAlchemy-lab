"""Qualified publication hypotheses plus actual absence-of-carrier and prototype/schema observations."""
import copy,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
AXES=['identity','kind','carrier','owner_scope','sources','slice','claims','policies','generator','bytes','digest','audience','channel','publisher']
FORBIDDEN=['generation_grants_permission','validation_grants_permission','promotion_grants_permission','proof_grants_permission','discharge_grants_permission','adoption_grants_permission','receipt_grants_permission','tool_grants_owner_role','tool_grants_publisher_role','permission_proves_publication','permission_proves_truth']
def envelope():return {n:'hyp:'+n for n in AXES}
def qualify(before,after,flags):return ['binding-changed:'+n for n in AXES if before[n]!=after[n]]+['forbidden-inference:'+n for n in FORBIDDEN if flags[n]]
def profiles():
 rows=[];base=envelope();flags={n:False for n in FORBIDDEN}
 def add(id,after,f,expected):
  errors=qualify(base,after,f);assert bool(errors)==expected;rows.append({'case_id':id,'before':base,'after':after,'flags':f,'errors':errors,'expected_rejection':expected,'actual_runtime_execution':False,'actual_authorization_privacy_or_publication_verified':False,'source_fidelity_accepted':False})
 add('exact-qualified-hypothesis',copy.deepcopy(base),copy.deepcopy(flags),False);add('declared-permission-with-independent-no-publication-claim',copy.deepcopy(base),copy.deepcopy(flags),False)
 for n in AXES:a=copy.deepcopy(base);a[n]='hyp:changed';add('changed-'+n,a,copy.deepcopy(flags),True)
 for n in FORBIDDEN:f=copy.deepcopy(flags);f[n]=True;add('forbidden-'+n,copy.deepcopy(base),f,True)
 return rows
def frames():
 base={'before':envelope(),'after':envelope(),'owner_releases':True,'exact_output_approval':False,'privacy_pass':False,'requested_permission':False,'receipt_present':False,'actual_publication_claim':False,'inferred_permission':False};rows=[]
 def add(id,mutate,expected):
  x=copy.deepcopy(base);mutate(x);errors=[]
  if x['before']!=x['after']:errors.append('exact-bindings-changed-repeat-applicable-decisions')
  if x['requested_permission'] and not all(x[n] for n in ['owner_releases','exact_output_approval','privacy_pass']):errors.append('missing-independent-permission-prerequisite')
  if x['actual_publication_claim']:errors.append('permission-not-actual-publication-evidence')
  if x['inferred_permission']:errors.append('forbidden-source-receipt-tool-or-generation-inference')
  assert bool(errors)==expected;rows.append({'case_id':id,'frame':x,'errors':errors,'expected_rejection':expected,'actual_runtime_execution':False,'universal_authorization_privacy_publication_or_trace_proof':False})
 add('owner-release-private-preparation',lambda x:None,False)
 add('independent-exact-output-approval-and-privacy-pass',lambda x:x.update(exact_output_approval=True,privacy_pass=True,requested_permission=True),False)
 add('no-optional-receipt-required-for-permission',lambda x:x.update(exact_output_approval=True,privacy_pass=True,requested_permission=True,receipt_present=False),False)
 add('receipt-without-claiming-permission',lambda x:x.update(owner_releases=False,receipt_present=True),False)
 add('same-principal-with-separately-qualified-roles',lambda x:x.update(exact_output_approval=True,privacy_pass=True,requested_permission=True),False)
 for n in ['sources','slice','claims','policies','generator','bytes','digest','audience','channel','publisher']:add('changed-'+n,lambda x,n=n:x['after'].update({n:'hyp:changed'}),True)
 for n in ['generation','validation','promotion','receipt','tool-role','actual-publication']:
  add('unsupported-'+n,lambda x,n=n:x.update(actual_publication_claim=n=='actual-publication',inferred_permission=n!='actual-publication'),True)
 return rows
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();source=load('t.json')['payload']['source'];paths={'registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json','prototype':b.ROOT/'evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/semantic/semantic-exact-publication-authorization-invariant/v1/artifact.json','Definition_schema':b.ROOT/'authority/artifact-types/definition/v1/schema.json','current_Definition_schema':b.ROOT/'authority/artifact-types/definition/v2/schema.json','source':b.ROOT/source['path'],'checker':b.UNIT/'verify_authority_profile.py'};refs={k:b.ref(p) for k,p in paths.items()};docs={k:json.loads(p.read_bytes()) for k,p in paths.items() if p.suffix=='.json'};registry=docs['registry'];rows=registry['admitted_contracts'];current=[x for x in rows if x['lifecycle_state']=='admitted-current'];direct=[x for x in current if source['version_ref'] in x['semantic_definition_refs']];invariants=[x for x in current if x['semantic_kind']=='invariant'];proto=docs['prototype'];schema=docs['Definition_schema'];b.c.Draft202012Validator.check_schema(schema);validator=b.c.Draft202012Validator(schema);current_validator=b.c.Draft202012Validator(docs['current_Definition_schema']);checks=[]
 def ck(id,ok):checks.append({'check_id':id,'result':bool(ok)})
 ck('registry143rows121current',len(rows)==143 and len(current)==121);ck('no-admitted-direct-selected-Definition-carrier',not direct);ck('no-admitted-generic-invariant-carrier',not invariants);ck('prototype-remains-prototype-scaffold',proto['status']=='prototype-scaffold');ck('prototype-authority-effect-none',proto['authority_effect']=='none');ck('prototype-exact-normalized-identity',proto['normalized_contract']['concept_id']==proto['target_id']=='semantic.exact-publication-authorization-invariant');ck('prototype-independent-kind-carrier-owner-axes',proto['normalized_contract']['semantic_kind']=='invariant' and proto['normalized_contract']['carrier_ref']=='type.invariant' and proto['normalized_contract']['owner_scope']=='scope.repository-governance');ck('prototype-no-admitted-schema',proto['four_facets']['schema']['admitted_schema_ref'] is None and proto['four_facets']['schema']['schema_state']=='definition-voice-shape-prototyped');ck('prototype-D57-source-selector-and-digest-exact',proto['source_refs'][0]['selector']=='## CAV2-D57: Exact Publication Authorization' and proto['source_refs'][0]['section_sha256']==load('source-checks.json')['selected_source_section_sha256']);ck('prototype-normalization-is-split-not-source-identity-merge',proto['accepted_source_decisions'][0]['legacy_id']=='CAV2-D57' and proto['accepted_source_decisions'][0]['decision']=='split');ck('prototype-owner-normalization-is-not-publication-approval',proto['owner_decision_ref']=='CAL-DECISION-0012-NORMALIZE-01-DEFAULTS' and proto['normalization_ref']=='CAL-NORMALIZE-01');ck('prototype-gap-for-family-specific-admitted-type-preserved',any('family-specific admitted Artifact Type' in x for x in proto['gaps']));ck('selected-Definition-shape-valid-not-publication-authorization',not list(validator.iter_errors(docs['source'])) and docs['source']['classification']['artifact_type_ref']=='cal.artifact-type.definition/v1');ck('source-body-is-candidate-while-C53-overlay-admitted',docs['source']['source_refs'][0]['admission_posture']=='candidate-unadmitted' and load('source-checks.json')['current_registry_entry_lifecycle']=='admitted')
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 probes=[]
 def probe(id,doc,expected):
  errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in validator.iter_errors(doc)];accepted=not errors
  if accepted!=expected:raise ValueError('Wrong authored Definition-shape probe '+id+' '+str(errors))
  probes.append({'case_id':id,'schema_accepted':accepted,'errors':errors,'actual_publication_authorization_or_owner_verified':False,'scope':'Definition/v1 shape only;no admitted publication-authorization carrier'})
 original=docs['source'];probe('selected-exact-Definition-shape',copy.deepcopy(original),True)
 for n in schema['required']:
  d=copy.deepcopy(original);d.pop(n);probe('missing-required-root-'+n,d,False)
 for n in ['release_authorizations','exact_output_approval','publication_receipt','publication_permission']:
  d=copy.deepcopy(original);d[n]='hyp:claimed';probe('publication-field-not-in-Definition-schema-'+n,d,False)
 for n in ['definition_id','term','semantic_owner_ref']:
  d=copy.deepcopy(original);d[n]='hyp:unresolved';probe('shape-does-not-resolve-'+n,d,True)
 d=copy.deepcopy(original);d['voices']['scientific_formal']['normative_statement']='hyp:publication granted';probe('shape-valid-overclaimed-normative-text',d,True)
 errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in current_validator.iter_errors(original)]
 inputs=[b.ref(b.UNIT/n) for n in ['t.json','source-checks.json','comparison-selection.json']];bindings=[b.ref(p) for p in [b.UNIT/'verify_authority_profile.py',b.IMPL/'contracts.py',b.IMPL/'ir.py',b.IMPL/'verifier.py']];report={'schema_version':'definition-assurance-EPAI-profile/v1-candidate','status':'PASS-for-qualified-publication-hypotheses-and-actual-no-carrier-prototype-observations','authority_effect':'none','checker_bindings':bindings,'input_refs':inputs,'runtime_bindings':runtime,'selected_inputs':refs,'profiles':profiles(),'finite_publication_frames':frames(),'actual_checks':checks,'actual_check_count':len(checks),'current_type_registry_rows':len(rows),'admitted_current_type_rows':len(current),'direct_current_definition_binding_types':[x['artifact_type_ref'] for x in direct],'current_invariant_carrier_types':[x['artifact_type_ref'] for x in invariants],'prototype_status':proto['status'],'prototype_authority_effect':proto['authority_effect'],'admitted_publication_schema_ref':None,'schema_probe_surface':'selected Definition/v1;not a publication authorization schema','schema_probes':probes,'historical_source_current_definition_shape':{'errors':errors,'exact_source_admission_invalidated':False},'bound_package_validator_executed':False,'generator_module_or_materialization_writer_executed':False,'native_or_live_consumer_executed':False,'actual_authorization_privacy_publication_or_receipt_created':False,'generic_carrier_or_consumer_alignment_accepted':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Qualified authored hypotheses plus14actual registry/prototype/Definition observations and scoped Definition schema probes. No admitted publication authorization carrier,type.invariant schema,actual owner/publisher decision,privacy execution,publication,receipt or consumer proof.'}
 b.unchanged(list(refs.values())+inputs+bindings+context['sources']);b.external_current(context);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh profile observations differ')
 return report
def main():
 r=verify('--write' in b.sys.argv);print(json.dumps({'status':r['status'],'profiles':len(r['profiles']),'rejected_profiles':sum(x['expected_rejection'] for x in r['profiles']),'frames':len(r['finite_publication_frames']),'rejected_frames':sum(x['expected_rejection'] for x in r['finite_publication_frames']),'catalog_checks':r['actual_check_count'],'Definition_schema_probes':len(r['schema_probes']),'schema_acceptances':sum(x['schema_accepted'] for x in r['schema_probes']),'direct_current_definition_binding_types':r['direct_current_definition_binding_types']},indent=2))
if __name__=='__main__':main()
