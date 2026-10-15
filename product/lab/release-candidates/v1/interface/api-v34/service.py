"""Authenticated bounded API dispatch; original result/error schemas are enforced."""
import re
from datetime import timezone
from .handlers import *
from .workspace import Vault
from .candidate import CandidateHandlers
from . import jcs
from .context_sessions import ContextSessions
from .custody_context_sessions import ContextSessions as CustodyContextSessions
from .projection_refresh import ProjectionRefresh
from .file_exports import FileExports
from .review_preparation import ReviewPreparation


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
        self.projections=ProjectionRefresh(self.handlers,self.vault,schemas)
        self.exports=FileExports(self.handlers,self.vault,schemas)
        self.sessions=CustodyContextSessions(view,channel,schemas,self.vault) if hasattr(view,'custody_signed_sources') and channel.policy['session_control'] is not None else ContextSessions(view,channel,schemas,self.vault) if hasattr(view,'fresh_signed_sources') and channel.policy['session_control'] is not None else None
        self.code_files={name:source.sha((HERE/name).read_bytes()) for name in ('protocol.py','auth.py','handlers.py','service.py','serve.py','artifact_model.py','projection.py','projection_refresh.py','representations.py','authentication.schema.json','workspace.py','workspace.schema.json','candidate.py','jcs.py','context_sessions.py','custody_context_sessions.py','source_bridge.py','guard.py','guarded_reads.py','scope_preparation.py','scope-preparation-profile.json','file_exports.py','export_kernel.py','review_preparation.py','review-routing.schema.json')}
        self.handler_binding={'ref':str((HERE/'handlers.py').relative_to(ROOT)),'sha256':self.code_files['handlers.py']}
    def select_review(self,message,outer):
        selected=self.vault.inputs.get('candidate:review-routing')
        if selected is None:raise ApplicationError('closure-missing','Independently selected exact review routing is unavailable in this owned workspace.')
        try:
            raw=self.vault.material({'ref':selected['ref'],'sha256':selected['sha256']})
            builder=ReviewPreparation(self,self.vault.root/selected['path'],source.sha(raw),source.sha((HERE/'source-manifest.json').read_bytes()))
            builder.preflight(message,outer)
            return builder
        except ApplicationError:raise
        except Exception:raise ApplicationError('invalid-contract','Exact independent review routing, source cut, core order or original proposal could not be verified.')
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
            'handler_binding':binding(str((HERE/'review_preparation.py').relative_to(ROOT)),(HERE/'review_preparation.py').read_bytes()) if call['operation']=='proposal.review' else binding(str((HERE/'file_exports.py').relative_to(ROOT)),(HERE/'file_exports.py').read_bytes()) if call['operation']=='files.materialize' else binding(str((HERE/'projection_refresh.py').relative_to(ROOT)),(HERE/'projection_refresh.py').read_bytes()) if call['operation']=='projection.refresh' else binding(str((HERE/'candidate.py').relative_to(ROOT)),(HERE/'candidate.py').read_bytes()) if call['operation'] in ('change.prepare','change.validate','operation.inspect') else binding(str((HERE/('custody_context_sessions.py' if isinstance(self.sessions,CustodyContextSessions) else 'context_sessions.py')).relative_to(ROOT)),(HERE/('custody_context_sessions.py' if isinstance(self.sessions,CustodyContextSessions) else 'context_sessions.py')).read_bytes()) if call['operation'] in ('context.get','session.open','session.close','session.inspect') else self.handler_binding,
            'observed_at':now().isoformat(),'kind':kind,'message':message}
        source.require(self.schemas.valid('api-reply',value),'actual API result/error violates its original exact contract')
        return copy.deepcopy(value)
    def call(self,raw):
        try:parsed=frame_parse(raw)
        except Exception:parsed=None
        self.channel.bound_termination_call=isinstance(parsed,dict) and parsed.get('operation')=='session.close' and self.schemas.valid('api-call',parsed)
        try:return self._call(raw)
        finally:self.channel.bound_termination_call=False
    def _call(self,raw):
        from .auth import FACT_SCOPE
        try:FACT_SCOPE.require_outside_scope()
        except ValueError:return transport('unauthenticated-channel',raw)
        try:context=self.channel.guard()
        except Exception:
            if self.sessions is not None:
                try:self.sessions.dispose_all()
                except Exception:pass
            return transport('unauthenticated-channel',raw)
        if len(raw)>context['limits']['max_request_bytes']:return transport('input-too-large',raw)
        try:call=frame_parse(raw)
        except Exception:return transport('malformed-json',raw)
        if not isinstance(call,dict):return transport('invalid-envelope',raw)
        if call.get('schema_version')!='lab-api-call/v2-candidate':return transport('unsupported-protocol',raw)
        name=call.get('operation')
        if name not in self.schemas.operations or name not in SUPPORTED or name not in self.channel.policy['allowed_operations']:return transport('unsupported-operation',raw)
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
            effectful=name in ('change.prepare','change.validate','session.open','session.close','projection.refresh','files.materialize','proposal.review')
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
                # Recorded outcomes are historical operation evidence. Exact
                # retries do not rerun creation or require an old live resource.
                old,recorded=self.vault.lookup({'operation':name,'idempotency_key':call['idempotency_key']},context)
                if old is not None:
                    if old['fingerprint']!=jcs.fingerprint(call,context):raise ApplicationError('idempotency-conflict','Key names different exact control inputs.')
                    if recorded is None:raise ApplicationError('recovery-required','Durable key is pending; inspect without redispatch.')
                    domain=source.parse(self.vault.object_read(recorded['domain_binding']))
                    if name=='files.materialize':domain=self.exports.readback(message,call['expected_source_cut'],effective,domain)
                    return self.deliver_recorded(call,raw,domain,recorded['posture'],ceiling,effective)
                session_plan=None
                if name in ('session.open','session.close'):
                    if self.sessions is None:raise ApplicationError('unresolved-reference','Fresh source-bound Session host is unavailable for this branch.')
                    if name=='session.open':session_plan=self.sessions.open_plan(message,call['expected_source_cut'])
                    else:
                        row=self.sessions.selected(message['session_ref'])
                        if row['source_cut']!=call['expected_source_cut'] or row['agent_instance_ref']!=message['agent_instance_ref'] or row['session_state_binding']!=message['expected_session_binding']:raise ApplicationError('conflict','Exact Session preimage or Agent differs.')
                        if message['eligible_audit_bindings']!=[]:raise ApplicationError('unauthorized','Audit export eligibility is unresolved.')
                        if row['posture']!='active' or row['session_ref'] not in self.sessions.live:raise ApplicationError('recovery-required','Lost or closed Session cannot be redispatched.')
                elif name=='projection.refresh':self.projections.preflight(message,call['expected_source_cut'])
                elif name=='files.materialize':self.exports.preflight(message,call['expected_source_cut'],effective)
                elif name=='proposal.review':self.review_builder=self.select_review(message,call['expected_source_cut'])
                else:self.candidates.preflight(message,call['expected_source_cut'])
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
                    if name=='files.materialize':domain=self.exports.readback(message,call['expected_source_cut'],effective,domain)
                    return self.deliver_recorded(call,raw,domain,record['posture'],ceiling,effective)
                if effective<=now():raise ApplicationError('indeterminate','Deadline expired after durable claim; inspect the operation before any reconciliation.')
                if name=='session.open':domain,evidence=self.sessions.open(message,request,call['expected_source_cut'],inner,session_plan)
                elif name=='session.close':domain,evidence=self.sessions.close_session(message,request,call['expected_source_cut'])
                elif name=='change.prepare':domain,evidence=self.candidates.prepare(message,request,call['expected_source_cut'],inner)
                elif name=='projection.refresh':domain,evidence=self.projections.refresh(message,request,call['expected_source_cut'],inner)
                elif name=='files.materialize':domain,evidence=self.exports.materialize(message,request,call['expected_source_cut'],effective,inner)
                elif name=='proposal.review':domain,evidence=self.review_builder.build(message,inner)
                else:
                    domain,details=self.candidates.validate(message,request,call['expected_source_cut'],inner);evidence=details['evidence']
                self.channel.guard();self.schemas.guard()
                self.vault.finish(namespace,domain,evidence)
                return self.deliver_recorded(call,raw,domain,'completed',ceiling,effective)
            if name in ('context.get','session.inspect'):
                if self.sessions is None:raise ApplicationError('unresolved-reference','Fresh source-bound Session host is unavailable for this branch.')
                domain=self.sessions.view_get(message,request,call['expected_source_cut'],inner) if name=='context.get' else self.sessions.inspect(message,request,call['expected_source_cut'])
            elif name=='operation.inspect':domain=self.candidates.inspect(message,request,call['expected_source_cut'])
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
    def close(self):
        try:
            if self.sessions is not None:self.sessions.close()
        finally:self.handlers.close();self.seen.clear();self.channel.close()
