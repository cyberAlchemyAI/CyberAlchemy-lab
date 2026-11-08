"""Explicit kind/owner hypotheses and bounded legacy/current carrier observations."""
import copy,json,types
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
NAMED=['Definition','Constitution','Discipline','Decision','Spec','Runtime contract','Projection','Evidence','Residue']
AXES=['kind','table','table_revision','scope','before_state','after_state','owner','owner_route','lifecycle']
SUPPORT=['classification_map','kind_identity','exact_table_revision','complete_membership','closed_negative_membership','owner_authentication','owner_authorization','lifecycle_owner_route_map','state_history_coverage','source_fidelity']
def baseline():
 c=dict(zip(AXES,['NewKind','hyp:table','hyp:table-v1','hyp:scope','hyp:before','hyp:after','hyp:owner','hyp:owner-route','hyp:lifecycle']))
 return {'context':c,'query':copy.deepcopy(c),'known_kinds':NAMED.copy(),'independent_support':dict.fromkeys(SUPPORT),'qualified':False,'addition_applied':False,'owner_decision':None,'instance_independently_qualified':False,'may_acquire':False,'may_exercise':False,'actual_owner_or_table_verified':False,'actual_enforcement_verified':False,'source_owner_accepted':False}
def supported(p):p.update(qualified=True,independent_support={x:'hyp:'+x for x in SUPPORT})
def amendment(p):p.update(owner_decision={'decision':'hyp:decision','exact_context':copy.deepcopy(p['context']),'gate':'hyp:gate'},addition_applied=True)
def evaluate(p):
 es=[]
 def ck(ok,msg):
  if not ok:es.append(msg)
 ck(set(p)==set(baseline()),'closed selected kind profile')
 ck(set(p['context'])==set(p['query'])==set(AXES) and all(p['context'].values()) and all(p['query'].values()),'nine exact context axes')
 ck(set(p['independent_support'])==set(SUPPORT),'ten independent support axes')
 if p['qualified']:ck(all(p['independent_support'].values()),'independent kind/table/negative-membership/owner/lifecycle/history/fidelity support')
 ck(p['known_kinds']==NAMED,'selected historical nine-kind hypothesis; changes are explicit applied additions')
 for n in ['qualified','addition_applied','instance_independently_qualified','may_acquire','may_exercise','actual_owner_or_table_verified','actual_enforcement_verified','source_owner_accepted']:ck(type(p[n]) is bool,'Boolean '+n)
 d=p['owner_decision']
 if p['addition_applied']:ck(d is not None and set(d)=={'decision','exact_context','gate'} and d['decision'] and d['gate'] and d['exact_context']==p['context'],'applied addition needs separate exact-context qualified owner/gate hypothesis')
 known=p['context']['kind'] in p['known_kinds'] or p['addition_applied']
 if not known:ck(p['may_acquire'] is False and p['may_exercise'] is False,'unknown kind does not obtain normative permission')
 if p['may_acquire'] or p['may_exercise']:ck(p['instance_independently_qualified'] is True,'listed kind still needs its own instance qualification')
 ck(p['actual_owner_or_table_verified'] is False and p['actual_enforcement_verified'] is False and p['source_owner_accepted'] is False,'no actual owner/table/enforcement or accepted translation generated')
 exact=bool(p['qualified'] and p['context']==p['query'])
 return es,{'normatively_blocked_under_stronger_hypotheses':None if es or not exact else not known,'routes_to_own_ladder_owner_under_hypotheses':None if es or not exact else known,'actual_permission_or_enforcement_verified':False,'source_fidelity_accepted':False}
def profiles():
 rows=[]
 def add(id,change,bad=False,blocked=None,routed=None):
  p=baseline();change(p);es,obs=evaluate(p)
  if bool(es)!=bad or obs['normatively_blocked_under_stronger_hypotheses']!=blocked or obs['routes_to_own_ladder_owner_under_hypotheses']!=routed:raise ValueError('Unexpected kind profile '+id)
  rows.append({'case_id':id,'profile':p,'errors':es,'expected_rejection':bad,'expected_blocked':blocked,'expected_routed':routed,'observations':obs,'actual_runtime_execution':False})
 add('raw-kind-and-table-labels-no-qualified-verdict',lambda p:None)
 add('qualified-unknown-kind-normatively-blocked',supported,blocked=True,routed=False)
 for kind in NAMED:add('known-kind-routes-without-automatic-permission-'+kind,lambda p,kind=kind:supported(p) or p['context'].update(kind=kind) or p['query'].update(kind=kind),blocked=False,routed=True)
 add('qualified-exact-owner-gated-applied-addition',lambda p:supported(p) or amendment(p),blocked=False,routed=True)
 add('approved-owner-record-without-applied-addition',lambda p:supported(p) or p.update(owner_decision={'decision':'hyp:proposal','exact_context':copy.deepcopy(p['context']),'gate':'hyp:gate'}),blocked=True,routed=False)
 add('known-kind-own-independent-permission',lambda p:supported(p) or p['context'].update(kind='Definition') or p['query'].update(kind='Definition') or p.update(instance_independently_qualified=True,may_acquire=True,may_exercise=True),blocked=False,routed=True)
 for n in AXES:add('qualified-context-does-not-transfer-'+n,lambda p,n=n:supported(p) or p['query'].update({n:'hyp:other-'+n}))
 for n in SUPPORT:add('qualification-missing-'+n,lambda p,n=n:supported(p) or p['independent_support'].update({n:None}),bad=True)
 for n in AXES:add('addition-with-wrong-owner-decision-context-'+n,lambda p,n=n:supported(p) or amendment(p) or p['owner_decision']['exact_context'].update({n:'hyp:other-'+n}),bad=True)
 for n in ['may_acquire','may_exercise']:add('unknown-kind-forbidden-'+n,lambda p,n=n:p.update({n:True},instance_independently_qualified=True),bad=True)
 add('known-kind-permission-without-own-instance-qualification',lambda p:p['context'].update(kind='Definition') or p['query'].update(kind='Definition') or p.update(may_acquire=True),bad=True)
 add('addition-without-owner-decision',lambda p:p.update(addition_applied=True),bad=True)
 for n in ['actual_owner_or_table_verified','actual_enforcement_verified','source_owner_accepted']:add('actual-claim-not-produced-'+n,lambda p,n=n:p.update({n:True}),bad=True)
 return rows
def frames():
 rows=[]
 def add(id,change,bad=False):
  f={'operation':'inspect','before_kinds':NAMED.copy(),'after_kinds':NAMED.copy(),'table_before':'hyp:table','table_after':'hyp:table','scope_before':'hyp:scope','scope_after':'hyp:scope','before_revision':'hyp:v1','after_revision':'hyp:v1','selected_kind':'NewKind','owner_gate_decision':None,'declared_lifecycle':'hyp:lifecycle','declared_owner_route':'hyp:route','original_table_retained':True,'instance_grants':[],'actual_transition_verified':False};change(f);es=[]
  def ck(ok,msg):
   if not ok:es.append(msg)
  ck(f['operation'] in ['inspect','promote-definition','project-table','add-kind'],'selected operation')
  ck(f['table_before']==f['table_after'] and f['scope_before']==f['scope_after'] and f['original_table_retained'] is True,'same selected table/scope with original history retained')
  if f['operation']=='add-kind':ck(f['after_kinds']==f['before_kinds']+[f['selected_kind']] and f['selected_kind'] not in f['before_kinds'] and f['before_revision']!=f['after_revision'] and bool(f['owner_gate_decision']) and bool(f['declared_lifecycle']) and bool(f['declared_owner_route']),'one explicit fresh-kind revision with owner/lifecycle/route hypotheses')
  else:ck(f['after_kinds']==f['before_kinds'] and f['after_revision']==f['before_revision'],'inspection/definition promotion/projection does not amend table')
  ck(not f['instance_grants'] and f['actual_transition_verified'] is False,'no automatic instance grant or real transition generated')
  if bool(es)!=bad:raise ValueError('Unexpected frame '+id)
  rows.append({'case_id':id,'frame':f,'errors':es,'expected_rejection':bad,'universal_temporal_proof':False,'actual_runtime_execution':False})
 for op in ['inspect','promote-definition','project-table']:add(op+'-preserves-selected-table',lambda f,op=op:f.update(operation=op))
 def applied(f):f.update(operation='add-kind',after_kinds=NAMED+['NewKind'],after_revision='hyp:v2',owner_gate_decision='hyp:qualified-owner-gate')
 add('explicit-owner-gated-addition-no-instance-grant',applied)
 for n,value in [('owner_gate_decision',None),('declared_lifecycle',''),('declared_owner_route',''),('after_revision','hyp:v1'),('original_table_retained',False),('table_after','hyp:other'),('scope_after','hyp:other'),('instance_grants',['hyp:automatic']),('actual_transition_verified',True)]:add('addition-cannot-omit-or-change-'+n,lambda f,n=n,value=value:applied(f) or f.update({n:value}),True)
 add('definition-promotion-not-kind-amendment',lambda f:f.update(operation='promote-definition',after_kinds=NAMED+['NewKind']),True)
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
 source=load('t.json')['payload']['source'];direct=[x['artifact_type_ref'] for x in current if source['version_ref'] in x['semantic_definition_refs']];dedicated=[x['artifact_type_ref'] for x in current if x['semantic_kind'] in ['closed-authority-kind-invariant','authority-kind','authority-kind-enumeration','invariant']];ck('no-dedicated-or-direct-current-kind-invariant-carrier-in-selected-catalog',direct==dedicated==[])
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
    probes.append({'semantic_kind':semantic,'case_id':id,'schema_accepted':accepted,'record':candidate,'errors':[x.message for x in errors],'real_closed_authority_kind_or_owner_resolution_verified':False})
   for state in ['candidate','active','historical','retired']:
    candidate=copy.deepcopy(fixture);candidate['lifecycle_state']=state;errors=list(validator.iter_errors(candidate));lifecycle.append({'semantic_kind':semantic,'lifecycle_state':state,'schema_accepted':not errors,'record':candidate,'actual_posture_grant_or_runtime_verified':False})
  observations.append({'semantic_kind':semantic,'artifact_type_ref':row['artifact_type_ref'],'fixture_shape_valid':True,'declared_validator_executed':False,'whole_kind_invariant_alignment_verified':False,'actual_kind_addition_or_enforcement_verified':False})
 ck('29-selected-hostile-fixtures-reject',len(negatives)==29 and all(x['schema_rejected'] for x in negatives));ck('20-related-lifecycle-shapes-not-actual-lifecycle-or-grants',len(lifecycle)==20 and all(x['schema_accepted'] for x in lifecycle))
 definition=docs['definition_schema'];selected_source=json.loads((b.ROOT/source['path']).read_bytes());errors=list(b.c.Draft202012Validator(definition).iter_errors(selected_source));current_shape={'source_schema_version':selected_source['schema_version'],'source_artifact_type_ref':selected_source['classification']['artifact_type_ref'],'selected_current_definition_type':selected['definition']['artifact_type_ref'],'current_schema_accepted':not errors,'errors':[{'path':'/'+('/'.join(map(str,x.path))),'message':x.message} for x in errors],'instance_migrated':False,'exact_source_admission_invalidated':False};ck('admitted-Definition-v1-source-does-not-conform-to-current-Definition-v2-shape',bool(errors) and {x['path'] for x in current_shape['errors']}=={'/schema_version','/classification/artifact_type_ref','/schema_ref','/source_direction/generator_ref'})
 field=definition['properties']['classification'];classification={'semantic_kind':field['properties']['semantic_kind'],'authority_kind':field['properties']['authority_kind'],'artifact_type_ref':field['properties']['artifact_type_ref'],'normalized_wrapper_mentions_type_invariant':'type.invariant' in selected_source['voices']['scientific_formal']['normative_statement'],'wrapper_to_record_or_legacy_authority_kind_map_accepted':False};ck('current-definition-classification-has-distinct-fixed-type-and-semantic-authority-axes',classification['semantic_kind']=={'const':'definition'} and classification['authority_kind']=={'const':'semantic-authority'} and classification['artifact_type_ref']=={'const':'cal.artifact-type.definition/v2'} and classification['normalized_wrapper_mentions_type_invariant'])
 legacy=(b.UNIT/'legacy-model-context.md').read_text();decision=(b.UNIT/'legacy-review-decision-context.md').read_text();section=(b.UNIT/'legacy-source-section.md').read_text();lines=legacy.splitlines();start=lines.index('## Authority Kinds');end=next(i for i in range(start+1,len(lines)) if lines[i].startswith('## '));table=[x for x in lines[start:end] if x.startswith('| ')];rows=[x for x in table if not x.startswith('| Kind') and not x.startswith('| ---')];names=[x.split('|')[1].strip() for x in rows];names=[x if x!='[Constitution](definitions/DEFINITIONS.md#cav2-d58-constitution)' else 'Constitution' for x in names];ck('historical-nine-named-kinds-plus-default-deny-catch-all-exact',names==NAMED+['*(any unenumerated kind)*'] and len(rows)==10 and 'decision-gate + constitution-governance' in rows[-1] and '**default-deny**' in rows[-1]);ck('historical-source-and-decision-distinguish-review-enactment-from-deterministic-enforcement',all(x in section for x in ['**enacted\nin review mode**','enforcement','still pending']) and all(x in decision for x in ['Enforcement mode: **review**','OQ-2 stays OPEN.','currently govern','**as the `Definition` kind**']))
 ck('Axiom-Invariant-separate-kind-elevation-not-inferred',not any('Axiom' in x or 'Invariant' in x for x in names) and '**Add `invariant` + `axiom` as kinds now**' in decision and 'Rejected options:' in decision and '`invariant`/`axiom` kind-table addition remains deferred' in decision)
 semantic_counts={k:sum(x['semantic_kind']==k for x in current) for k in sorted({x['semantic_kind'] for x in current})};tr=docs['typed-relation_schema'];counterparts=sorted(set(conditional_endpoint_kinds(tr['allOf'])));axis_context={'historical_authority_kind_names':NAMED,'historical_authority_kind_count':9,'current_carrier_semantic_kind_count':len(semantic_counts),'current_carrier_semantic_kind_counts':semantic_counts,'current_Relation_Kind_count':len(kr['entries']),'current_TR_base_source_kind_shape':tr['properties']['payload']['properties']['source']['properties']['kind'],'current_TR_conditioned_endpoint_kind_count':len(counterparts),'current_TR_conditioned_endpoint_kind_names':counterparts,'authority_table_to_carrier_or_Relation_Kind_or_endpoint_enum_map_accepted':False,'current_selected_kind_invariant_carrier_absences':dedicated};ck('three-kind-vocabularies-inspected-without-equating-membership',len(kr['entries'])==41 and len(counterparts)==104 and axis_context['authority_table_to_carrier_or_Relation_Kind_or_endpoint_enum_map_accepted'] is False)
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 ps=profiles();fs=frames();bindings=[b.ref(q) for q in [b.UNIT/'verify_authority_profile.py',b.UNIT/'build_candidate.py',b.IMPL/'contracts.py',b.IMPL/'verifier.py']];prior=load('../cal.definition.challenge-event/delivery-manifest.json');b.unchanged(prior['files']+context['sources']+list(refs.values())+bindings);b.external_current(context);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 report={'schema_version':'definition-assurance-ClosedAuthorityKinds-profile/v1-candidate','status':'PASS-for-explicit-kind-table-owner-hypotheses-and-bounded-legacy-current-carrier-observations','authority_effect':'none','checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','source-checks.json','comparison-selection.json','legacy-source-section.md','legacy-model-context.md','legacy-review-decision-context.md']],'selected_inputs':refs,'profile_control_count':len(ps),'rejected_profile_controls':sum(x['expected_rejection'] for x in ps),'profiles':ps,'finite_history_frame_count':len(fs),'rejected_history_frames':sum(x['expected_rejection'] for x in fs),'finite_history_frames':fs,'actual_check_count':len(checks),'actual_checks':checks,'current_type_registry_rows':len(reg['admitted_contracts']),'admitted_current_type_rows':len(current),'current_Kind_rows':len(kr['entries']),'current_kind_invariant_carrier_selection':{'dedicated_current_carrier_established':False,'direct_definition_binding_types':direct,'semantic_kind_absences':dedicated},'related_carrier_observations':observations,'negative_fixture_checks':negatives,'actual_related_schema_probes':probes,'related_lifecycle_shape_probes':lifecycle,'historical_source_current_definition_shape':current_shape,'current_definition_classification_observations':classification,'historical_legacy_table_rows':rows,'historical_review_decision_boundary':{'source_context_exact':True,'review_mode_enactment_recorded':True,'deterministic_scan_recorded_pending':True,'Axiom_Invariant_kind_addition_recorded_deferred':True,'new_kind_amendment_or_current_real_enforcement_established':False,'imported_into_primary_T':False},'kind_axis_context':axis_context,'source_mapping_gaps':{'closed_world_table_state_kind_classification_permission_maps_accepted':False,'owner_lifecycle_route_and_gate_identity_maps_accepted':False,'registered_state_history_coverage_and_universal_temporal_enforcement_proved':False,'definition_promotion_review_enactment_and_runtime_enforcement_equated':False,'current_carrier_or_whole_source_alignment_accepted':False},'new_authorities_or_relations_created':0,'actual_kind_addition_or_permission_created':False,'actual_runtime_activated':False,'semantic_ready':False,'source_fidelity':'pending','mechanized_proof':False,'claim_ceiling':'Explicit hypothetical scoped unknown/known kinds and necessary qualified addition contexts, finite frames and current related carrier/source shape observations. Historical nine-kind catch-all review-mode decision remains contextual; deterministic enforcement and Axiom/Invariant elevation are not inferred. Exact admitted v1 source fails current v2 shape without migration/admission invalidation. Type semantic kinds, Relation Kinds and endpoint kinds are not authority-table membership. No actual owner/table amendment, grant, runtime or universal temporal/closed-world meaning proof.'}
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh kind profile differs')
 return report
def main():
 r=verify('--write' in b.sys.argv);print(json.dumps({k:r[k] for k in ['status','profile_control_count','rejected_profile_controls','finite_history_frame_count','rejected_history_frames','actual_check_count','current_type_registry_rows','admitted_current_type_rows','current_Kind_rows','semantic_ready']},indent=2,sort_keys=True))
if __name__=='__main__':main()
