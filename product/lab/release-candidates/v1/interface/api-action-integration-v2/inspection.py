"""Original generic operation.inspect for the independently owned Action journal."""
import base64,time
from .runtime import *

def owns_inspection(service,message):
 lookup=message.get('lookup',{})
 if lookup.get('operation') in OPERATIONS:return True
 b=lookup.get('call_binding')
 if not isinstance(b,dict):return False
 path=service.runtime.root/'calls'/b.get('sha256','invalid')
 if not path.is_file():return False
 service.channel.guard()
 return parse(private(path)).get('original_call_binding')==b

def record_call(service,operation,key,mapped,*,operation_path=None,result=None):
 from .service import save
 b=service.active_original_call_binding
 item={'original_call_binding':b,'operation':operation,'key':key,'scope_ref':service.runtime.grant().scope_ref,'principal_ref':service.channel.context['principal_ref'],'mapped_b64':base64.b64encode(mapped).decode(),'operation_path':operation_path.relative_to(service.runtime.root).as_posix() if operation_path is not None else None,'result':result,'recorded_at':now()}
 save(service.runtime.root/'calls'/b['sha256'],item)

def dispatch_original(service,subject):
 matches=[]
 for path in (service.runtime.root/'operations').iterdir():
  item=parse(private(path));receipt=item.get('result')
  if item['operation']=='action.dispatch' and receipt is not None and binding(receipt['receipt_ref'],P.compact(receipt))==subject:matches.append(item)
 from .service import need
 need(len(matches)==1,'not-found','Exact original Action receipt for owned inspection is unavailable.')
 return base64.b64decode(matches[0]['mapped_b64'],validate=True)

def inspect(service,message,call,inner):
 from .service import need
 need(message['actor']==service.actor(),'unauthorized','Inspector Actor differs from this actual Action channel.')
 need(call['expected_source_cut'] is None or call['expected_source_cut']==service.cut(),'stale-cut','Inspector selected Action source cut differs.')
 need(service.channel.policy['inspection_operations']==['operation.inspect'],'unauthorized','Independent Action inspection permission is unavailable.')
 grant=parse(private(service.runtime.root/'grant.json'));need(grant['inspection_operations']==['operation.inspect'],'unauthorized','Independent private Action grant denies inspection.')
 budget=message['budget'];need(budget['max_actions']==0 and 1<=budget['max_input_bytes']<=service.channel.policy['max_request_bytes'] and 32768<=budget['max_output_bytes']<=service.channel.policy['max_response_bytes'],'budget-exceeded','Inspection budget differs from its independent read-only scope.')
 need(timestamp(budget['deadline'])>time.time(),'deadline-exceeded','Inspection message deadline expired.')
 service.runtime.current_call_deadline=min(service.runtime.current_call_deadline,timestamp(budget['deadline']))
 matches=[];lookup=message['lookup']
 for path in (service.runtime.root/'calls').iterdir():
  item=parse(private(path))
  if 'call_binding' in lookup:
   if item['original_call_binding']==lookup['call_binding']:matches.append(item)
  elif item['operation']==lookup['operation'] and item['key']==lookup['idempotency_key']:matches.append(item)
 need(bool(matches),'not-found','Selected Action call or key is not present in this independently owned journal.')
 # Key lookup selects the latest actual public observation; exact call lookup is immutable.
 item=max(matches,key=lambda row:row['recorded_at'])
 need(item['principal_ref']==service.actor()['principal_ref'] and item['scope_ref']==service.runtime.grant().scope_ref,'unauthorized','Selected Action journal belongs to another current Actor or scope.')
 original=base64.b64decode(item['mapped_b64'],validate=True);check=parse(original)
 check['deadline']=iso(min(service.runtime.current_call_deadline,service.runtime.grant().expires_at,service.runtime.session.expires))
 observed=service.runtime.authority.check(encoded(check),recovery=item['operation']=='action.reconcile')
 need(observed['posture']=='permitted','unauthorized','Current exact Action read authority is unavailable.')
 dispatcher=service.runtime.dispatcher();journal=dispatcher.verify()
 result=item['result'];pending=False
 if item['operation_path'] is not None:
  expected=service.operation_path(item['operation'],item['key'])
  need(item['operation_path']==expected.relative_to(service.runtime.root).as_posix(),'integrity-failed','Owned Action operation mapping differs.')
  operation=parse(private(expected));result=operation.get('result');pending=result is None
 if pending:posture='pending'
 elif item['operation']=='action.dispatch':posture='indeterminate' if result['posture']=='indeterminate' else 'failed' if result['posture'] in ('failed','denied') else 'completed'
 elif item['operation']=='action.reconcile':posture='indeterminate' if result['posture']=='indeterminate' else 'completed'
 else:posture='completed'
 if item['operation']=='action.dispatch':
  selected=parse(original);namespace=[selected['principal_ref'],selected['scope_ref'],selected['idempotency_key']]
  entries=[row for row in journal['entries'] if row['namespace']==namespace]
  need(len(entries)<=1,'integrity-failed','Ambiguous owned Action ledger entry.')
  if entries:
   entry=entries[0];need(entry['fingerprint']==dispatcher.fingerprint(selected,original),'integrity-failed','Exact original Action ledger fingerprint differs.')
   if entry['posture'] in ('completed','failed'):
    posture=entry['posture']
    if pending or result.get('posture')=='indeterminate':result=entry['receipt']
 result_binding=binding('action-operation-result:'+byte_sha(P.compact(result)),P.compact(result)) if result is not None else None
 if result is not None:service.evidence(result_binding['ref'],P.compact(result))
 evidence=[binding('action-ledger:'+dispatcher.expected.ledger_id+':journal',(service.runtime.root/'ledger/journal.json').read_bytes()),binding('action-ledger:'+dispatcher.expected.ledger_id+':counter',(service.runtime.root/'ledger/counter.json').read_bytes())]
 return {'schema_version':'lab-operation-inspect-result/v1-candidate','request_binding':binding(message['request_ref'],inner),'original_call_binding':item['original_call_binding'],'operation':item['operation'],'posture':posture,'result_binding':result_binding,'effect_evidence_bindings':evidence,'reconciliation_required':posture in ('pending','indeterminate'),'retry_allowed':False,'gaps':[],'claim_ceiling':CEILING+' Inspector observes recorded evidence and never dispatches or reconciles.','authority_effect':'none'}
