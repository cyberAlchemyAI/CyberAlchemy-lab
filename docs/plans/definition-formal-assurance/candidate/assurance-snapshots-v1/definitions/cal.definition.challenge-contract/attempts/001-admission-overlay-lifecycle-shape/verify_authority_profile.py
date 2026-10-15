"""Hypothetical challenge qualification/frames and bounded admitted carrier/instance evidence."""
import copy,itertools,json,types
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
AXES=['contract','contract_version','policy','policy_version','scope','subject','subject_version','challenger','mode']
SUPPORT=['closed_specification','version_identity','current_policy','subject_eligibility','challenger_standing','accepted_ground','accepted_evidence','response_permission','owner_route','resolution_gate','timing','source_fidelity']
def baseline():
 context=dict(zip(AXES,['hyp:contract','hyp:contract-v1','hyp:policy','hyp:policy-v1','hyp:scope','hyp:subject','hyp:subject-v1','hyp:challenger','hyp:contradiction']))
 return {'field_maps':{n:'hyp:map-'+n for n in b.FIELDS},'context':context,'query':copy.deepcopy(context),'independent_qualification':False,'support':dict.fromkeys(SUPPORT),'eligible_subject':True,'eligible_challenger':True,'ground_accepted':True,'evidence_accepted':True,'mode_allowed':True,'timing_satisfied':True,'blocked':False,'filed':True,'subject_effect_decision':None,'unresolved_residue_retained':True,'actual_filing_or_effect_verified':False,'source_owner_accepted':False,'implicit_effects':[]}
def supported(p):p.update(independent_qualification=True,support={n:'hyp:independent-'+n for n in SUPPORT})
def effect(p):p.update(subject_effect_decision={'decision':'hyp:owner-decision','owner':'hyp:separate-owner-role','gate':'hyp:authenticated-gate','subject':p['context']['subject'],'subject_version':p['context']['subject_version'],'scope':p['context']['scope'],'effect':'suspend','independent_authorization':'hyp:separate-authorization'})
def evaluate(p):
 es=[]
 def ck(ok,msg):
  if not ok:es.append(msg)
 ck(set(p)==set(baseline()),'closed selected hypothetical challenge profile')
 ck(set(p['field_maps'])==set(b.FIELDS) and all(p['field_maps'].values()),'ten explicit selected specification maps')
 ck(set(p['context'])==set(p['query'])==set(AXES) and all(p['context'].values()) and all(p['query'].values()),'nine explicit context axes')
 ck(set(p['support'])==set(SUPPORT),'twelve support axes')
 if p['independent_qualification']:ck(all(p['support'].values()),'separate qualification support hypotheses')
 for n in ['independent_qualification','eligible_subject','eligible_challenger','ground_accepted','evidence_accepted','mode_allowed','timing_satisfied','blocked','filed','unresolved_residue_retained','actual_filing_or_effect_verified','source_owner_accepted']:ck(type(p[n]) is bool,'Boolean '+n)
 ck(p['unresolved_residue_retained'] is True and p['actual_filing_or_effect_verified'] is False and p['source_owner_accepted'] is False and not p['implicit_effects'],'residue retained and no real execution/acceptance/automatic effect fabricated')
 decision=p['subject_effect_decision']
 if decision is not None:ck(set(decision)=={'decision','owner','gate','subject','subject_version','scope','effect','independent_authorization'} and all(decision.values()) and decision['effect'] in ['suspend','reverse'],'separate bounded owner/gate/subject/version/scope/effect/authorization hypotheses')
 eligible=None if es else bool(p['independent_qualification'] and p['context']==p['query'] and all(p[n] for n in ['eligible_subject','eligible_challenger','ground_accepted','evidence_accepted','mode_allowed','timing_satisfied']) and not p['blocked'])
 subject_effect=None if es else bool(decision is not None and decision['subject']==p['query']['subject'] and decision['subject_version']==p['query']['subject_version'] and decision['scope']==p['query']['scope'] and decision['independent_authorization'])
 return es,{'qualified_filing_under_stronger_hypotheses':None if es else bool(eligible and p['filed']),'separate_subject_effect_under_hypotheses':subject_effect,'filing_alone_suspends_or_reverses':False,'actual_filing_or_effect_verified':False,'source_fidelity_accepted':False}
def profiles():
 rows=[]
 def add(id,change,bad=False,filing=False,subject_effect=False):
  p=baseline();change(p);es,obs=evaluate(p)
  if bool(es)!=bad or obs['qualified_filing_under_stronger_hypotheses']!=(None if bad else filing) or obs['separate_subject_effect_under_hypotheses']!=(None if bad else subject_effect):raise ValueError('Unexpected profile '+id+' '+str((es,obs)))
  rows.append({'case_id':id,'profile':p,'errors':es,'expected_rejection':bad,'expected_filing':None if bad else filing,'expected_subject_effect':None if bad else subject_effect,'observations':obs,'actual_runtime_execution':False})
 add('declared-fields-and-filing-no-independent-qualification',lambda p:None)
 add('qualified-filing-does-not-resolve-or-reverse',supported,filing=True)
 add('qualified-filing-plus-separate-subject-effect',lambda p:supported(p) or effect(p),filing=True,subject_effect=True)
 add('separate-subject-effect-can-exist-without-qualified-filing',effect,subject_effect=True)
 add('separate-subject-effect-can-exist-without-any-filing',lambda p:effect(p) or p.update(filed=False),subject_effect=True)
 add('separate-reversal-also-needs-independent-decision',lambda p:supported(p) or effect(p) or p['subject_effect_decision'].update(effect='reverse'),filing=True,subject_effect=True)
 for n in AXES:add('filing-does-not-transfer-'+n,lambda p,n=n:supported(p) or p['query'].update({n:'hyp:other-'+n}))
 for n in b.FIELDS:add('missing-field-map-'+n,lambda p,n=n:p['field_maps'].update({n:None}),bad=True)
 for n in SUPPORT:add('selected-qualification-missing-'+n,lambda p,n=n:supported(p) or p['support'].update({n:None}),bad=True)
 for n in ['eligible_subject','eligible_challenger','ground_accepted','evidence_accepted','mode_allowed','timing_satisfied']:add('not-qualified-'+n,lambda p,n=n:supported(p) or p.update({n:False}))
 add('explicit-block-overrides-qualification',lambda p:supported(p) or p.update(blocked=True))
 add('not-filed-eligible-capability-is-not-an-event',lambda p:supported(p) or p.update(filed=False))
 for n in ['subject','subject_version','scope']:add('separate-effect-does-not-transfer-'+n,lambda p,n=n:supported(p) or effect(p) or p['subject_effect_decision'].update({n:'hyp:other-'+n}),filing=True)
 for n in ['decision','owner','gate','independent_authorization']:add('effect-missing-'+n,lambda p,n=n:effect(p) or p['subject_effect_decision'].update({n:None}),bad=True)
 add('filing-cannot-destroy-unresolved-residue',lambda p:p.update(unresolved_residue_retained=False),bad=True)
 add('filing-cannot-create-automatic-reversal',lambda p:p.update(implicit_effects=['hyp:automatic-reversal']),bad=True)
 for n in ['actual_filing_or_effect_verified','source_owner_accepted']:add('actual-claim-not-generated-'+n,lambda p,n=n:p.update({n:True}),bad=True)
 return rows
def frames():
 rows=[]
 def base():return {'operation':'file-challenge','contract_before':'hyp:c1','contract_after':'hyp:c1','contract_version':'hyp:v1','subject_before':'hyp:s1','subject_after':'hyp:s1','subject_version':'hyp:subject-v1','scope':'hyp:scope','decision_scope':None,'decision_subject_version':None,'subject_state_before':'active','subject_state_after':'active','contract_meaning_before':'hyp:meaning1','contract_meaning_after':'hyp:meaning1','unresolved_residue_retained':True,'history_retained':True,'separate_owner_decision':None,'resolution_gate':None,'actual_transition_verified':False}
 observations=['file-challenge','submit-evidence','record-contradiction','request-owner-review','record-response','validate-shape','project-view']
 def add(id,change,bad=False):
  f=base();change(f);es=[]
  def ck(ok,msg):
   if not ok:es.append(msg)
  ck(f['operation'] in observations+['suspend-subject','reverse-subject'],'selected finite operation')
  ck(f['contract_before']==f['contract_after'] and f['subject_before']==f['subject_after'] and f['history_retained'] is True and f['unresolved_residue_retained'] is True,'separate contract/subject identity, history and unresolved residue retained')
  ck(f['contract_meaning_before']==f['contract_meaning_after'],'filing/response/subject effects do not silently rewrite contract meaning')
  if f['operation'] in observations:ck(f['subject_state_before']==f['subject_state_after'],'filing and evidence/response observations do not automatically alter subject state')
  else:ck(bool(f['separate_owner_decision']) and bool(f['resolution_gate']) and f['decision_scope']==f['scope'] and f['decision_subject_version']==f['subject_version'],'separate exact subject/version/scope owner/gate decision')
  ck(f['actual_transition_verified'] is False,'no actual transition generated')
  if bool(es)!=bad:raise ValueError('Unexpected frame '+id)
  rows.append({'case_id':id,'frame':f,'errors':es,'expected_rejection':bad,'universal_temporal_proof':False,'actual_runtime_execution':False})
 for op in observations:add(op+'-without-automatic-subject-effects',lambda f,op=op:f.update(operation=op))
 def decide(f,op='suspend-subject'):f.update(operation=op,separate_owner_decision='hyp:separate-owner-decision',resolution_gate='hyp:separate-gate',decision_scope=f['scope'],decision_subject_version=f['subject_version'],subject_state_after='suspended' if op=='suspend-subject' else 'reversed')
 add('separate-qualified-suspension',decide);add('separate-qualified-reversal',lambda f:decide(f,'reverse-subject'))
 for n,value in [('subject_state_after','reversed'),('contract_meaning_after','hyp:changed'),('contract_after','hyp:c2'),('subject_after','hyp:s2'),('history_retained',False),('unresolved_residue_retained',False),('actual_transition_verified',True)]:add('filing-cannot-change-'+n,lambda f,n=n,value=value:f.update({n:value}),True)
 for n,value in [('separate_owner_decision',None),('resolution_gate',None),('decision_scope','hyp:other-scope'),('decision_subject_version','hyp:other-version')]:add('effect-missing-or-wrong-'+n,lambda f,n=n,value=value:decide(f) or f.update({n:value}),True)
 add('separate-effect-does-not-rewrite-contract',lambda f:decide(f) or f.update(contract_meaning_after='hyp:new'),True)
 return rows
def relation_conditions(schema,kind):
 def mentions(x):return isinstance(x,dict) and (x.get('const')==kind or any(mentions(v) for v in x.values())) or isinstance(x,list) and any(mentions(v) for v in x)
 def visit(x):
  if isinstance(x,dict):return ([x] if 'if' in x and mentions(x['if']) else [])+sum([visit(v) for v in x.values()],[])
  if isinstance(x,list):return sum([visit(v) for v in x],[])
  return []
 found=visit(schema)
 if len(found)!=1:raise ValueError('Ambiguous relation condition '+kind)
 return [{'source_kind':x['properties']['source']['properties']['kind']['const'],'target_kind':x['properties']['target']['properties']['kind']['const']} for x in found[0]['then']['properties']['payload']['oneOf']]
RELATED=['challenge-contract','challenge-event','policy','decision','evidence-set']
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();root=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries';foundation=b.ROOT/'authority/admissions/cyberalchemy-lab-operational-foundation/v1'
 paths={'type_registry':root/'artifact-type-registry.json','kind_registry':root/'relation-kind-registry.json','root_descriptor':b.ROOT/'authority/artifact-types/artifact-type/v2/artifact.json','foundation_artifact_admission':foundation/'artifact-instance-admission.json','foundation_relation_admission':foundation/'typed-relation-admission.json','foundation_policy':foundation/'instances/artifacts/policy.json','foundation_contract':foundation/'instances/artifacts/challenge-contract.json','foundation_relation':foundation/'instances/typed-relations/challenge-governed-by-policy.json','ontology_node':b.ROOT/'ontology-lifecycle/domainspec/specs/ontology-lifecycle/nodes/challenge-contract.json','ontology_state_schema':b.ROOT/'ontology-lifecycle/domainspec/event-sourcing/schemas/challenge-contract-state.schema.json'}
 reg=json.loads(paths['type_registry'].read_bytes());kr=json.loads(paths['kind_registry'].read_bytes());current=[x for x in reg['admitted_contracts'] if x['lifecycle_state']=='admitted-current'];selected={}
 for semantic in RELATED+['typed-relation']:
  rows=[x for x in current if x['semantic_kind']==semantic]
  if len(rows)!=1:raise ValueError('Ambiguous current carrier '+semantic)
  row=rows[0];selected[semantic]=row;folder=(b.ROOT/row['artifact_path']).parent;artifact=json.loads((folder/'artifact.json').read_bytes());paths[semantic+'_descriptor']=folder/'artifact.json';paths[semantic+'_schema']=b.ROOT/row['schema_path'];paths[semantic+'_fixture']=folder/artifact['validation_contract']['positive_witness']
  if semantic in RELATED:
   paths[semantic+'_generator']=b.ROOT/artifact['source_direction']['shared_generator_path'];paths[semantic+'_validator']=b.ROOT/artifact['validation_contract']['shared_validator_path'];paths[semantic+'_artifact_projection']=folder/'ARTIFACT.md';paths[semantic+'_fixture_projection']=folder/artifact['validation_contract']['positive_projection']
   for relative in artifact['validation_contract']['negative_witnesses']:paths[semantic+'_negative_'+b.Path(relative).stem]=folder/relative
 historical_rows={}
 for kind in ['policy','typed-relation']:
  row=next(x for x in reg['admitted_contracts'] if x['artifact_type_ref']=='cal.artifact-type.'+kind+('/v1' if kind=='policy' else '/v2'));historical_rows[kind]=row;paths['historical_'+kind+'_schema']=b.ROOT/row['schema_path'];paths['historical_'+kind+'_descriptor']=b.ROOT/row['artifact_path']
 for row in kr['entries']:paths[row['relation_kind_ref']]=b.ROOT/row['instance_path']
 for overlay in ['foundation_artifact_admission','foundation_relation_admission']:
  admission=json.loads(paths[overlay].read_bytes())
  for i,row in enumerate(admission['entries']):paths[overlay+'_admitted_'+str(i)]=b.ROOT/row['admitted_instance_path'];paths[overlay+'_source_'+str(i)]=b.ROOT/row['source_path']
 refs={n:b.ref(p) for n,p in paths.items()};raws={n:p.read_bytes() for n,p in paths.items()};docs={n:json.loads(raws[n]) for n,p in paths.items() if p.suffix=='.json'};checks=[]
 def ck(id,test):checks.append({'check_id':id,'result':bool(test)})
 for kind,row in historical_rows.items():ck('historical-'+kind+'-exact-descriptor-schema-and-status',row['lifecycle_state']=='admitted-historical' and row['artifact_sha256']==refs['historical_'+kind+'_descriptor']['sha256'] and row['schema_sha256']==refs['historical_'+kind+'_schema']['sha256'])
 source=load('t.json')['payload']['source'];a=docs['challenge-contract_descriptor'];direct=[x['artifact_type_ref'] for x in current if source['version_ref'] in x['semantic_definition_refs']];binding=a['semantic_definition_bindings'][0];ck('dedicated-current-exact-ChallengeContract-definition-binding',direct==['cal.artifact-type.challenge-contract/v1'] and binding['definition_ref']==source['version_ref'] and binding['path']==source['path'] and binding['sha256']==source['sha256'] and binding['admission_posture']=='admitted')
 absences={kind:[x['artifact_type_ref'] for x in current if x['semantic_kind']==kind] for kind in ['gate','residue']};ck('no-current-Gate-or-Residue-carrier-in-selected-catalog',not any(absences.values()))
 observations=[];negatives=[];probes=[]
 for semantic,row in selected.items():
  artifact=docs[semantic+'_descriptor'];schema=docs[semantic+'_schema'];fixture=docs[semantic+'_fixture'];validator=b.c.Draft202012Validator(schema);b.c.Draft202012Validator.check_schema(schema);ck(semantic+'-exact-current-descriptor-schema',row['artifact_sha256']==refs[semantic+'_descriptor']['sha256'] and row['schema_sha256']==refs[semantic+'_schema']['sha256']);ck(semantic+'-positive-fixture-valid',not list(validator.iter_errors(fixture)))
  if semantic in RELATED:
   mod=types.ModuleType('_pure_'+semantic);exec(compile(raws[semantic+'_generator'],str(paths[semantic+'_generator']),'exec'),mod.__dict__);before=copy.deepcopy([artifact,fixture]);ck(semantic+'-declared-generator-validator-root-digests',artifact['source_direction']['shared_generator_sha256']==refs[semantic+'_generator']['sha256'] and artifact['validation_contract']['shared_validator_sha256']==refs[semantic+'_validator']['sha256'] and artifact['artifact_type_root_binding']['sha256']==refs['root_descriptor']['sha256']);ck(semantic+'-two-artifact-renders-exact',mod.render_artifact(artifact).encode()==mod.render_artifact(artifact).encode()==raws[semantic+'_artifact_projection']);ck(semantic+'-two-record-renders-exact',mod.render_instance(artifact,fixture).encode()==mod.render_instance(artifact,fixture).encode()==raws[semantic+'_fixture_projection']);ck(semantic+'-render-inputs-preserved',before==[artifact,fixture])
   for name in [n for n in paths if n.startswith(semantic+'_negative_')]:
    es=list(validator.iter_errors(docs[name]));negatives.append({'semantic_kind':semantic,'path':refs[name]['path'],'schema_rejected':bool(es),'errors':[x.message for x in es]})
   for id,change,expected in [('unresolved-owner-and-scope',lambda x:x.update(owner_ref='absent:owner',scope_ref='absent:scope'),True),('grant-authority-effect',lambda x:x.update(authority_effect='grant'),False),('neighbor-kind-substitution',lambda x:x.update(kind='challenge-event' if semantic=='challenge-contract' else 'challenge-contract'),False)]:
    candidate=copy.deepcopy(fixture);change(candidate);es=list(validator.iter_errors(candidate));accepted=not es
    if accepted!=expected:raise ValueError('Unexpected related schema probe '+semantic+' '+id)
    probes.append({'semantic_kind':semantic,'case_id':id,'record':candidate,'schema_accepted':accepted,'errors':[x.message for x in es],'actual_reference_resolution_or_filing_verified':False})
  observations.append({'semantic_kind':semantic,'artifact_type_ref':row['artifact_type_ref'],'fixture_shape_valid':True,'declared_validator_executed':False,'whole_ChallengeContract_meaning_alignment_established':False,'actual_filing_or_effect_verified':False})
 ck('all-related-hostile-fixtures-reject',len(negatives)==25 and all(x['schema_rejected'] for x in negatives));sv=b.c.Draft202012Validator(docs['challenge-contract_schema']);special=[];fixture=docs['challenge-contract_fixture'];payload=fixture['payload'];array_fields=[n for n,x in docs['challenge-contract_schema']['properties']['payload']['properties'].items() if x['type']=='array'];string_fields=[n for n,x in docs['challenge-contract_schema']['properties']['payload']['properties'].items() if x['type']=='string']
 cases=[('empty-selected-extension-'+n,lambda x,n=n:x['payload'].update({n:[]}),True) for n in array_fields]+[('unresolved-selected-reference-or-timing-'+n,lambda x,n=n:x['payload'].update({n:'absent:unresolved'}),True) for n in string_fields]+[('all-five-selected-extensions-empty',lambda x:[x['payload'].update({n:[]}) for n in array_fields],True),('unknown-kind-ground-evidence-and-response-vocabulary',lambda x:[x['payload'].update({n:['absent:unknown']}) for n in array_fields],True),('added-mechanism-version-field-not-in-current-record-schema',lambda x:x.update(version_ref='hyp:contract-v1'),False),('route-string-alone-not-record',lambda x:x.clear() or x.update(challenge_route='hyp:route'),False)]
 for id,change,expected in cases:
  candidate=copy.deepcopy(fixture);change(candidate);es=list(sv.iter_errors(candidate));accepted=not es
  if accepted!=expected:raise ValueError('Unexpected dedicated shape probe '+id)
  special.append({'case_id':id,'record':candidate,'schema_accepted':accepted,'errors':[x.message for x in es],'accepted_extension_nonvacuity_or_reference_meaning_verified':False})
 embedded=[];declared_roles={(x['relation_kind_ref'],x['direction'],kind) for x in a['relation_roles'] for kind in x['counterpart_kinds']};rs=docs['challenge-contract_schema']['properties']['relation_refs']['items']['properties']
 for kind,direction,neighbor in itertools.product(rs['relation_kind_ref']['enum'],rs['direction']['enum'],rs['counterpart_kind']['enum']):
  candidate=copy.deepcopy(fixture);candidate['relation_refs']=[{'relation_kind_ref':kind,'direction':direction,'counterpart_kind':neighbor,'counterpart_ref':'hyp:counterpart'}];es=list(sv.iter_errors(candidate));embedded.append({'relation_kind_ref':kind,'direction':direction,'counterpart_kind':neighbor,'schema_accepted':not es,'declared_role':(kind,direction,neighbor) in declared_roles,'actual_relation_created':False})
 ck('embedded-role-schema-accepts32-combinations-versus6-declared-roles',len(embedded)==32 and all(x['schema_accepted'] for x in embedded) and sum(x['declared_role'] for x in embedded)==6)
 endpoints=[]
 for row in kr['entries']:
  id=row['relation_kind_ref'];p=docs[id]['payload'];ck('current-Kind-'+id,row['lifecycle_state']=='admitted-current' and row['instance_sha256']==refs[id]['sha256'] and row['exact_endpoint_pair_count']==len(p['allowed_endpoint_pairs']) and row['required_qualifier_axes']==p['qualifier_contract']['required_axes'])
  for pair in p['allowed_endpoint_pairs']:
   if pair['source_kind']=='challenge-contract':endpoints.append({'relation_kind_ref':id,'direction':'source','counterpart_kind':pair['target_kind']})
   if pair['target_kind']=='challenge-contract':endpoints.append({'relation_kind_ref':id,'direction':'target','counterpart_kind':pair['source_kind']})
 ck('six-declared-role-tuples-match-current-Kind-endpoint-selection',declared_roles=={(x['relation_kind_ref'],x['direction'],x['counterpart_kind']) for x in endpoints})
 gaps=[];pairs=[];tv=b.c.Draft202012Validator(docs['typed-relation_schema'])
 for id in ['relation.governed-by','relation.challenges','relation.successor-of','relation.violates','relation.scopes-authority-over']:
  p=docs[id]['payload'];allowed=relation_conditions(docs['typed-relation_schema'],id);gaps.append({'relation_kind_ref':id,'current_Kind_pairs':len(p['allowed_endpoint_pairs']),'current_TR_schema_pairs':len(allowed),'missing_TR_pairs':[x for x in p['allowed_endpoint_pairs'] if x not in allowed],'extra_TR_pairs':[x for x in allowed if x not in p['allowed_endpoint_pairs']],'meaning_alignment_reviewed':False})
  testpairs=p['allowed_endpoint_pairs'] if id in ['relation.governed-by','relation.scopes-authority-over'] else [x for x in p['allowed_endpoint_pairs'] if 'challenge-contract' in x.values()]
  for pair in testpairs:
   candidate=copy.deepcopy(docs['typed-relation_fixture']);candidate['payload'].update(relation_kind_ref=id,source={'kind':pair['source_kind'],'ref':'hyp:source','version_ref':'hyp:source-v1'},target={'kind':pair['target_kind'],'ref':'hyp:target','version_ref':'hyp:target-v1'},qualifiers={n:'hyp:qualifier' for n in p['qualifier_contract']['required_axes']});es=list(tv.iter_errors(candidate));accepted=not es
   if accepted!=(pair in allowed):raise ValueError('Kind/TR pair mismatch')
   pairs.append({'relation_kind_ref':id,'pair':pair,'record':candidate,'schema_accepted':accepted,'errors':[x.message for x in es],'actual_relation_or_subject_effect_created':False})
 ck('governed-by-six-current-schema-gaps',len(gaps[0]['missing_TR_pairs'])==6 and gaps[0]['current_Kind_pairs']==29 and gaps[0]['current_TR_schema_pairs']==23 and not gaps[0]['extra_TR_pairs']);ck('Boundary-to-DecisionScope-gap',gaps[4]['missing_TR_pairs']==[{'source_kind':'authority-boundary','target_kind':'decision-scope'}])
 overlay_checks=[]
 for name,count in [('foundation_artifact_admission',9),('foundation_relation_admission',13)]:
  admission=docs[name];ck(name+'-exact-overlay-count-and-decision',admission['count']==len(admission['entries'])==count and admission['decision_id']=='CAL-DECISION-0071-CYBERALCHEMY-LAB-OPERATIONAL-FOUNDATION-ADMISSION')
  for i,row in enumerate(admission['entries']):
   ok=refs[name+'_admitted_'+str(i)]['sha256']==row['admitted_instance_sha256']==row['source_sha256']==refs[name+'_source_'+str(i)]['sha256'] and row['lifecycle_state']=='admitted-current';ck(name+'-exact-source-admitted-binding-'+str(i),ok);overlay_checks.append({'admission':name,'admitted_path':row['admitted_instance_path'],'source_path':row['source_path'],'exact_bytes_match':ok,'effective_lifecycle_state':row['lifecycle_state'],'embedded_lifecycle_state':docs[name+'_admitted_'+str(i)]['lifecycle_state'],'runtime_activation_or_world_execution_verified':False})
 fc=docs['foundation_contract'];fp=docs['foundation_policy'];fr=docs['foundation_relation'];ca=next(x for x in docs['foundation_artifact_admission']['entries'] if x['semantic_kind']=='challenge-contract');pa=next(x for x in docs['foundation_artifact_admission']['entries'] if x['semantic_kind']=='policy');ra=next(x for x in docs['foundation_relation_admission']['entries'] if x['source_kind']=='challenge-contract' and x['relation_kind_ref']=='relation.governed-by');joins={'Policy_reference_literal_matches':fc['payload']['policy_ref']==fp['node_id']==fr['payload']['target']['ref'],'Contract_identity_literal_matches':fc['node_id']==fr['payload']['source']['ref']==ra['source_ref'],'source_version_literal_matches_overlay':fr['payload']['source']['version_ref']==ca['version_ref'],'target_version_literal_matches_overlay':fr['payload']['target']['version_ref']==pa['version_ref'],'scope_literal_matches':fc['scope_ref']==fp['scope_ref']==fr['scope_ref'],'owner_route_literal_matches_challenge_route':fc['payload']['owner_route']==fc['challenge_route'],'actual_qualified_Policy_eligibility_owner_gate_timing_or_enforcement_verified':False};ck('six-foundation-literal-joins-not-runtime-qualification',all(joins[n] is True for n in joins if n!='actual_qualified_Policy_eligibility_owner_gate_timing_or_enforcement_verified'))
 foundation_shapes=[]
 for name,schema_name,expected in [('foundation_contract','challenge-contract_schema',True),('foundation_policy','historical_policy_schema',True),('foundation_policy','policy_schema',False),('foundation_relation','historical_typed-relation_schema',True),('foundation_relation','typed-relation_schema',False)]:
  schema=docs[schema_name];b.c.Draft202012Validator.check_schema(schema);es=list(b.c.Draft202012Validator(schema).iter_errors(docs[name]));accepted=not es
  if accepted!=expected:raise ValueError('Unexpected foundation historical/current shape observation '+name+' '+schema_name)
  foundation_shapes.append({'record':name,'schema':schema_name,'schema_accepted':accepted,'errors':[x.message for x in es],'instance_migrated':False,'admission_overlay_invalidated':False})
 ck('dedicated-record-version-not-present-overlay-supplies-literal-version','version_ref' not in fc and 'version' not in fc and 'version_ref' not in docs['challenge-contract_schema']['properties'] and ca['version_ref']==fr['payload']['source']['version_ref']);ck('foundation-historical-Policy-and-TR-schema-currentness-separated',pa['carrier_type_ref']=='cal.artifact-type.policy/v1' and selected['policy']['artifact_type_ref']=='cal.artifact-type.policy/v2' and fr['schema_version']=='cyberalchemy-lab-typed-relation/v2' and docs['typed-relation_schema']['properties']['schema_version']['const']=='cyberalchemy-lab-typed-relation/v3')
 ontology={'node_id':docs['ontology_node']['node_id'],'node_equality_statement':docs['ontology_node']['body']['equality'],'node_source_context':docs['ontology_node']['intent'],'schema_definition_ref':docs['ontology_state_schema']['x-definition-ref'],'schema_required_fields':docs['ontology_state_schema']['required'],'schema_valid_challenge_modes':docs['ontology_state_schema']['properties']['valid_challenge_modes']['items']['enum'],'current_carrier_response_modes':payload['response_modes'],'component_to_mechanism_identity_or_field_map_reviewed':False,'whole_ontology_schema_validated':False,'imported_into_primary_T':False};ck('scoped-ontology-component-and-mode-spelling-differences-preserved','All eight selected challenge fields' in ontology['node_equality_statement'] and 'owner_review' in ontology['schema_valid_challenge_modes'] and 'owner-review' in ontology['current_carrier_response_modes'] and len(ontology['schema_required_fields'])==8)
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 ps=profiles();fs=frames();bindings=[b.ref(p) for p in [b.UNIT/'verify_authority_profile.py',b.UNIT/'build_candidate.py',b.IMPL/'contracts.py',b.IMPL/'verifier.py']];prior=load('../cal.definition.authority-surface/delivery-manifest.json');b.unchanged(prior['files']+context['sources']+list(refs.values())+bindings);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 report={'schema_version':'definition-assurance-ChallengeContract-profile/v1-candidate','status':'PASS-for-explicit-challenge-hypotheses-and-bounded-current-carrier-foundation-observations','authority_effect':'none','checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','source-checks.json','comparison-selection.json']],'selected_inputs':refs,'profile_control_count':len(ps),'rejected_profile_controls':sum(x['expected_rejection'] for x in ps),'profiles':ps,'finite_history_frame_count':len(fs),'rejected_history_frames':sum(x['expected_rejection'] for x in fs),'finite_history_frames':fs,'actual_check_count':len(checks),'actual_checks':checks,'current_type_registry_rows':len(reg['admitted_contracts']),'admitted_current_type_rows':len(current),'current_Kind_rows':len(kr['entries']),'current_ChallengeContract_carrier_selection':{'artifact_type_ref':selected['challenge-contract']['artifact_type_ref'],'exact_definition_binding':binding,'direct_definition_binding_types':direct,'dedicated_current_carrier_established':True},'selected_semantic_kind_absences':absences,'related_carrier_observations':observations,'negative_fixture_checks':negatives,'actual_related_schema_probes':probes,'dedicated_contract_schema_probes':special,'embedded_relation_role_probes':embedded,'current_ChallengeContract_endpoint_roles':endpoints,'Kind_TR_schema_gaps':gaps,'all_selected_current_Kind_TR_pair_observations':pairs,'foundation_exact_admission_checks':overlay_checks,'foundation_literal_joins':joins,'foundation_historical_current_schema_observations':foundation_shapes,'foundation_contract_version_overlay':{'instance_ref':ca,'record_has_dedicated_version_field':False,'literal_relation_version_matches_overlay':True,'actual_version_denotation_or_eligibility_authenticated':False},'ontology_context_observations':ontology,'source_mapping_gaps':{'genus_iff_and_source_precedence_reviewed':False,'closed_versioned_Policy_field_and_population_maps_accepted':False,'real_challenger_subject_owner_gate_timing_or_eligibility_verified':False,'universal_causal_and_temporal_automatic_effect_prevention_established':False},'new_authorities_or_relations_created':0,'actual_filing_resolution_or_subject_effect_created':False,'actual_runtime_activated':False,'semantic_ready':False,'source_fidelity':'pending','mechanized_proof':False,'claim_ceiling':'Explicit hypothetical filing/eligibility/context and independently governed subject effects, finite frames, exact admitted dedicated carrier and foundation admission-overlay bindings, shape/generator/role/Kind/TR observations. Raw fields, empty extension acceptance, vocabulary or exact admission do not prove version/Policy/owner/eligibility/temporal meaning or runtime enforcement. Foundation historical Policy/TR shapes and ontology component/equality/mode spelling remain separate; no source migration, actual challenge effect, owner fidelity or universal proof.'}
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh Challenge profile differs')
 return report
def main():
 r=verify('--write' in b.sys.argv);print(json.dumps({k:r[k] for k in ['status','profile_control_count','rejected_profile_controls','finite_history_frame_count','rejected_history_frames','actual_check_count','current_type_registry_rows','admitted_current_type_rows','current_Kind_rows','semantic_ready']},indent=2,sort_keys=True))
if __name__=='__main__':main()
