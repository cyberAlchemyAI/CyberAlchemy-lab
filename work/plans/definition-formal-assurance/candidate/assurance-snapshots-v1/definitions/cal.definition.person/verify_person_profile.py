"""Bounded hypothetical Person profiles and read-only current carrier observations."""
import ast,copy,json,types
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def baseline():
 return {'human':'Human:hyp1','carrier':'Record:hyp1','stable_token':'PersonToken:hyp1','associated':[{'kind':k,'entity':k+':hyp1','person':'Human:hyp1'} for k in ['Account','PersonReference','IdentityClaim','Role','Membership','PermissionRecord','SessionRecord','MachineRecord']], 'member_of':[{'person':'Human:hyp1','team':'Team:hyp1','state':'before'}],'membership_records':[{'entity':'Membership:hyp1','person':'Human:hyp1','team':'Team:hyp1','state':'before'}],'participation_roles':['HumanParticipant','WorkOwner','Reviewer'],'reference_only_conclusions':[],'independent_outcomes':[],'human_identity_verified':False,'owner_policy_reviewed':False}
def errors(p):
 es=[]
 def ck(ok,msg):
  if not ok:es.append(msg)
 ck(set(p)==set(baseline()),'closed selected hypothetical profile')
 ck(bool(p['human']) and bool(p['carrier']) and p['human']!=p['carrier'],'selected Human and carrier entities distinct')
 ck(bool(p['stable_token']),'selected Person token declared separately')
 ck(all(x['entity']!=p['human'] and x['person']==p['human'] for x in p['associated']),'associated record entity and exact subject separation')
 for edge in p['member_of']:
  ck(edge['person']==p['human'] and edge['team']!=p['human'],'selected membership subject and Team distinct')
  ck(any(x['person']==edge['person'] and x['team']==edge['team'] and x['state']==edge['state'] and x['entity']!=p['human'] for x in p['membership_records']),'member-of requires separate exact Person Team state membership record')
 ck(set(p['participation_roles'])<=set(['HumanParticipant','WorkOwner','Reviewer']),'selected role example vocabulary; overlap allowed')
 ck(not p['reference_only_conclusions'],'no selected conclusion from Person/reference/participation alone')
 ck(set(p['independent_outcomes'])<=set(b.OUTCOMES),'independent outcomes require their own semantics outside this profile')
 ck(p['human_identity_verified'] is False and p['owner_policy_reviewed'] is False,'hypothetical markers never real verification or owner approval')
 return es
def controls():
 rows=[]
 def add(id,change,bad=False):
  p=baseline();change(p);es=errors(p)
  if bool(es)!=bad:raise ValueError('Unexpected Person profile '+id+' '+str(es))
  rows.append({'case_id':id,'profile':p,'errors':es,'expected_rejection':bad,'owner_policy_reviewed':False,'actual_Human_denotation_established':False,'actual_runtime_execution':False})
 add('Human-carrier-and-eight-associated-records-separated',lambda p:None)
 add('overlapping-participation-role-examples-permitted',lambda p:None)
 add('Person-without-account-or-digital-records-permitted',lambda p:p.update(associated=[],member_of=[],membership_records=[],participation_roles=[]))
 add('membership-record-no-member-of-converse',lambda p:p.update(member_of=[]))
 add('independently-supported-world-outcomes-permitted',lambda p:p.update(independent_outcomes=b.OUTCOMES))
 add('Human-carrier-collapsed',lambda p:p.update(carrier=p['human']),True)
 for index in range(8):add('associated-'+baseline()['associated'][index]['kind']+'-collapsed',lambda p,index=index:p['associated'][index].update(entity=p['human']),True)
 add('associated-record-wrong-Person',lambda p:p['associated'][0].update(person='Human:other'),True)
 add('member-of-without-membership-record',lambda p:p.update(membership_records=[]),True)
 add('membership-wrong-state',lambda p:p['membership_records'][0].update(state='after'),True)
 add('membership-wrong-Team',lambda p:p['membership_records'][0].update(team='Team:other'),True)
 add('membership-wrong-Person',lambda p:p['membership_records'][0].update(person='Human:other'),True)
 add('membership-entity-collapsed',lambda p:p['membership_records'][0].update(entity=p['human']),True)
 add('member-Team-collapsed',lambda p:p['member_of'][0].update(team=p['human']),True)
 for n in b.OUTCOMES:add('participation-alone-not-'+n,lambda p,n=n:p.update(reference_only_conclusions=[n]),True)
 add('identity-verification-invented',lambda p:p.update(human_identity_verified=True),True)
 add('owner-policy-review-invented',lambda p:p.update(owner_policy_reviewed=True),True)
 add('unselected-runtime-field',lambda p:p.update(runtime=True),True)
 return rows
def frames():
 def baseline_frame():return {'operation':'participation-only','before':{'human':'Human:hyp1','token':'PersonToken:hyp1','present':True,'accounts':['Account:hyp1'],'roles':['Role:hyp1'],'memberships':['Membership:hyp1'],'carrier':'Record:hyp1'},'after':{'human':'Human:hyp1','token':'PersonToken:hyp1','present':True,'accounts':['Account:hyp2'],'roles':['Role:hyp2'],'memberships':['Membership:hyp2'],'carrier':'Record:hyp1'},'before_authority':[],'after_authority':[],'separate_authority_decision_ref':None,'reference_only_conclusions':[]}
 def check(f):
  es=[]
  if f['operation']!='participation-only':es.append('operation outside selected allowed frame')
  if f['before']['human']!=f['after']['human'] or f['before']['token']!=f['after']['token']:es.append('selected participation change retains Person identity')
  if not f['before']['present'] or not f['after']['present']:es.append('Person present at both selected states')
  if f['before_authority']!=f['after_authority'] and not f['separate_authority_decision_ref']:es.append('participation alone does not change independent authority')
  if f['reference_only_conclusions']:es.append('participation not a world conclusion')
  return es
 rows=[]
 def add(id,change,bad=False):
  f=baseline_frame();change(f);es=check(f)
  if bool(es)!=bad:raise ValueError('Unexpected Person frame '+id+' '+str(es))
  rows.append({'case_id':id,'frame':f,'errors':es,'expected_rejection':bad,'owner_policy_reviewed':False,'actual_runtime_execution':False,'mechanized_unbounded_proof':False})
 add('account-role-membership-change-same-Person',lambda f:None)
 add('projection-wrapper-can-revise-without-Human-change',lambda f:f['after'].update(carrier='Record:hyp2'))
 add('independent-authority-decision-can-coexist',lambda f:f.update(after_authority=['Permission:hyp1'],separate_authority_decision_ref='Decision:hyp1'))
 for key in ['human','token']:add('participation-changes-'+key,lambda f,key=key:f['after'].__setitem__(key,'other'),True)
 for state in ['before','after']:add('Person-absent-'+state,lambda f,state=state:f[state].update(present=False),True)
 add('participation-alone-grants-authority',lambda f:f.update(after_authority=['Permission:hyp1']),True)
 add('participation-alone-revokes-authority',lambda f:f.update(before_authority=['Permission:hyp1']),True)
 add('private-facts-inferred-from-participation',lambda f:f.update(reference_only_conclusions=['PrivateAttributesEstablished']),True)
 add('unselected-identity-correction-operation',lambda f:f.update(operation='correct-identity'),True)
 return rows
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();root=b.ROOT/'authority/artifact-types/person/v1'
 paths={'descriptor':root/'artifact.json','schema':root/'schema.json','fixture':root/'fixtures/valid/record.json','artifact_projection':root/'ARTIFACT.md','fixture_projection':root/'fixtures/valid/RECORD.md','root_descriptor':b.ROOT/'authority/artifact-types/artifact-type/v2/artifact.json','generator':b.ROOT/'tooling/generators/endpoint_carrier.py','shared_validator':b.ROOT/'tooling/validators/endpoint_carrier.py','historical_role_model':b.ROOT/'authority/relation-kinds/candidates/0002-axis-orthogonal-model/model.json','type_registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json','kind_registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/relation-kind-registry.json'}
 for p in sorted((root/'fixtures/invalid').glob('*.json')):paths['negative_'+p.stem]=p
 reg=json.loads(paths['type_registry'].read_bytes());kr=json.loads(paths['kind_registry'].read_bytes());tr=next(x for x in reg['admitted_contracts'] if x['semantic_kind']=='typed-relation' and x['lifecycle_state']=='admitted-current');paths['TR_schema']=b.ROOT/tr['schema_path'];paths['TR_fixture']=(b.ROOT/tr['artifact_path']).parent/'fixtures/valid/record.json'
 for semantic in ['identity-claim','person-reference']:
  row=next(x for x in reg['admitted_contracts'] if x['semantic_kind']==semantic and x['lifecycle_state']=='admitted-current');paths[semantic+'_schema']=b.ROOT/row['schema_path'];paths[semantic+'_fixture']=(b.ROOT/row['artifact_path']).parent/'fixtures/valid/record.json'
 for row in kr['entries']:paths['Kind_'+row['relation_kind_ref']]=b.ROOT/row['instance_path']
 refs={n:b.ref(p) for n,p in paths.items()};raws={n:p.read_bytes() for n,p in paths.items()};docs={n:json.loads(raws[n]) for n,p in paths.items() if p.suffix=='.json'};artifact=docs['descriptor'];fixture=docs['fixture'];schema=docs['schema'];b.c.Draft202012Validator.check_schema(schema);validator=b.c.Draft202012Validator(schema);checks=[]
 def ck(id,test):checks.append({'check_id':id,'result':bool(test)})
 entry=next(x for x in reg['admitted_contracts'] if x['artifact_type_ref']==artifact['artifact_type_ref']);source=load('t.json')['payload']['source'];binding=artifact['semantic_definition_bindings'][0]
 ck('exact-current-Type-overlay-0070',entry['lifecycle_state']=='admitted-current' and entry['admission_decision_ref']=='CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION' and entry['artifact_sha256']==refs['descriptor']['sha256'] and entry['schema_sha256']==refs['schema']['sha256'])
 ck('historical-candidate-descriptor-wording-retained',artifact['status']=='candidate-unadmitted' and artifact['authority_effect']==fixture['authority_effect']=='none')
 ck('exact-admitted-Definition-0053-binding',binding['definition_ref']==source['version_ref'] and binding['path']==source['path'] and binding['sha256']==source['sha256'] and binding['admission_decision_ref']=='CAL-DECISION-0053-FULL-DEFINITION-QUEUE-ADMISSION')
 ck('root-descriptor-and-closed-schema-bound',artifact['artifact_type_root_binding']['sha256']==refs['root_descriptor']['sha256'] and artifact['schema_digest']==refs['schema']['sha256'] and schema['additionalProperties'] is False)
 ck('shared-renderer-validator-digests',artifact['source_direction']['shared_generator_sha256']==refs['generator']['sha256'] and artifact['validation_contract']['shared_validator_sha256']==refs['shared_validator']['sha256'])
 ck('fixture-shape-valid',not list(validator.iter_errors(fixture)))
 negative=[{'path':refs[n]['path'],'schema_rejected':bool(list(validator.iter_errors(docs[n])))} for n in sorted(refs) if n.startswith('negative_')];ck('five-hostiles-rejected',len(negative)==5 and all(x['schema_rejected'] for x in negative))
 mod=types.ModuleType('_bound_endpoint_renderer');mod.__file__=str(paths['generator']);exec(compile(raws['generator'],str(paths['generator']),'exec'),mod.__dict__);before=copy.deepcopy([artifact,fixture])
 ck('two-artifact-renders-exact-projection',mod.render_artifact(artifact).encode()==mod.render_artifact(artifact).encode()==raws['artifact_projection']);ck('two-fixture-renders-exact-projection',mod.render_instance(artifact,fixture).encode()==mod.render_instance(artifact,fixture).encode()==raws['fixture_projection']);ck('renderers-preserve-inputs',before==[artifact,fixture])
 tree=ast.parse(raws['shared_validator']);fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='expected_roles');namespace={};exec(compile(ast.Module(body=[fn],type_ignores=[]),str(paths['shared_validator']),'exec'),namespace)
 old=namespace['expected_roles']('person',docs['historical_role_model']);current=[]
 for row in kr['entries']:
  key='Kind_'+row['relation_kind_ref'];payload=docs[key]['payload'];ck('current-Kind-'+row['relation_kind_ref'],row['lifecycle_state']=='admitted-current' and row['instance_sha256']==refs[key]['sha256'] and row['exact_endpoint_pair_count']==len(payload['allowed_endpoint_pairs']) and row['required_qualifier_axes']==payload['qualifier_contract']['required_axes'])
  for direction,own,other in [('source','source_kind','target_kind'),('target','target_kind','source_kind')]:
   counterparts=sorted({x[other] for x in payload['allowed_endpoint_pairs'] if x[own]=='person'})
   if counterparts:current.append({'relation_kind_ref':row['relation_kind_ref'],'direction':direction,'counterpart_kinds':counterparts})
 current.sort(key=lambda x:(x['relation_kind_ref'],x['direction']))
 expected=[{'relation_kind_ref':'relation.asserts-identity-of','direction':'target','counterpart_kinds':['person-reference']},{'relation_kind_ref':'relation.challenges','direction':'target','counterpart_kinds':['challenge-event']},{'relation_kind_ref':'relation.successor-of','direction':'source','counterpart_kinds':['person']},{'relation_kind_ref':'relation.successor-of','direction':'target','counterpart_kinds':['person']}]
 ck('historical-23-Kind-role-model-matches-one-carrier-role',len(docs['historical_role_model']['entries'])==23 and old==artifact['relation_roles'] and len(old)==1)
 ck('current-41-Kind-model-exposes-four-Person-roles',len(kr['entries'])==41 and current==expected)
 for semantic in ['identity-claim','person-reference']:ck(semantic+'-fixture-shape-valid',not list(b.c.Draft202012Validator(docs[semantic+'_schema']).iter_errors(docs[semantic+'_fixture'])))
 joins={'carrier_node_equals_stable_identity_ref':fixture['node_id']==fixture['payload']['stable_identity_ref'],'Person_claim_reference_matches_selected_Claim':docs['identity-claim_fixture']['node_id'] in fixture['payload']['identity_evidence_refs'],'Person_reference_link_matches_selected_Reference':any(x['counterpart_ref']==docs['person-reference_fixture']['node_id'] for x in fixture['relation_refs']),'actual_Human_mapping_verified':False,'actual_evidence_authenticity_verified':False}
 ck('literal-Person-joins-do-not-resolve-Human',not any(joins.values()))
 probes=[]
 def probe(id,change,expected):
  rec=copy.deepcopy(fixture);change(rec);es=list(validator.iter_errors(rec));accepted=not es
  if accepted!=expected:raise ValueError('Unexpected actual Person schema probe '+id+' '+str([x.message for x in es]))
  probes.append({'case_id':id,'record':rec,'schema_accepted':accepted,'errors':[x.message for x in es],'actual_Human_denotation_established':False,'actual_privacy_or_minimization_enforced':False,'actual_runtime_execution':False,'whole_source_conformance_established':False})
 probe('empty-root-evidence-shape-accepted',lambda r:r.update(evidence_refs=[]),True)
 probe('stable-token-equals-wrapper-node-shape-accepted',lambda r:r['payload'].update(stable_identity_ref=r['node_id']),True)
 probe('account-looking-stable-token-shape-accepted',lambda r:r['payload'].update(stable_identity_ref='Account:hyp1'),True)
 probe('unresolved-identity-evidence-shape-accepted',lambda r:r['payload'].update(identity_evidence_refs=['absent:Claim']),True)
 probe('unsupported-privacy-label-shape-accepted',lambda r:r['payload'].update(privacy_classification='unreviewed'),True)
 probe('unsupported-identity-boundary-sentence-shape-accepted',lambda r:r['payload'].update(identity_boundary='Unreviewed assertion'),True)
 probe('display-name-differs-from-name-shape-accepted',lambda r:r['payload'].update(display_name='other'),True)
 probe('duplicate-relation-projection-shape-accepted',lambda r:r['relation_refs'].append(copy.deepcopy(r['relation_refs'][0])),True)
 probe('self-successor-token-shape-accepted',lambda r:r['successor_refs'].append(r['node_id']),True)
 probe('active-label-shape-accepted-with-no-effect',lambda r:r.update(lifecycle_state='active'),True)
 probe('extra-private-attribute-field-rejected',lambda r:r['payload'].update(private_attribute='synthetic'),False)
 probe('authority-effect-rejected',lambda r:r.update(authority_effect='grant'),False)
 probe('empty-identity-evidence-list-rejected',lambda r:r['payload'].update(identity_evidence_refs=[]),False)
 probe('current-challenges-role-outside-Person-schema',lambda r:r['relation_refs'].append({'relation_kind_ref':'relation.challenges','direction':'target','counterpart_kind':'challenge-event','counterpart_ref':'Challenge:hyp1'}),False)
 probe('current-successor-role-outside-Person-schema',lambda r:r['relation_refs'].append({'relation_kind_ref':'relation.successor-of','direction':'source','counterpart_kind':'person','counterpart_ref':'Person:hyp2'}),False)
 kp=docs['Kind_relation.asserts-identity-of']['payload'];ck('identity-Kind-forbids-merge-authority-private-inference',kp['forbidden_inferences']==['identity-merge','authority-transfer','private-attribute-inference']);ck('current-TR-v3-schema-bound',tr['artifact_type_ref']=='cal.artifact-type.typed-relation/v3' and tr['schema_sha256']==refs['TR_schema']['sha256'])
 relation=copy.deepcopy(docs['TR_fixture']);relation['payload'].update(relation_kind_ref='relation.asserts-identity-of',source={'kind':'person-reference','ref':docs['person-reference_fixture']['node_id'],'version_ref':'Reference@hyp'},target={'kind':'person','ref':fixture['node_id'],'version_ref':'Person@hyp'},qualifiers={'assertion_kind':'person-reference','claim_scope':fixture['scope_ref']});tv=b.c.Draft202012Validator(docs['TR_schema']);relation_probes=[]
 def rp(id,change,expected):
  rec=copy.deepcopy(relation);change(rec);es=list(tv.iter_errors(rec));accepted=not es
  if accepted!=expected:raise ValueError('Unexpected relation shape '+id+' '+str([x.message for x in es]))
  relation_probes.append({'case_id':id,'record':rec,'schema_accepted':accepted,'errors':[x.message for x in es],'actual_Human_denotation_established':False,'actual_relation_created':False,'whole_source_conformance_established':False})
 rp('Reference-to-Person-shape-valid',lambda r:None,True)
 rp('unresolved-Human-target-token-shape-accepted',lambda r:r['payload']['target'].update(ref='absent:Person'),True)
 rp('different-claim-scope-string-shape-accepted',lambda r:r['payload']['qualifiers'].update(claim_scope='other'),True)
 rp('Person-to-Person-not-asserts-identity-pair',lambda r:r['payload']['source'].update(kind='person'),False)
 rp('missing-claim-scope-rejected',lambda r:r['payload']['qualifiers'].pop('claim_scope'),False)
 rp('extra-private-inference-qualifier-rejected',lambda r:r['payload']['qualifiers'].update(private_attributes=True),False)
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 profiles=controls();history=frames();bindings=[b.ref(p) for p in [b.UNIT/'verify_person_profile.py',b.UNIT/'build_candidate.py',b.IMPL/'contracts.py',b.IMPL/'verifier.py']];prior=json.loads((b.BASE/'definitions/cal.definition.person-reference/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+list(refs.values())+bindings);b.external_current(context);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 report={'schema_version':'definition-assurance-person-profile/v1-candidate','status':'PASS-for-bounded-Human-record-membership-participation-frames-and-current-carrier-observations','authority_effect':'none','checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/'t.json')],'selected_inputs':refs,'profile_control_count':len(profiles),'rejected_profile_controls':sum(x['expected_rejection'] for x in profiles),'profiles':profiles,'finite_history_frame_count':len(history),'rejected_history_frames':sum(x['expected_rejection'] for x in history),'finite_history_frames':history,'actual_check_count':len(checks),'actual_checks':checks,'actual_schema_boundary_probes':probes,'actual_relation_schema_probes':relation_probes,'negative_fixture_checks':negative,'actual_join_observations':joins,'historical_Person_relation_roles':old,'current_Person_relation_roles':current,'role_surface_gap':'one historical carrier role versus four current Kind roles; no repair or whole-catalog closure claimed','actual_relation_endpoint_pairs':kp['allowed_endpoint_pairs'],'source_mapping_gaps':{'actual_Human_carrier_and_token_denotation_reviewed':False,'membership_and_state_mapping_reviewed':False,'privacy_minimization_and_authorization_enforcement_reviewed':False,'allowed_participation_frame_and_history_policy_reviewed':False,'source_precedence_and_role_surface_alignment_reviewed':False,'whole_source_conformance_established':False},'new_Person_data_references_or_relations_created':0,'actual_admission_created':False,'actual_runtime_activated':False,'semantic_ready':False,'source_fidelity':'pending','mechanized_proof':False,'claim_ceiling':'Hypothetical common Entity separation and exact membership/state profiles, bounded participation frames, current schemas/fixtures/projections and historical/current role observations. No actual Human identity, authentic evidence, minimization/privacy/rights enforcement, operational preservation/liveness proof, relation creation, owner acceptance or whole-definition proof.'}
 if write:b.put('person-profile-checks.json',report)
 elif not b.r.same_json(report,load('person-profile-checks.json')):raise ValueError('Fresh Person profile differs')
 return report
def main():
 report=verify('--write' in b.sys.argv);print(json.dumps({k:report[k] for k in ['status','profile_control_count','rejected_profile_controls','finite_history_frame_count','rejected_history_frames','actual_check_count','semantic_ready']},indent=2,sort_keys=True))
if __name__=='__main__':main()
