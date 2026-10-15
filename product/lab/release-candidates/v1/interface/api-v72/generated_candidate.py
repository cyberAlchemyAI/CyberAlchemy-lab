"""Exact producer result selection; metadata grants no authority or admission."""
import copy
from . import protocol as P
from .candidate import CandidateHandlers
from .handlers import ApplicationError
from .challenge_submission import ChallengeSubmission
from .guarded_candidate import selection,calculation
require=P.source.require

class ExistingObjects:
    """Pure renderer: every deterministic object must already exist unchanged."""
    def __init__(self,vault):self.vault=vault;self.bindings={}
    def object(self,raw):
        binding={'ref':'workspace-object:'+self.vault.manifest['workspace_ref']+':'+P.source.sha(raw),'sha256':P.source.sha(raw)}
        require(self.vault.object_read(binding)==raw,'reconstructed producer output bytes differ or are absent')
        self.bindings[binding['ref']]=binding
        return binding

class SelectedOutputs:
    """Local read facade; actual Vault, manifest, grants and callbacks stay intact."""
    def __init__(self,vault,proposal,objects,writer):
        self.vault=vault;self.manifest=copy.deepcopy(vault.manifest);self.inputs=vault.inputs
        self.manifest['target_metadata']={t['artifact']['version_ref']:copy.deepcopy(t['candidate_binding']) for t in proposal['targets']}
        self.selected=copy.deepcopy(objects.bindings);self.writer=writer
    @property
    def control_binding(self):return self.vault.control_binding
    def guard(self):return self.vault.guard()
    def material(self,b):
        if b['ref'] in self.inputs:
            return self.vault.material(b)
        require(self.selected.get(b['ref'])==b,'material not selected by exact reconstructed completed producer')
        return self.vault.object_read(b)
    def object(self,raw):
        require(self.writer is not None,'pure selection cannot stage evidence')
        return self.writer.object(raw)

class GeneratedCandidateHandlers(CandidateHandlers):
    def __init__(self,host):
        self.host=host
        super().__init__(host.handlers,host.vault,host.schemas)
    def needed(self,message):
        return self.host.channel.policy['schema_version']=='lab-local-challenge-candidate-policy/v1-candidate' and any(
            t['artifact']['version_ref'] not in self.vault.manifest['target_metadata'] for t in message['targets'])
    def selected(self,message,outer,writer=None):
        context=self.host.channel.guard();policy=self.host.channel.policy_guard()
        require(policy['schema_version'] in ('lab-local-challenge-candidate-policy/v1-candidate','lab-local-challenge-review-policy/v1-candidate')
            and 'challenge.submit' in policy['allowed_operations'],'independent challenge producer grant unavailable')
        claim,record=self.vault.lookup({'operation':'challenge.submit','idempotency_key':message['idempotency_key']},context)
        require(claim is not None and record is not None and record['posture']=='completed',
            'a completed exact challenge producer result is required')
        raw=self.vault.object_read(record['domain_binding']);original_proposal=P.frame_parse(raw)
        require(P.compact(original_proposal)==P.compact(message),'proposal differs from exact completed challenge result')
        call_raw=self.vault.object_read(claim['original_call_material_binding']);call=P.frame_parse(call_raw)
        require(call['operation']=='challenge.submit' and call['idempotency_key']==message['idempotency_key']
            and call['expected_source_cut']==outer,'completed producer operation, key or cut differs')
        builder=ChallengeSubmission(self.host,policy['challenge_control']['routing_binding'])
        plan=builder._plan(call['message'],outer,call['idempotency_key'])
        objects=ExistingObjects(self.vault)
        reproduced,evidence=builder.render(plan,call['message'],outer,call['idempotency_key'],P.compact(call['message']),objects)
        require(P.compact(reproduced)==P.compact(message) and evidence==record['evidence_bindings'],
            'completed producer result does not match independent current reconstruction')
        return SelectedOutputs(self.vault,message,objects,writer)
    def preflight(self,message,outer):
        observed=super().preflight(message,outer)
        if self.needed(message):
            try:
                with selection(self.host):self.selected(message,outer)
            except ApplicationError:raise
            except Exception as e:raise ApplicationError('invalid-contract','Exact completed producer output selection could not be verified.') from e
        return observed
    def validate(self,message,request,outer,inner,*,evidence_writer=None):
        if not self.needed(message):return super().validate(message,request,outer,inner,evidence_writer=evidence_writer)
        if evidence_writer is not None:
            selected=self.selected(message,outer,evidence_writer)
            return CandidateHandlers(self.readers,selected,self.schemas).validate(message,request,outer,inner,evidence_writer=evidence_writer)
        with calculation(self.host) as writer:
            selected=self.selected(message,outer,writer)
            result=CandidateHandlers(self.readers,selected,self.schemas).validate(message,request,outer,inner,evidence_writer=writer)
        return result
    def prepare(self,message,request,outer,inner):
        if not self.needed(message):return super().prepare(message,request,outer,inner)
        with calculation(self.host) as writer:
            selected=self.selected(message,outer,writer)
            result=CandidateHandlers(self.readers,selected,self.schemas).prepare(message,request,outer,inner)
        return result
