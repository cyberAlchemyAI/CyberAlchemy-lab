"""Qualified hypothetical contexts and actual selected carrier/map/index observations."""
import ast,copy,json
from typing import Any
from urllib.parse import urljoin
from referencing import Registry,Resource
from referencing.exceptions import NoSuchResource
from referencing.jsonschema import DRAFT202012
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
AXES=['context','identity','context_version','model','language','scope','owner','revision','source_epoch','map_registry']
SUPPORT=['context_resolution','identity_unique','metadata_coherence','consistency_intent','owner_governance','exact_map','projection_boundary','consumer_conformance']
FORBIDDEN=['global_consistency','admission','owner_transfer','authority','canonical_context_backreference','actual_claim']
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
  cases.append({'case_id':id,'profile':x,'errors':errors,'expected_rejection':reject,'expected_use':use,'use_allowed_under_hypotheses':allowed,'actual_runtime_execution':False,'actual_context_model_owner_registry_or_consumer_verified':False,'source_fidelity_accepted':False})
 add('qualified-owned-context-map-registry',lambda x:None)
 for n in AXES:add('wrong-query-'+n,lambda x,n=n:x['query'].update({n:'hyp:wrong'}),True,False)
 for n in SUPPORT:add('missing-'+n,lambda x,n=n:x['supports'].update({n:False}),True,False)
 for n in FORBIDDEN:add('forbidden-'+n,lambda x,n=n:x.update({n:True}),True,False)
 add('stale-current-binding-request',lambda x:x.update(bindings_current=False),True,False)
 add('stale-binding-with-no-current-use',lambda x:x.update(bindings_current=False,request_current=False),False,False)
 return cases
def frames():
 base={'source_before':{'context':'hyp:c','version':'hyp:v','owner':'hyp:o','membership':'hyp:m'},'source_after':{'context':'hyp:c','version':'hyp:v','owner':'hyp:o','membership':'hyp:m'},'registry_before':'hyp:reg','registry_after':'hyp:reg','lookup_before':['hyp:m'],'lookup_after':['hyp:m'],'rebuild_requested':True,'context_owns_membership':False,'lookup_omission_amends_map':False,'owner_transfer':False,'authority_transfer':False,'actual_claim':False};rows=[]
 def add(id,change,reject=False):
  x=copy.deepcopy(base);change(x);errors=[]
  for n in x['source_before']:
   if x['source_before'][n]!=x['source_after'][n]:errors.append('source-changed:'+n)
  if x['rebuild_requested'] and (x['registry_before']!=x['registry_after'] or x['lookup_before']!=x['lookup_after']):errors.append('changed-rebuild-input-or-output')
  for n in ['context_owns_membership','lookup_omission_amends_map','owner_transfer','authority_transfer','actual_claim']:
   if x[n]:errors.append('forbidden:'+n)
  assert bool(errors)==reject
  rows.append({'case_id':id,'frame':x,'errors':errors,'expected_rejection':reject,'actual_runtime_execution':False,'universal_consistency_projection_or_authority_proof':False})
 add('same-source-same-registry-rebuild-hypothesis',lambda x:None)
 add('different-selected-registry-relative-lookup',lambda x:x.update(rebuild_requested=False,registry_after='hyp:subset',lookup_after=[]))
 for n in base['source_before']:add('changed-source-'+n,lambda x,n=n:x['source_after'].update({n:'hyp:changed'}),True)
 add('rebuild-registry-changed',lambda x:x.update(registry_after='hyp:other'),True)
 add('rebuild-lookup-changed',lambda x:x.update(lookup_after=[]),True)
 for n in ['context_owns_membership','lookup_omission_amends_map','owner_transfer','authority_transfer','actual_claim']:add('forbidden-'+n,lambda x,n=n:x.update({n:True}),True)
 return rows
def extracted(raw,path,names,namespace):
 tree=ast.parse(raw);selected=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in names];assert {x.name for x in selected}==set(names);exec(compile(ast.Module(body=selected,type_ignores=[]),str(path),'exec'),namespace);return namespace
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();source=load('t.json')['payload']['source'];rp=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json';reg=json.loads(rp.read_bytes());current=[x for x in reg['admitted_contracts'] if x['lifecycle_state']=='admitted-current'];direct=[x for x in current if source['version_ref'] in x['semantic_definition_refs']];assert [x['artifact_type_ref'] for x in direct]==['cal.artifact-type.bounded-context/v3'];row=direct[0];pkg=(b.ROOT/row['artifact_path']).parent;artifact=json.loads((pkg/'artifact.json').read_bytes())
 paths={'registry':rp,'descriptor':pkg/'artifact.json','schema':b.ROOT/row['schema_path'],'fixture':pkg/'fixtures/valid/context.json','artifact_projection':pkg/'ARTIFACT.md','fixture_projection':pkg/'fixtures/valid/CONTEXT.md','generator':b.ROOT/artifact['source_direction']['shared_generator_path'],'wrapper':pkg/'validate.py','validator':b.ROOT/'tooling/validators/artifact_type_successor.py','predecessor_descriptor':b.ROOT/artifact['predecessor_contract']['path'],'predecessor_schema':b.ROOT/artifact['predecessor_contract']['schema_path'],'predecessor_validator':b.ROOT/'tooling/validators/ctx07_artifact_type.py','predecessor_core_schema':b.ROOT/'tooling/schemas/ctx07/v2/schema.json','index_generator':b.ROOT/'tooling/generators/ctx07_artifact.py','root_descriptor':b.ROOT/artifact['artifact_type_root_binding']['path'],'definition_schema':b.ROOT/'authority/artifact-types/definition/v2/schema.json','C25':b.ROOT/'docs/decisions/0025-governance-ontology-lifecycle-successor-promotion/decision.json','map_fixture':b.ROOT/'authority/artifact-types/context-map/v2/fixtures/valid/map.json','index_fixture':b.ROOT/'authority/artifact-types/context-map/v2/fixtures/valid/context-map-membership-index.json','actual_map':b.ROOT/'contexts/maps/governance-ontology-lifecycle/v2/map.json'}
 for slug in ['governance','ontology-lifecycle']:
  for version in ['v1','v2','v3']:paths[slug+'_'+version+'_context']=b.ROOT/'contexts'/slug/version/'context.json'
  paths[slug+'_v2_language']=b.ROOT/'contexts'/slug/'v2/language.json'
 for i,n in enumerate(artifact['validation_contract']['negative_witnesses']):paths['negative_'+str(i)]=pkg/n
 refs={n:b.ref(p) for n,p in paths.items()};raw={n:p.read_bytes() for n,p in paths.items()};docs={n:json.loads(x) for n,x in raw.items() if paths[n].suffix=='.json'};schema=docs['schema'];b.c.Draft202012Validator.check_schema(schema);validator=b.c.Draft202012Validator(schema);core=docs['predecessor_core_schema'];wrapper=docs['predecessor_schema'];baseURI=paths['predecessor_schema'].as_uri();resolvedURI=urljoin(baseURI,wrapper['$ref'].split('#')[0]);resource=Resource.from_contents(core,default_specification=DRAFT202012);registry=Registry(retrieve=lambda uri:(_ for _ in ()).throw(NoSuchResource(ref=uri))).with_resources([(resolvedURI,resource),(core['$id'],resource)]);predschema={**wrapper,'$id':baseURI};predvalidator=b.c.Draft202012Validator(predschema,registry=registry);fixture=docs['fixture'];binding=artifact['semantic_definition_bindings'];checks=[]
 def ck(id,ok):checks.append({'check_id':id,'result':bool(ok)})
 ck('one-current-C26-exact-definition-binding',len(binding)==1 and all(binding[0][k]==source[z] for k,z in [('definition_ref','version_ref'),('path','path'),('sha256','sha256')]) and binding[0]['admission_decision_ref']=='CAL-DECISION-0026-CTX06-REFERENCE-NORMALIZATION-DEFINITION-PROMOTION')
 ck('current-v3-C70-and-historical-v2-C27',row['admission_decision_ref']=='CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION' and any(x['artifact_type_ref']=='cal.artifact-type.bounded-context/v2' and x['lifecycle_state']=='admitted-historical' and x['admission_decision_ref']=='CAL-DECISION-0027-CTX07-NORMALIZED-CONTEXT-ARTIFACT-TYPE-PROMOTION' for x in reg['admitted_contracts']))
 ck('descriptor-fixture-candidate-posture',artifact['status']==fixture['status']=='candidate-unadmitted' and artifact['authority_effect']==fixture['authority_effect']=='none');ck('registry-descriptor-schema-digests',row['artifact_sha256']==refs['descriptor']['sha256'] and row['schema_sha256']==artifact['schema_digest']==refs['schema']['sha256']);ck('root-predecessor-bytes-bound',artifact['artifact_type_root_binding']['sha256']==refs['root_descriptor']['sha256'] and artifact['predecessor_contract']['sha256']==refs['predecessor_descriptor']['sha256'] and artifact['predecessor_contract']['schema_sha256']==refs['predecessor_schema']['sha256']);ck('fixture-valid-current-schema',not list(validator.iter_errors(fixture)))
 renderer=extracted(raw['generator'],paths['generator'],['render_artifact','render_instance'],{'json':json,'Any':Any});before=copy.deepcopy(fixture);ck('two-pure-fixture-renders-exact',renderer['render_instance'](artifact,fixture).encode()==renderer['render_instance'](artifact,fixture).encode()==raw['fixture_projection']);ck('pure-artifact-render-exact',renderer['render_artifact'](artifact).encode()==raw['artifact_projection']);ck('renderer-input-preserved',fixture==before)
 d=schema['$defs']['boundedContext'];fields=d['allOf'][1]['properties'];forbidden=artifact['instance_contract']['forbidden_canonical_fields'];ck('closed-seven-context-required-fields',d['unevaluatedProperties'] is False and len(d['allOf'][1]['required'])==7);ck('v3-discriminator-retains-v2-classification',fields['schema_version']['const']=='cyberalchemy-lab-bounded-context/v3' and fields['classification']['properties']['artifact_type_ref']['const']=='cal.artifact-type.bounded-context/v2' and fixture['classification']['artifact_type_ref']=='cal.artifact-type.bounded-context/v2');ck('three-canonical-backreference-fields-forbidden',set(forbidden)=={'context_map_refs','map_membership','canonical_reverse_membership_index'} and not set(forbidden)&fixture.keys());ck('contract-evidence-empty-list-shape-permitted','minItems' not in schema['$defs']['refList']);ck('lifecycle-posture-token-not-independent-lifecycle-proof','lifecycle' not in fields and 'lifecycle_posture_ref' in fixture['classification']);ck('three-declared-relation-roles-two-kinds',len(artifact['relation_roles'])==3 and artifact['allowed_relation_kinds']==['relation.frames','relation.successor-of'])
 hostiles=[]
 for n in paths:
  if n.startswith('negative_'):
   errors=[e.message for e in validator.iter_errors(docs[n])];hostiles.append({'fixture_ref':refs[n],'schema_rejected':bool(errors),'errors':errors})
 ck('two-hostiles-rejected',len(hostiles)==2 and all(x['schema_rejected'] for x in hostiles))
 probes=[]
 def probe(id,change,accept):
  x=copy.deepcopy(fixture);change(x);errors=[{'path':'/'+('/'.join(str(y) for y in e.absolute_path)),'message':e.message} for e in validator.iter_errors(x)];ok=not errors;assert ok==accept,(id,errors);probes.append({'case_id':id,'schema_accepted':ok,'errors':errors,'actual_identity_owner_consistency_or_admission_verified':False})
 for n in d['allOf'][1]['required']:probe('missing-'+n,lambda x,n=n:x.pop(n),False)
 for n in ['context_id','domain_model_ref','ubiquitous_language_ref','semantic_owner_ref','challenge_route']:probe('unresolved-'+n,lambda x,n=n:x.update({n:'unresolved:'+n}),True)
 for n in forbidden:probe('forbidden-'+n,lambda x,n=n:x.update({n:[]}),False)
 for n in ['contract_refs','evidence_refs']:probe('empty-'+n,lambda x,n=n:x.update({n:[]}),True)
 probe('duplicate-contract-ref',lambda x:x['contract_refs'].append(x['contract_refs'][0]),False)
 probe('empty-scope-exclusions',lambda x:x['scope'].update(exclusions=[]),False)
 probe('missing-scope-exclusions',lambda x:x['scope'].pop('exclusions'),False)
 probe('opaque-explicit-scope',lambda x:x['scope'].update(statement='unresolved scope',exclusions=['unresolved exclusions']),True)
 probe('context-language-same-string',lambda x:x.update(ubiquitous_language_ref=x['context_id']),True)
 probe('unverified-lifecycle-posture',lambda x:x['classification'].update(lifecycle_posture_ref='unresolved:lifecycle'),True)
 probe('extra-lifecycle-field',lambda x:x.update(lifecycle='active'),False)
 probe('equivalent-extra-canonical-backref-field',lambda x:x.update(context_membership=[]),False)
 probe('v3-classification-in-v3-schema',lambda x:x['classification'].update(artifact_type_ref='cal.artifact-type.bounded-context/v3'),False)
 probe('schema-status-admitted',lambda x:x.update(status='admitted'),False)
 probe('authority-effect-grant',lambda x:x.update(authority_effect='grant'),False)
 probe('actual-consistency-claim-text',lambda x:x.update(claim_ceiling='This proves complete semantic consistency.'),True)
 probe('opaque-version-token',lambda x:x.update(version='opaque'),False)
 probe('different-valid-semver',lambda x:x.update(version='3.0.0-candidate.2'),True)
 pure=extracted(raw['predecessor_validator'],paths['predecessor_validator'],['semantic_invariants'],{})['semantic_invariants'];pureControls=[]
 def pc(id,change,accept):
  x=copy.deepcopy(fixture);change(x);old=copy.deepcopy(x);results=pure('bounded-context',x);ok=all(z[1] for z in results);assert ok==accept,id;pureControls.append({'case_id':id,'input':x,'pure_checker_accepted':ok,'schema_accepted':not list(validator.iter_errors(x)),'input_preserved':old==x,'results':results,'package_validator_executed':False,'actual_consistency_owner_or_registry_verified':False})
 pc('baseline-context-language-distinct',lambda x:None,True)
 pc('context-language-same-string',lambda x:x.update(ubiquitous_language_ref=x['context_id']),False)
 for n in forbidden:pc('forbidden-'+n,lambda x,n=n:x.update({n:[]}),False)
 pc('unresolved-model-owner-not-resolved',lambda x:x.update(domain_model_ref='unresolved:model',semantic_owner_ref='unresolved:owner'),True)
 pc('empty-contracts-evidence-not-resolved',lambda x:x.update(contract_refs=[],evidence_refs=[]),True)
 pc('schema-invalid-extra-field-outside-pure-scope',lambda x:x.update(context_membership=[]),True)
 pc('same-key-two-schema-valid-independent-records',lambda x:None,True)
 ck('pure-CTX07-scope-observed',len(pureControls)==9 and all(x['input_preserved'] for x in pureControls));ck('successor-validator-source-lacks-CTX07-semantic-hook',all(n not in raw['validator'].decode() for n in ['semantic_invariants','ctx07_artifact_type','context-language-distinct']))
 from collections import defaultdict
 builder=extracted(raw['index_generator'],paths['index_generator'],['build_membership_index'],{'defaultdict':defaultdict})['build_membership_index'];indexControls=[];fm=docs['map_fixture'];actual=docs['actual_map'];fixtureInput=[(refs['map_fixture']['path'],fm,refs['map_fixture']['sha256'])]
 def ic(id,inputs,test):
  before=copy.deepcopy(inputs);first=builder(inputs);second=builder(inputs);ok=test(first);assert ok,id;indexControls.append({'case_id':id,'inputs':inputs,'output':first,'output_sha256':b.ir.digest(first),'two_outputs_equal':first==second,'input_preserved':before==inputs,'expected_observation':ok,'function_only_executed':True,'actual_registry_coverage_or_input_admission_verified':False});return first
 fi=ic('fixture-exact-recorded-index',fixtureInput,lambda out:out==docs['index_fixture'])
 secondmap=copy.deepcopy(fm);secondmap['context_map_id']='cal.context-map.other';pair=fixtureInput+[('candidate:other',secondmap,'supplied:other-digest')]
 out=ic('two-map-order-independent',pair,lambda out:out==builder(list(reversed(pair))))
 dup=copy.deepcopy(fm);dup['context_refs'].append(dup['context_refs'][0]);ic('duplicate-endpoint-projected-once',[('candidate:duplicate',dup,'supplied:duplicate')],lambda out:len(out['memberships'])==len(fi['memberships']))
 revision=copy.deepcopy(fm);revision['version']='3.0.0-candidate.1';ic('same-id-two-versions-fixed-v2-map-reference-collapses',fixtureInput+[('candidate:later',revision,'supplied:later')],lambda out:len(out['generated_from'])==2 and len({x['context_map_ref'] for x in out['generated_from']})==1 and all(len(x['context_map_refs'])==1 for x in out['memberships']))
 ic('supplied-wrong-digest-retained-without-authentication',[('candidate:wrong',fm,'not-a-sha256')],lambda out:out['generated_from'][0]['sha256']=='not-a-sha256')
 bogus=copy.deepcopy(fm);bogus['context_refs'].append('unresolved:context');ic('unresolved-endpoint-still-projected',[('candidate:unresolved',bogus,'supplied:bogus')],lambda out:any(x['context_ref']=='unresolved:context' for x in out['memberships']))
 ic('empty-selected-map-set',[],lambda out:out['memberships']==out['generated_from']==[] and out['canonical'] is False)
 actualIndex=ic('actual-v2-map-has-no-normalized-v3-endpoints',[(refs['actual_map']['path'],actual,refs['actual_map']['sha256'])],lambda out:all(x['context_ref'].endswith('/v2') for x in out['memberships']))
 changed=copy.deepcopy(fm);changed['context_refs'][0]='candidate:new-endpoint';ic('changed-map-input-changes-projection-without-mutating-original',[('candidate:changed',changed,'supplied:changed')],lambda out:out['memberships']!=fi['memberships'] and fm==docs['map_fixture'])
 ck('nine-pure-index-controls-exact-local-properties',len(indexControls)==9 and all(x['input_preserved'] and x['two_outputs_equal'] for x in indexControls))
 observations=[]
 for slug in ['governance','ontology-lifecycle']:
  lang=docs[slug+'_v2_language']
  for epoch in ['v1','v2','v3']:
   key=slug+'_'+epoch+'_context';x=docs[key];backrefs=sorted(set(forbidden)&x.keys());selected=[r for r in docs['C25']['admitted_artifacts'] if r['path']==refs[key]['path']];bound=any(r['sha256']==refs[key]['sha256'] and r['decision_overlay_status']=='admitted' for r in selected);obs={'case_id':slug+'-'+epoch,'context_ref':refs[key],'context_id':x['context_id'],'document_version':x['version'],'retained_schema_version':x['schema_version'],'retained_status':x['status'],'canonical_map_fields':backrefs,'normalized_v2_schema_valid':not list(predvalidator.iter_errors(x)),'current_v3_schema_valid':not list(validator.iter_errors(x)),'C25_exact_recorded_admission_overlay':bound,'language_identity_matches':lang['bounded_context_ref'].rsplit('/',1)[0]==x['context_id'],'language_exact_epoch_matches':lang['bounded_context_ref']==x['context_id']+'/'+epoch,'context_language_epoch_matches_v2_language':x['ubiquitous_language_ref']==lang['language_id']+'/v2','actual_model_language_consistency_or_owner_verified':False};observations.append(obs)
 ck('six-contexts-normalization-shape-observed',len(observations)==6 and all(x['normalized_v2_schema_valid']==x['case_id'].endswith('v3') and not x['current_v3_schema_valid'] for x in observations));ck('C25-only-exact-v2-context-bytes-selected',[x['C25_exact_recorded_admission_overlay'] for x in observations]==[False,True,False,False,True,False]);ck('normalized-v3-language-identity-matches-but-epoch-does-not',all(x['language_identity_matches'] and not x['language_exact_epoch_matches'] and x['context_language_epoch_matches_v2_language'] and not x['canonical_map_fields'] for x in observations if x['case_id'].endswith('v3')))
 keys=[(x['context_id'],x['document_version']) for x in observations];ck('selected-six-context-identity-version-keys-unique',len(keys)==len(set(keys)))
 relationships=actual['relationships'];mapchecks=pure('context-map',actual);mapobs={'map_ref':refs['actual_map'],'context_refs':actual['context_refs'],'relationships':relationships,'pure_CTX07_map_checks':mapchecks,'normalized_v3_endpoints_present':False,'exact_endpoint_refs_match_old_v2_contexts':set(actual['context_refs'])=={docs[slug+'_v2_context']['context_id']+'/v2' for slug in ['governance','ontology-lifecycle']},'normalized_v3_implicit_retarget_performed':False,'C25_does_not_select_v2_map':not any(x['path']==refs['actual_map']['path'] for x in docs['C25']['admitted_artifacts']),'actual_adapter_execution_or_map_admission_verified':False};ck('v2-map-exact-old-epoch-direction-retained',mapobs['exact_endpoint_refs_match_old_v2_contexts'] and all(x[1] for x in mapchecks) and mapobs['C25_does_not_select_v2_map'])
 old=b.co.source_document(snap,source);dv=b.c.Draft202012Validator(docs['definition_schema']);shape={'errors':[{'path':'/'+('/'.join(str(y) for y in e.absolute_path)),'message':e.message} for e in dv.iter_errors(old)],'exact_source_admission_invalidated':False,'instance_migrated':False};ck('Definition-v1-v2-shape-gap-observed',len(shape['errors'])==4)
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 report={'schema_version':'definition-assurance-BoundedContext-profile/v1-candidate','status':'PASS-for-qualified-context-hypotheses-and-selected-carrier-map-index-observations','authority_effect':'none','checker_bindings':[b.ref(b.UNIT/'verify_authority_profile.py'),b.ref(b.IMPL/'contracts.py'),b.ref(b.IMPL/'ir.py'),b.ref(b.IMPL/'verifier.py')],'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','source-checks.json','comparison-selection.json']],'selected_inputs':refs,'current_type_registry_rows':len(reg['admitted_contracts']),'admitted_current_type_rows':len(current),'direct_current_definition_binding_types':[x['artifact_type_ref'] for x in direct],'current_registry_selection':row,'exact_definition_binding':binding[0],'registry_carrier_state':row['lifecycle_state'],'retained_descriptor_status':artifact['status'],'fixture_status':fixture['status'],'actual_check_count':len(checks),'actual_checks':checks,'schema_probes':probes,'negative_fixture_checks':hostiles,'offline_predecessor_schema_bindings':{'wrapper_resolved_core_URI':resolvedURI,'core_declared_id':core['$id'],'core_schema_ref':refs['predecessor_core_schema'],'external_schema_network_retrieval_enabled':False},'profiles':profiles(),'profile_context_axes':AXES,'profile_support_axes':SUPPORT,'finite_context_frames':frames(),'pure_CTX07_context_controls':pureControls,'pure_CTX07_membership_index_controls':indexControls,'context_epoch_observations':observations,'explicit_map_observation':mapobs,'historical_source_current_definition_shape':shape,'native_or_live_consumer_executed':False,'bound_package_validator_executed':False,'generator_module_or_materialization_writer_executed':False,'selected_pure_render_semantic_invariant_and_index_functions_executed':True,'generic_carrier_CTX07_context_map_or_consumer_alignment_accepted':False,'actual_context_admission_owner_transfer_or_consistency_created':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Exact source/carrier shape,selected pure functions and C25 recorded v2 context overlay;normalized v3 candidate records preserve language v2 refs and old map v2 endpoints. Fixed v2 projection references and trusted supplied digests are observed gaps. No accepted actual consistency,registry coverage,owner,consumer or whole fidelity proof.'}
 b.unchanged(context['sources']+list(refs.values())+report['checker_bindings']+report['input_refs']);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh profile differs')
 return report
def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({'status':x['status'],'profiles':len(x['profiles']),'rejected_profiles':sum(y['expected_rejection'] for y in x['profiles']),'frames':len(x['finite_context_frames']),'rejected_frames':sum(y['expected_rejection'] for y in x['finite_context_frames']),'schema_probes':len(x['schema_probes']),'schema_acceptances':sum(y['schema_accepted'] for y in x['schema_probes']),'catalog_checks':x['actual_check_count'],'pure_context_controls':len(x['pure_CTX07_context_controls']),'pure_context_acceptances':sum(y['pure_checker_accepted'] for y in x['pure_CTX07_context_controls']),'pure_index_controls':len(x['pure_CTX07_membership_index_controls'])},indent=2))
if __name__=='__main__':main()
