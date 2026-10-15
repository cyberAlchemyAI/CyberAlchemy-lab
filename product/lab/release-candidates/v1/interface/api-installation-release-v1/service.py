"""Authenticated bounded API dispatch; original result/error schemas are enforced."""
import re
from datetime import timezone
from .handlers import *
from .workspace import Vault
from .candidate import CandidateHandlers
from .generated_candidate import GeneratedCandidateHandlers
from .workflow_composition import WorkflowCandidateHandlers
from . import jcs
from .context_sessions import ContextSessions
from .custody_context_sessions import ContextSessions as CustodyContextSessions, MachineContextSessions
from .projection_refresh import ProjectionRefresh
from .file_exports import FileExports
from .review_preparation import ReviewPreparation
from .classification_preparation import ClassificationPreparation, RuleFailure, PendingValidationRefusal
from .failure_preparation import FailurePreparation, FailureRuleFailure
from .typed_preparation import TypedPreparation
from .lesson_selection import LessonHost
from .package_import import PackageImport
from .package_export import PackageExport
from .challenge_submission import ChallengeSubmission
from .installation_release import InstallationRelease


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
    def __init__(self,view,channel,schemas,*,parent_host=None):
        self.channel=channel;self.schemas=schemas;self.handlers=ReadHandlers(view,channel,schemas);self.seen=set()
        self.vault=Vault(channel);self.candidates=WorkflowCandidateHandlers(self)
        self.projections=ProjectionRefresh(self.handlers,self.vault,schemas)
        self.exports=FileExports(self.handlers,self.vault,schemas)
        self.packages=PackageImport(self) if channel.policy['schema_version']=='lab-local-package-import-policy/v1-candidate' else None
        self.package_exports=PackageExport(self) if channel.policy['schema_version']=='lab-local-package-export-policy/v1-candidate' else None
        if parent_host is not None:
            from .machine_transport import MachinePeer
            source.require(type(parent_host) is Service and type(channel) is MachinePeer
                and channel.owner is parent_host and channel.service is None
                and view is parent_host.handlers.view and schemas is parent_host.schemas,
                'Machine dispatcher requires its actual selected parent host')
            channel.guard();self.sessions=MachineContextSessions(parent_host.sessions,channel,self.vault)
        else:
            self.sessions=CustodyContextSessions(view,channel,schemas,self.vault) if hasattr(view,'custody_signed_sources') and channel.policy['session_control'] is not None else ContextSessions(view,channel,schemas,self.vault) if hasattr(view,'fresh_signed_sources') and channel.policy['session_control'] is not None else None
        self.code_files={name:source.sha((HERE/name).read_bytes()) for name in ('protocol.py','auth.py','handlers.py','service.py','serve.py','artifact_model.py','projection.py','projection_refresh.py','representations.py','authentication.schema.json','workspace.py','workspace.schema.json','candidate.py','jcs.py','context_sessions.py','custody_context_sessions.py','source_bridge.py','guard.py','guarded_reads.py','scope_preparation.py','scope-preparation-profile.json','file_exports.py','export_kernel.py','review_preparation.py','review-routing.schema.json','classification_preparation.py','failure_preparation.py','typed_preparation.py','lesson_selection.py','package_import.py','package_export.py','challenge_submission.py','challenge-routing.schema.json','generated_candidate.py','workflow_composition.py','workflow-composition.schema.json','carrier_references.py','carrier-reference-check.schema.json','lesson_assessment.py','lesson_application.py','machine_context_scope.py','challenge_resolution.py','integrated_guard.py','workflow_transition.py','ontology_projection.py','installation_release.py','r02_installer.py','r02_common.py')}
        self.handler_binding={'ref':str((HERE/'handlers.py').relative_to(ROOT)),'sha256':self.code_files['handlers.py']}
    def select_ontology(self,message,outer,key,deadline):
        from .ontology_projection import OntologyProjection
        if self.channel.policy_guard()['schema_version']!='lab-local-ontology-projection-policy/v1-candidate':
            raise ApplicationError('unauthorized','Independent owned ontology representation permission is unavailable.')
        builder=OntologyProjection(self,deadline)
        builder.preflight(message,outer,key)
        return builder
    def select_workflow_transition(self,message,outer,key):
        from .workflow_transition import WorkflowTransition
        if self.channel.policy_guard().get('workflow_control') is None:
            raise ApplicationError('unauthorized','Independent exact workflow transition grant is unavailable.')
        try:
            builder=WorkflowTransition(self);builder.preflight(message,outer,key);return builder
        except ApplicationError:raise
        except ValueError as error:
            raise ApplicationError('closure-missing','Exact workflow lifecycle, current references, private grant or named satisfaction evidence is incomplete.') from error

    def select_challenge(self,message,outer,key):
        selected=self.channel.policy_guard().get('challenge_control')
        if selected is None:raise ApplicationError('closure-missing','Independent challenger eligibility and exact routing are unavailable.')
        builder=ChallengeSubmission(self,copy.deepcopy(selected['routing_binding']))
        builder.preflight(message,outer,key)
        return builder
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
    def select_classification(self,message,outer,key):
        from .guarded_candidate import selection
        with selection(self):
            return self._select_classification(message,outer,key)
    def _select_classification(self,message,outer,key):
        selected=self.channel.policy_guard().get('classification_control')
        if selected is None:
            raise ApplicationError('closure-missing','Independently selected exact classification routing is unavailable in this owned workspace.')
        try:
            routing=copy.deepcopy(selected['routing_binding'])
            source_path=HERE/'source-manifest.json'
            builder=ClassificationPreparation(self,routing,{'path':str(source_path.relative_to(ROOT)),'sha256':source.sha(source_path.read_bytes())})
            builder.preflight(message,outer,key)
            return builder
        except ApplicationError:raise
        except Exception:
            raise ApplicationError('invalid-contract','Exact classification routing, source cut, Actor, scope, key or original proposal could not be verified.')
    def select_assessment(self,message,outer,key):
        from .lesson_assessment import LessonAssessment
        selected=self.channel.policy_guard().get('assessment_control')
        if selected is None:raise ApplicationError('closure-missing','Independently selected lesson assessment method and routing are unavailable.')
        path=HERE/'source-manifest.json'
        builder=LessonAssessment(self,selected['routing_binding'],{'path':str(path.relative_to(ROOT)),'sha256':source.sha(path.read_bytes())})
        builder.preflight(message,outer,key)
        return builder
    def select_application(self,message,outer,key):
        from .lesson_application import LessonApplication
        selected=self.channel.policy_guard().get('application_control')
        if selected is None:raise ApplicationError('closure-missing','Independently selected lesson application method and routing are unavailable.')
        path=HERE/'source-manifest.json'
        builder=LessonApplication(self,selected['routing_binding'],{'path':str(path.relative_to(ROOT)),'sha256':source.sha(path.read_bytes())})
        builder.preflight(message,outer,key)
        return builder
    def select_resolution(self,message,outer,key):
        from .challenge_resolution import implementation
        ChallengeResolution,_=implementation(self.channel.policy_guard())
        from .guarded_candidate import selection
        with selection(self):
            selected=self.channel.policy_guard().get('resolution_control')
            if selected is None:raise ApplicationError('closure-missing','Independent exact challenge resolution method and routing are unavailable.')
            path=HERE/'source-manifest.json'
            try:
                builder=ChallengeResolution(self,selected['routing_binding'],{'path':str(path.relative_to(ROOT)),'sha256':source.sha(path.read_bytes())})
                builder.preflight(message,outer,key)
                return builder
            except ApplicationError:raise
            except Exception as error:raise ApplicationError('invalid-contract','Exact challenge authority, response obligations or consequence closure could not be verified.') from error
    def select_failure(self,message,outer,key):
        from .guarded_candidate import selection
        with selection(self):
            return self._select_failure(message,outer,key)
    def _select_failure(self,message,outer,key):
        selected=self.channel.policy_guard().get('failure_control')
        if selected is None:
            raise ApplicationError('closure-missing','Independently selected exact failure routing is unavailable in this owned workspace.')
        try:
            routing=copy.deepcopy(selected['routing_binding'])
            source_path=HERE/'source-manifest.json'
            builder=FailurePreparation(self,routing,{'path':str(source_path.relative_to(ROOT)),'sha256':source.sha(source_path.read_bytes())})
            builder.preflight(message,outer,key)
            return builder
        except ApplicationError:raise
        except Exception:
            raise ApplicationError('invalid-contract','Exact failure routing, source cut, Actor, scope, key or original proposal could not be verified.')
    def select_typed(self,message,outer,key):
        from .guarded_candidate import selection
        with selection(self):
            selected=self.channel.policy_guard().get('typed_control')
            if selected is None:
                raise ApplicationError('closure-missing','Independently selected typed routing is unavailable in this owned workspace.')
            try:
                path=HERE/'source-manifest.json'
                builder=TypedPreparation(self,copy.deepcopy(selected['routing_binding']),
                    {'path':str(path.relative_to(ROOT)),'sha256':source.sha(path.read_bytes())})
                builder.preflight(message,outer,key)
                return builder
            except ApplicationError:raise
            except Exception:
                raise ApplicationError('invalid-contract','Exact typed routing, source cut, Actor, scope, key or proposal could not be verified.')
    def error(self,call,raw,message_raw,error):
        return self.reply(call,raw,{'schema_version':'lab-error-result/v1-candidate',
            'request_binding':binding('message:'+self.channel.connection+':'+call['call_id'],message_raw),
            'code':error.code,'message':error.message,'gaps':[],'retry_policy':'reconcile-first' if error.code in ('indeterminate','recovery-required') else 'no-retry',
            'evidence_bindings':[],'authority_effect':'none'},kind='error')
    def reply(self,call,raw,message,kind='result'):
        context=self.channel.context
        if context is None:return transport('unauthenticated-channel',raw,call['call_id'])
        value={'schema_version':'lab-api-reply/v2-candidate','contract_profile_binding':self.schemas.profile_binding,'call_id':call['call_id'],'operation':call['operation'],
            'request_binding':binding('call:'+self.channel.connection+':'+call['call_id'],raw),
            'trusted_context_binding':binding(context['context_ref'],compact(context)),
            'handler_binding':binding(str((HERE/'installation_release.py').relative_to(ROOT)),(HERE/'installation_release.py').read_bytes()) if call['operation'] in ('installation.execute','release.prepare') else binding(str((HERE.parent/('challenge-resolution-v6' if self.channel.policy['schema_version']=='lab-local-integrated-challenge-resolution-policy/v3-candidate' else 'challenge-resolution-v3' if self.channel.policy['schema_version']=='lab-local-integrated-challenge-resolution-policy/v2-candidate' else 'challenge-resolution-v1')/'preparation.py').relative_to(ROOT)),(HERE.parent/('challenge-resolution-v6' if self.channel.policy['schema_version']=='lab-local-integrated-challenge-resolution-policy/v3-candidate' else 'challenge-resolution-v3' if self.channel.policy['schema_version']=='lab-local-integrated-challenge-resolution-policy/v2-candidate' else 'challenge-resolution-v1')/'preparation.py').read_bytes()) if call['operation']=='challenge.resolve' else binding(str((HERE/'ontology_projection.py').relative_to(ROOT)),(HERE/'ontology_projection.py').read_bytes()) if call['operation']=='ontology.project' else binding(str((HERE/'workflow_transition.py').relative_to(ROOT)),(HERE/'workflow_transition.py').read_bytes()) if call['operation']=='workflow.transition' else binding(str((HERE/'challenge_submission.py').relative_to(ROOT)),(HERE/'challenge_submission.py').read_bytes()) if call['operation']=='challenge.submit' else binding(str((HERE/'package_import.py').relative_to(ROOT)),(HERE/'package_import.py').read_bytes()) if call['operation']=='package.import' else binding(str((HERE/'package_export.py').relative_to(ROOT)),(HERE/'package_export.py').read_bytes()) if call['operation']=='package.export' else binding(str((HERE/'lesson_selection.py').relative_to(ROOT)),(HERE/'lesson_selection.py').read_bytes()) if call['operation']=='lesson.select' else binding(str((HERE/'typed_preparation.py').relative_to(ROOT)),(HERE/'typed_preparation.py').read_bytes()) if call['operation']=='typed.extension.prepare' else binding(str((HERE/'failure_preparation.py').relative_to(ROOT)),(HERE/'failure_preparation.py').read_bytes()) if call['operation']=='failure.assess' else binding(str((HERE/'classification_preparation.py').relative_to(ROOT)),(HERE/'classification_preparation.py').read_bytes()) if call['operation']=='classification.prepare' else binding(str((HERE/'review_preparation.py').relative_to(ROOT)),(HERE/'review_preparation.py').read_bytes()) if call['operation']=='proposal.review' else binding(str((HERE/'file_exports.py').relative_to(ROOT)),(HERE/'file_exports.py').read_bytes()) if call['operation']=='files.materialize' else binding(str((HERE/'projection_refresh.py').relative_to(ROOT)),(HERE/'projection_refresh.py').read_bytes()) if call['operation']=='projection.refresh' else binding(str((HERE/'candidate.py').relative_to(ROOT)),(HERE/'candidate.py').read_bytes()) if call['operation'] in ('change.prepare','change.validate','operation.inspect') else binding(str((HERE/('custody_context_sessions.py' if isinstance(self.sessions,CustodyContextSessions) else 'context_sessions.py')).relative_to(ROOT)),(HERE/('custody_context_sessions.py' if isinstance(self.sessions,CustodyContextSessions) else 'context_sessions.py')).read_bytes()) if call['operation'] in ('context.get','session.open','session.close','session.inspect') else self.handler_binding,
            'observed_at':now().isoformat(),'kind':kind,'message':message}
        source.require(self.schemas.valid('api-reply',value),'actual API result/error violates its original exact contract')
        return copy.deepcopy(value)
    def call(self,raw):
        from .integrated_guard import require_outside
        require_outside()
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
            effectful=name in ('installation.execute','release.prepare','challenge.submit','change.prepare','change.validate','session.open','session.close','projection.refresh','files.materialize','proposal.review','classification.prepare','failure.assess','typed.extension.prepare','package.import','package.export','lesson.assess','lesson.apply','challenge.resolve','workflow.transition','ontology.project')
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
                    if name=='package.import':domain=self.packages.readback(message,call['expected_source_cut'],call['idempotency_key'],effective,domain)
                    if name=='package.export':domain=self.package_exports.readback(message,call['expected_source_cut'],call['idempotency_key'],effective,domain)
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
                elif name in ('installation.execute','release.prepare'):
                    installation_release_builder=InstallationRelease(self,name,effective)
                    installation_release_builder.preflight(message,call['expected_source_cut'],call['idempotency_key'])
                elif name=='ontology.project':ontology_builder=self.select_ontology(message,call['expected_source_cut'],call['idempotency_key'],effective)
                elif name=='workflow.transition':workflow_transition_builder=self.select_workflow_transition(message,call['expected_source_cut'],call['idempotency_key'])
                elif name=='projection.refresh':self.projections.preflight(message,call['expected_source_cut'])
                elif name=='files.materialize':self.exports.preflight(message,call['expected_source_cut'],effective)
                elif name=='challenge.submit':challenge_builder=self.select_challenge(message,call['expected_source_cut'],call['idempotency_key'])
                elif name=='proposal.review':self.review_builder=self.select_review(message,call['expected_source_cut'])
                elif name=='classification.prepare':classification_builder=self.select_classification(message,call['expected_source_cut'],call['idempotency_key'])
                elif name=='failure.assess':failure_builder=self.select_failure(message,call['expected_source_cut'],call['idempotency_key'])
                elif name=='lesson.apply':application_builder=self.select_application(message,call['expected_source_cut'],call['idempotency_key'])
                elif name=='challenge.resolve':resolution_builder=self.select_resolution(message,call['expected_source_cut'],call['idempotency_key'])
                elif name=='lesson.assess':assessment_builder=self.select_assessment(message,call['expected_source_cut'],call['idempotency_key'])
                elif name=='typed.extension.prepare':typed_builder=self.select_typed(message,call['expected_source_cut'],call['idempotency_key'])
                elif name=='package.import':self.packages.preflight(message,call['expected_source_cut'],call['idempotency_key'],effective)
                elif name=='package.export':
                    if self.package_exports is None:raise ApplicationError('unauthorized','Independently selected package export authority is unavailable.')
                    self.package_exports.preflight(message,call['expected_source_cut'],call['idempotency_key'],effective)
                else:self.candidates.preflight(message,call['expected_source_cut'])
                if effective<=now():raise ApplicationError('deadline-exceeded','Deadline expired before candidate journal claim.')
                try:namespace,fp,prior,record,fresh=self.vault.claim(call,raw,context,deadline=effective)
                except Exception as error:
                    from .workspace import DeadlineBeforeClaim
                    if isinstance(error,DeadlineBeforeClaim):raise ApplicationError('deadline-exceeded','Deadline expired during guarded journal-lock acquisition; no operation claim was written.')
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
                    if name=='package.import':domain=self.packages.readback(message,call['expected_source_cut'],call['idempotency_key'],effective,domain)
                    if name=='package.export':domain=self.package_exports.readback(message,call['expected_source_cut'],call['idempotency_key'],effective,domain)
                    return self.deliver_recorded(call,raw,domain,record['posture'],ceiling,effective)
                if effective<=now():raise ApplicationError('indeterminate','Deadline expired after durable claim; inspect the operation before any reconciliation.')
                if name=='session.open':domain,evidence=self.sessions.open(message,request,call['expected_source_cut'],inner,session_plan)
                elif name=='session.close':domain,evidence=self.sessions.close_session(message,request,call['expected_source_cut'])
                elif name in ('installation.execute','release.prepare'):domain,evidence=installation_release_builder.prepare(message,request,call['expected_source_cut'],call['idempotency_key'])
                elif name=='ontology.project':domain,evidence=ontology_builder.apply(message,request,call['expected_source_cut'],call['idempotency_key'])
                elif name=='workflow.transition':domain,evidence=workflow_transition_builder.apply(message,request,call['expected_source_cut'],call['idempotency_key'])
                elif name=='change.prepare':domain,evidence=self.candidates.prepare(message,request,call['expected_source_cut'],inner)
                elif name=='projection.refresh':domain,evidence=self.projections.refresh(message,request,call['expected_source_cut'],inner)
                elif name=='files.materialize':domain,evidence=self.exports.materialize(message,request,call['expected_source_cut'],effective,inner)
                elif name=='challenge.submit':domain,evidence=challenge_builder.prepare(message,request,call['expected_source_cut'],call['idempotency_key'],inner)
                elif name=='proposal.review':domain,evidence=self.review_builder.build(message,inner)
                elif name=='typed.extension.prepare':domain,evidence=typed_builder.prepare(message,request,call['expected_source_cut'],call['idempotency_key'])
                elif name=='package.import':domain,evidence=self.packages.prepare(message,request,call['expected_source_cut'],call['idempotency_key'],effective)
                elif name=='package.export':domain,evidence=self.package_exports.prepare(message,request,call['expected_source_cut'],call['idempotency_key'],effective,inner)
                elif name=='lesson.assess':
                    from .lesson_assessment import LessonAssessmentFailure
                    try:domain,evidence=assessment_builder.prepare(message,request,call['expected_source_cut'],call['idempotency_key'])
                    except LessonAssessmentFailure as error:
                        self.channel.guard();self.schemas.guard()
                        source.require(self.handlers.current(),'lesson assessment source changed before failure recording')
                        for item in error.evidence:self.vault.object_read(item)
                        domain={'schema_version':'lab-error-result/v1-candidate','request_binding':request,
                                'code':error.code,'message':error.message,'gaps':[],
                                'retry_policy':'no-retry','evidence_bindings':error.evidence,'authority_effect':'none'}
                        source.require(self.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:error-result:v1-candidate',domain),'known assessment outcome violates original error contract')
                        self.vault.finish(namespace,domain,error.evidence,posture='failed')
                        return self.deliver_recorded(call,raw,domain,'failed',ceiling,effective)
                elif name=='lesson.apply':
                    from .lesson_application import LessonApplicationFailure
                    try:domain,evidence=application_builder.prepare(message,request,call['expected_source_cut'],call['idempotency_key'])
                    except LessonApplicationFailure as error:
                        self.channel.guard();self.schemas.guard()
                        source.require(self.handlers.current(),'lesson application source changed before failure recording')
                        for item in error.evidence:self.vault.object_read(item)
                        domain={'schema_version':'lab-error-result/v1-candidate','request_binding':request,'code':error.code,'message':error.message,'gaps':[],'retry_policy':'no-retry','evidence_bindings':error.evidence,'authority_effect':'none'}
                        self.vault.finish(namespace,domain,error.evidence,posture='failed')
                        return self.deliver_recorded(call,raw,domain,'failed',ceiling,effective)
                elif name=='challenge.resolve':
                    from .challenge_resolution import implementation
                    _,ChallengeResolutionFailure=implementation(self.channel.policy_guard())
                    try:domain,evidence=resolution_builder.prepare(message,request,call['expected_source_cut'],call['idempotency_key'])
                    except ChallengeResolutionFailure as error:
                        self.channel.guard();self.schemas.guard()
                        source.require(self.handlers.current(),'challenge resolution source changed before failure recording')
                        for item in error.evidence:self.vault.object_read(item)
                        domain={'schema_version':'lab-error-result/v1-candidate','request_binding':request,'code':error.code,'message':error.message,'gaps':[],'retry_policy':'no-retry','evidence_bindings':error.evidence,'authority_effect':'none'}
                        self.vault.finish(namespace,domain,error.evidence,posture='failed')
                        return self.deliver_recorded(call,raw,domain,'failed',ceiling,effective)
                elif name=='classification.prepare':
                    try:domain,evidence=classification_builder.prepare(message,request,call['expected_source_cut'],call['idempotency_key'])
                    except PendingValidationRefusal as error:
                        from .guarded_candidate import selection
                        with selection(self):
                            self.channel.guard();self.schemas.guard()
                            source.require(self.handlers.current(),'classification source changed before recording pending native evidence')
                            for item in error.evidence:self.vault.object_read(item)
                        self.vault.record_pending_evidence(namespace,error.evidence)
                        raise ApplicationError('indeterminate','Native validation refused incomplete stable cores. Retained verification evidence is available through operation.inspect; reconciliation is required.')
                    except RuleFailure as error:
                        from .guarded_candidate import selection
                        with selection(self):
                            self.channel.guard();self.schemas.guard()
                            source.require(self.handlers.current(),'classification source changed before recording known rule failure')
                            domain={'schema_version':'lab-error-result/v1-candidate','request_binding':request,
                                    'code':error.code,'message':error.message,'gaps':[],
                                    'retry_policy':'no-retry','evidence_bindings':error.evidence,'authority_effect':'none'}
                            source.require(self.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:error-result:v1-candidate',domain),'known classification failure violates its original error contract')
                        self.vault.finish(namespace,domain,error.evidence,posture='failed')
                        return self.deliver_recorded(call,raw,domain,'failed',ceiling,effective)
                elif name=='failure.assess':
                    try:domain,evidence=failure_builder.prepare(message,request,call['expected_source_cut'],call['idempotency_key'])
                    except FailureRuleFailure as error:
                        from .guarded_candidate import selection
                        with selection(self):
                            self.channel.guard();self.schemas.guard()
                            source.require(self.handlers.current(),'failure source changed before recording known rule failure')
                            domain={'schema_version':'lab-error-result/v1-candidate','request_binding':request,
                                    'code':error.code,'message':error.message,'gaps':[],
                                    'retry_policy':'no-retry','evidence_bindings':error.evidence,'authority_effect':'none'}
                            source.require(self.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:error-result:v1-candidate',domain),'known failure outcome violates its original error contract')
                        self.vault.finish(namespace,domain,error.evidence,posture='failed')
                        return self.deliver_recorded(call,raw,domain,'failed',ceiling,effective)
                else:
                    domain,details=self.candidates.validate(message,request,call['expected_source_cut'],inner);evidence=details['evidence']
                self.channel.guard();self.schemas.guard()
                self.vault.finish(namespace,domain,evidence)
                return self.deliver_recorded(call,raw,domain,'completed',ceiling,effective)
            if name in ('context.get','session.inspect'):
                if self.sessions is None:raise ApplicationError('unresolved-reference','Fresh source-bound Session host is unavailable for this branch.')
                domain=self.sessions.view_get(message,request,call['expected_source_cut'],inner) if name=='context.get' else self.sessions.inspect(message,request,call['expected_source_cut'])
            elif name=='lesson.select':
                path=HERE/'source-manifest.json'
                builder=LessonHost(self,{'path':str(path.relative_to(ROOT)),'sha256':source.sha(path.read_bytes())})
                domain=builder.select(message,request,call['expected_source_cut'],inner,effective,ceiling)
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
        self.channel.guard()
        if effective<=now():raise ApplicationError('indeterminate','Deadline expired during final verification; inspect the exact recorded operation outcome.')
        return result
    def close(self):
        try:
            if self.sessions is not None:self.sessions.close()
        finally:self.handlers.close();self.seen.clear();self.channel.close()
