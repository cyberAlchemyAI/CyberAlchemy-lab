"""Diagnostic joins from original sources; never a caller-supplied replay authority."""
import collections
from jsonschema import Draft202012Validator
from base import *

def snapshot():
 index=load(ORIGINAL/'record-index.json');core=load(ORIGINAL/'core.json');archive=load(ORIGINAL/'native.snapshot');prepared=load(PREPARED/'preparation.json')
 records={r['version_ref']:load(ORIGINAL/r['path']) for r in index}
 families={f:[parse(base64.b64decode(archive['files'][f'{f}/{i:08d}-ontology-{f}:O05:{i}.json']['base64_original_bytes'],validate=True)) for i in range(1,89)] for f in ['semantic','governance']}
 imports=[m for m in prepared['members'] if m['member_class']=='metadata-carrier-admission'];adoptions=[m for m in prepared['members'] if m['member_class']=='representation-adoption-intent']
 intents={original(m['postimage_binding'])['subject_carrier_version_ref']:original(m['postimage_binding']) for m in adoptions}
 return {'index':index,'records':records,'semantic':families['semantic'],'governance':families['governance'],'imports':imports,'adoptions':adoptions,'intents':intents,
  'dispositions':core['dispositions'],'excluded_packages':core['excluded_packages'],'deferred_source_epoch':core['deferred_source_epoch'],'outside_references':core['outside_references'],
  'definition_witnesses':core['definition_witnesses'],'actual_effects':prepared['actual_effects'],'actual_owner_outcome':prepared['actual_owner_outcome'],'final_assembly_obligations':prepared['final_assembly_obligations'],
  'archive_flags':{k:archive[k] for k in ['private_key_included','Session_memory_included','ontology_admission','source_effects_applied']}}

def assess(v):
 """Pure negative-check surface; inputs are diagnostic observations, never grants."""
 checks=[]
 def check(name,x):require(x,name);checks.append({'test':name,'result':'PASS'})
 index=v['index'];records=v['records'];core=load(ORIGINAL/'core.json');profile=load(ONTOLOGY/'migration/adapters/translation-profile.json')
 check('all 220 exact unique carrier rows',len(index)==len({r['version_ref'] for r in index})==len({r['path'] for r in index})==len(records)==220)
 check('exact metadata carrier partition',dict(collections.Counter(r['kind'] for r in index))=={'source':131,'ontology-node':38,'ontology-edge':50,'generated-output':1})
 check('all 140 original dispositions remain exact',v['dispositions']==core['dispositions'] and len(v['dispositions'])==140)
 check('88 adaptations 43 references nine blocked exact revisions',dict(collections.Counter(r['disposition'] for r in v['dispositions']))=={'adapt':88,'reference':43,'block':9})
 check('all exclusions deferred epoch and outside questions retained',v['excluded_packages']==core['excluded_packages'] and len(v['excluded_packages'])==20 and v['deferred_source_epoch']==core['deferred_source_epoch'] and v['outside_references']==core['outside_references'])
 check('no source effects or archive key memory adoption',v['archive_flags']=={'private_key_included':False,'Session_memory_included':False,'ontology_admission':False,'source_effects_applied':0})
 check('no actual owner outcome or effects',v['actual_owner_outcome'] is None and set(v['actual_effects'])==set(load(PREPARED/'preparation.json')['actual_effects']) and not any(v['actual_effects'].values()))
 check('four exact Definition voice witnesses retained',v['definition_witnesses']==core['definition_witnesses'] and len(v['definition_witnesses'])==4)
 for d in v['definition_witnesses'].values():
  w=d['witness'];selected=original(w['source_binding'])
  for token in w['selector'].strip('/').split('/'):selected=selected[token]
  require(sha(json.dumps(selected,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode())==w['selector_sha256']==d['reference']['selector_sha256'],'Definition scientific-formal selector differs')
 definitions={d['reference']['definition_id']:d['reference'] for d in v['definition_witnesses'].values()}
 check('complete final assembly obligations retained',v['final_assembly_obligations']==load(PREPARED/'preparation.json')['final_assembly_obligations'])
 imports=v['imports'];adoptions=v['adoptions'];intents=v['intents']
 check('220 metadata and 88 separate adoption members',len(imports)==len({m['member_ref'] for m in imports})==220 and len(adoptions)==len({m['member_ref'] for m in adoptions})==len(intents)==88)
 check('metadata admission and ontology adoption axes separate',all(m['requested_axes']['metadata_carrier_admission'] and not m['requested_axes']['ontology_representation_adoption'] for m in imports) and all(m['requested_axes']['ontology_representation_adoption'] and not m['requested_axes']['metadata_carrier_admission'] for m in adoptions))
 check('candidate protocol owners never final accountable owners',all(m['scope']['fixture_owner_is_final_owner'] is False and m['actual_owner_outcome'] is None and not m['current_owner_authority_verified'] for m in imports))
 check('all adoption member outcomes and denied axes ungranted',all(m['actual_owner_outcome'] is None and not m['current_owner_authority_verified'] and not any(m['requested_axes'][k] for k in ['source_semantic_admission','source_body_import','source_execution','public_export','runtime_activation','source_retirement','new_action_authorization','domain_instance_admission','global_relation_creation']) for m in imports+adoptions))
 check('no metadata admission of original semantics or domain conformance',all(not m['scope']['source_semantic_admission'] and not m['scope']['domain_instance_conformance'] for m in imports))
 check('exact source postimage coverage',{m['scope']['exact_version_ref'] for m in imports}==set(records))
 for m in imports:
  row=next(r for r in index if r['version_ref']==m['scope']['exact_version_ref'])
  require(m['postimage_binding']['sha256']==m['targets'][1]['sha256']==row['sha256'] and m['scope']['schema_binding']==row['schema_binding'],'metadata source/postimage/schema digest join differs')
 checks.append({'test':'220 independent exact schema/source/postimage joins','result':'PASS'})
 semantic=v['semantic'];governance=v['governance']
 check('separate complete semantic governance event cursors',len(semantic)==len(governance)==88 and [s['semantic_cursor'] for s in semantic]==list(range(1,89)) and [g['governance_cursor'] for g in governance]==list(range(1,89)))
 check('88 unique event and subject identities',len({s['event_id'] for s in semantic})==len({s['subject_identity']['subject_id'] for s in semantic})==len({g['event_id'] for g in governance})==88)
 smap={s['subject_identity']['subject_id']:s for s in semantic};gmap={g['semantic_ref']['semantic_event_id']:g for g in governance}
 check('every governance event joins exact semantic tuple',all(gmap[s['event_id']]['semantic_ref']=={'semantic_event_id':s['event_id'],'semantic_event_digest':s['event_digest'],'semantic_cursor':s['semantic_cursor']} for s in semantic))
 check('nested governance semantic refs and native identities exact',all(g['complete_resulting_governance_state']['semantic_ref']==g['semantic_ref'] for g in governance) and all(s['complete_resulting_semantic_state']['identity']==s['subject_identity'] for s in semantic))
 check('unknown evidence and commitment confidence retained',all(g['complete_resulting_governance_state']['evidence_confidence']==g['complete_resulting_governance_state']['commitment_confidence']=={'scheme_ref':'protocol:O02-unassessed-confidence/v1','level':'not-assessed'} for g in governance))
 check('candidate governance maturity and authority separate',all(g['complete_resulting_governance_state']['candidate_or_maturity_status']=='candidate-unadmitted' and g['complete_resulting_governance_state']['authority_effect']=='none' for g in governance))
 check('challenge contract owner modes and resolution gate retained',all(g['complete_resulting_governance_state']['challenge_contract']['valid_challenge_modes']==['evidence','contradiction','owner_review'] and g['complete_resulting_governance_state']['challenge_contract']['resolution_gate']=='protocol:O05-exact-R08-review' and g['complete_resulting_governance_state']['challenge_contract']['owner_route']=='protocol:O05-exact-candidate-review' for g in governance))
 nodes={r['node_id']:records[r['version_ref']] for r in index if r['kind']=='ontology-node'};edges=[records[r['version_ref']] for r in index if r['kind']=='ontology-edge']
 check('50 local interpretations with original direction',collections.Counter(e['payload']['direction'] for e in edges)=={'directed':49,'symmetric':1})
 check('closed twenty-predicate source-local vocabulary',len(profile['predicates'])==20 and {e['payload']['relation_type_ref'] for e in edges}=={profile['local_predicate_prefix']+p+'/v1-candidate' for p in profile['predicates']})
 check('local interpretations never global Typed Relations',all(e['payload']['edge_mode']=='local-interpretation' and e['payload']['global_typed_relation_binding'] is None and e['payload']['replay_source'] is False for e in edges))
 for row in index:
  record=records[row['version_ref']];require(record['node_id']==row['node_id'] and record['kind']==row['kind'] and record['authority_effect']=='none','carrier identity/kind/authority differs')
  if row['kind']=='ontology-node':
   p=record['payload'];r=p['represented_subject'];require(r['kind']=='source' and r['version_ref'] in records,'ontology node label collapsed into domain endpoint')
   represented=records[r['version_ref']];source_row=next(x for x in index if x['version_ref']==r['version_ref'])
   require(represented['kind']=='source' and r['ref']==represented['node_id'] and r['digest']==source_row['sha256'],'represented exact source revision/digest differs')
   s=smap[row['node_id']];require(s['complete_resulting_semantic_state']['semantic_definition_refs']==[definitions['cal.definition.ontology-node'],definitions['cal.definition.source']],'native source/node Definition selectors differ');properties=s['complete_resulting_semantic_state']['typed_properties']['values']
   require(properties['represented_kind']==properties['carrier_kind']=='source' and properties['version_ref']==r['version_ref'] and properties['record_sha256']==r['digest'],'native represented revision/digest bridge differs')
   require(p['governance_binding']['semantic_event_ref']==gmap[s['event_id']]['semantic_ref'] and p['governance_binding']['governance_event_refs']==[gmap[s['event_id']]['event_id']],'rich node native semantic/governance tuple differs')
   require(p['replay_source'] is False and p['governance_binding']['authority_effect']=='none','rich projection became source or authority')
  elif row['kind']=='ontology-edge':
   p=record['payload'];s=smap[row['node_id']];state=s['complete_resulting_semantic_state'];q=p['closed_qualifiers']
   require(p['source_node_ref'] in nodes and p['target_node_ref'] in nodes,'missing local endpoint')
   require(p['source_node_ref']==state['source_node_id'] and p['target_node_ref']==state['target_node_id'] and p['direction']==state['direction'],'native endpoint direction bridge differs')
   require(q['source_node_version_ref']==nodes[p['source_node_ref']]['payload']['represented_subject']['version_ref'] and q['target_node_version_ref']==nodes[p['target_node_ref']]['payload']['represented_subject']['version_ref'],'exact source endpoint versions differ')
   require(p['semantic_event_ref']==gmap[s['event_id']]['semantic_ref'],'rich edge semantic tuple differs')
  if row['kind'] in ['ontology-node','ontology-edge']:
   s=smap[row['node_id']];g=gmap[s['event_id']];intent=intents[row['version_ref']];am=next(m for m in adoptions if m['member_ref']=='protocol:O06:ontology-adoption:'+row['version_ref'])
   require(intent['subject_carrier_version_ref']==row['version_ref'] and intent['metadata_record_binding']==binding(ORIGINAL/row['path']) and intent['archive_binding']==binding(ORIGINAL/'native.snapshot'),'adoption exact metadata/archive/body bindings differ')
   require(am['scope']['exact_semantic_tuple']==intent['semantic_tuple'] and am['scope']['exact_predecessor_governance_tuple']==intent['predecessor_governance_tuple'],'adoption member scope/intent differs')
   require(intent['semantic_tuple']==g['semantic_ref'] and intent['predecessor_governance_tuple']=={k:g[k] for k in ['event_id','event_digest','governance_cursor']},'adoption exact semantic/predecessor governance tuple differs')
   rule=intent['consequence_rule'];require(rule['preserve_original_semantic_bytes'] and not rule['old_candidate_event_relabeling_allowed'] and rule['evidence_confidence']==rule['commitment_confidence']=='not-assessed' and rule['provenance_requires_actual_owner_Decision_binding'] and rule['owner_route_requires_verified_current_accountable_owner'] and not rule['source_meaning_admitted'],'adoption authority/confidence/source axes collapsed')
   require(sha(encoded(intent))==am['postimage_binding']['sha256'],'adoption exact body digest differs')
   require(intent['owner_outcome_required'] and intent['verified_owner_required'] and intent['actual_owner_outcome'] is None and intent['authority_effect']=='none' and intent['final_event_bytes_and_owner_core_must_be_materialized_at']=='S02' and not intent['permanent_runtime_installation_authorized'],'adoption intent falsely applied or finalized')
  Draft202012Validator(original(row['schema_binding'])).validate(record)
  require(sha(encoded(record))==row['sha256'],'carrier original bytes differ')
 checks.extend({'test':x,'result':'PASS'} for x in ['38 node-to-Source revision/digest bridges','50 qualified original endpoint/direction bridges','88 rich/native semantic and governance bridges','88 independent adoption consequence and predecessor bridges','all inherited carrier schemas and original bytes'])
 return {'result':'PASS','checks':checks,'counts':{'carriers':220,'items':140,'blocked_revisions':9,'excluded_packages':20,'native_semantic':88,'native_governance':88,'local_edges':50,'directed':49,'symmetric':1,'adoption_intents':88},
  'authority_effect':'none','actual_owner_outcome':None,'source_semantic_admission':False,'current_operation_permission':False,'admitted_coherence':False}

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--manifest-sha256',required=True);p.add_argument('--output',required=True);a=p.parse_args()
 source_guard(a.manifest_sha256);v=snapshot();result=assess(v);source_guard(a.manifest_sha256);emit(Path(a.output),result);print(json.dumps({'result':'PASS','checks':len(result['checks']),'output_binding':binding(Path(a.output))}))
