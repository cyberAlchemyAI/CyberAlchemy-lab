"""Exact Event revision hypotheses, finite frames, carrier gaps and stored candidate observations."""
import ast,copy,itertools,json,types
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
AXES=['event_revision','business_event_id','subject','subject_revision','contract','contract_revision','challenger','scope','recorded_at']
SUPPORT=['record_revision_identity','original_bytes','recorded_state_coverage','attribution','challenger_eligibility','subject_revision_identity','Contract_revision_identity','stated_grounds','stated_evidence','source_fidelity']
def baseline():
 context=dict(zip(AXES,['hyp:event-v1','hyp:business-event','hyp:subject','hyp:subject-v1','hyp:Contract','hyp:Contract-v1','hyp:challenger','hyp:scope','hyp:record-time']))
 return {'context':context,'query':copy.deepcopy(context),'independent_qualification':False,'support':dict.fromkeys(SUPPORT),'eligible':True,'original_revision':'hyp:event-v1','current_revision':'hyp:event-v1','original_payload':'hyp:bytes1','current_payload':'hyp:bytes1','original_retained':True,'response_projection_before':'submitted','response_projection_after':'responded','separate_disposition':None,'subject_effects':[],'actual_event_or_gate_verified':False,'source_owner_accepted':False}
def supported(p):p.update(independent_qualification=True,support={n:'hyp:independent-'+n for n in SUPPORT})
def decision(p):p.update(separate_disposition={'decision':'hyp:separate-decision','target_revision':p['context']['event_revision'],'subject_revision':p['context']['subject_revision'],'scope':p['context']['scope'],'owner':'hyp:separate-owner','gate':'hyp:separate-gate','effect':'challenge-disposition'})
def evaluate(p):
 es=[]
 def ck(ok,msg):
  if not ok:es.append(msg)
 ck(set(p)==set(baseline()),'closed selected Event profile')
 ck(set(p['context'])==set(p['query'])==set(AXES) and all(p['context'].values()) and all(p['query'].values()),'nine exact selected context axes')
 ck(set(p['support'])==set(SUPPORT),'ten support axes')
 if p['independent_qualification']:ck(all(p['support'].values()),'independent reference/byte/state/attribution/eligibility/ground/evidence/fidelity hypotheses')
 for n in ['independent_qualification','eligible','original_retained','actual_event_or_gate_verified','source_owner_accepted']:ck(type(p[n]) is bool,'Boolean '+n)
 ck(all(p[n] for n in ['original_revision','current_revision','original_payload','current_payload']) and p['original_retained'] is True,'original exact revision/bytes retained')
 if p['original_revision']==p['current_revision']:ck(p['original_payload']==p['current_payload'],'same exact record revision cannot change payload under hypothesis')
 ck(not p['subject_effects'] and p['actual_event_or_gate_verified'] is False and p['source_owner_accepted'] is False,'no automatic subject effect, actual event/gate or owner acceptance generated')
 d=p['separate_disposition']
 if d is not None:ck(set(d)=={'decision','target_revision','subject_revision','scope','owner','gate','effect'} and all(d.values()) and d['effect']=='challenge-disposition','separate bounded exact disposition hypotheses')
 qualified=None if es else bool(p['independent_qualification'] and p['eligible'] and p['context']==p['query'] and p['original_revision']==p['query']['event_revision'])
 disposition=None if es else bool(d is not None and d['target_revision']==p['query']['event_revision'] and d['subject_revision']==p['query']['subject_revision'] and d['scope']==p['query']['scope'])
 return es,{'qualified_exact_filing_under_stronger_hypotheses':qualified,'separate_exact_disposition_under_hypotheses':disposition,'response_projection_is_immutable_record_identity':False,'actual_event_or_gate_verified':False,'source_fidelity_accepted':False}
def profiles():
 rows=[]
 def add(id,change,bad=False,qualified=False,disposition=False):
  p=baseline();change(p);es,obs=evaluate(p)
  if bool(es)!=bad or obs['qualified_exact_filing_under_stronger_hypotheses']!=(None if bad else qualified) or obs['separate_exact_disposition_under_hypotheses']!=(None if bad else disposition):raise ValueError('Unexpected Event profile '+id)
  rows.append({'case_id':id,'profile':p,'errors':es,'expected_rejection':bad,'expected_qualified':None if bad else qualified,'expected_disposition':None if bad else disposition,'observations':obs,'actual_runtime_execution':False})
 add('raw-reference-and-response-labels-no-qualified-event',lambda p:None)
 add('selected-qualified-exact-filing-with-independent-response',supported,qualified=True)
 add('selected-filing-plus-separate-exact-disposition',lambda p:supported(p) or decision(p),qualified=True,disposition=True)
 add('disposition-marker-without-filing-qualification',decision,disposition=True)
 for n in AXES:add('exact-filing-does-not-transfer-'+n,lambda p,n=n:supported(p) or p['query'].update({n:'hyp:other-'+n}))
 for n in SUPPORT:add('qualification-missing-'+n,lambda p,n=n:supported(p) or p['support'].update({n:None}),bad=True)
 add('ineligible-selected-challenger',lambda p:supported(p) or p.update(eligible=False))
 add('same-exact-revision-payload-overwritten',lambda p:p.update(current_payload='hyp:bytes2'),bad=True)
 add('same-business-id-new-record-revision-original-retained',lambda p:supported(p) or p.update(current_revision='hyp:event-v2',current_payload='hyp:bytes2'),qualified=True)
 add('new-revision-is-not-the-selected-original-revision',lambda p:supported(p) or p.update(current_revision='hyp:event-v2',current_payload='hyp:bytes2') or p['query'].update(event_revision='hyp:event-v2'))
 for n in ['target_revision','subject_revision','scope']:add('disposition-does-not-transfer-'+n,lambda p,n=n:supported(p) or decision(p) or p['separate_disposition'].update({n:'hyp:other-'+n}),qualified=True)
 for n in ['decision','owner','gate']:add('disposition-missing-'+n,lambda p,n=n:decision(p) or p['separate_disposition'].update({n:None}),bad=True)
 add('disposition-cannot-be-subject-reversal',lambda p:decision(p) or p['separate_disposition'].update(effect='subject-reversal'),bad=True)
 add('response-projection-may-advance-without-original-byte-change',lambda p:supported(p) or p.update(response_projection_after='resolved-for-revision'),qualified=True)
 add('original-filing-revision-erased',lambda p:p.update(original_retained=False),bad=True)
 add('event-label-creates-subject-effect',lambda p:p.update(subject_effects=['hyp:automatic-reversal']),bad=True)
 for n in ['actual_event_or_gate_verified','source_owner_accepted']:add('actual-claim-not-generated-'+n,lambda p,n=n:p.update({n:True}),bad=True)
 return rows
def frames():
 rows=[]
 def base():return {'operation':'project-response','business_event_before':'hyp:business1','business_event_after':'hyp:business1','original_revision':'hyp:event-v1','current_revision_before':'hyp:event-v1','current_revision_after':'hyp:event-v1','original_payload_before':'hyp:bytes1','original_payload_after':'hyp:bytes1','current_payload_before':'hyp:bytes1','current_payload_after':'hyp:bytes1','subject_revision_before':'hyp:subject-v1','subject_revision_after':'hyp:subject-v1','Contract_revision_before':'hyp:Contract-v1','Contract_revision_after':'hyp:Contract-v1','response_before':'submitted','response_after':'responded','history_retained':True,'separate_gate_decision':None,'subject_effects':[],'actual_transition_verified':False}
 def add(id,change,bad=False):
  f=base();change(f);es=[]
  def ck(ok,msg):
   if not ok:es.append(msg)
  ck(f['operation'] in ['file','project-response','append-successor','record-disposition','validate-shape'],'selected operation')
  ck(f['business_event_before']==f['business_event_after'] and f['original_payload_before']==f['original_payload_after'] and f['history_retained'] is True,'business context and original exact revision/history preserved')
  ck(f['subject_revision_before']==f['subject_revision_after'] and f['Contract_revision_before']==f['Contract_revision_after'],'selected response lineage preserves original filing subject/Contract context')
  if f['current_revision_before']==f['current_revision_after']:ck(f['current_payload_before']==f['current_payload_after'],'same exact revision does not mutate')
  if f['operation']=='append-successor':ck(f['current_revision_before']!=f['current_revision_after'],'successor has separate exact revision identity')
  if f['operation']=='record-disposition':ck(bool(f['separate_gate_decision']),'separate gate/owner decision hypothesis')
  ck(not f['subject_effects'] and f['actual_transition_verified'] is False,'no implicit subject effects or actual transition created')
  if bool(es)!=bad:raise ValueError('Unexpected frame '+id)
  rows.append({'case_id':id,'frame':f,'errors':es,'expected_rejection':bad,'universal_temporal_proof':False,'actual_runtime_execution':False})
 add('independent-response-projection',lambda f:None)
 add('filing-preserves-subject',lambda f:f.update(operation='file',response_after='submitted'))
 add('shape-validation-no-mutation',lambda f:f.update(operation='validate-shape'))
 def successor(f):f.update(operation='append-successor',current_revision_after='hyp:event-v2',current_payload_after='hyp:bytes2')
 add('separate-successor-response-record',successor)
 add('separate-disposition-record',lambda f:f.update(operation='record-disposition',separate_gate_decision='hyp:gate-decision'))
 for n,value in [('business_event_after','hyp:other'),('original_payload_after','hyp:changed'),('current_payload_after','hyp:changed'),('subject_revision_after','hyp:other-subject'),('Contract_revision_after','hyp:other-Contract'),('history_retained',False),('subject_effects',['hyp:reverse']),('actual_transition_verified',True)]:add('response-cannot-change-'+n,lambda f,n=n,value=value:f.update({n:value}),True)
 add('successor-cannot-reuse-original-exact-revision',lambda f:successor(f) or f.update(current_revision_after=f['current_revision_before']),True)
 add('successor-cannot-delete-original-payload',lambda f:successor(f) or f.update(original_payload_after=None),True)
 add('disposition-missing-gate-decision',lambda f:f.update(operation='record-disposition'),True)
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
RELATED=['challenge-event','challenge-contract','decision','finding','evidence-set']
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();root=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries';observed=b.ROOT/'implementation/lab-workflows/candidates/v1/failures/receipts/0004/observed'
 paths={'type_registry':root/'artifact-type-registry.json','kind_registry':root/'relation-kind-registry.json','root_descriptor':b.ROOT/'authority/artifact-types/artifact-type/v2/artifact.json','stored_index':observed/'episode-index.json','stored_cold_summary':observed.parent/'cold-stdout.json','ChallengeService':b.ROOT/'implementation/lab-workflows/candidates/v1/challenges/service.py','EvidenceService':b.ROOT/'implementation/lab-workflows/candidates/v1/evidence/service.py'}
 reg=json.loads(paths['type_registry'].read_bytes());kr=json.loads(paths['kind_registry'].read_bytes());current=[x for x in reg['admitted_contracts'] if x['lifecycle_state']=='admitted-current'];selected={}
 for semantic in RELATED+['typed-relation']:
  rows=[x for x in current if x['semantic_kind']==semantic]
  if len(rows)!=1:raise ValueError('Ambiguous current carrier '+semantic)
  row=rows[0];selected[semantic]=row;folder=(b.ROOT/row['artifact_path']).parent;artifact=json.loads((folder/'artifact.json').read_bytes());paths[semantic+'_descriptor']=folder/'artifact.json';paths[semantic+'_schema']=b.ROOT/row['schema_path'];paths[semantic+'_fixture']=folder/artifact['validation_contract']['positive_witness']
  if semantic in RELATED:
   paths[semantic+'_generator']=b.ROOT/artifact['source_direction']['shared_generator_path'];paths[semantic+'_validator']=b.ROOT/artifact['validation_contract']['shared_validator_path'];paths[semantic+'_artifact_projection']=folder/'ARTIFACT.md';paths[semantic+'_fixture_projection']=folder/artifact['validation_contract']['positive_projection']
   for relative in artifact['validation_contract']['negative_witnesses']:paths[semantic+'_negative_'+b.Path(relative).stem]=folder/relative
 for row in kr['entries']:paths[row['relation_kind_ref']]=b.ROOT/row['instance_path']
 index=json.loads(paths['stored_index'].read_bytes());event_rows=[x for x in index['records'] if x['kind']=='challenge-event'];stored_rows=[x for x in index['records'] if x['kind']=='typed-relation'];by_version={x['version_ref']:x for x in index['records']}
 for i,row in enumerate(event_rows):paths['stored_event_'+str(i)]=observed/row['path']
 for i,row in enumerate(stored_rows):paths['stored_relation_'+str(i)]=observed/row['path']
 first=json.loads(paths['stored_event_0'].read_bytes())
 for label,version in [('Contract',first['payload']['challenge_contract_ref']),('subject',first['payload']['subject_version_ref'])]:paths['stored_'+label]=observed/by_version[version]['path']
 refs={n:b.ref(p) for n,p in paths.items()};raws={n:p.read_bytes() for n,p in paths.items()};docs={n:json.loads(raws[n]) for n,p in paths.items() if p.suffix=='.json'};checks=[]
 def ck(id,test):checks.append({'check_id':id,'result':bool(test)})
 source=load('t.json')['payload']['source'];a=docs['challenge-event_descriptor'];binding=a['semantic_definition_bindings'][0];direct=[x['artifact_type_ref'] for x in current if source['version_ref'] in x['semantic_definition_refs']];ck('dedicated-current-exact-Event-definition-binding',direct==['cal.artifact-type.challenge-event/v1'] and binding['definition_ref']==source['version_ref'] and binding['path']==source['path'] and binding['sha256']==source['sha256'] and binding['admission_posture']=='admitted')
 observations=[];negatives=[];probes=[]
 for semantic,row in selected.items():
  artifact=docs[semantic+'_descriptor'];schema=docs[semantic+'_schema'];fixture=docs[semantic+'_fixture'];validator=b.c.Draft202012Validator(schema);b.c.Draft202012Validator.check_schema(schema);ck(semantic+'-exact-current-descriptor-schema',row['artifact_sha256']==refs[semantic+'_descriptor']['sha256'] and row['schema_sha256']==refs[semantic+'_schema']['sha256']);ck(semantic+'-positive-fixture-valid',not list(validator.iter_errors(fixture)))
  if semantic in RELATED:
   mod=types.ModuleType('_pure_'+semantic);exec(compile(raws[semantic+'_generator'],str(paths[semantic+'_generator']),'exec'),mod.__dict__);before=copy.deepcopy([artifact,fixture]);ck(semantic+'-declared-generator-validator-root-digests',artifact['source_direction']['shared_generator_sha256']==refs[semantic+'_generator']['sha256'] and artifact['validation_contract']['shared_validator_sha256']==refs[semantic+'_validator']['sha256'] and artifact['artifact_type_root_binding']['sha256']==refs['root_descriptor']['sha256']);ck(semantic+'-two-artifact-renders-exact',mod.render_artifact(artifact).encode()==mod.render_artifact(artifact).encode()==raws[semantic+'_artifact_projection']);ck(semantic+'-two-record-renders-exact',mod.render_instance(artifact,fixture).encode()==mod.render_instance(artifact,fixture).encode()==raws[semantic+'_fixture_projection']);ck(semantic+'-render-inputs-preserved',before==[artifact,fixture])
   for name in [n for n in paths if n.startswith(semantic+'_negative_')]:
    es=list(validator.iter_errors(docs[name]));negatives.append({'semantic_kind':semantic,'path':refs[name]['path'],'schema_rejected':bool(es),'errors':[x.message for x in es]})
   for id,change,expected in [('unresolved-owner-and-scope',lambda x:x.update(owner_ref='absent:owner',scope_ref='absent:scope'),True),('grant-authority-effect',lambda x:x.update(authority_effect='grant'),False),('neighbor-kind-substitution',lambda x:x.update(kind='decision' if semantic=='challenge-event' else 'challenge-event'),False)]:
    candidate=copy.deepcopy(fixture);change(candidate);es=list(validator.iter_errors(candidate));accepted=not es
    if accepted!=expected:raise ValueError('Unexpected related probe '+semantic+' '+id)
    probes.append({'semantic_kind':semantic,'case_id':id,'record':candidate,'schema_accepted':accepted,'errors':[x.message for x in es],'actual_reference_resolution_or_standing_verified':False})
  observations.append({'semantic_kind':semantic,'artifact_type_ref':row['artifact_type_ref'],'fixture_shape_valid':True,'declared_validator_executed':False,'whole_Event_meaning_alignment_established':False,'actual_event_or_gate_verified':False})
 ck('all25-related-hostile-fixtures-reject',len(negatives)==25 and all(x['schema_rejected'] for x in negatives));sv=b.c.Draft202012Validator(docs['challenge-event_schema']);fixture=docs['challenge-event_fixture'];special=[]
 strings=[n for n,x in docs['challenge-event_schema']['properties']['payload']['properties'].items() if x['type']=='string'];cases=[('unresolved-selected-field-'+n,lambda x,n=n:x['payload'].update({n:'absent:unresolved'}),True) for n in strings]+[('empty-evidence-at-both-layers',lambda x:x.update(evidence_refs=[]) or x['payload'].update(evidence_refs=[]),True),('duplicate-payload-evidence-rejects',lambda x:x['payload'].update(evidence_refs=['hyp:e1','hyp:e1']),False),('duplicate-residue-labels-accepted',lambda x:x['payload'].update(residue_refs=['hyp:r1','hyp:r1']),True),('malformed-time-label-accepted',lambda x:x['payload'].update(submitted_at='not-a-time'),True),('unknown-response-state-accepted',lambda x:x['payload'].update(response_state='unknown-state'),True),('resolved-label-with-no-resolution-decision-accepted',lambda x:x['payload'].update(response_state='resolved-for-revision',resolution_decision_ref='none'),True),('unversioned-Contract-reference-accepted',lambda x:x['payload'].update(challenge_contract_ref='hyp:Contract-without-version'),True),('subject-and-subject-revision-labels-inconsistent-accepted',lambda x:x['payload'].update(subject_ref='hyp:subject1',subject_version_ref='hyp:other-subject@v2'),True),('same-node-id-changed-evidence-and-response-shape-accepted',lambda x:x['payload'].update(response_state='responded',evidence_refs=['hyp:new-evidence']),True),('dedicated-event-version-field-not-in-record-schema',lambda x:x.update(version_ref='hyp:event@v1'),False)]
 for id,change,expected in cases:
  candidate=copy.deepcopy(fixture);change(candidate);es=list(sv.iter_errors(candidate));accepted=not es
  if accepted!=expected:raise ValueError('Unexpected Event dedicated probe '+id)
  special.append({'case_id':id,'record':candidate,'schema_accepted':accepted,'errors':[x.message for x in es],'real_version_time_eligibility_or_immutability_verified':False})
 embedded=[];declared_roles={(x['relation_kind_ref'],x['direction'],kind) for x in a['relation_roles'] for kind in x['counterpart_kinds']};rs=docs['challenge-event_schema']['properties']['relation_refs']['items']['properties']
 for kind,direction,neighbor in itertools.product(rs['relation_kind_ref']['enum'],rs['direction']['enum'],rs['counterpart_kind']['enum']):
  candidate=copy.deepcopy(fixture);candidate['relation_refs']=[{'relation_kind_ref':kind,'direction':direction,'counterpart_kind':neighbor,'counterpart_ref':'hyp:counterpart'}];es=list(sv.iter_errors(candidate));embedded.append({'relation_kind_ref':kind,'direction':direction,'counterpart_kind':neighbor,'schema_accepted':not es,'declared_role':(kind,direction,neighbor) in declared_roles,'actual_relation_created':False})
 ck('embedded-schema1200-combinations-versus112-declared-role-tuples',len(embedded)==1200 and all(x['schema_accepted'] for x in embedded) and sum(x['declared_role'] for x in embedded)==112)
 literal_fixture={'payload_subject_ref':fixture['payload']['subject_ref'],'embedded_challenges_counterpart_ref':fixture['relation_refs'][0]['counterpart_ref'],'literal_refs_match':fixture['payload']['subject_ref']==fixture['relation_refs'][0]['counterpart_ref'],'fixture_Contract_matches_selected_Contract_fixture':fixture['payload']['challenge_contract_ref']==docs['challenge-contract_fixture']['node_id'],'actual_reference_resolution_or_semantic_alignment_established':False};ck('fixture-literal-subject-and-Contract-joins-not-assumed',literal_fixture['literal_refs_match'] is False and literal_fixture['fixture_Contract_matches_selected_Contract_fixture'] is False)
 endpoints=[]
 for row in kr['entries']:
  id=row['relation_kind_ref'];p=docs[id]['payload'];ck('current-Kind-'+id,row['lifecycle_state']=='admitted-current' and row['instance_sha256']==refs[id]['sha256'] and row['exact_endpoint_pair_count']==len(p['allowed_endpoint_pairs']) and row['required_qualifier_axes']==p['qualifier_contract']['required_axes'])
  for pair in p['allowed_endpoint_pairs']:
   if pair['source_kind']=='challenge-event':endpoints.append({'relation_kind_ref':id,'direction':'source','counterpart_kind':pair['target_kind']})
   if pair['target_kind']=='challenge-event':endpoints.append({'relation_kind_ref':id,'direction':'target','counterpart_kind':pair['source_kind']})
 ck('112-declared-roles-match-current-Kind-selection',declared_roles=={(x['relation_kind_ref'],x['direction'],x['counterpart_kind']) for x in endpoints})
 gaps=[];pairs=[];tv=b.c.Draft202012Validator(docs['typed-relation_schema'])
 for id in ['relation.challenges','relation.governed-by','relation.evidence-bears-on','relation.produces','relation.declares-effect-on','relation.successor-of','relation.scopes-authority-over']:
  p=docs[id]['payload'];allowed=relation_conditions(docs['typed-relation_schema'],id);gaps.append({'relation_kind_ref':id,'current_Kind_pairs':len(p['allowed_endpoint_pairs']),'current_TR_schema_pairs':len(allowed),'missing_TR_pairs':[x for x in p['allowed_endpoint_pairs'] if x not in allowed],'extra_TR_pairs':[x for x in allowed if x not in p['allowed_endpoint_pairs']],'meaning_alignment_reviewed':False})
  testpairs=p['allowed_endpoint_pairs'] if id in ['relation.challenges','relation.governed-by','relation.scopes-authority-over'] else [x for x in p['allowed_endpoint_pairs'] if 'challenge-event' in x.values()]
  for pair in testpairs:
   candidate=copy.deepcopy(docs['typed-relation_fixture']);candidate['payload'].update(relation_kind_ref=id,source={'kind':pair['source_kind'],'ref':'hyp:source','version_ref':'hyp:source-v1'},target={'kind':pair['target_kind'],'ref':'hyp:target','version_ref':'hyp:target-v1'},qualifiers={n:'hyp:qualifier' for n in p['qualifier_contract']['required_axes']});es=list(tv.iter_errors(candidate));accepted=not es
   if accepted!=(pair in allowed):raise ValueError('Kind/TR pair mismatch')
   pairs.append({'relation_kind_ref':id,'pair':pair,'record':candidate,'schema_accepted':accepted,'errors':[x.message for x in es],'actual_relation_or_effect_created':False})
 qualifier_probes=[]
 for id,pair in [('relation.challenges',{'source_kind':'challenge-event','target_kind':'artifact-type'}),('relation.declares-effect-on',{'source_kind':'decision','target_kind':'challenge-event'})]:
  p=docs[id]['payload'];candidate=copy.deepcopy(docs['typed-relation_fixture']);candidate['payload'].update(relation_kind_ref=id,source={'kind':pair['source_kind'],'ref':'hyp:source','version_ref':'hyp:source-v1'},target={'kind':pair['target_kind'],'ref':'hyp:target','version_ref':'hyp:target-v1'},qualifiers={n:'hyp:unresolved-or-wrong-target-version' for n in p['qualifier_contract']['required_axes']});es=list(tv.iter_errors(candidate));ck('qualifier-string-shape-not-target-version-authentication-'+id,not es);qualifier_probes.append({'relation_kind_ref':id,'record':candidate,'schema_accepted':not es,'qualifier_to_endpoint_version_or_Contract_alignment_verified':False})
 ck('challenge-governance-evidence-production-disposition-succession-claim-ceilings',docs['relation.challenges']['payload']['forbidden_inferences']==['suspension','reversal','contradiction-proof','authority'] and 'effect-execution' in docs['relation.declares-effect-on']['payload']['forbidden_inferences'] and 'truth' in docs['relation.evidence-bears-on']['payload']['forbidden_inferences'] and 'automatic-supersession' in docs['relation.successor-of']['payload']['forbidden_inferences'])
 stored=[];stored_relations=[];chronology=[]
 for i,row in enumerate(event_rows):
  doc=docs['stored_event_'+str(i)];ck('stored-exact-event-binding-'+str(i),row['sha256']==refs['stored_event_'+str(i)]['sha256'] and row['version_ref'].startswith(doc['node_id']+'@') and not list(sv.iter_errors(doc)));stored.append({'index_row':row,'response_state':doc['payload']['response_state'],'payload':doc['payload'],'node_id':doc['node_id'],'schema_accepted':True,'exact_index_bytes_match':True,'real_eligibility_or_owner_gate_verified':False})
 for i,row in enumerate(stored_rows):
  doc=docs['stored_relation_'+str(i)];es=list(tv.iter_errors(doc));ck('stored-exact-relation-binding-'+str(i),row['sha256']==refs['stored_relation_'+str(i)]['sha256'] and row['version_ref'].startswith(doc['node_id']+'@') and not es);p=doc['payload'];stored_relations.append({'index_row':row,'payload':p,'schema_accepted':True,'actual_relation_admitted_or_effect_executed':False})
  if p['relation_kind_ref']=='relation.successor-of' and p['source']['kind']==p['target']['kind']=='challenge-event':chronology.append({'source':p['source']['version_ref'],'target':p['target']['version_ref'],'succession_effect':p['qualifiers']['succession_effect']})
 events=[x['index_row']['version_ref'] for x in stored];ck('four-stored-versions-and-three-candidate-response-successors',len(stored)==4 and len(stored_relations)==26 and [x['response_state'] for x in stored]==['submitted','eligible','responded','resolved-for-revision'] and chronology==[{'source':events[i],'target':events[i-1],'succession_effect':'candidate-contest-state-only'} for i in [1,2,3]])
 filing_fields=['challenge_contract_ref','challenger_ref','subject_ref','subject_version_ref','ground','submitted_at'];filing_stable=all(all(x['payload'][n]==stored[0]['payload'][n] for n in filing_fields) for x in stored);ck('stored-filing-core-stable-response-evidence-resolution-fields-change',filing_stable and len({x['node_id'] for x in stored})==1 and len({x['index_row']['sha256'] for x in stored})==4 and stored[1]['payload']['evidence_refs']!=stored[2]['payload']['evidence_refs'] and stored[0]['payload']['resolution_decision_ref']=='none' and stored[3]['payload']['resolution_decision_ref']!='none')
 stored_joins={}
 for label,version in [('Contract',first['payload']['challenge_contract_ref']),('subject',first['payload']['subject_version_ref'])]:
  row=by_version[version];doc=docs['stored_'+label];ok=refs['stored_'+label]['sha256']==row['sha256'] and version.startswith(doc['node_id']+'@');ck('stored-exact-'+label+'-reference-index-binding',ok);stored_joins[label]={'index_row':row,'exact_index_bytes_match':ok,'reference_literal_matches_all_event_revisions':all(x['payload']['challenge_contract_ref' if label=='Contract' else 'subject_version_ref']==version for x in stored),'actual_reference_identity_or_eligibility_authenticated':False}
 static=[]
 for label,class_name,names in [('ChallengeService','ChallengeService',['submit','eligible','respond','_transition','resolve']),('EvidenceService','EvidenceService',['put','get'])]:
  tree=ast.parse(raws[label]);cls=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name==class_name);functions=[x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name in names];texts={x.name:ast.get_source_segment(raws[label].decode(),x) for x in functions};old=next(x for x in index['source_bindings'] if x['path']==refs[label]['path']);static.append({'class':class_name,'selected_functions':names,'source_ref':refs[label],'stored_index_source_sha256':old['sha256'],'stored_source_digest_matches_current_file':old['sha256']==refs[label]['sha256'],'functions_inspected_not_executed':True,'actual_runtime_or_gate_verified':False})
  if label=='EvidenceService':ck('inspected-put-get-exact-revision-and-byte-guards',len(functions)==2 and 'key not in self.records' in texts['put'] and "path.open('xb')" in texts['put'] and 'byte_sha(p.read_bytes()) == digest' in texts['get'] and 'v = parse(p.read_bytes())' in texts['get'])
  else:ck('inspected-transition-new-version-and-separate-fixture-gate',len(functions)==5 and 'self.e.put(value, version)' in texts['_transition'] and "value['payload']['response_state'] = state" in texts['_transition'] and 'isinstance(gate, ControlledGate)' in texts['resolve'] and "'actual_owner_outcome': None" in texts['resolve'] and "'challenged subject changed during disposition'" in texts['resolve'])
 ck('stored-controlled-summary-is-not-real-owner-or-canonical-effect',index['controlled'] is True and index['actual_owner_outcome'] is None and index['canonical_effects_applied']==0 and index['authority_effect']=='none' and docs['stored_cold_summary']['controlled'] is True and docs['stored_cold_summary']['actual_owner_outcome'] is None and docs['stored_cold_summary']['retry_dispatched'] is False)
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 ps=profiles();fs=frames();bindings=[b.ref(p) for p in [b.UNIT/'verify_authority_profile.py',b.UNIT/'build_candidate.py',b.IMPL/'contracts.py',b.IMPL/'verifier.py']];prior=load('../cal.definition.challenge-contract/delivery-manifest.json');b.unchanged(prior['files']+context['sources']+list(refs.values())+bindings);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 report={'schema_version':'definition-assurance-ChallengeEvent-profile/v1-candidate','status':'PASS-for-explicit-Event-revision-hypotheses-and-bounded-current-carrier-stored-candidate-observations','authority_effect':'none','checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','source-checks.json','comparison-selection.json']],'selected_inputs':refs,'profile_control_count':len(ps),'rejected_profile_controls':sum(x['expected_rejection'] for x in ps),'profiles':ps,'finite_history_frame_count':len(fs),'rejected_history_frames':sum(x['expected_rejection'] for x in fs),'finite_history_frames':fs,'actual_check_count':len(checks),'actual_checks':checks,'current_type_registry_rows':len(reg['admitted_contracts']),'admitted_current_type_rows':len(current),'current_Kind_rows':len(kr['entries']),'current_Event_carrier_selection':{'artifact_type_ref':selected['challenge-event']['artifact_type_ref'],'exact_definition_binding':binding,'direct_definition_binding_types':direct,'dedicated_current_carrier_established':True},'related_carrier_observations':observations,'negative_fixture_checks':negatives,'actual_related_schema_probes':probes,'dedicated_Event_schema_probes':special,'embedded_relation_role_probes':embedded,'fixture_literal_join_observations':literal_fixture,'current_Event_endpoint_roles':endpoints,'Kind_TR_schema_gaps':gaps,'all_selected_current_Kind_TR_pair_observations':pairs,'qualifier_reference_shape_probes':qualifier_probes,'stored_candidate_event_revisions':stored,'stored_candidate_relation_observations':stored_relations,'stored_candidate_successor_chain':chronology,'stored_filing_core_fields':filing_fields,'stored_filing_core_stable':filing_stable,'stored_Contract_subject_reference_joins':stored_joins,'inspected_workflow_source_observations':static,'stored_candidate_claim_boundary':{'controlled':True,'actual_owner_outcome':None,'canonical_effects_applied':0,'workflow_reexecuted':False,'complete_pipeline_validation_claimed':False,'stored_response_labels_prove_real_resolution':False},'source_mapping_gaps':{'genus_iff_and_source_precedence_reviewed':False,'exact_Entity_version_attribution_and_eligibility_maps_accepted':False,'recorded_state_payload_equality_proves_complete_byte_or_trace_immutability':False,'business_event_record_revision_and_response_identity_map_accepted':False,'actual_owner_gate_response_or_subject_effect_verified':False},'new_authorities_or_relations_created':0,'actual_event_resolution_or_subject_effect_created':False,'actual_runtime_activated':False,'semantic_ready':False,'source_fidelity':'pending','mechanized_proof':False,'claim_ceiling':'Explicit hypothetical exact record-revision qualification and finite frames; exact dedicated current carrier, permissive shape/role/qualifier observations, four stored candidate revisions and indexed successor/Contract/subject joins. AST source patterns inspected without executing workflow services. Record version, recorded-state coverage, byte denotation, eligibility, attribution and common meaning remain unaccepted. Stored controlled response labels/source or schema success do not prove real owner gates, admission, subject mutation, complete pipeline replay or universal trace proof.'}
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh Event profile differs')
 return report
def main():
 r=verify('--write' in b.sys.argv);print(json.dumps({k:r[k] for k in ['status','profile_control_count','rejected_profile_controls','finite_history_frame_count','rejected_history_frames','actual_check_count','current_type_registry_rows','admitted_current_type_rows','current_Kind_rows','semantic_ready']},indent=2,sort_keys=True))
if __name__=='__main__':main()
