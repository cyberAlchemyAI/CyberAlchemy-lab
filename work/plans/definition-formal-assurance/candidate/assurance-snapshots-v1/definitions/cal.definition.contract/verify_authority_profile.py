"""Qualified hypothetical contracts and exact current carrier/role observations."""
import ast,copy,json
from typing import Any
from urllib.parse import urljoin
from referencing import Registry,Resource
from referencing.exceptions import NoSuchResource
from referencing.jsonschema import DRAFT202012
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
AXES=['contract','identity','version','subjects','parties','scope','owner','revision','source_epoch','breach_route']
SUPPORT=['definition_resolution','version_binding','metadata_coherence','normative_interpretation','owner_governance','exact_roles','evidence_boundary','consumer_conformance']
FORBIDDEN=['global_compliance','admission','owner_transfer','authority','satisfaction_from_declaration','actual_claim']
def profiles():
 base={'context':{n:'hyp:'+n for n in AXES},'query':{n:'hyp:'+n for n in AXES},'supports':{n:True for n in SUPPORT},'bindings_current':True,'request_current':True,**{n:False for n in FORBIDDEN}};cases=[]
 def add(id,change,reject=False,use=True):
  x=copy.deepcopy(base);change(x);errors=[]
  for n in AXES:
   if x['context'][n]!=x['query'][n]:errors.append('context-mismatch:'+n)
  for n in SUPPORT:
   if not x['supports'][n]:errors.append('missing-support:'+n)
  for n in FORBIDDEN:
   if x[n]:errors.append('forbidden:'+n)
  if x['request_current'] and not x['bindings_current']:errors.append('stale-current-bindings')
  assert bool(errors)==reject
  allowed=not errors and x['bindings_current'];assert allowed==use
  cases.append({'case_id':id,'profile':x,'errors':errors,'expected_rejection':reject,'expected_use':use,'use_allowed_under_hypotheses':allowed,'actual_runtime_execution':False,'actual_contract_normative_owner_or_consumer_verified':False,'source_fidelity_accepted':False})
 add('qualified-governed-contract',lambda x:None)
 for n in AXES:add('wrong-query-'+n,lambda x,n=n:x['query'].update({n:'hyp:wrong'}),True,False)
 for n in SUPPORT:add('missing-'+n,lambda x,n=n:x['supports'].update({n:False}),True,False)
 for n in FORBIDDEN:add('forbidden-'+n,lambda x,n=n:x.update({n:True}),True,False)
 add('stale-current-binding-request',lambda x:x.update(bindings_current=False),True,False)
 add('stale-binding-with-no-current-use',lambda x:x.update(bindings_current=False,request_current=False),False,False)
 return cases
def frames():
 base={'source_before':{'contract':'hyp:c','version':'hyp:v','owner':'hyp:o','scope':'hyp:s'},'source_after':{'contract':'hyp:c','version':'hyp:v','owner':'hyp:o','scope':'hyp:s'},'obligation_declared':True,'actual_satisfaction':False,'permission_declared':True,'actual_grant':False,'separate_grant_evidence':False,'effect_requested':False,'satisfaction_inferred':False,'grant_inferred':False,'implementation_collapsed':False,'evidence_collapsed':False,'issuer_collapsed':False,'breach_execution_inferred':False,'authority_transfer':False,'actual_claim':False};rows=[]
 def add(id,change,reject=False):
  x=copy.deepcopy(base);change(x);errors=[]
  for n in x['source_before']:
   if x['source_before'][n]!=x['source_after'][n]:errors.append('contract-envelope-changed:'+n)
  if x['effect_requested'] and not (x['actual_grant'] and x['separate_grant_evidence']):errors.append('effect-without-independent-grant')
  for n in ['satisfaction_inferred','grant_inferred','implementation_collapsed','evidence_collapsed','issuer_collapsed','breach_execution_inferred','authority_transfer','actual_claim']:
   if x[n]:errors.append('forbidden:'+n)
  assert bool(errors)==reject
  rows.append({'case_id':id,'frame':x,'errors':errors,'expected_rejection':reject,'actual_runtime_execution':False,'universal_compliance_grant_breach_or_authority_proof':False})
 add('declarations-retain-unsatisfied-and-ungranted-status',lambda x:None)
 add('separately-evidenced-grant-hypothesis',lambda x:x.update(actual_grant=True,separate_grant_evidence=True,effect_requested=True))
 add('independent-satisfaction-hypothesis-no-inference',lambda x:x.update(actual_satisfaction=True))
 for n in base['source_before']:add('changed-contract-'+n,lambda x,n=n:x['source_after'].update({n:'hyp:changed'}),True)
 add('declared-permission-alone-cannot-authorize-effect',lambda x:x.update(effect_requested=True),True)
 add('grant-marker-alone-without-independent-evidence',lambda x:x.update(effect_requested=True,actual_grant=True),True)
 for n in ['satisfaction_inferred','grant_inferred','implementation_collapsed','evidence_collapsed','issuer_collapsed','breach_execution_inferred','authority_transfer','actual_claim']:add('forbidden-'+n,lambda x,n=n:x.update({n:True}),True)
 return rows
def extracted(raw,path,names,namespace):
 tree=ast.parse(raw);selected=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in names];assert {x.name for x in selected}==set(names);exec(compile(ast.Module(body=selected,type_ignores=[]),str(path),'exec'),namespace);return namespace
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();source=load('t.json')['payload']['source'];rp=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json';reg=json.loads(rp.read_bytes());current=[x for x in reg['admitted_contracts'] if x['lifecycle_state']=='admitted-current'];direct=[x for x in current if source['version_ref'] in x['semantic_definition_refs']];assert [x['artifact_type_ref'] for x in direct]==['cal.artifact-type.contract/v1'];row=direct[0];pkg=(b.ROOT/row['artifact_path']).parent;artifact=json.loads((pkg/'artifact.json').read_bytes())
 paths={'registry':rp,'descriptor':pkg/'artifact.json','schema':b.ROOT/row['schema_path'],'fixture':pkg/artifact['validation_contract']['positive_witness'],'artifact_projection':pkg/'ARTIFACT.md','fixture_projection':pkg/artifact['validation_contract']['positive_projection'],'generator':b.ROOT/artifact['source_direction']['shared_generator_path'],'wrapper':pkg/'validate.py','validator':b.ROOT/artifact['validation_contract']['shared_validator_path'],'relation_model':b.ROOT/'authority/relation-kinds/candidates/0002-axis-orthogonal-model/model.json','root_descriptor':b.ROOT/artifact['artifact_type_root_binding']['path'],'definition_schema':b.ROOT/'authority/artifact-types/definition/v2/schema.json'}
 for i,n in enumerate(artifact['validation_contract']['negative_witnesses']):paths['negative_'+str(i)]=pkg/n
 refs={n:b.ref(p) for n,p in paths.items()};raw={n:p.read_bytes() for n,p in paths.items()};docs={n:json.loads(x) for n,x in raw.items() if paths[n].suffix=='.json'};schema=docs['schema'];b.c.Draft202012Validator.check_schema(schema);validator=b.c.Draft202012Validator(schema);fixture=docs['fixture'];binding=artifact['semantic_definition_bindings'];checks=[]
 def ck(id,ok):checks.append({'check_id':id,'result':bool(ok)})
 ck('one-current-C65-exact-definition-binding',len(binding)==1 and all(binding[0][k]==source[z] for k,z in [('definition_ref','version_ref'),('path','path'),('sha256','sha256')]) and binding[0]['admission_decision_ref']=='CAL-DECISION-0065-INTEGRATED-LAB-DEFINITION-MODEL-ADMISSION');ck('current-v1-C70-recorded-admission',row['admission_decision_ref']=='CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION');ck('retained-descriptor-and-fixture-posture',artifact['status']=='candidate-unadmitted' and fixture['lifecycle_state']=='candidate' and artifact['authority_effect']==fixture['authority_effect']=='none');ck('registry-descriptor-schema-digests',row['artifact_sha256']==refs['descriptor']['sha256'] and row['schema_sha256']==artifact['schema_digest']==refs['schema']['sha256']);ck('root-type-exact-binding',artifact['artifact_type_root_binding']['sha256']==refs['root_descriptor']['sha256']);ck('fixture-valid-current-schema',not list(validator.iter_errors(fixture)))
 renderer=extracted(raw['generator'],paths['generator'],['render_artifact','render_instance'],{'json':json,'Any':Any});before=copy.deepcopy(fixture);ck('two-pure-fixture-renders-exact',renderer['render_instance'](artifact,fixture).encode()==renderer['render_instance'](artifact,fixture).encode()==raw['fixture_projection']);ck('pure-artifact-render-exact',renderer['render_artifact'](artifact).encode()==raw['artifact_projection']);ck('renderer-input-preserved',fixture==before)
 fields=schema['properties'];payload=fields['payload'];ck('closed-fourteen-root-six-payload-required-fields',schema['additionalProperties'] is False and payload['additionalProperties'] is False and len(schema['required'])==14 and len(payload['required'])==6);ck('both-party-and-subject-lists-required',all(n in payload['required'] and payload['properties'][n]['minItems']==1 for n in ['party_refs','subject_refs']));ck('no-explicit-version-interface-boundary-evidence-requirement-fields',not any(n in fields or n in payload['properties'] for n in ['version','version_ref','interface_refs','boundary_refs','evidence_requirement_refs']));ck('obligation-permission-prohibition-list-members-unresolved-strings',all(payload['properties'][n]['items']=={'type':'string','minLength':1} for n in ['obligation_refs','permission_refs','prohibition_refs']));ck('evidence-list-can-be-empty','minItems' not in fields['evidence_refs']);ck('breach-route-is-nonempty-string',payload['properties']['breach_route']=={'type':'string','minLength':1})
 hostiles=[]
 for n in paths:
  if n.startswith('negative_'):
   errors=[e.message for e in validator.iter_errors(docs[n])];hostiles.append({'fixture_ref':refs[n],'schema_rejected':bool(errors),'errors':errors})
 ck('five-hostiles-rejected',len(hostiles)==5 and all(x['schema_rejected'] for x in hostiles))
 pure=extracted(raw['validator'],paths['validator'],['expected_roles'],{})['expected_roles'];roles=pure('contract',docs['relation_model']);ck('pure-role-model-exact-four-roles-three-kinds',roles==artifact['relation_roles'] and len(roles)==4 and sorted({x['relation_kind_ref'] for x in roles})==artifact['allowed_relation_kinds']);eligible={(x['relation_kind_ref'],x['direction'],kind) for x in roles for kind in x['counterpart_kinds']};roleobs=[]
 for kind in fields['relation_refs']['items']['properties']['relation_kind_ref']['enum']:
  for direction in ['source','target']:
   for counterpart in ['capability-instance','contract']:
    x=copy.deepcopy(fixture);x['relation_refs'][0].update(relation_kind_ref=kind,direction=direction,counterpart_kind=counterpart);ok=not list(validator.iter_errors(x));assert ok;roleobs.append({'relation_kind_ref':kind,'direction':direction,'counterpart_kind':counterpart,'schema_accepted':ok,'exact_role_eligible':(kind,direction,counterpart) in eligible,'actual_relation_endpoint_or_admission_verified':False})
 ck('schema-cartesian-twelve-combinations-four-eligible',len(roleobs)==12 and sum(x['exact_role_eligible'] for x in roleobs)==4)
 probes=[]
 def probe(id,change,accept):
  x=copy.deepcopy(fixture);change(x);errors=[{'path':'/'+('/'.join(str(y) for y in e.absolute_path)),'message':e.message} for e in validator.iter_errors(x)];ok=not errors;assert ok==accept,(id,errors);probes.append({'case_id':id,'schema_accepted':ok,'errors':errors,'actual_normative_compliance_grant_breach_or_admission_verified':False})
 for n in schema['required']:probe('missing-root-'+n,lambda x,n=n:x.pop(n),False)
 for n in payload['required']:probe('missing-payload-'+n,lambda x,n=n:x['payload'].pop(n),False)
 for n in ['party_refs','subject_refs','obligation_refs','permission_refs','prohibition_refs']:
  probe('empty-'+n,lambda x,n=n:x['payload'].update({n:[]}),False);probe('duplicate-'+n,lambda x,n=n:x['payload'][n].append(x['payload'][n][0]),False);probe('unresolved-'+n,lambda x,n=n:x['payload'].update({n:['unresolved:'+n]}),True)
 for n in ['node_id','owner_ref','scope_ref','challenge_route']:probe('unresolved-'+n,lambda x,n=n:x.update({n:'unresolved:'+n}),True)
 for n in ['version','interface_refs','boundary_refs','evidence_requirement_refs']:probe('extra-payload-'+n,lambda x,n=n:x['payload'].update({n:'unresolved'}),False)
 probe('extra-root-version',lambda x:x.update(version='1.0.0'),False);probe('empty-evidence',lambda x:x.update(evidence_refs=[]),True);probe('active-lifecycle-with-no-admission-or-effects',lambda x:x.update(lifecycle_state='active'),True);probe('unresolved-breach-route',lambda x:x['payload'].update(breach_route='unresolved:breach-route'),True);probe('empty-breach-route',lambda x:x['payload'].update(breach_route=''),False);probe('same-party-and-subject-ref',lambda x:x['payload'].update(subject_refs=list(x['payload']['party_refs'])),True);probe('same-obligation-permission-prohibition-ref',lambda x:x['payload'].update(permission_refs=list(x['payload']['obligation_refs']),prohibition_refs=list(x['payload']['obligation_refs'])),True);probe('unsupported-actual-compliance-claim-text',lambda x:x.update(claim_ceiling='All obligations are satisfied and all permissions granted.'),True);probe('duplicate-relation-record',lambda x:x['relation_refs'].append(copy.deepcopy(x['relation_refs'][0])),True);probe('no-relations',lambda x:x.update(relation_refs=[]),False);probe('authority-effect-grant',lambda x:x.update(authority_effect='grant'),False);probe('collapsed-policy-kind',lambda x:x.update(kind='policy'),False)
 old=b.co.source_document(snap,source);dv=b.c.Draft202012Validator(docs['definition_schema']);shape={'errors':[{'path':'/'+('/'.join(str(y) for y in e.absolute_path)),'message':e.message} for e in dv.iter_errors(old)],'exact_source_admission_invalidated':False,'instance_migrated':False};ck('Definition-v1-v2-shape-gap-observed',len(shape['errors'])==4)
 sourceText=raw['validator'].decode();ck('package-validator-source-has-separate-exact-role-subset-check','fixture_roles <= role_set' in sourceText and 'fixture-relations-declared' in sourceText);ck('package-validator-source-emits-receipt-so-not-executed','dump(root / "receipts/validation.json", receipt)' in sourceText)
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 report={'schema_version':'definition-assurance-Contract-profile/v1-candidate','status':'PASS-for-qualified-contract-hypotheses-and-selected-carrier-role-observations','authority_effect':'none','checker_bindings':[b.ref(b.UNIT/'verify_authority_profile.py'),b.ref(b.IMPL/'contracts.py'),b.ref(b.IMPL/'ir.py'),b.ref(b.IMPL/'verifier.py')],'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','source-checks.json','comparison-selection.json']],'selected_inputs':refs,'current_type_registry_rows':len(reg['admitted_contracts']),'admitted_current_type_rows':len(current),'direct_current_definition_binding_types':[x['artifact_type_ref'] for x in direct],'current_registry_selection':row,'exact_definition_binding':binding[0],'registry_carrier_state':row['lifecycle_state'],'retained_descriptor_status':artifact['status'],'fixture_lifecycle_state':fixture['lifecycle_state'],'actual_check_count':len(checks),'actual_checks':checks,'schema_probes':probes,'negative_fixture_checks':hostiles,'profiles':profiles(),'profile_context_axes':AXES,'profile_support_axes':SUPPORT,'finite_contract_frames':frames(),'pure_expected_role_observation':{'roles':roles,'eligible_role_triples':sorted(eligible),'selected_role_model_ref':refs['relation_model'],'function_only_executed':True,'model_input_preserved':docs['relation_model']==json.loads(raw['relation_model']),'actual_relation_kind_or_instance_admission_verified':False},'relation_schema_role_observations':roleobs,'historical_source_current_definition_shape':shape,'native_or_live_consumer_executed':False,'bound_package_validator_executed':False,'generator_module_or_materialization_writer_executed':False,'selected_pure_render_and_expected_role_functions_executed':True,'generic_carrier_normative_contract_or_consumer_alignment_accepted':False,'actual_contract_admission_compliance_grants_or_breach_execution_created':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Exact source/carrier shape and pure projections/role calculation;schema misses version/interface/boundary/evidence-requirement fields and forces both party and subject lists. Cartesian relation shape differs from exact role eligibility. No actual normative consistency,compliance,grants,breach,owner,consumer or whole fidelity proof.'}
 b.unchanged(context['sources']+list(refs.values())+report['checker_bindings']+report['input_refs']);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh profile differs')
 return report
def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({'status':x['status'],'profiles':len(x['profiles']),'rejected_profiles':sum(y['expected_rejection'] for y in x['profiles']),'frames':len(x['finite_contract_frames']),'rejected_frames':sum(y['expected_rejection'] for y in x['finite_contract_frames']),'schema_probes':len(x['schema_probes']),'schema_acceptances':sum(y['schema_accepted'] for y in x['schema_probes']),'catalog_checks':x['actual_check_count'],'relation_combinations':len(x['relation_schema_role_observations']),'role_eligible_combinations':sum(y['exact_role_eligible'] for y in x['relation_schema_role_observations'])},indent=2))
if __name__=='__main__':main()
