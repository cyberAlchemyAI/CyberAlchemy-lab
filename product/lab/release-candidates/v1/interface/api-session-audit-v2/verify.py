"""Independent original bytes, closed signatures, live test and process outcome audit."""
import argparse,base64,copy,hashlib,importlib.metadata,importlib.util,json,os,sys
from pathlib import Path
from jsonschema import Draft202012Validator,FormatChecker
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5];API=HERE.parent/'api-v14';checks=[]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
def binding(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes())}
def check(label,value):
 checks.append({'test':label,'result':'PASS' if value else 'FAIL'})
 if not value:raise AssertionError(label)
def exact(row):
 p=ROOT/row.get('path',row.get('ref'));raw=p.read_bytes();check('original bytes '+str(p.relative_to(ROOT)),sha(raw)==row['sha256']);return raw
def main():
 p=argparse.ArgumentParser();p.add_argument('--source-sha256',required=True);a=p.parse_args()
 check('selected audit producer',sha((HERE/'source-manifest.json').read_bytes())==a.source_sha256)
 for row in load(HERE/'source-manifest.json')['files']:exact(row)
 parent=HERE.parent/'context-delivery-v3/receipts/R03-0014.json';check('unchanged selected parent receipt',sha(parent.read_bytes())=='4755b2961df56acbecc6c1e944cb6877fc9fd2c660a5dcd93a84fcb70ee8540b')
 for row in load(parent)['files']:exact(row)
 for row in load(API/'source-manifest.json')['files']:exact(row)
 check('exact selected libraries',all(importlib.metadata.version(k)==v for k,v in {'jsonschema':'4.23.0','cryptography':'46.0.5','referencing':'0.36.2'}.items()))
 name='_cal_api_v14';spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)])
 module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
 K=__import__(name+'.run_session_checks',fromlist=['Sessions']);W=__import__(name+'.workspace',fromlist=['privacy']);SCHEMAS=K.Schemas('a7e194f479942a86992627d1415ef2234587640ededa2cdc4eda473a83ba6cc3')
 tests=load(HERE.parent/'api-session-tests-v4/receipts/0001/tests.json');regression=load(API/'receipts/preparation-regression/0001/terminal.json');legacy=load(API/'receipts/parent-regression/0001/terminal.json')
 check('complete selected 34 Session assertions',tests['result']=='PASS' and tests['tests_run']==34 and tests['errors']==tests['failures']==0 and tests['owned_fixture_root_removed'])
 check('all original preparation guards',regression['result']=='PASS' and regression['tests_run']==47 and regression['terminal_observed'] and regression['exit_code']==0)
 check('all immutable original reader guards',legacy['result']=='PASS' and legacy['tests_run']==157 and legacy['terminal_observed'] and legacy['exit_code']==0)
 check('original 34 contracts retained, eleven implemented',len(SCHEMAS.operations)==34 and len(K.SUPPORTED)==11 and SCHEMAS.profile['implemented_operations']==list(K.SUPPORTED))
 observations=load(HERE.parent/'api-session-tests-v4/receipts/0001/wire-observations.json');seen=set();client_samples=0
 snapshot=load(HERE.parent/'api-session-snapshot-v1/receipts/0001/tests.json');check('actual independently repeated snapshot assertion',snapshot['result']=='PASS' and snapshot['tests_run']==1 and snapshot['errors']==snapshot['failures']==0 and snapshot['owned_fixture_root_removed'])
 snapshot_observations=load(HERE.parent/'api-session-snapshot-v1/receipts/0001/wire-observations.json')
 for i,row in enumerate(observations):
  request=row['original_call'];reply=row['reply'];W.privacy(reply);K.D.EL.no_private_memory(reply)
  if reply['contract_profile_binding']['sha256']=='0'*64:
   check('explicit known intentional client mutation',i==len(observations)-1 and request['operation']==reply['operation']=='lab.status' and reply['kind']=='result' and row['request_byte_sha256']==reply['request_binding']['sha256'] and request['expected_contract_profile_binding']==SCHEMAS.profile_binding)
   client_samples+=1;continue
  check('selected actual reply '+str(i),SCHEMAS.valid('api-reply',reply) and reply['contract_profile_binding']==SCHEMAS.profile_binding and reply['request_binding']['sha256']==row['request_byte_sha256'])
  check('original request schema '+str(i),SCHEMAS.valid('api-call',request))
  if reply['kind']=='result':seen.add(reply['operation'])
 check('one intentional client-mutated sample kept separate',client_samples==1)
 for row in snapshot_observations:
  r=row['reply'];W.privacy(r);K.D.EL.no_private_memory(r);check('immutable supplemental actual returned reply',SCHEMAS.valid('api-reply',r) and r['contract_profile_binding']==SCHEMAS.profile_binding and r['request_binding']['sha256']==row['request_byte_sha256'])
 check('all eleven actual successes under same selected profile',seen==set(K.SUPPORTED))
 process=load(HERE.parent/'api-session-process-v2/receipts/0001/result.json');terminal=load(HERE.parent/'api-session-process-v2/receipts/0001/terminal.json')
 check('actual process proof completed',process['result']==terminal['result']=='PASS' and terminal['exit_code']==0 and terminal['terminal_observed'])
 check('three actual producers terminal including interruption',len(process['children'])==3 and len({c['pid'] for c in process['children']})==3 and all(c['terminal_observed'] for c in process['children']) and sum(c['exit_code']==-9 and c['intentional_interruption'] for c in process['children'])==1 and sum(c['exit_code']==0 for c in process['children'])==2)
 check('candidate custody cleanup and privacy',process['owned_fixture_roots_removed'] and process['canonical_effects_applied']==0 and not process['private_keys_exported'] and not process['short_memory_exported'])
 objects={};events=[];calls={};deliveries={};frame_count=0
 for row in process['files']:
  raw=exact(row);body=json.loads(raw);W.privacy(body)
  if '/objects/' in row['path']:
   check('content addressed object '+str(frame_count),Path(row['path']).stem==sha(raw));objects[sha(raw)]=(raw,body)
  if '/journal/session-' in row['path']:events.append(body)
  if body.get('schema_version')!='lab-original-wire-transcript/v1-candidate':continue
  last=None;context=None
  for frame in body['frames']:
   wire=base64.b64decode(frame['base64_original_bytes'],validate=True);v=K.frame_parse(wire);check('actual original wire frame '+str(frame_count),sha(wire)==frame['sha256']);frame_count+=1;W.privacy(v)
   if frame['direction']=='request':
    last=wire
    if v.get('schema_version')=='lab-api-call/v2-candidate':check('actual call schema '+v['call_id'],SCHEMAS.valid('api-call',v));calls[sha(wire)]=(v,wire)
    else:check('actual proof schema',SCHEMAS.valid('reader-authentication',v))
   elif v.get('schema_version')=='lab-local-reader-authenticated/v1-candidate':context=v['context'];check('actual authenticated context schema',SCHEMAS.valid('reader-authentication',v))
   elif v.get('schema_version')=='lab-api-reply/v2-candidate':
    original=K.frame_parse(last);check('reply original schemas',SCHEMAS.valid('api-reply',v));check('wire/trusted/profile binding',v['request_binding']['sha256']==sha(last) and v['trusted_context_binding']==K.binding(context['context_ref'],K.compact(context)) and v['contract_profile_binding']==SCHEMAS.profile_binding)
    if v['operation']=='context.get' and v['kind']=='result':
     delivery=v['message'];deliveries[sha(K.compact(delivery))]=delivery
     check('Context exact received inner span',delivery['request_binding']['sha256']==sha(K.message_bytes(last)))
   else:check('actual host challenge schema',SCHEMAS.valid('reader-authentication',v))
 # Independently validate exact runtime candidate connections. The ephemeral
 # Session declaration is reconstructed only for its hash; no memory body is exported.
 profile_rows=[row for row in load(HERE.parent/'session-participation-v2/packages/0001/record-index.json') if row['version_ref']==K.R.PROFILE+'@'+K.R.VERSION]
 check('unique immutable exact Profile witness',len(profile_rows)==1)
 profile_raw=exact(profile_rows[0]['original_binding'])
 unique={}
 for event in events:unique[(event['session_ref'],event['sequence'])]=event
 opening_results={digest:body for digest,(raw,body) in objects.items() if body.get('schema_version')=='lab-agent-session-result/v1-candidate'}
 for (sid,sequence),event in unique.items():
  check('exact receipt object binding '+sid,sha(objects[event['result_object_binding']['sha256']][0])==event['session_state_binding']['sha256'])
  check('persistent metadata excludes short memory '+sid,event['short_memory_persisted'] is False and event['authority_effect']=='none')
  for key,kind in [('agent_record','agent-instance'),('classification_record','classification-assignment')]:
   Draft202012Validator(load(ROOT/'authority/artifact-types'/kind/'v1/schema.json'),format_checker=FormatChecker()).validate(event[key])
   check('original carrier schema '+sid+' '+kind,True)
  if sequence:continue
  opened=opening_results[event['session_state_binding']['sha256']];wanted=opened['request_binding']['sha256'];matches=[(request,raw) for request,raw in calls.values() if request['operation']=='session.open' and sha(K.message_bytes(raw))==wanted]
  check('original opening message uniquely resolved '+sid,len(matches)==1);request,wire=matches[0];m=request['message'];delivery=deliveries[opened['context_delivery_binding']['sha256']]
  session=K.R.common('agent-session',sid,event['scope_ref']);session.update(owner_ref=event['principal_ref'],claim_ceiling=K.CLAIM if hasattr(K,'CLAIM') else __import__(name+'.context_sessions',fromlist=['CLAIM']).CLAIM,challenge_route='protocol:R03-owned-Session-review')
  session['payload'].update(agent_instance_ref=event['agent_instance_ref'],assignment_ref=m['assignment']['version_ref'],authority_envelope_ref=m['authority_envelope_binding']['ref'],context_view_ref=delivery['context_view']['version_ref'],ontology_view_ref=delivery['ontology_view']['version_ref'],input_refs=[K.R.INTENT+'@'+K.R.VERSION],policy_refs=[K.R.POLICY],budget_refs=['protocol:exact-opening-budget:'+sha(K.compact(m['budget']))],event_cursor='protocol:source-cut:'+sha(K.compact(event['source_cut'])),session_memory={'selected_input_refs':[delivery['context_view']['version_ref'],delivery['ontology_view']['version_ref']],'working_record_refs':[],'unresolved_questions':[],'expires_with_session':True},termination_state='active')
  session['relation_refs']=[K.R.relation_ref('relation.consumes-view','context-view',delivery['context_view']['version_ref']),K.R.relation_ref('relation.consumes-view','ontology-view',delivery['ontology_view']['version_ref'])]
  Draft202012Validator(load(ROOT/'authority/artifact-types/agent-session/v1/schema.json'),format_checker=FormatChecker()).validate(session)
  known={event['agent_record']['node_id']:K.source.encoded(event['agent_record']),event['classification_record']['node_id']:K.source.encoded(event['classification_record']),sid:K.source.encoded(session)}
  for filename in ['classification-scheme','classification-value']:
   body=load(API/'session-inputs'/(filename+'.json'));known[body['node_id']]=K.source.encoded(body)
  check('seven separate candidate typed connections '+sid,len(event['connection_records'])==7)
  for connection in event['connection_records']:
   record=connection['record'];payload=record['payload'];signature=load(ROOT/connection['signature_binding']['ref']);exact(connection['signature_binding']);contract=signature['payload']
   Draft202012Validator(load(ROOT/'authority/artifact-types/candidates/0013-governance-transaction-surface/impacted-carrier-successors/typed-relation/v3/schema.json')).validate(record)
   check('closed endpoint pair and orthogonal axis '+sid,{'source_kind':payload['source']['kind'],'target_kind':payload['target']['kind']} in contract['allowed_endpoint_pairs'] and connection['axis_ref']==contract['axis_id'])
   qc=contract['qualifier_contract'];Draft202012Validator({'type':'object','additionalProperties':False,'properties':qc['properties'],'required':qc['required_axes']}).validate(payload['qualifiers'])
   for side in ['source','target']:
    ref=connection[side+'_artifact'];endpoint=payload[side];check('exact identity, revision and scope '+sid+' '+side,endpoint['ref']==ref['identity_ref'] and endpoint['version_ref']==ref['version_ref'] and ref['scope_ref']==event['scope_ref'])
    if ref['identity_ref'] in known:check('independent original endpoint digest '+sid+' '+side,sha(known[ref['identity_ref']])==ref['byte_sha256'])
    elif ref['byte_sha256'] in objects:check('generated view endpoint digest '+sid+' '+side,sha(objects[ref['byte_sha256']][0])==ref['byte_sha256'])
    else:check('selected immutable Profile endpoint '+sid,ref['identity_ref']==K.R.PROFILE and ref['version_ref']==profile_rows[0]['version_ref'] and sha(profile_raw)==ref['byte_sha256'])
 check('no completed task or owner outcome inferred',tests['task_complete'] is False and process['task_complete'] is False and process['actual_owner_outcome'] is None and SCHEMAS.profile['actual_owner_outcome'] is None)
 result={'result':'PASS','checks':checks,'wire_frames':frame_count,'actual_session_metadata_events':len(unique),'intentional_client_mutated_samples':client_samples,'actual_public_operations':11,'original_public_operation_obligations':34,'authority_effect':'none','actual_owner_outcome':None,'task_complete':False,'schema_version':'lab-context-session-independent-audit/v1-candidate','claim_ceiling':'Selected candidate runtime, actual original wire and reconstructed ephemeral declaration digest evidence; no exported Session memory, canonical admission, Tool or model dispatch, full API or complete plan.'}
 out=HERE/'result.json';fd=os.open(out,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'wb') as f:f.write(K.source.encoded(result))
 print(json.dumps({'result':'PASS','checks':len(checks),'wire_frames':frame_count,'Session_events':len(unique),'public_operations':11}))
if __name__=='__main__':main()
