"""Qualified hypothetical languages and actual selected carrier/context/map observations."""
import ast,copy,json
from typing import Any
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
AXES=['language','context','context_version','model','expression','concept_disposition','owner','revision','source_epoch','map_envelope']
SUPPORT=['context_resolution','current_disposition','load_bearing_coverage','ambiguity_record','owner_governance','explicit_map','projection_boundary','consumer_conformance']
FORBIDDEN=['global_meaning','admission','owner_transfer','authority','independent_human_source','actual_claim']
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
  cases.append({'case_id':id,'profile':x,'errors':errors,'expected_rejection':reject,'expected_use':use,'use_allowed_under_hypotheses':allowed,'actual_runtime_execution':False,'actual_context_concept_owner_meaning_or_consumer_verified':False,'source_fidelity_accepted':False})
 add('qualified-owned-context-language',lambda x:None)
 for n in AXES:add('wrong-query-'+n,lambda x,n=n:x['query'].update({n:'hyp:wrong'}),True,False)
 for n in SUPPORT:add('missing-'+n,lambda x,n=n:x['supports'].update({n:False}),True,False)
 for n in FORBIDDEN:add('forbidden-'+n,lambda x,n=n:x.update({n:True}),True,False)
 add('stale-current-binding-request',lambda x:x.update(bindings_current=False),True,False)
 add('stale-binding-with-no-current-use',lambda x:x.update(bindings_current=False,request_current=False),False,False)
 return cases
def frames():
 base={'source_before':{'context':'hyp:c','version':'hyp:v','owner':'hyp:o','meaning':'hyp:d'},'source_after':{'context':'hyp:c','version':'hyp:v','owner':'hyp:o','meaning':'hyp:d'},'target_context':'hyp:t','bridge_source':'hyp:c','bridge_target':'hyp:t','has_explicit_map':True,'reuse':True,'same_spelling':True,'equivalence_inferred_from_spelling':False,'unresolved_before':True,'unresolved_after':True,'has_owner_resolution':False,'owner_transfer':False,'authority_transfer':False,'independent_human_source':False,'actual_claim':False};rows=[]
 def add(id,change,reject=False):
  x=copy.deepcopy(base);change(x);errors=[]
  for n in x['source_before']:
   if x['source_before'][n]!=x['source_after'][n]:errors.append('source-envelope-changed:'+n)
  if x['reuse'] and (not x['has_explicit_map'] or x['bridge_source']!=x['source_before']['context'] or x['bridge_target']!=x['target_context']):errors.append('invalid-explicit-map')
  if x['equivalence_inferred_from_spelling']:errors.append('spelling-promoted-to-meaning')
  if x['unresolved_before'] and not x['unresolved_after'] and not x['has_owner_resolution']:errors.append('silent-unresolved-collapse')
  for n in ['owner_transfer','authority_transfer','independent_human_source','actual_claim']:
   if x[n]:errors.append('forbidden:'+n)
  assert bool(errors)==reject
  rows.append({'case_id':id,'frame':x,'errors':errors,'expected_rejection':reject,'actual_runtime_execution':False,'universal_meaning_revision_or_authority_proof':False})
 add('explicit-reuse-retains-source-meaning-owner-envelope',lambda x:None)
 add('no-reuse-no-map-required',lambda x:x.update(reuse=False,has_explicit_map=False))
 add('owner-recorded-resolution-hypothesis',lambda x:x.update(unresolved_after=False,has_owner_resolution=True))
 for n in base['source_before']:add('changed-upstream-'+n,lambda x,n=n:x['source_after'].update({n:'hyp:changed'}),True)
 add('missing-explicit-map',lambda x:x.update(has_explicit_map=False),True)
 for n in ['bridge_source','bridge_target']:add('wrong-'+n,lambda x,n=n:x.update({n:'hyp:wrong'}),True)
 add('same-label-promoted-to-meaning',lambda x:x.update(equivalence_inferred_from_spelling=True),True)
 add('unresolved-silently-collapsed',lambda x:x.update(unresolved_after=False),True)
 for n in ['owner_transfer','authority_transfer','independent_human_source','actual_claim']:add('forbidden-'+n,lambda x,n=n:x.update({n:True}),True)
 return rows
def extracted(raw,path,names,namespace):
 tree=ast.parse(raw);selected=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in names];assert {x.name for x in selected}==set(names);exec(compile(ast.Module(body=selected,type_ignores=[]),str(path),'exec'),namespace);return namespace
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();source=load('t.json')['payload']['source'];rp=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json';reg=json.loads(rp.read_bytes());current=[x for x in reg['admitted_contracts'] if x['lifecycle_state']=='admitted-current'];direct=[x for x in current if source['version_ref'] in x['semantic_definition_refs']];assert [x['artifact_type_ref'] for x in direct]==['cal.artifact-type.ubiquitous-language/v2'];row=direct[0];pkg=(b.ROOT/row['artifact_path']).parent;artifact=json.loads((pkg/'artifact.json').read_bytes())
 paths={'registry':rp,'descriptor':pkg/'artifact.json','schema':b.ROOT/row['schema_path'],'fixture':pkg/'fixtures/valid/language.json','artifact_projection':pkg/'ARTIFACT.md','fixture_projection':pkg/'fixtures/valid/LANGUAGE.md','generator':b.ROOT/artifact['source_direction']['shared_generator_path'],'wrapper':pkg/'validate.py','validator':b.ROOT/'tooling/validators/artifact_type_successor.py','predecessor_descriptor':b.ROOT/artifact['predecessor_contract']['path'],'predecessor_schema':b.ROOT/artifact['predecessor_contract']['schema_path'],'predecessor_validator':b.ROOT/'tooling/validators/ctx01_artifact_type.py','root_descriptor':b.ROOT/artifact['artifact_type_root_binding']['path'],'definition_schema':b.ROOT/'authority/artifact-types/definition/v2/schema.json','C23':b.ROOT/'docs/decisions/0023-governance-and-ontology-lifecycle-context-promotion/decision.json','C24':b.ROOT/'docs/decisions/0024-governance-ontology-lifecycle-context-map-promotion/decision.json'}
 for slug in ['governance','ontology-lifecycle']:
  for version in ['v1','v2']:
   for kind in ['language','context']:paths[slug+'_'+version+'_'+kind]=b.ROOT/'contexts'/slug/version/(kind+'.json')
 for version in ['v1','v2']:paths['map_'+version]=b.ROOT/'contexts/maps/governance-ontology-lifecycle'/version/'map.json'
 for i,n in enumerate(artifact['validation_contract']['negative_witnesses']):paths['negative_'+str(i)]=pkg/n
 refs={n:b.ref(p) for n,p in paths.items()};raw={n:p.read_bytes() for n,p in paths.items()};docs={n:json.loads(x) for n,x in raw.items() if paths[n].suffix=='.json'};schema=docs['schema'];b.c.Draft202012Validator.check_schema(schema);validator=b.c.Draft202012Validator(schema);v1validator=b.c.Draft202012Validator(docs['predecessor_schema']);fixture=docs['fixture'];binding=artifact['semantic_definition_bindings'];checks=[]
 def ck(id,ok):checks.append({'check_id':id,'result':bool(ok)})
 ck('one-current-exact-Definition-binding',len(binding)==1 and all(binding[0][k]==source[z] for k,z in [('definition_ref','version_ref'),('path','path'),('sha256','sha256')]) and binding[0]['admission_decision_ref']=='CAL-DECISION-0018-DEFINITION-AND-CTX00-PROMOTION')
 ck('current-v2-C70-and-historical-v1-C21',row['admission_decision_ref']=='CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION' and any(x['artifact_type_ref']=='cal.artifact-type.ubiquitous-language/v1' and x['lifecycle_state']=='admitted-historical' and x['admission_decision_ref']=='CAL-DECISION-0021-CTX01-ARTIFACT-TYPE-PROMOTION' for x in reg['admitted_contracts']))
 ck('retained-descriptor-and-fixture-candidate-posture',artifact['status']==fixture['status']=='candidate-unadmitted' and artifact['authority_effect']==fixture['authority_effect']=='none');ck('registry-descriptor-schema-digests',row['artifact_sha256']==refs['descriptor']['sha256'] and row['schema_sha256']==artifact['schema_digest']==refs['schema']['sha256']);ck('root-and-predecessor-descriptor-schema-bindings',artifact['artifact_type_root_binding']['sha256']==refs['root_descriptor']['sha256'] and artifact['predecessor_contract']['sha256']==refs['predecessor_descriptor']['sha256'] and artifact['predecessor_contract']['schema_sha256']==refs['predecessor_schema']['sha256']);ck('fixture-shape-valid',not list(validator.iter_errors(fixture)))
 renderer=extracted(raw['generator'],paths['generator'],['render_artifact','render_instance'],{'json':json,'Any':Any});before=copy.deepcopy(fixture);ck('two-pure-fixture-renders-exact',renderer['render_instance'](artifact,fixture).encode()==renderer['render_instance'](artifact,fixture).encode()==raw['fixture_projection']);ck('pure-artifact-projection-exact',renderer['render_artifact'](artifact).encode()==raw['artifact_projection']);ck('render-input-preserved',fixture==before)
 definition=schema['$defs']['ubiquitousLanguage'];fields=definition['allOf'][1]['properties'];ck('closed-schema-eleven-language-required-fields',definition['unevaluatedProperties'] is False and len(definition['allOf'][1]['required'])==11);ck('v2-schema-retains-v1-classification',fields['schema_version']['const']=='cyberalchemy-lab-ubiquitous-language/v2' and fields['classification']['properties']['artifact_type_ref']['const']=='cal.artifact-type.ubiquitous-language/v1' and fixture['classification']['artifact_type_ref']=='cal.artifact-type.ubiquitous-language/v1');ck('current-binding-entry-lacks-own-context-version-fields',set(fields['expression_bindings']['items']['properties'])=={'expression','concept_ref','disposition'});ck('binding-array-without-uniqueness-contract','uniqueItems' not in fields['expression_bindings']);ck('empty-relations-and-ambiguity-permitted',all('minItems' not in fields[n] for n in ['relation_bindings','ambiguity_records']));ck('closed-empty-type-relation-surface',artifact['relation_roles']==artifact['allowed_relation_kinds']==[])
 hostiles=[]
 for n in paths:
  if n.startswith('negative_'):
   errors=[e.message for e in validator.iter_errors(docs[n])];hostiles.append({'fixture_ref':refs[n],'schema_rejected':bool(errors),'errors':errors})
 ck('both-hostiles-rejected',len(hostiles)==2 and all(x['schema_rejected'] for x in hostiles))
 probes=[]
 def probe(id,change,accept):
  x=copy.deepcopy(fixture);change(x);errors=[{'path':'/'+('/'.join(str(y) for y in e.absolute_path)),'message':e.message} for e in validator.iter_errors(x)];ok=not errors;assert ok==accept,(id,errors);probes.append({'case_id':id,'schema_accepted':ok,'errors':errors,'actual_context_concept_owner_meaning_or_admission_verified':False})
 for n in definition['allOf'][1]['required']:probe('missing-'+n,lambda x,n=n:x.pop(n),False)
 for n in ['language_id','bounded_context_ref','revision_state','challenge_route']:probe('unresolved-'+n,lambda x,n=n:x.update({n:'unresolved:'+n}),True)
 for n in ['concept_refs','owner_refs','interpretation_rules','usage_surfaces']:
  probe('empty-required-'+n,lambda x,n=n:x.update({n:[]}),False);probe('duplicate-required-'+n,lambda x,n=n:x[n].append(x[n][0]),False)
 for n in ['relation_bindings','ambiguity_records']:probe('empty-optional-'+n,lambda x,n=n:x.update({n:[]}),True)
 probe('same-expression-identical-duplicate-record',lambda x:x['expression_bindings'].append(copy.deepcopy(x['expression_bindings'][0])),True)
 probe('same-expression-conflicting-current-concepts',lambda x:x['expression_bindings'].append({'expression':'Example','concept_ref':'unresolved:another-concept','disposition':'current'}),True)
 probe('concept-not-in-owned-concept-refs',lambda x:x['expression_bindings'][0].update(concept_ref='unresolved:unlisted-concept'),True)
 probe('unresolved-binding-still-names-placeholder-concept',lambda x:x['expression_bindings'][0].update(disposition='unresolved',concept_ref='unresolved:concept'),True)
 probe('currentness-unrelated-to-revision-label',lambda x:x.update(revision_state='deprecated-label'),True)
 probe('ambiguity-expression-not-in-binding-set',lambda x:x['ambiguity_records'].append({'expression':'Unknown','disposition':'explicit-but-unchecked'}),True)
 probe('cross-context-reuse-as-unchecked-interpretation-text',lambda x:x['interpretation_rules'].append('Reuse meaning from an unresolved foreign context without a map.'),True)
 probe('schema-accepts-common-understanding-claim-text',lambda x:x.update(claim_ceiling='This proves universal common understanding.'),True)
 probe('extra-binding-context-field',lambda x:x['expression_bindings'][0].update(bounded_context_ref='unresolved:context'),False)
 probe('extra-binding-version-field',lambda x:x['expression_bindings'][0].update(context_version='v2'),False)
 probe('unresolved-null-concept',lambda x:x['expression_bindings'][0].update(concept_ref=None,disposition='unresolved'),False)
 probe('empty-binding-concept',lambda x:x['expression_bindings'][0].update(concept_ref=''),False)
 probe('bad-binding-disposition',lambda x:x['expression_bindings'][0].update(disposition='active'),False)
 probe('empty-expression-bindings',lambda x:x.update(expression_bindings=[]),False)
 probe('v2-classification-in-v2-schema',lambda x:x['classification'].update(artifact_type_ref='cal.artifact-type.ubiquitous-language/v2'),False)
 probe('implicit-authority-effect',lambda x:x.update(authority_effect='grant'),False)
 probe('schema-status-admitted',lambda x:x.update(status='admitted'),False)
 pure=extracted(raw['predecessor_validator'],paths['predecessor_validator'],['semantic_invariants'],{})['semantic_invariants'];pureControls=[]
 def purecase(id,change,expected):
  x=copy.deepcopy(fixture);change(x);before=copy.deepcopy(x);results=pure('ubiquitous-language',x);ok=all(z[1] for z in results);assert ok==expected,id;pureControls.append({'case_id':id,'input':x,'pure_checker_accepted':ok,'schema_accepted':not list(validator.iter_errors(x)),'input_preserved':x==before,'results':results,'package_validator_executed':False,'actual_meaning_or_owner_or_consumer_verified':False})
 purecase('baseline-unique-expression',lambda x:None,True)
 purecase('duplicate-same-expression-same-disposition',lambda x:x['expression_bindings'].append(copy.deepcopy(x['expression_bindings'][0])),False)
 purecase('duplicate-same-expression-conflicting-disposition',lambda x:x['expression_bindings'].append({'expression':'Example','concept_ref':'unresolved:another','disposition':'current'}),False)
 purecase('duplicate-expression-deprecated-second-record',lambda x:x['expression_bindings'].append({'expression':'Example','concept_ref':x['concept_refs'][0],'disposition':'deprecated'}),False)
 purecase('unlisted-current-concept-not-resolved-by-pure-checker',lambda x:x['expression_bindings'][0].update(concept_ref='unresolved:unlisted'),True)
 purecase('unresolved-placeholder-concept-permitted',lambda x:x['expression_bindings'][0].update(concept_ref='unresolved:concept',disposition='unresolved'),True)
 purecase('case-distinct-expression-records-permitted',lambda x:x['expression_bindings'].append({'expression':'example','concept_ref':x['concept_refs'][0],'disposition':'current'}),True)
 purecase('distinct-label-same-concept-permitted',lambda x:x['expression_bindings'].append({'expression':'Synonym','concept_ref':x['concept_refs'][0],'disposition':'current'}),True)
 purecase('unresolved-context-not-resolved-by-pure-checker',lambda x:x.update(bounded_context_ref='unresolved:context'),True)
 purecase('empty-binding-set-passes-only-pure-checker',lambda x:x.update(expression_bindings=[]),True)
 ck('pure-CTX01-unique-expression-scope-observed',len(pureControls)==10 and all(x['input_preserved'] for x in pureControls))
 successor=raw['validator'].decode();ck('successor-package-source-lacks-expression-resolution-invariant',all(n not in successor for n in ['expression-binding-unique','expression_bindings','semantic_invariants']))
 observed=[]
 for slug in ['governance','ontology-lifecycle']:
  for version in ['v1','v2']:
   name=slug+'_'+version+'_language';lang=docs[name];ctx=docs[slug+'_'+version+'_context'];records=[x for x in docs['C23']['admitted_artifacts'] if x['path']==refs[name]['path']];recordBound=any(x['sha256']==refs[name]['sha256'] and x['decision_overlay_status']=='admitted' for x in records);bindings=lang['expression_bindings'];obs={'case_id':slug+'-'+version,'language_ref':refs[name],'context_ref':refs[slug+'_'+version+'_context'],'language_id':lang['language_id'],'bounded_context_ref':lang['bounded_context_ref'],'retained_status':lang['status'],'revision_state':lang['revision_state'],'owner_refs':lang['owner_refs'],'schema_v1_valid':not list(v1validator.iter_errors(lang)),'schema_v2_valid':not list(validator.iter_errors(lang)),'reciprocal_context_language_refs':lang['bounded_context_ref']==ctx['context_id']+'/'+version and ctx['ubiquitous_language_ref']==lang['language_id']+'/'+version,'counts':{k:len(lang[k]) for k in ['concept_refs','expression_bindings','relation_bindings','interpretation_rules','usage_surfaces','ambiguity_records']},'current_expression_labels_unique':len({x['expression'] for x in bindings if x['disposition']=='current'})==sum(x['disposition']=='current' for x in bindings),'binding_concepts_listed':all(x['concept_ref'] in lang['concept_refs'] for x in bindings),'C23_exact_recorded_admission_overlay':recordBound,'actual_consumer_conformance_or_shared_meaning_verified':False};observed.append(obs)
 ck('four-selected-language-context-pairs-structurally-linked',len(observed)==4 and all(x['schema_v1_valid'] and not x['schema_v2_valid'] and x['reciprocal_context_language_refs'] and x['current_expression_labels_unique'] and x['binding_concepts_listed'] for x in observed));ck('C23-v1-overlays-match-and-v2-not-selected-by-that-decision',[x['C23_exact_recorded_admission_overlay'] for x in observed]==[True,False,True,False])
 overlap=[]
 for version in ['v1','v2']:
  g=docs['governance_'+version+'_language'];o=docs['ontology-lifecycle_'+version+'_language'];a={x['expression']:x['concept_ref'] for x in g['expression_bindings']};z={x['expression']:x['concept_ref'] for x in o['expression_bindings']};overlap.append({'version':version,'shared_exact_expression_labels':[{'expression':label,'Governance_concept_ref':a[label],'OntologyLifecycle_concept_ref':z[label],'concept_ref_strings_equal':a[label]==z[label]} for label in sorted(a.keys()&z.keys())],'actual_meaning_equivalence_or_mapping_completeness_verified':False})
 maps=[]
 for version in ['v1','v2']:
  d=docs['map_'+version];rel=d['relationships'][0];maps.append({'version':version,'map_ref':refs['map_'+version],'retained_status':d['status'],'context_refs':d['context_refs'],'relationships':d['relationships'],'endpoint_refs_in_selected_context_set':rel['source_context_ref'] in d['context_refs'] and rel['target_context_ref'] in d['context_refs'],'authority_boundary_text_retained':rel['authority_boundary'],'translation_refs_retained':rel['translation_refs'],'actual_anticorruption_adapter_or_authority_enforcement_verified':False})
 ck('two-explicit-versioned-maps-with-closed-distinct-endpoints',all(x['endpoint_refs_in_selected_context_set'] and x['relationships'][0]['source_context_ref']!=x['relationships'][0]['target_context_ref'] and x['translation_refs_retained'] and x['authority_boundary_text_retained'] for x in maps));ck('C24-exact-v1-map-bytes-bound',docs['C24']['admitted_map']['sha256']==refs['map_v1']['sha256'] and docs['C24']['admitted_map']['path']==refs['map_v1']['path'])
 currentDef=b.c.Draft202012Validator(docs['definition_schema']);old=b.co.source_document(snap,source);shape={'current_schema_accepted':not list(currentDef.iter_errors(old)),'errors':[{'path':'/'+('/'.join(str(y) for y in e.absolute_path)),'message':e.message} for e in currentDef.iter_errors(old)],'exact_source_admission_invalidated':False,'instance_migrated':False};ck('Definition-v1-current-v2-shape-gap-observed',len(shape['errors'])==4)
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 report={'schema_version':'definition-assurance-UbiquitousLanguage-profile/v1-candidate','status':'PASS-for-qualified-language-hypotheses-and-selected-carrier-context-map-pure-checker-observations','authority_effect':'none','checker_bindings':[b.ref(b.UNIT/'verify_authority_profile.py'),b.ref(b.IMPL/'contracts.py'),b.ref(b.IMPL/'ir.py'),b.ref(b.IMPL/'verifier.py')],'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','source-checks.json','comparison-selection.json']],'selected_inputs':refs,'current_type_registry_rows':len(reg['admitted_contracts']),'admitted_current_type_rows':len(current),'direct_current_definition_binding_types':[x['artifact_type_ref'] for x in direct],'exact_definition_binding':binding[0],'current_registry_selection':row,'registry_carrier_state':row['lifecycle_state'],'retained_descriptor_status':artifact['status'],'fixture_status':fixture['status'],'actual_check_count':len(checks),'actual_checks':checks,'schema_probes':probes,'negative_fixture_checks':hostiles,'profiles':profiles(),'profile_context_axes':AXES,'profile_support_axes':SUPPORT,'finite_language_frames':frames(),'pure_CTX01_expression_controls':pureControls,'context_language_observations':observed,'cross_context_label_observations':overlap,'explicit_map_observations':maps,'native_or_live_consumer_executed':False,'bound_package_validator_executed':False,'generator_module_or_materialization_writer_executed':False,'selected_pure_render_and_semantic_invariant_functions_executed':True,'generic_carrier_CTX01_context_map_or_consumer_alignment_accepted':False,'actual_language_admission_owner_transfer_or_shared_understanding_created':False,'new_authorities_or_relations_created':0,'historical_source_current_definition_shape':shape,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Selected actual schema/catalog/pure projections and CTX01 uniqueness function;exact C23 v1 language/context and C24 v1 map recorded overlays;later candidate v2 language/map bytes. No private source recovery,live consumer/adapter/package-validator execution,actual concept/owner/shared-meaning proof,accepted source fidelity or joint closure.'}
 b.unchanged(context['sources']+list(refs.values())+report['checker_bindings']+report['input_refs']);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh profile differs')
 return report
def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({'status':x['status'],'profiles':len(x['profiles']),'rejected_profiles':sum(y['expected_rejection'] for y in x['profiles']),'frames':len(x['finite_language_frames']),'rejected_frames':sum(y['expected_rejection'] for y in x['finite_language_frames']),'schema_probes':len(x['schema_probes']),'schema_acceptances':sum(y['schema_accepted'] for y in x['schema_probes']),'catalog_checks':x['actual_check_count'],'pure_expression_controls':len(x['pure_CTX01_expression_controls']),'pure_expression_acceptances':sum(y['pure_checker_accepted'] for y in x['pure_CTX01_expression_controls'])},indent=2))
if __name__=='__main__':main()
