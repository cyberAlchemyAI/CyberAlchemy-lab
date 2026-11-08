"""Private caller witness over an already authenticated, actual Machine Session.

This creates no Session, exports no sentinel or RAM hash, and changes no API
callback. Call finish only after the original explicit parent close succeeds.
"""
import base64,contextlib,hashlib,io,json,os,uuid
from pathlib import Path

def need(value,reason):
 if not value:raise ValueError(reason)

class Witness:
 def __init__(self,resource):
  self.resource=resource;self.sentinel=('private-Machine-RAM-'+uuid.uuid4().hex).encode()
  self.forbidden=(self.sentinel,base64.b64encode(self.sentinel),self.sentinel.hex().encode())
  resource.note(self.sentinel);self.held=resource.memory[-1]
  need(bytes(self.held)==self.sentinel,'actual Machine Session note differs')
  self.checked={'wire_replies':0,'captured_stream_bytes':0,'durable_files':0}
  self.replies=[];self.vaults={};self.private_write_refused=False
 def scan(self,raw):
  need(type(raw)is bytes and not any(value in raw for value in self.forbidden),'private Machine RAM reached an observed surface')
 def invoke(self,service,raw,compact,operation,expected_kind,dispatcher=None,expected_code=None):
  streams=io.StringIO(),io.StringIO()
  with contextlib.redirect_stdout(streams[0]),contextlib.redirect_stderr(streams[1]):reply=(service if dispatcher is None else dispatcher).call(raw)
  for stream in streams:
   captured=stream.getvalue().encode();self.scan(captured);self.checked['captured_stream_bytes']+=len(captured)
  wire=compact(reply);self.scan(wire);self.checked['wire_replies']+=1
  if expected_kind=='transport-error':
   need(service.schemas.valid('transport-error',reply) and reply.get('kind') is None
        and reply.get('request_byte_sha256')==hashlib.sha256(raw).hexdigest()
        and reply.get('effect_may_have_started') is False and reply.get('code')==expected_code,
        'Machine malformed transport response differs')
  else:
   need(reply.get('kind')==expected_kind and service.schemas.valid('api-reply',reply)
        and reply.get('request_binding',{}).get('sha256')==hashlib.sha256(raw).hexdigest()
        and reply.get('contract_profile_binding')==service.schemas.profile_binding,
        'Machine privacy call posture or binding differs')
   request=json.loads(raw);row=service.schemas.operations[request['operation']]
   need(service.schemas.protocol_valid(row['result_schema' if expected_kind=='result' else 'error_schema']['resource_uri'],reply['message']),
        'Machine privacy actual domain response differs')
   if expected_code is not None:need(reply['message'].get('code')==expected_code,'Machine privacy causal refusal differs')
  self.replies.append({'operation':operation,'kind':expected_kind,'code':reply.get('message',{}).get('code',reply.get('code')),
      'reply_sha256':hashlib.sha256(wire).hexdigest(),'request_sha256':hashlib.sha256(raw).hexdigest(),
      'actual_schema_and_request_binding_valid':True})
  self.vaults[str(service.vault.root)]=service.vault
  return reply
 def refuse_private_write(self,vault,compact):
  before={p.name for p in (vault.root/'objects').iterdir()}
  try:vault.object(compact({'session_memory':self.sentinel.decode()}))
  except ValueError:pass
  else:raise ValueError('private typed Machine RAM entered Vault')
  need(before=={p.name for p in (vault.root/'objects').iterdir()},'refused Machine RAM write left an object')
  self.private_write_refused=True;self.vaults[str(vault.root)]=vault
 def finish(self,read_private):
  need(self.resource.closed and self.resource.memory==[] and self.resource.lesson_selections=={} and not any(self.held),'explicit close did not erase held Machine RAM')
  need(self.private_write_refused and self.checked['wire_replies']>=4,'complete Machine success/refusal and Vault observations required')
  for root in self.vaults:
   for path in sorted(Path(root).rglob('*')):
    need(not path.is_symlink(),'unexpected link in owned privacy observation')
    if path.is_file():self.scan(read_private(path));self.checked['durable_files']+=1
  return {'result':'PASS-actual-Machine-Session-private-memory-boundaries','held_note_zeroed':True,
          'memory_erased':True,'selection_registry_erased':True,'private_vault_write_refused':True,
          'checked':dict(self.checked),'wire_observations':list(self.replies),'authority_effect':'none',
          'fixture_only':True,'claim_ceiling':'Named actual Machine replies, captured streams and owned Vault files only; no general workflow/export privacy or Tool execution claim.'}

def probe(M,D,selected,parent,machine,opened,provider,dispatcher):
 """Use original context.get/session.inspect and refusals on a real peer."""
 P=M['protocol'];service=machine.service;resource=parent.sessions.live[opened['session_ref']]
 witness=Witness(resource);witness.vaults[str(parent.vault.root)]=parent.vault
 query=D.query(selected,service.sessions.bridge)
 call=provider.call(M,service,'context.get',query)
 witness.invoke(service,P.compact(call),P.compact,'context.get','result',dispatcher)
 actor=service.sessions.bridge.actor()
 inspect={'schema_version':'lab-session-inspect-request/v1-candidate',
          'request_ref':'request:T20-Machine-privacy:'+uuid.uuid4().hex,'actor':actor,
          'session_ref':opened['session_ref'],'budget':{**query['budget'],'max_actions':0},'authority_effect':'none'}
 call=provider.call(M,service,'session.inspect',inspect)
 witness.invoke(service,P.compact(call),P.compact,'session.inspect','result',dispatcher)
 foreign={**inspect,'actor':{**actor,'principal_ref':'principal:privacy-foreign'}}
 call=provider.call(M,service,'session.inspect',foreign)
 witness.invoke(service,P.compact(call),P.compact,'session.inspect:foreign-Actor','error',dispatcher,expected_code='unauthorized')
 witness.invoke(service,b'{not-json',P.compact,'malformed-envelope','transport-error',dispatcher,expected_code='malformed-json')
 witness.refuse_private_write(parent.vault,P.compact)
 return witness
