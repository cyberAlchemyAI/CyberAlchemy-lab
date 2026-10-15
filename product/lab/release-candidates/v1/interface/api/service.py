"""Authenticated bounded API dispatch; original result/error schemas are enforced."""
import re
from datetime import timezone
from handlers import *


def transport(code,raw=None,call_id=None):
    return {'schema_version':'lab-api-transport-error/v1-candidate','call_id':call_id,
        'request_byte_sha256':source.sha(raw) if raw is not None else None,'code':code,
        'public_message':{'malformed-json':'Input is not a supported bounded UTF-8 JSON object.',
            'invalid-envelope':'Call does not match its exact declared envelope.',
            'unauthenticated-channel':'This channel has no current verified reader authentication.',
            'unsupported-protocol':'Protocol version is not supported.',
            'unsupported-operation':'This operation is not implemented by the selected API handler package.',
            'invalid-call-id':'Call identifier is invalid or already used on this connection.',
            'input-too-large':'Input exceeds the host request budget.','deadline-exceeded':'Request deadline has expired.'}[code],
        'effect_may_have_started':False,'recovery_policy':'no-retry','authority_effect':'none'}


class Service:
    def __init__(self,view,channel,schemas):
        self.channel=channel;self.schemas=schemas;self.handlers=ReadHandlers(view,channel);self.seen=set()
        self.code_files={name:source.sha((HERE/name).read_bytes()) for name in ('protocol.py','auth.py','handlers.py','service.py','serve.py','authentication.schema.json')}
        self.handler_binding={'ref':str((HERE/'handlers.py').relative_to(ROOT)),'sha256':self.code_files['handlers.py']}
    def error(self,call,raw,message_raw,error):
        return self.reply(call,raw,{'schema_version':'lab-error-result/v1-candidate',
            'request_binding':binding('message:'+self.channel.connection+':'+call['call_id'],message_raw),
            'code':error.code,'message':error.message,'gaps':[],'retry_policy':'no-retry',
            'evidence_bindings':[],'authority_effect':'none'},kind='error')
    def reply(self,call,raw,message,kind='result'):
        context=self.channel.context
        value={'schema_version':'lab-api-reply/v1-candidate','call_id':call['call_id'],'operation':call['operation'],
            'request_binding':binding('call:'+self.channel.connection+':'+call['call_id'],raw),
            'trusted_context_binding':binding(context['context_ref'],compact(context)),
            'handler_binding':self.handler_binding,
            'observed_at':now().isoformat(),'kind':kind,'message':message}
        source.require(self.schemas.valid('api-reply',value),'actual API result/error violates its original exact contract')
        return value
    def call(self,raw):
        try:context=self.channel.guard()
        except Exception:return transport('unauthenticated-channel',raw)
        if len(raw)>context['limits']['max_request_bytes']:return transport('input-too-large',raw)
        try:call=frame_parse(raw)
        except Exception:return transport('malformed-json',raw)
        if not isinstance(call,dict):return transport('invalid-envelope',raw)
        if call.get('schema_version')!='lab-api-call/v1-candidate':return transport('unsupported-protocol',raw)
        name=call.get('operation')
        if name not in self.schemas.operations or name not in SUPPORTED:return transport('unsupported-operation',raw)
        identifier=call.get('call_id')
        if not isinstance(identifier,str) or re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9:._/-]{0,255}',identifier) is None or identifier in self.seen:
            return transport('invalid-call-id',raw)
        if not self.schemas.valid('api-call',call):return transport('invalid-envelope',raw,identifier)
        if len(self.seen)>=self.channel.policy['max_calls']:return transport('input-too-large',raw,identifier)
        self.seen.add(identifier)
        message=call['message'];inner=message_bytes(raw)
        try:
            self.schemas.guard()
            if any(source.sha((HERE/name).read_bytes())!=digest for name,digest in self.code_files.items()):
                raise ApplicationError('integrity-failed','Captured API handler code changed during this connection.')
            if call['caller_context_ref']!=context['context_ref']:raise ApplicationError('unauthorized','Opaque context reference is not this verified connection context.')
            expected_actor={k:context[k] for k in ('principal_ref','agent_instance_ref','assignment_ref','session_ref')}
            expected_actor['role_assignment_refs']=context['role_assignment_bindings']
            if message['actor']!=expected_actor:raise ApplicationError('unauthorized','Actor claims differ from verified transport context.')
            effective=min(instant(call['deadline']),instant(message['budget']['deadline']),instant(context['limits']['deadline']))
            if effective<=now():raise ApplicationError('deadline-exceeded','Strictest request/policy deadline has expired.')
            if message['budget']['max_actions']!=0:raise ApplicationError('unauthorized','This independently provisioned reader scope authorizes zero actions.')
            if message['budget']['max_input_bytes']<len(raw):raise ApplicationError('budget-exceeded','Caller request byte budget is too small.')
            ceiling=min(call['max_response_bytes'],message['budget']['max_output_bytes'],context['limits']['max_response_bytes'])
            if ceiling<4096:raise ApplicationError('budget-exceeded','Effective response byte budget is too small.')
            request=binding('message:'+self.channel.connection+':'+identifier,inner)
            function=self.handlers.status if name=='lab.status' else self.handlers.catalog
            domain=function(message,request,call['expected_source_cut'])
            if effective<=now():raise ApplicationError('deadline-exceeded','Strictest deadline expired while reading; no effect was dispatched.')
            result=self.reply(call,raw,domain)
            if len(compact(result))>ceiling:raise ApplicationError('budget-exceeded','Complete result exceeds the effective byte budget; no partial body returned.')
            self.channel.guard()
            return result
        except ApplicationError as error:
            return self.error(call,raw,inner,error)
        except Exception:
            return self.error(call,raw,inner,ApplicationError('integrity-failed','Selected source, authentication policy or handler could not be verified.'))
    def close(self):self.handlers.close();self.seen.clear();self.channel.close()
