"""Authenticated bounded API dispatch; original result/error schemas are enforced."""
import re
from datetime import timezone
from handlers import *
from workspace import Vault
from candidate import CandidateHandlers
import jcs


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
        self.channel=channel;self.schemas=schemas;self.handlers=ReadHandlers(view,channel,schemas);self.seen=set()
        self.vault=Vault(channel);self.candidates=CandidateHandlers(self.handlers,self.vault,schemas)
        self.code_files={name:source.sha((HERE/name).read_bytes()) for name in ('protocol.py','auth.py','handlers.py','service.py','serve.py','artifact_model.py','projection.py','representations.py','authentication.schema.json','workspace.py','workspace.schema.json','candidate.py','jcs.py')}
        self.handler_binding={'ref':str((HERE/'handlers.py').relative_to(ROOT)),'sha256':self.code_files['handlers.py']}
    def error(self,call,raw,message_raw,error):
        return self.reply(call,raw,{'schema_version':'lab-error-result/v1-candidate',
            'request_binding':binding('message:'+self.channel.connection+':'+call['call_id'],message_raw),
            'code':error.code,'message':error.message,'gaps':[],'retry_policy':'reconcile-first' if error.code in ('indeterminate','recovery-required') else 'no-retry',
            'evidence_bindings':[],'authority_effect':'none'},kind='error')
    def reply(self,call,raw,message,kind='result'):
        context=self.channel.context
        value={'schema_version':'lab-api-reply/v2-candidate','contract_profile_binding':self.schemas.profile_binding,'call_id':call['call_id'],'operation':call['operation'],
            'request_binding':binding('call:'+self.channel.connection+':'+call['call_id'],raw),
            'trusted_context_binding':binding(context['context_ref'],compact(context)),
            'handler_binding':binding(str((HERE/'candidate.py').relative_to(ROOT)),(HERE/'candidate.py').read_bytes()) if call['operation'] in ('change.prepare','change.validate','operation.inspect') else self.handler_binding,
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
        if call.get('schema_version')!='lab-api-call/v2-candidate':return transport('unsupported-protocol',raw)
        name=call.get('operation')
        if name not in self.schemas.operations or name not in SUPPORTED:return transport('unsupported-operation',raw)
        identifier=call.get('call_id')
        if not isinstance(identifier,str) or re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9:._/-]{0,255}',identifier) is None or identifier in self.seen:
            return transport('invalid-call-id',raw)
        if not self.schemas.valid('api-call',call):return transport('invalid-envelope',raw,identifier)
        if len(self.seen)>=self.channel.policy['max_calls']:return transport('input-too-large',raw,identifier)
        self.seen.add(identifier)
        message=call['message'];inner=message_bytes(raw);effect_started=False;namespace=None
        try:
            self.schemas.guard()
            expected_profile=call['expected_contract_profile_binding']
            if expected_profile!=self.schemas.profile_binding and not (name=='lab.status' and expected_profile is None):
                raise ApplicationError('invalid-contract','Call does not select this exact reader contract profile.')
            if any(source.sha((HERE/name).read_bytes())!=digest for name,digest in self.code_files.items()):
                raise ApplicationError('integrity-failed','Captured API handler code changed during this connection.')
            if call['caller_context_ref']!=context['context_ref']:raise ApplicationError('unauthorized','Opaque context reference is not this verified connection context.')
            expected_actor={k:context[k] for k in ('principal_ref','agent_instance_ref','assignment_ref','session_ref')}
            expected_actor['role_assignment_refs']=context['role_assignment_bindings']
            if message.get('actor',expected_actor)!=expected_actor:raise ApplicationError('unauthorized','Actor claims differ from verified transport context.')
            budget=message.get('budget',{'max_actions':context['limits']['max_actions'],'max_input_bytes':context['limits']['max_request_bytes'],
                'max_output_bytes':context['limits']['max_response_bytes'],'deadline':context['limits']['deadline']})
            effective=min(instant(call['deadline']),instant(budget['deadline']),instant(context['limits']['deadline']))
            if effective<=now():raise ApplicationError('deadline-exceeded','Strictest request/policy deadline has expired.')
            effectful=name in ('change.prepare','change.validate')
            if (not effectful and budget['max_actions']!=0) or (effectful and min(budget['max_actions'],context['limits']['max_actions'])<1):
                raise ApplicationError('unauthorized','Requested action budget differs from this operation and independently provisioned scope.')
            if budget['max_input_bytes']<len(raw):raise ApplicationError('budget-exceeded','Caller request byte budget is too small.')
            ceiling=min(call['max_response_bytes'],budget['max_output_bytes'],context['limits']['max_response_bytes'])
            if ceiling<4096:raise ApplicationError('budget-exceeded','Effective response byte budget is too small.')
            request=binding('message:'+self.channel.connection+':'+identifier,inner)
            if effectful:
                if not isinstance(call['idempotency_key'],str) or not call['idempotency_key']:
                    raise ApplicationError('invalid-contract','Candidate effects require an envelope idempotency key.')
                if name=='change.prepare' and call['idempotency_key']!=message['idempotency_key']:
                    raise ApplicationError('invalid-contract','Preparation command key and envelope key disagree.')
                try:jcs.fingerprint(call,context)
                except Exception:raise ApplicationError('invalid-contract','Control inputs are outside the independently selected JCS domain.')
                self.candidates.preflight(message,call['expected_source_cut'])
                if effective<=now():raise ApplicationError('deadline-exceeded','Deadline expired before candidate journal claim.')
                try:namespace,fp,prior,record,fresh=self.vault.claim(call,raw,context)
                except Exception as error:
                    if 'budget exhausted' in str(error):raise ApplicationError('budget-exceeded','Independently provisioned workspace action budget exhausted.')
                    raise
                effect_started=True
                if prior['fingerprint']!=fp:
                    effect_started=False
                    raise ApplicationError('idempotency-conflict','Key is already bound to different exact control inputs; no new effect was dispatched.')
                if not fresh:
                    if record is None:raise ApplicationError('recovery-required','Key has a durable claim but no complete result. Use operation.inspect; do not redispatch.')
                    domain=source.parse(self.vault.object_read(record['domain_binding']))
                    return self.deliver_recorded(call,raw,domain,record['posture'],ceiling,effective)
                if effective<=now():raise ApplicationError('indeterminate','Deadline expired after durable claim; inspect the operation before any reconciliation.')
                if name=='change.prepare':domain,evidence=self.candidates.prepare(message,request,call['expected_source_cut'],inner)
                else:
                    domain,details=self.candidates.validate(message,request,call['expected_source_cut'],inner);evidence=details['evidence']
                self.channel.guard();self.schemas.guard()
                self.vault.finish(namespace,domain,evidence)
                return self.deliver_recorded(call,raw,domain,'completed',ceiling,effective)
            if name=='operation.inspect':domain=self.candidates.inspect(message,request,call['expected_source_cut'])
            else:
                function={'lab.status':self.handlers.status,'catalog.get':self.handlers.catalog,
                    'artifact.inspect':self.handlers.inspect,'artifact.query':self.handlers.query}[name]
                domain=function(message,request,call['expected_source_cut'])
            if effective<=now():raise ApplicationError('deadline-exceeded','Strictest deadline expired while reading; no effect was dispatched.')
            result=self.reply(call,raw,domain)
            if len(compact(result))>ceiling:raise ApplicationError('budget-exceeded','Complete result exceeds the effective byte budget; no partial body returned.')
            self.channel.guard()
            return result
        except ApplicationError as error:
            if effect_started and error.code not in ('indeterminate','recovery-required'):
                error=ApplicationError('indeterminate','Candidate operation may have staged evidence. Inspect its exact durable operation record before reconciliation.')
            return self.error(call,raw,inner,error)
        except Exception:
            return self.error(call,raw,inner,ApplicationError('indeterminate' if effect_started else 'integrity-failed',
                'Candidate operation may have started; use its scoped operation inspection record.' if effect_started else 'Selected source, authentication policy or handler could not be verified.'))
    def deliver_recorded(self,call,raw,domain,posture,ceiling,effective):
        if effective<=now():raise ApplicationError('indeterminate','Deadline expired after candidate claim/evidence; the recorded outcome is available through operation.inspect.')
        result=self.reply(call,raw,domain,kind='error' if posture=='failed' else 'result')
        if len(compact(result))>ceiling:raise ApplicationError('indeterminate','Complete outcome is retained privately and exceeds this response budget; use operation.inspect for the exact result binding.')
        self.channel.guard();return result
    def close(self):self.handlers.close();self.seen.clear();self.channel.close()
