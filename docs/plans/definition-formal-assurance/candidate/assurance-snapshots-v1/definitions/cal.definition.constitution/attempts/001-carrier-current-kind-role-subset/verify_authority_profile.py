"""Constitution context hypotheses, tuple/carrier gaps, roles and documentary observations."""
import copy,itertools,json,re,types
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
AXES=['constitution','version','scope','subject','subject_kind','selector','owner','owner_route','authority_level','precedence','composition','rule','mode','validation_binding','downstream_effect','challenge_route','retirement_rule']
SUPPORT=['genus_tuple_field_map','identity_exact_version','scope_selector_kind_map','owner_authentication_authorization','exact_adoption_decision','promotion','precedence_composition','rule_mode_binding','effect_boundary','retirement_history','source_fidelity']
KINDS=['artifact','task_or_workflow','repository_owned_agent_action','system_operation_or_state_transition','validation_surface','authority_movement'];MODES=['deterministic','review','hybrid','none-yet']
def baseline():
 c={n:'hyp:'+n for n in AXES};c.update(subject_kind='artifact',mode='none-yet')
 return {'context':c,'query':copy.deepcopy(c),'qualified':False,'support':dict.fromkeys(SUPPORT),'promoted':True,'owner_authorized':True,'owner_adoption':None,'in_scope':True,'selector_matches':True,'higher_precedence_block':False,'candidate':True,'selected':True,'context_loaded':True,'binding_enabled':False,'actual_adoption_or_application_verified':False,'actual_validation_or_effect_verified':False,'source_owner_accepted':False}
def supported(p):p.update(qualified=True,support={n:'hyp:independent-'+n for n in SUPPORT},owner_adoption={'decision':'hyp:decision',**{n:p['context'][n] for n in ['constitution','version','scope','owner','owner_route']}})
def evaluate(p):
 es=[]
 def ck(ok,msg):
  if not ok:es.append(msg)
 ck(set(p)==set(baseline()),'closed selected Constitution profile')
 ck(set(p['context'])==set(p['query'])==set(AXES) and all(p['context'].values()) and all(p['query'].values()),'17 exact context axes')
 ck(set(p['support'])==set(SUPPORT),'11 independent support axes')
 if p['qualified']:ck(all(p['support'].values()),'independent tuple/version/owner/scope/selector/kind/mode/precedence/effect/retirement/fidelity hypotheses')
 ck(p['context']['subject_kind'] in KINDS and p['context']['mode'] in MODES,'six named subject kinds and four mode hypotheses')
 for n in ['qualified','promoted','owner_authorized','in_scope','selector_matches','higher_precedence_block','candidate','selected','context_loaded','binding_enabled','actual_adoption_or_application_verified','actual_validation_or_effect_verified','source_owner_accepted']:ck(type(p[n]) is bool,'Boolean '+n)
 if p['context']['mode']=='none-yet':ck(p['binding_enabled'] is False,'none-yet does not activate validation')
 d=p['owner_adoption']
 if d is not None:ck(set(d)=={'decision','constitution','version','scope','owner','owner_route'} and all(d.values()),'separate exact-version/scope owner adoption hypothesis')
 ck(p['actual_adoption_or_application_verified'] is False and p['actual_validation_or_effect_verified'] is False and p['source_owner_accepted'] is False,'no real adoption/application/check/effect or source acceptance generated')
 adoption=bool(d and all(d[n]==p['context'][n] for n in ['constitution','version','scope','owner','owner_route']))
 applies=None if es else bool(p['qualified'] and p['context']==p['query'] and p['promoted'] and p['owner_authorized'] and adoption and p['in_scope'] and p['selector_matches'] and not p['higher_precedence_block'])
 return es,{'application_under_stronger_hypotheses':applies,'actual_owner_or_application_verified':False,'actual_validation_or_effect_verified':False,'source_fidelity_accepted':False}
def profiles():
 rows=[]
 def add(id,change,bad=False,applies=False):
  p=baseline();change(p);es,obs=evaluate(p)
  if bool(es)!=bad or obs['application_under_stronger_hypotheses']!=(None if bad else applies):raise ValueError('Unexpected Constitution profile '+id)
  rows.append({'case_id':id,'profile':p,'errors':es,'expected_rejection':bad,'expected_application':None if bad else applies,'observations':obs,'actual_runtime_execution':False})
 add('raw-complete-candidate-selected-loaded-no-qualified-application',lambda p:None)
 add('qualified-exact-adoption-promoted-in-scope-selector-match-none-yet',supported,applies=True)
 for n in AXES:add('qualified-context-does-not-transfer-'+n,lambda p,n=n:supported(p) or p['query'].update({n:'hyp:other-'+n}))
 for n in SUPPORT:add('qualification-missing-'+n,lambda p,n=n:supported(p) or p['support'].update({n:None}),bad=True)
 for n in ['constitution','version','scope','owner','owner_route']:add('adoption-of-other-'+n,lambda p,n=n:supported(p) or p['owner_adoption'].update({n:'hyp:other-'+n}))
 for n in ['promoted','owner_authorized','in_scope','selector_matches']:add('missing-application-condition-'+n,lambda p,n=n:supported(p) or p.update({n:False}))
 add('qualified-owner-record-not-applied-if-none',lambda p:supported(p) or p.update(owner_adoption=None))
 add('higher-precedence-block-under-stronger-hypothesis',lambda p:supported(p) or p.update(higher_precedence_block=True))
 for kind in KINDS:add('named-subject-kind-'+kind,lambda p,kind=kind:supported(p) or p['context'].update(subject_kind=kind) or p['query'].update(subject_kind=kind),applies=True)
 for mode in MODES:add('allowed-mode-without-implied-actual-check-'+mode,lambda p,mode=mode:supported(p) or p['context'].update(mode=mode) or p['query'].update(mode=mode),applies=True)
 add('independent-binding-hypothesis-with-no-actual-check',lambda p:supported(p) or p['context'].update(mode='deterministic') or p['query'].update(mode='deterministic') or p.update(binding_enabled=True),applies=True)
 for n in ['candidate','selected','context_loaded']:add('application-does-not-depend-on-'+n+'-label',lambda p,n=n:supported(p) or p.update({n:False}),applies=True)
 add('none-yet-cannot-imply-active-binding',lambda p:supported(p) or p.update(binding_enabled=True),bad=True)
 add('unknown-subject-kind',lambda p:p['context'].update(subject_kind='unknown'),bad=True)
 add('unknown-validation-mode',lambda p:p['context'].update(mode='unknown'),bad=True)
 for n in ['actual_adoption_or_application_verified','actual_validation_or_effect_verified','source_owner_accepted']:add('actual-claim-not-generated-'+n,lambda p,n=n:p.update({n:True}),bad=True)
 return rows
def frames():
 rows=[]
 def add(id,change,bad=False):
  f={'operation':'select','constitution_before':'hyp:c1','constitution_after':'hyp:c1','version_before':'hyp:v1','version_after':'hyp:v1','scope_before':'hyp:scope','scope_after':'hyp:scope','tuple_before':'hyp:bytes1','tuple_after':'hyp:bytes1','original_retained':True,'promoted':True,'exact_owner_adoption':None,'in_scope':True,'selector_matches':True,'mode':'none-yet','binding_enabled':False,'subject_effects':[],'actual_transition_verified':False};change(f);es=[]
  def ck(ok,msg):
   if not ok:es.append(msg)
  ck(f['operation'] in ['select','load-context','render','declare-mode','apply','retire'],'selected operation')
  ck(all(f[n+'_before']==f[n+'_after'] for n in ['constitution','version','scope','tuple']) and f['original_retained'] is True,'exact original Constitution version/scope/tuple/history retained')
  ck(f['mode'] in MODES and (f['mode']!='none-yet' or f['binding_enabled'] is False),'mode/binding hypotheses')
  if f['operation']=='apply':ck(f['promoted'] and bool(f['exact_owner_adoption']) and f['in_scope'] and f['selector_matches'],'promoted exact owner adoption scope/selector hypotheses')
  if f['operation']=='retire':ck(bool(f['exact_owner_adoption']),'retirement owner hypothesis separate from selection')
  ck(not f['subject_effects'] and f['actual_transition_verified'] is False,'no automatic actual subject effect or real transition generated')
  if bool(es)!=bad:raise ValueError('Unexpected Constitution frame '+id)
  rows.append({'case_id':id,'frame':f,'errors':es,'expected_rejection':bad,'universal_temporal_proof':False,'actual_runtime_execution':False})
 for op in ['select','load-context','render','declare-mode']:add(op+'-no-automatic-effect',lambda f,op=op:f.update(operation=op))
 add('apply-under-exact-hypotheses-none-yet-no-check',lambda f:f.update(operation='apply',exact_owner_adoption='hyp:separate-owner-decision'))
 add('retirement-needs-separate-owner-and-history-hypothesis',lambda f:f.update(operation='retire',exact_owner_adoption='hyp:retirement-owner-decision'))
 for n,value in [('constitution_after','hyp:other'),('version_after','hyp:v2'),('scope_after','hyp:other'),('tuple_after','hyp:changed'),('original_retained',False),('subject_effects',['hyp:automatic-effect']),('actual_transition_verified',True),('binding_enabled',True)]:add('selection-cannot-change-or-create-'+n,lambda f,n=n,value=value:f.update({n:value}),True)
 for n,value in [('promoted',False),('exact_owner_adoption',None),('in_scope',False),('selector_matches',False)]:add('apply-missing-'+n,lambda f,n=n,value=value:f.update(operation='apply',exact_owner_adoption='hyp:owner-decision') or f.update({n:value}),True)
 add('retirement-without-owner-hypothesis',lambda f:f.update(operation='retire'),True)
 return rows
RELATED=['constitution','decision','policy','authority-claim','authority-boundary']
def conditional_endpoint_kinds(value):
 if isinstance(value,dict):
  k=value.get('properties',{}).get('kind',{});return ([k['const']] if isinstance(k,dict) and isinstance(k.get('const'),str) else [])+sum([conditional_endpoint_kinds(x) for x in value.values()],[])
 if isinstance(value,list):return sum([conditional_endpoint_kinds(x) for x in value],[])
 return []
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();root=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries';paths={'type_registry':root/'artifact-type-registry.json','kind_registry':root/'relation-kind-registry.json','root_descriptor':b.ROOT/'authority/artifact-types/artifact-type/v2/artifact.json'};reg=json.loads(paths['type_registry'].read_bytes());kr=json.loads(paths['kind_registry'].read_bytes());current=[x for x in reg['admitted_contracts'] if x['lifecycle_state']=='admitted-current'];selected={}
 for semantic in RELATED+['typed-relation','definition']:
  matches=[x for x in current if x['semantic_kind']==semantic]
  if len(matches)!=1:raise ValueError('Ambiguous carrier '+semantic)
  row=matches[0];selected[semantic]=row;folder=(b.ROOT/row['artifact_path']).parent;a=json.loads((folder/'artifact.json').read_bytes());paths[semantic+'_descriptor']=folder/'artifact.json';paths[semantic+'_schema']=b.ROOT/row['schema_path'];paths[semantic+'_fixture']=folder/a['validation_contract']['positive_witness']
  if semantic in RELATED:
   paths[semantic+'_generator']=b.ROOT/a['source_direction']['shared_generator_path'];paths[semantic+'_validator']=b.ROOT/a['validation_contract']['shared_validator_path'];paths[semantic+'_artifact_projection']=folder/'ARTIFACT.md';paths[semantic+'_fixture_projection']=folder/a['validation_contract']['positive_projection']
   for relative in a['validation_contract']['negative_witnesses']:paths[semantic+'_negative_'+b.Path(relative).stem]=folder/relative
  if semantic=='definition':
   for relative in a['validation_contract']['negative_witnesses']:paths[semantic+'_negative_'+b.Path(relative).stem]=folder/relative
 refs={n:b.ref(q) for n,q in paths.items()};raws={n:q.read_bytes() for n,q in paths.items()};docs={n:json.loads(raws[n]) for n,q in paths.items() if q.suffix=='.json'};checks=[]
 def ck(id,value):checks.append({'check_id':id,'result':bool(value)})
 source=load('t.json')['payload']['source'];direct=[x['artifact_type_ref'] for x in current if source['version_ref'] in x['semantic_definition_refs']];binding=docs['constitution_descriptor']['semantic_definition_bindings'][0];ck('dedicated-current-exact-Constitution-binding',direct==['cal.artifact-type.constitution/v1'] and binding['definition_ref']==source['version_ref'] and binding['path']==source['path'] and binding['sha256']==source['sha256'])
 observations=[];negatives=[];probes=[];lifecycle=[]
 for semantic,row in selected.items():
  artifact=docs[semantic+'_descriptor'];schema=docs[semantic+'_schema'];fixture=docs[semantic+'_fixture'];validator=b.c.Draft202012Validator(schema);b.c.Draft202012Validator.check_schema(schema);ck(semantic+'-exact-current-descriptor-schema',row['artifact_sha256']==refs[semantic+'_descriptor']['sha256'] and row['schema_sha256']==refs[semantic+'_schema']['sha256']);ck(semantic+'-positive-fixture-shape-valid',not list(validator.iter_errors(fixture)))
  for name in [n for n in paths if n.startswith(semantic+'_negative_')]:
   errors=list(validator.iter_errors(docs[name]));negatives.append({'semantic_kind':semantic,'path':refs[name]['path'],'schema_rejected':bool(errors),'errors':[x.message for x in errors]})
  if semantic in RELATED:
   module=types.ModuleType('_pure_'+semantic);exec(compile(raws[semantic+'_generator'],str(paths[semantic+'_generator']),'exec'),module.__dict__);before=copy.deepcopy([artifact,fixture]);ck(semantic+'-declared-generator-validator-root-bindings',artifact['source_direction']['shared_generator_sha256']==refs[semantic+'_generator']['sha256'] and artifact['validation_contract']['shared_validator_sha256']==refs[semantic+'_validator']['sha256'] and artifact['artifact_type_root_binding']['sha256']==refs['root_descriptor']['sha256']);ck(semantic+'-two-exact-artifact-renders',module.render_artifact(artifact).encode()==module.render_artifact(artifact).encode()==raws[semantic+'_artifact_projection']);ck(semantic+'-two-exact-fixture-renders',module.render_instance(artifact,fixture).encode()==module.render_instance(artifact,fixture).encode()==raws[semantic+'_fixture_projection']);ck(semantic+'-render-inputs-preserved',before==[artifact,fixture])
   for id,change,expected in [('unresolved-owner-scope',lambda x:x.update(owner_ref='absent:owner',scope_ref='absent:scope'),True),('unknown-kind-in-selected-carrier',lambda x:x.update(kind='unknown-authority-kind'),False),('grant-authority-effect',lambda x:x.update(authority_effect='grant'),False),('unrecognized-top-level-authority-kind-field',lambda x:x.update(authority_kind='unknown-authority-kind'),False)]:
    candidate=copy.deepcopy(fixture);change(candidate);errors=list(validator.iter_errors(candidate));accepted=not errors
    if accepted!=expected:raise ValueError('Unexpected carrier probe '+semantic+' '+id)
    probes.append({'semantic_kind':semantic,'case_id':id,'schema_accepted':accepted,'record':candidate,'errors':[x.message for x in errors],'real_adoption_or_reference_resolution_verified':False})
   for state in ['candidate','active','historical','retired']:
    candidate=copy.deepcopy(fixture);candidate['lifecycle_state']=state;errors=list(validator.iter_errors(candidate));lifecycle.append({'semantic_kind':semantic,'lifecycle_state':state,'schema_accepted':not errors,'record':candidate,'actual_posture_grant_or_runtime_verified':False})
  observations.append({'semantic_kind':semantic,'artifact_type_ref':row['artifact_type_ref'],'fixture_shape_valid':True,'declared_validator_executed':False,'whole_Constitution_alignment_verified':False,'actual_adoption_application_or_enforcement_verified':False})
 ck('29-selected-hostile-fixtures-reject',len(negatives)==29 and all(x['schema_rejected'] for x in negatives));ck('20-related-lifecycle-shapes-not-actual-lifecycle-or-grants',len(lifecycle)==20 and all(x['schema_accepted'] for x in lifecycle))
 definition=docs['definition_schema'];selected_source=json.loads((b.ROOT/source['path']).read_bytes());errors=list(b.c.Draft202012Validator(definition).iter_errors(selected_source));current_shape={'source_schema_version':selected_source['schema_version'],'source_artifact_type_ref':selected_source['classification']['artifact_type_ref'],'selected_current_definition_type':selected['definition']['artifact_type_ref'],'current_schema_accepted':not errors,'errors':[{'path':'/'+('/'.join(map(str,x.path))),'message':x.message} for x in errors],'instance_migrated':False,'exact_source_admission_invalidated':False};ck('admitted-Definition-v1-source-does-not-conform-to-current-Definition-v2-shape',bool(errors) and {x['path'] for x in current_shape['errors']}=={'/schema_version','/classification/artifact_type_ref','/schema_ref','/source_direction/generator_ref'})
 field=definition['properties']['classification'];classification={'semantic_kind':field['properties']['semantic_kind'],'authority_kind':field['properties']['authority_kind'],'artifact_type_ref':field['properties']['artifact_type_ref'],'normalized_wrapper_mentions_type_definition':'type.definition' in selected_source['voices']['scientific_formal']['normative_statement'],'wrapper_to_record_or_legacy_authority_kind_map_accepted':False};ck('current-definition-classification-has-distinct-fixed-type-and-semantic-authority-axes',classification['semantic_kind']=={'const':'definition'} and classification['authority_kind']=={'const':'semantic-authority'} and classification['artifact_type_ref']=={'const':'cal.artifact-type.definition/v2'} and classification['normalized_wrapper_mentions_type_definition'])
 schema_row=(b.UNIT/'legacy-schema-row-context.md').read_text();instance=(b.UNIT/'legacy-candidate-constitution-context.md').read_text();model_context=(b.UNIT/'legacy-model-context.md').read_text();tuple_match=re.search(r'Constitution = \(([^)]+)\)',schema_row);tuple_fields=[x.strip() for x in tuple_match.group(1).split(',')] if tuple_match else [];ck('documentary-fifteen-field-tuple-exact-and-not-activated',tuple_fields==b.FIELDS and 'tracked (documentary)' in schema_row and 'no constitution or validator activation' in schema_row);ck('referenced-legacy-Constitution-kind-not-an-instance-grant','| [Constitution](definitions/DEFINITIONS.md#cav2-d58-constitution) | constitution-governance |' in model_context)
 rule_ids=re.findall(r'^### (CAV2-C\d+)\..*$',instance,re.M);mode_lines=re.findall(r'^Validation mode: (.*)$',instance,re.M);mode_counts={n:mode_lines.count(n) for n in MODES};ck('legacy-candidate-seventeen-rules-eight-review-nine-hybrid-no-activation',len(rule_ids)==len(mode_lines)==17 and len(set(rule_ids))==17 and mode_counts=={'deterministic':0,'review':8,'hybrid':9,'none-yet':0} and 'Status: candidate' in instance and 'Selectors: `cyberAlchemy-v2/**`' in instance and 'Status: OPEN.' in instance)
 legacy_observations={'rule_ids':rule_ids,'validation_mode_lines':mode_lines,'mode_counts':mode_counts,'candidate_status_recorded':True,'scope_selector_literal':'cyberAlchemy-v2/**','explicit_exact_instance_version_field_recorded':bool(re.search(r'^Version:',instance,re.M)),'documentary_schema_tuple_fields':tuple_fields,'candidate_instance_adopted_or_rules_validated':False,'complete_instance_schema_validation_performed':False,'imported_rules_or_runtime_instructions':False}
 sv=b.c.Draft202012Validator(docs['constitution_schema']);fixture=docs['constitution_fixture'];special=[]
 cases=[('unresolved-governed-scope',lambda x:x['payload'].update(governed_scope_ref='absent:scope'),True),('unresolved-amendment-policy',lambda x:x['payload'].update(amendment_policy_ref='absent:policy'),True),('unresolved-rule',lambda x:x['payload'].update(rule_refs=['absent:rule']),True),('unresolved-invariant',lambda x:x['payload'].update(invariant_refs=['absent:invariant']),True),('empty-rule-list',lambda x:x['payload'].update(rule_refs=[]),False),('empty-invariant-list',lambda x:x['payload'].update(invariant_refs=[]),False),('duplicate-rules',lambda x:x['payload'].update(rule_refs=['hyp:r','hyp:r']),False),('duplicate-invariants',lambda x:x['payload'].update(invariant_refs=['hyp:i','hyp:i']),False),('missing-exact-adoption-still-shape-valid',lambda x:None,True),('add-undeclared-instance-version-field',lambda x:x.update(version_ref='hyp:c@v1'),False),('add-undeclared-selector-field',lambda x:x['payload'].update(selectors=['hyp:selector']),False),('add-undeclared-adoption-field',lambda x:x['payload'].update(owner_adoption_ref='hyp:decision'),False),('add-undeclared-validation-mode-field',lambda x:x['payload'].update(validation_mode='none-yet'),False)]
 for id,change,expected in cases:
  candidate=copy.deepcopy(fixture);change(candidate);errors=list(sv.iter_errors(candidate));accepted=not errors
  if accepted!=expected:raise ValueError('Unexpected Constitution dedicated probe '+id)
  special.append({'case_id':id,'record':candidate,'schema_accepted':accepted,'errors':[x.message for x in errors],'actual_exact_adoption_selector_mode_or_application_verified':False})
 a=docs['constitution_descriptor'];rs=docs['constitution_schema']['properties']['relation_refs']['items']['properties'];declared={(x['relation_kind_ref'],x['direction'],n) for x in a['relation_roles'] for n in x['counterpart_kinds']};embedded=[]
 for kind,direction,neighbor in itertools.product(rs['relation_kind_ref']['enum'],rs['direction']['enum'],rs['counterpart_kind']['enum']):
  candidate=copy.deepcopy(fixture);candidate['relation_refs']=[{'relation_kind_ref':kind,'direction':direction,'counterpart_kind':neighbor,'counterpart_ref':'absent:counterpart'}];errors=list(sv.iter_errors(candidate));embedded.append({'relation_kind_ref':kind,'direction':direction,'counterpart_kind':neighbor,'schema_accepted':not errors,'declared_role':(kind,direction,neighbor) in declared,'actual_relation_created':False})
 ck('sixteen-embedded-combinations-five-declared-roles',len(embedded)==16 and all(x['schema_accepted'] for x in embedded) and sum(x['declared_role'] for x in embedded)==5)
 kind_paths={row['relation_kind_ref']:b.ROOT/row['instance_path'] for row in kr['entries']};kind_refs={n:b.ref(q) for n,q in kind_paths.items()};kind_docs={n:json.loads(q.read_bytes()) for n,q in kind_paths.items()};roles=[]
 for row in kr['entries']:
  id=row['relation_kind_ref'];payload=kind_docs[id]['payload'];ck('current-Kind-exact-'+id,row['lifecycle_state']=='admitted-current' and row['instance_sha256']==kind_refs[id]['sha256'] and row['exact_endpoint_pair_count']==len(payload['allowed_endpoint_pairs']))
  for pair in payload['allowed_endpoint_pairs']:
   if pair['source_kind']=='constitution':roles.append({'relation_kind_ref':id,'direction':'source','counterpart_kind':pair['target_kind']})
   if pair['target_kind']=='constitution':roles.append({'relation_kind_ref':id,'direction':'target','counterpart_kind':pair['source_kind']})
 ck('five-carrier-roles-match-current-Kind-endpoints',declared=={(x['relation_kind_ref'],x['direction'],x['counterpart_kind']) for x in roles})
 def relation_pairs(schema,id):
  def mentions(x):return isinstance(x,dict) and (x.get('const')==id or any(mentions(v) for v in x.values())) or isinstance(x,list) and any(mentions(v) for v in x)
  branches=[x for x in schema['allOf'] if 'if' in x and mentions(x['if'])]
  if len(branches)!=1:raise ValueError('Ambiguous conditional relation '+id)
  return [{'source_kind':x['properties']['source']['properties']['kind']['const'],'target_kind':x['properties']['target']['properties']['kind']['const']} for x in branches[0]['then']['properties']['payload']['oneOf']]
 gaps=[];pairs=[];tv=b.c.Draft202012Validator(docs['typed-relation_schema'])
 for id in ['relation.governed-by','relation.successor-of']:
  payload=kind_docs[id]['payload'];allowed=relation_pairs(docs['typed-relation_schema'],id);gaps.append({'relation_kind_ref':id,'current_Kind_pairs':len(payload['allowed_endpoint_pairs']),'current_TR_schema_pairs':len(allowed),'missing_TR_pairs':[x for x in payload['allowed_endpoint_pairs'] if x not in allowed],'extra_TR_pairs':[x for x in allowed if x not in payload['allowed_endpoint_pairs']],'meaning_alignment_reviewed':False});selected_pairs=payload['allowed_endpoint_pairs'] if id=='relation.governed-by' else [x for x in payload['allowed_endpoint_pairs'] if 'constitution' in x.values()]
  for pair in selected_pairs:
   candidate=copy.deepcopy(docs['typed-relation_fixture']);candidate['payload'].update(relation_kind_ref=id,source={'kind':pair['source_kind'],'ref':'absent:source','version_ref':'absent:source-v1'},target={'kind':pair['target_kind'],'ref':'absent:target','version_ref':'absent:target-v1'},qualifiers={n:'absent:qualifier' for n in payload['qualifier_contract']['required_axes']});errors=list(tv.iter_errors(candidate));accepted=not errors
   if accepted!=(pair in allowed):raise ValueError('Unexpected Kind/TR pair')
   pairs.append({'relation_kind_ref':id,'pair':pair,'record':candidate,'schema_accepted':accepted,'errors':[x.message for x in errors],'actual_qualified_adoption_application_or_succession_verified':False})
 locators={'id':'/node_id','version':None,'scope':'/payload/governed_scope_ref','subject_kinds':None,'selectors':None,'rules':'/payload/rule_refs','policies':None,'precedence':None,'composition':None,'owner_route':'/owner_ref','authority_level':None,'validation_bindings':None,'downstream_effect':None,'challenge_route':'/challenge_route','retirement_or_split_rule':None};mapping={'source_tuple_fields':b.FIELDS,'carrier_required_payload_fields':docs['constitution_schema']['properties']['payload']['required'],'possible_locators_not_accepted_maps':locators,'tuple_fields_without_direct_named_locator':[n for n,q in locators.items() if q is None],'top_scope_ref':fixture['scope_ref'],'payload_governed_scope_ref':fixture['payload']['governed_scope_ref'],'scope_labels_literal_equal':fixture['scope_ref']==fixture['payload']['governed_scope_ref'],'instance_version_field_present':'version_ref' in fixture,'full_tuple_owner_selector_or_kind_map_accepted':False,'governed_by_Constitution_counterpart_kinds':[x['counterpart_kind'] for x in roles if x['relation_kind_ref']=='relation.governed-by'],'semantic_subject_kinds_equated_with_global_relation_endpoint_kinds':False};ck('fifteen-source-fields-four-payload-fields-five-unaccepted-locators-ten-without',len(b.FIELDS)==15 and len(mapping['carrier_required_payload_fields'])==4 and len(mapping['tuple_fields_without_direct_named_locator'])==10 and mapping['scope_labels_literal_equal'] is False and mapping['instance_version_field_present'] is False)
 absences={n:[x['artifact_type_ref'] for x in current if x['semantic_kind']==n] for n in ['axiom','invariant','rule']};ck('selected-grounding-rule-carrier-absence-observed-not-semantic-erasure',all(not x for x in absences.values()))
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 ps=profiles();fs=frames();bindings=[b.ref(q) for q in [b.UNIT/'verify_authority_profile.py',b.UNIT/'build_candidate.py',b.IMPL/'contracts.py',b.IMPL/'verifier.py']];prior=load('../cal.definition.closed-authority-kind-invariant/delivery-manifest.json');b.unchanged(prior['files']+context['sources']+list(refs.values())+list(kind_refs.values())+bindings);b.external_current(context);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 report={'schema_version':'definition-assurance-Constitution-profile/v1-candidate','status':'PASS-for-explicit-Constitution-adoption-context-hypotheses-and-bounded-source-carrier-documentary-observations','authority_effect':'none','checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','source-checks.json','comparison-selection.json','legacy-source-section.md','legacy-model-context.md','legacy-schema-row-context.md','legacy-candidate-constitution-context.md']],'selected_inputs':{**refs,**kind_refs},'profile_control_count':len(ps),'rejected_profile_controls':sum(x['expected_rejection'] for x in ps),'profiles':ps,'finite_history_frame_count':len(fs),'rejected_history_frames':sum(x['expected_rejection'] for x in fs),'finite_history_frames':fs,'actual_check_count':len(checks),'actual_checks':checks,'current_type_registry_rows':len(reg['admitted_contracts']),'admitted_current_type_rows':len(current),'current_Kind_rows':len(kr['entries']),'current_Constitution_carrier_selection':{'dedicated_current_carrier_established':True,'artifact_type_ref':selected['constitution']['artifact_type_ref'],'exact_definition_binding':binding,'direct_definition_binding_types':direct},'related_carrier_observations':observations,'negative_fixture_checks':negatives,'actual_related_schema_probes':probes,'related_lifecycle_shape_probes':lifecycle,'dedicated_Constitution_schema_probes':special,'embedded_relation_role_probes':embedded,'current_Constitution_endpoint_roles':roles,'Kind_TR_schema_gaps':gaps,'selected_Kind_TR_pair_probes':pairs,'historical_source_current_definition_shape':current_shape,'current_definition_classification_observations':classification,'documentary_and_legacy_candidate_observations':legacy_observations,'tuple_carrier_mapping_observations':mapping,'selected_semantic_kind_absences':absences,'source_mapping_gaps':{'genus_source_precedence_and_tuple_data_identity_maps_accepted':False,'exact_owner_adoption_scope_selector_kind_and_mode_maps_accepted':False,'precedence_composition_downstream_effect_or_retirement_semantics_implemented':False,'documentary_or_carrier_success_proves_actual_adoption_application_validation_or_effect':False,'whole_shared_meaning_or_universal_runtime_semantics_established':False},'new_authorities_or_relations_created':0,'actual_adoption_application_validation_or_effect_created':False,'actual_runtime_activated':False,'semantic_ready':False,'source_fidelity':'pending','mechanized_proof':False,'claim_ceiling':'Explicit hypothetical17-axis adoption/application contexts and finite frames; exact current dedicated carrier, permissive reference/lifecycle shapes, embedded role and global pair observations.15-field documentary tuple versus4 payload fields,10 unmapped direct locators,scope/version gaps,17-rule candidate8review9hybrid context retained. Exact admitted v1 source fails current generic Definition/v2 four bindings without migration/admission invalidation. No actual owner adoption,application,validation/effect,imported legacy rules,accepted tuple/selector/precedence/composition/retirement maps or universal proof.'}
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh Constitution profile differs')
 return report
def main():
 r=verify('--write' in b.sys.argv);print(json.dumps({k:r[k] for k in ['status','profile_control_count','rejected_profile_controls','finite_history_frame_count','rejected_history_frames','actual_check_count','current_type_registry_rows','admitted_current_type_rows','current_Kind_rows','semantic_ready']},indent=2,sort_keys=True))
if __name__=='__main__':main()
