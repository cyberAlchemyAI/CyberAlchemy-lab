"""Hypothetical routing qualification plus actual bounded current-catalog observations."""
import copy,itertools,json,re,types
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
KINDS=['Definition','Constitution','Discipline','Decision','Spec','Runtime contract','Projection','Evidence','Residue']
POSTURES=['Original authority','Evidence','Template','Research','Generated projection','Private evidence','Public framework','Unknown']
GATES=['pass','flag','block','defer']
ROUTES={'Definition':'definitions-governance','Constitution':'constitution-governance','Discipline':'discipline-governance','Decision':'decision-gate','Spec':'spec owner plus decision-gate','Runtime contract':'task-session after owner gates','Projection':'ontology route plus source owner','Evidence':'source, inventory, validation, or observability owner','Residue':'route named by residue type'}
CONTEXT_AXES=['model','candidate','purpose','surface','owner','source_space','state']
def baseline():
 context={n:'hyp:'+n for n in CONTEXT_AXES};context['purpose']='support-gates'
 return {'kind':'Evidence','posture':'Evidence','route':ROUTES['Evidence'],'allowed_use':['support-gates'],'blocked_use':['replace-owner-decision'],'gate':'pass','validation_surface':'hyp:validation','non_collapse_rules':['hyp:do-not-infer-authority'],'field_maps':{n:'hyp:review-needed-'+n for n in b.FIELDS},'context':context,'query':copy.deepcopy(context),'verdict_recorded':True,'allowed_use_covers':True,'crosses_into_local_authority':True,'promotion_gate_required':True,'promotion_gate_performed':False,'independent_qualification':False,'support':{n:None for n in ['owner_authentication','source_fidelity','narrowest_owner_selection','currentness','promotion_decision']},'risk_followup':None,'implicit_grants':[],'actual_movement_verified':False,'source_owner_reviewed':False}
def evaluate(p):
 es=[]
 def ck(ok,msg):
  if not ok:es.append(msg)
 ck(set(p)==set(baseline()),'closed selected hypothetical profile')
 ck(p['posture'] in POSTURES and p['gate'] in GATES,'selected contextual posture/gate vocabulary')
 ck(set(p['field_maps'])==set(b.FIELDS) and all(p['field_maps'].values()),'explicit eight field mapping hypotheses')
 ck(bool(p['validation_surface']) and bool(p['non_collapse_rules']),'selected validation/noncollapse names')
 ck(set(p['context'])==set(p['query'])==set(CONTEXT_AXES) and all(p['context'].values()) and all(p['query'].values()),'seven explicit selected context axes')
 for n in ['verdict_recorded','allowed_use_covers','crosses_into_local_authority','promotion_gate_required','promotion_gate_performed','independent_qualification']:ck(type(p[n]) is bool,'Boolean '+n)
 ck(not p['implicit_grants'] and p['actual_movement_verified'] is False and p['source_owner_reviewed'] is False,'no actual grant/world movement/owner acceptance generated')
 if p['independent_qualification']:ck(set(p['support'])==set(baseline()['support']) and all(p['support'].values()),'independent selected owner/fidelity/currentness/promotion hypotheses')
 necessary=bool(p['verdict_recorded'] and p['allowed_use_covers'] and (not p['crosses_into_local_authority'] or p['promotion_gate_required']))
 context_matches=p['context']==p['query'];known_kind=p['kind'] in KINDS;route_matches=known_kind and p['route']==ROUTES[p['kind']]
 gate_allows=p['gate']=='pass' or p['gate']=='flag' and bool(p['risk_followup']);purpose=p['query']['purpose'];use_allows=purpose in p['allowed_use'] and purpose not in p['blocked_use']
 qualified=None if es or p['posture']=='Unknown' else bool(necessary and context_matches and route_matches and gate_allows and use_allows and (not p['crosses_into_local_authority'] or p['promotion_gate_performed']) and p['independent_qualification'])
 return es,{'selected_necessary_conditions':necessary,'context_matches':context_matches,'kind_enumerated_in_contextual_table':known_kind,'route_matches_contextual_row':route_matches,'gate_allows_under_stronger_hypothesis':gate_allows,'qualified_movement_under_stronger_hypotheses':qualified,'actual_promotion_or_permission_verified':False,'source_necessities_alone_sufficient':False}
def profiles():
 rows=[]
 def add(id,change,bad=False,qualified=False):
  p=baseline();change(p);es,obs=evaluate(p)
  if bool(es)!=bad or obs['qualified_movement_under_stronger_hypotheses']!=(None if bad else qualified):raise ValueError('Unexpected Model profile '+id+' '+str((es,obs)))
  rows.append({'case_id':id,'profile':p,'errors':es,'expected_rejection':bad,'expected_qualified':None if bad else qualified,'observations':obs,'actual_runtime_execution':False})
 def supported(p):p.update(independent_qualification=True,promotion_gate_performed=True,support={n:'hyp:separate-'+n for n in p['support']})
 add('complete-routing-necessary-conditions-not-approval',lambda p:None)
 add('independent-qualified-movement-is-still-only-hypothesis',supported,qualified=True)
 for n in CONTEXT_AXES:add('supported-movement-does-not-transfer-'+n,lambda p,n=n:supported(p) or p['query'].update({n:'hyp:other-'+n}))
 for n in b.FIELDS:add('missing-'+n+'-mapping',lambda p,n=n:p['field_maps'].update({n:None}),bad=True)
 for n in baseline()['support']:add('missing-independent-'+n,lambda p,n=n:supported(p) or p['support'].update({n:None}),bad=True)
 add('recorded-block-verdict-still-recorded-not-approval',lambda p:supported(p) or p.update(gate='block'))
 add('recorded-defer-verdict-not-approval',lambda p:supported(p) or p.update(gate='defer'))
 add('flag-needs-named-risk-followup-under-selected-context',lambda p:supported(p) or p.update(gate='flag'))
 add('flag-with-separate-risk-followup-hypothesis',lambda p:supported(p) or p.update(gate='flag',risk_followup='hyp:risk-followup'),qualified=True)
 for n in ['verdict_recorded','allowed_use_covers','promotion_gate_required','promotion_gate_performed']:add('missing-'+n,lambda p,n=n:supported(p) or p.update({n:False}))
 add('blocked-use-overrides-selected-allowed-use',lambda p:supported(p) or p['blocked_use'].append(p['query']['purpose']))
 add('uncovered-purpose-no-qualification',lambda p:supported(p) or p.update(allowed_use=[]))
 add('unknown-posture-retains-unresolved',lambda p:supported(p) or p.update(posture='Unknown'),qualified=None)
 add('unenumerated-kind-default-denied-in-contextual-selection',lambda p:supported(p) or p.update(kind='NewKind'))
 add('axiom-not-new-kind-in-contextual-table',lambda p:supported(p) or p.update(kind='Axiom'))
 add('invariant-not-new-kind-in-contextual-table',lambda p:supported(p) or p.update(kind='Invariant'))
 add('route-does-not-match-kind',lambda p:supported(p) or p.update(route='hyp:other-owner'))
 for kind in KINDS:add('independent-selected-kind-row-'+kind,lambda p,kind=kind:supported(p) or p.update(kind=kind,route=ROUTES[kind]),qualified=True)
 for posture in POSTURES[:-1]:add('posture-label-alone-not-approval-'+posture,lambda p,posture=posture:p.update(posture=posture))
 for n in ['actual_movement_verified','source_owner_reviewed']:add('claim-not-created-'+n,lambda p,n=n:p.update({n:True}),bad=True)
 add('implicit-grant-not-created',lambda p:p.update(implicit_grants=['Grant:hyp']),bad=True)
 return rows
STATES=['source-evidence','import-candidate','inventory-or-ontology-candidate','owner-routed-local-authority','implemented-or-validated','stable-repository-asset']
def frames():
 rows=[]
 def base():return {'candidate_before':'hyp:candidate','candidate_after':'hyp:candidate','state_before':STATES[0],'state_after':STATES[1],'history_retained':True,'owner_route_marker':'hyp:owner','gate_marker':'hyp:gate','promotion_decision_marker':None,'requalification_marker':None,'independent_grants_before':['hyp:independent-grant'],'independent_grants_after':['hyp:independent-grant'],'actual_transition_verified':False}
 def es(f):
  errors=[]
  def ck(ok,msg):
   if not ok:errors.append(msg)
  ck(f['state_before'] in STATES and f['state_after'] in STATES,'selected review-flow states')
  ck(f['candidate_before']==f['candidate_after'],'continuing candidate identity')
  ck(f['history_retained'] and bool(f['owner_route_marker']) and bool(f['gate_marker']),'retained history and selected route/gate hypotheses')
  if f['state_after']=='owner-routed-local-authority':ck(bool(f['promotion_decision_marker']) and bool(f['requalification_marker']),'separate selected promotion/requalification support')
  ck(f['independent_grants_before']==f['independent_grants_after'],'transition cannot silently mutate independent grants')
  ck(f['actual_transition_verified'] is False,'no actual history transition claim')
  return errors
 def add(id,change,bad=False):
  f=base();change(f);errors=es(f)
  if bool(errors)!=bad:raise ValueError('Unexpected finite frame '+id)
  rows.append({'case_id':id,'frame':f,'errors':errors,'expected_rejection':bad,'universal_temporal_proof':False,'actual_runtime_execution':False})
 for state in STATES:
  def selected(f,state=state):f.update(state_after=state);f.update(promotion_decision_marker='hyp:decision',requalification_marker='hyp:qualified') if state=='owner-routed-local-authority' else None
  add('selected-review-state-'+state,selected)
 add('local-authority-without-promotion-decision',lambda f:f.update(state_after='owner-routed-local-authority'),True)
 add('local-authority-without-requalification',lambda f:f.update(state_after='owner-routed-local-authority',promotion_decision_marker='hyp:decision'),True)
 for n in ['owner_route_marker','gate_marker']:add('missing-'+n,lambda f,n=n:f.update({n:None}),True)
 add('lost-history',lambda f:f.update(history_retained=False),True)
 add('implicit-grant-transfer',lambda f:f.update(independent_grants_after=[]),True)
 add('candidate-identity-replaced',lambda f:f.update(candidate_after='hyp:other'),True)
 add('actual-transition-claim-not-created',lambda f:f.update(actual_transition_verified=True),True)
 add('rerouted-to-earlier-review-state-permitted',lambda f:f.update(state_before=STATES[4],state_after=STATES[1]))
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

def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings()
 paths={'type_registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json','kind_registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/relation-kind-registry.json','root_descriptor':b.ROOT/'authority/artifact-types/artifact-type/v2/artifact.json'}
 reg=json.loads(paths['type_registry'].read_bytes());kr=json.loads(paths['kind_registry'].read_bytes());current=[x for x in reg['admitted_contracts'] if x['lifecycle_state']=='admitted-current'];selected={}
 for semantic in ['constitution','policy','decision','authority-claim','authority-boundary','workflow-decision-profile','user-decision-preference','typed-relation']:
  rows=[x for x in current if x['semantic_kind']==semantic]
  if len(rows)!=1:raise ValueError('Ambiguous current carrier '+semantic)
  row=rows[0];selected[semantic]=row;root=(b.ROOT/row['artifact_path']).parent;artifact=json.loads((root/'artifact.json').read_bytes());paths[semantic+'_descriptor']=root/'artifact.json';paths[semantic+'_schema']=b.ROOT/row['schema_path'];paths[semantic+'_fixture']=root/'fixtures/valid/record.json'
  if semantic!='typed-relation':
   paths[semantic+'_generator']=b.ROOT/artifact['source_direction']['shared_generator_path'];paths[semantic+'_validator']=b.ROOT/artifact['validation_contract']['shared_validator_path'];paths[semantic+'_artifact_projection']=root/'ARTIFACT.md';paths[semantic+'_fixture_projection']=root/'fixtures/valid/RECORD.md'
   for p in sorted((root/'fixtures/invalid').glob('*.json')):paths[semantic+'_negative_'+p.stem]=p
 for row in kr['entries']:paths[row['relation_kind_ref']]=b.ROOT/row['instance_path']
 refs={n:b.ref(p) for n,p in paths.items()};raws={n:p.read_bytes() for n,p in paths.items()};docs={n:json.loads(raws[n]) for n,p in paths.items() if p.suffix=='.json'};checks=[]
 def ck(id,test):checks.append({'check_id':id,'result':bool(test)})
 source=load('t.json')['payload']['source'];modelrows=[x for x in current if x['semantic_kind']=='authority-model'];direct=[x['artifact_type_ref'] for x in current if source['version_ref'] in x['semantic_definition_refs']]
 ck('no-dedicated-current-Model-type-or-direct-definition-binding',not modelrows and not direct)
 observations=[];negatives=[];probes=[]
 for semantic,row in selected.items():
  artifact=docs[semantic+'_descriptor'];schema=docs[semantic+'_schema'];fixture=docs[semantic+'_fixture'];validator=b.c.Draft202012Validator(schema);b.c.Draft202012Validator.check_schema(schema)
  ck(semantic+'-current-descriptor-and-schema-binding',row['artifact_sha256']==refs[semantic+'_descriptor']['sha256'] and row['schema_sha256']==refs[semantic+'_schema']['sha256'])
  ck(semantic+'-current-valid-fixture',not list(validator.iter_errors(fixture)))
  if semantic!='typed-relation':
   mod=types.ModuleType('_bound_'+semantic);exec(compile(raws[semantic+'_generator'],str(paths[semantic+'_generator']),'exec'),mod.__dict__);before=copy.deepcopy([artifact,fixture])
   ck(semantic+'-declared-generator-validator-root-digests',artifact['source_direction']['shared_generator_sha256']==refs[semantic+'_generator']['sha256'] and artifact['validation_contract']['shared_validator_sha256']==refs[semantic+'_validator']['sha256'] and artifact['artifact_type_root_binding']['sha256']==refs['root_descriptor']['sha256'])
   ck(semantic+'-two-artifact-renders-exact',mod.render_artifact(artifact).encode()==mod.render_artifact(artifact).encode()==raws[semantic+'_artifact_projection'])
   ck(semantic+'-two-fixture-renders-exact',mod.render_instance(artifact,fixture).encode()==mod.render_instance(artifact,fixture).encode()==raws[semantic+'_fixture_projection'])
   ck(semantic+'-renderer-does-not-mutate',before==[artifact,fixture])
   for name in [n for n in paths if n.startswith(semantic+'_negative_')]:
    errors=list(validator.iter_errors(docs[name]));negatives.append({'semantic_kind':semantic,'path':refs[name]['path'],'schema_rejected':bool(errors),'errors':[x.message for x in errors]})
   for id,change,expected in [('unresolved-owner-and-scope-reference',lambda x:x.update(owner_ref='absent:Owner',scope_ref='absent:Scope'),True),('grant-authority-effect',lambda x:x.update(authority_effect='grant'),False),('Model-kind-cannot-replace-related-kind',lambda x:x.update(kind='authority-model'),False)]:
    candidate=copy.deepcopy(fixture);change(candidate);errors=list(validator.iter_errors(candidate));accepted=not errors
    if accepted!=expected:raise ValueError('Unexpected Model related carrier probe '+semantic+' '+id)
    probes.append({'semantic_kind':semantic,'case_id':id,'record':candidate,'schema_accepted':accepted,'errors':[x.message for x in errors],'actual_reference_resolution_or_grant_verified':False})
  observations.append({'semantic_kind':semantic,'artifact_type_ref':row['artifact_type_ref'],'declared_validator_executed':False,'fixture_shape_valid':True,'Model_tuple_alignment_established':False,'actual_owner_authentication_or_promotion_verified':False})
 ck('all-related-negative-fixtures-rejected',bool(negatives) and all(x['schema_rejected'] for x in negatives))
 endpoints=[]
 for row in kr['entries']:
  id=row['relation_kind_ref'];p=docs[id]['payload'];ck('current-Kind-'+id,row['lifecycle_state']=='admitted-current' and row['instance_sha256']==refs[id]['sha256'] and row['exact_endpoint_pair_count']==len(p['allowed_endpoint_pairs']) and row['required_qualifier_axes']==p['qualifier_contract']['required_axes']);endpoints += [{'relation_kind_ref':id,'pair':pair} for pair in p['allowed_endpoint_pairs'] if 'authority-model' in pair.values()]
 ck('no-Model-endpoint-in-all-current-Kinds',len(kr['entries'])==41 and not endpoints)
 gaps=[];pair_observations=[];tv=b.c.Draft202012Validator(docs['typed-relation_schema'])
 for id in ['relation.governed-by','relation.scopes-authority-over']:
  p=docs[id]['payload'];pairs=relation_conditions(docs['typed-relation_schema'],id);gaps.append({'relation_kind_ref':id,'current_Kind_pairs':len(p['allowed_endpoint_pairs']),'current_TR_schema_pairs':len(pairs),'missing_TR_pairs':[x for x in p['allowed_endpoint_pairs'] if x not in pairs],'extra_TR_pairs':[x for x in pairs if x not in p['allowed_endpoint_pairs']],'meaning_alignment_reviewed':False})
  for pair in p['allowed_endpoint_pairs']:
   candidate=copy.deepcopy(docs['typed-relation_fixture']);candidate['payload'].update(relation_kind_ref=id,source={'kind':pair['source_kind'],'ref':'Source:hyp','version_ref':'Source@hyp'},target={'kind':pair['target_kind'],'ref':'Target:hyp','version_ref':'Target@hyp'},qualifiers={n:'hyp:qualifier' for n in p['qualifier_contract']['required_axes']});errors=list(tv.iter_errors(candidate));accepted=not errors
   if accepted!=(pair in pairs):raise ValueError('Current Kind/TR actual pair differs')
   pair_observations.append({'relation_kind_ref':id,'pair':pair,'record':candidate,'schema_accepted':accepted,'errors':[x.message for x in errors],'actual_relation_or_authority_created':False})
 ck('governed-by-exact-six-current-gaps',gaps[0]['current_Kind_pairs']==29 and gaps[0]['current_TR_schema_pairs']==23 and gaps[0]['missing_TR_pairs']==[{'source_kind':n,'target_kind':'policy'} for n in ['admission-transaction','authority-boundary','decision-bundle','decision-checkpoint','user-decision-preference','workflow-decision-profile']] and not gaps[0]['extra_TR_pairs'])
 ck('scope-exact-Boundary-to-DecisionScope-gap',gaps[1]['current_Kind_pairs']==3 and gaps[1]['current_TR_schema_pairs']==2 and gaps[1]['missing_TR_pairs']==[{'source_kind':'authority-boundary','target_kind':'decision-scope'}] and not gaps[1]['extra_TR_pairs'])
 text=(b.UNIT/'legacy-model-context.md').read_text();kind_section=text.split('## Authority Kinds\n',1)[1].split('## Authority Postures\n',1)[0];posture_section=text.split('## Authority Postures\n',1)[1].split('## Narrowest Owner Rule\n',1)[0];kindrows=[x for x in kind_section.splitlines() if x.startswith('| ')][2:];posturerows=[x for x in posture_section.splitlines() if x.startswith('| ')][2:]
 ck('contextual-nine-kinds-plus-catchall',len(kindrows)==10 and all('| '+kind+' |' in kind_section if kind!='Constitution' else '| [Constitution]' in kind_section for kind in KINDS))
 ck('contextual-eight-postures',len(posturerows)==8 and all('| '+posture+' |' in posture_section for posture in POSTURES))
 ck('contextual-four-gates-and-review-mode-pending-scan',all('- `'+gate+'`:' in text for gate in GATES) and 'review-mode' in text and 'deterministic\nkind-enumeration scan is pending' in text and 'deferred' in kind_section)
 ck('context-document-not-admitted-into-primary-theory',load('comparison-selection.json')['comparison_assembled_into_primary_T'] is False and load('source-checks.json')['contextual_document_admitted_into_primary_theory'] is False)
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 ps=profiles();fs=frames();bindings=[b.ref(p) for p in [b.UNIT/'verify_authority_profile.py',b.UNIT/'build_candidate.py',b.IMPL/'contracts.py',b.IMPL/'verifier.py']];prior=load('../cal.definition.authority-boundary/delivery-manifest.json');b.unchanged(prior['files']+context['sources']+list(refs.values())+bindings);b.external_current(context);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 report={'schema_version':'definition-assurance-AuthorityModel-profile/v1-candidate','status':'PASS-for-explicit-Model-qualification-hypotheses-and-bounded-catalog-observations','authority_effect':'none','checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','source-checks.json','comparison-selection.json','legacy-model-context.md']],'selected_inputs':refs,'profile_control_count':len(ps),'rejected_profile_controls':sum(x['expected_rejection'] for x in ps),'profiles':ps,'finite_history_frame_count':len(fs),'rejected_history_frames':sum(x['expected_rejection'] for x in fs),'finite_history_frames':fs,'actual_check_count':len(checks),'actual_checks':checks,'current_type_registry_rows':len(reg['admitted_contracts']),'admitted_current_type_rows':len(current),'current_Kind_rows':len(kr['entries']),'current_Model_carrier_selection':{'semantic_kind_rows':modelrows,'direct_definition_binding_types':direct,'dedicated_Model_carrier_established':False,'scope':'selected admitted-current Type registry only'},'Model_endpoint_roles':endpoints,'related_carrier_observations':observations,'negative_fixture_checks':negatives,'actual_related_schema_probes':probes,'Kind_TR_schema_gaps':gaps,'all_selected_current_Kind_TR_pair_observations':pair_observations,'contextual_table_selection':{'kind_rows':kindrows,'posture_rows':posturerows,'gate_vocabulary':GATES,'review_flow_states':STATES,'tables_admitted_or_assembled_into_primary_theory':False,'deterministic_kind_scan_executed':False,'Axiom_Invariant_new_kind_decision':'deferred in selected legacy context'},'source_mapping_gaps':{'eight_tuple_denotation_reviewed':False,'complete_kind_posture_route_coverage_reviewed':False,'actual_verdict_owner_authentication_or_sufficient_approval_established':False,'universal_noncollapse_temporal_movement_and_carrier_conformance_established':False},'new_authorities_or_relations_created':0,'actual_promotion_created':False,'actual_runtime_activated':False,'semantic_ready':False,'source_fidelity':'pending','mechanized_proof':False,'claim_ceiling':'Explicit hypothetical seven-axis routing/independent qualification and selected finite review-flow frames. Related current carriers, generators, validator digests, schema controls and exact selected Kind/TR gaps observed; canonical package validators not executed. Legacy nine-kind/eight-posture/four-gate tables remain contextual comparison, not admitted Lab authority or universal proof. No actual promotion, owner authentication or full source fidelity.'}
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh Model profile differs')
 return report
def main():
 r=verify('--write' in b.sys.argv);print(json.dumps({k:r[k] for k in ['status','profile_control_count','rejected_profile_controls','finite_history_frame_count','rejected_history_frames','actual_check_count','current_type_registry_rows','admitted_current_type_rows','current_Kind_rows','semantic_ready']},indent=2,sort_keys=True))
if __name__=='__main__':main()
