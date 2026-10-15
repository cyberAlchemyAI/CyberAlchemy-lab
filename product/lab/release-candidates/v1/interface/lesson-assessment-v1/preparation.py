"""Prepare a scoped assessment proposal from an independently selected record.

The recorded-outcome method verifies correspondence, not truth or causality.
Additional outcome methods require a separately declared implementation binding.
"""
import copy
import importlib
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
KIND = 'lab-local-lesson-assessment-policy/v1-candidate'
METHOD = 'recorded-application-outcome/v1-candidate'
CEILING = 'Exact recorded application outcome only; no general or causal effectiveness inferred.'
CURRENT = ('admitted-current', 'local-admitted-current')
FIELDS = ('scope_ref', 'identity_ref', 'version_ref', 'carrier_ref', 'byte_sha256')


def require(value, reason):
    if not value:
        raise ValueError(reason)


class RuleFailure(Exception):
    def __init__(self, code, evidence):
        self.code = code
        self.message = 'Recorded application, outcome method or prospective assessment did not match; inspect exact evidence.'
        self.evidence = copy.deepcopy(evidence)
        super().__init__(self.message)


class LessonAssessment:
    def __init__(self, host, routing_binding, host_source_binding):
        module = sys.modules.get(type(host).__module__)
        require(module is not None and getattr(module, 'Service', None) is type(host), 'actual selected Service required')
        package = type(host).__module__.rsplit('.', 1)[0]
        self.P = importlib.import_module(package + '.protocol')
        self.M = importlib.import_module(package + '.artifact_model')
        self.H = importlib.import_module(package + '.handlers')
        self.G = importlib.import_module(package + '.guard')
        service_path = Path(module.__file__).resolve()
        require(service_path.parent.parent == HERE.parent and service_path.name == 'service.py', 'foreign Service source')
        source = service_path.parent / 'source-manifest.json'
        require(host_source_binding == {'path': str(source.relative_to(ROOT)), 'sha256': self.P.source.sha(source.read_bytes())}, 'host source selection differs')
        selected = self.G.verify(host_source_binding['sha256'])
        require({'path': str(Path(__file__).resolve().relative_to(ROOT)), 'sha256': self.P.source.sha(Path(__file__).read_bytes())} in selected['files'], 'assessment adapter outside selected host source')
        self.host = host
        self.vault = host.vault
        self.schemas = host.schemas
        self.host_source_binding = copy.deepcopy(host_source_binding)
        self.routing_binding = copy.deepcopy(routing_binding)
        policy = host.channel.policy_guard()
        require(policy['schema_version'] == KIND and policy['assessment_control']['routing_binding'] == routing_binding, 'independent assessment policy absent')
        self.raw = self.vault.object_read(routing_binding)
        self.routing = self.P.frame_parse(self.raw)
        require(set(self.routing) == {'schema_version', 'scope_ref', 'source_cut', 'proposal_binding', 'method_binding',
                                     'observation_binding', 'authorization_basis_binding', 'authority_effect', 'actual_owner_outcome'}, 'closed assessment routing required')
        require(self.routing['schema_version'] == 'lab-lesson-assessment-routing/v1-candidate'
                and self.routing['authority_effect'] == 'none' and self.routing['actual_owner_outcome'] is None, 'routing cannot supply authority')
        own = self.P.binding(str(Path(__file__).resolve().relative_to(ROOT)), Path(__file__).read_bytes())
        require(policy['assessment_control']['method_binding'] == self.routing['method_binding'] == own, 'method not independently selected')
        authority = ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'
        require(self.routing['authorization_basis_binding'] == self.P.binding(str(authority.relative_to(ROOT)), authority.read_bytes()), 'development authorization differs')

    def record(self, header, kind):
        subject = self.host.handlers.resolve_exact(header)
        require(subject['effective_state'] in CURRENT, 'assessment source is not current')
        require(subject['kind'] == kind, 'assessment source kind differs')
        raw = self.M.record_bytes(self.host.handlers.view, subject)[0]
        require(self.P.source.sha(raw) == header['byte_sha256'], 'current original body differs')
        body = self.P.frame_parse(raw)
        self.host.handlers.view.handle.operations.validate_record(body, header['carrier_ref'], self.host.handlers.view.data['projection'])
        return body

    def preflight(self, message, outer, key):
        self.G.verify(self.host_source_binding['sha256'])
        self.schemas.guard()
        context = self.host.channel.guard()
        policy = self.host.channel.policy_guard()
        require(policy['schema_version'] == KIND and 'lesson.assess' in policy['allowed_operations'], 'current assessment permission absent')
        require(policy['assessment_control']['routing_binding'] == self.routing_binding
                and self.vault.object_read(self.routing_binding) == self.raw, 'assessment routing changed')
        actor = {field: context[field] for field in ('principal_ref', 'agent_instance_ref', 'assignment_ref', 'session_ref')}
        actor['role_assignment_refs'] = context['role_assignment_bindings']
        require(message['actor'] == actor, 'assessment Actor differs from transport')
        require(message['source_cut'] == outer == self.routing['source_cut'] == self.H.cut(self.host.handlers.view), 'assessment source cut differs')
        require(message['causal_claim_ceiling'] == CEILING, 'recorded-outcome method cannot infer causal or general effectiveness')
        proposal_raw = self.vault.object_read(self.routing['proposal_binding'])
        proposal = self.P.frame_parse(proposal_raw)
        require(self.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:change-proposal:v1-candidate', proposal), 'original ChangeProposal required')
        require(proposal['actor'] == actor and proposal['base_cut'] == outer and proposal['idempotency_key'] == key
                and proposal['scope_ref'] == self.routing['scope_ref'], 'proposal Actor/key/cut/scope differs')
        self.host.candidates.preflight(proposal, outer)
        wanted = message['assessment_candidate_binding']
        targets = [target for target in proposal['targets'] if target['operation'] != 'withdraw'
                   and target['artifact']['carrier_ref'] == 'cal.artifact-type.lesson-outcome-assessment/v1'
                   and {'ref': target['content']['content_ref'], 'sha256': target['content']['byte_sha256']} == wanted]
        require(len(targets) == 1, 'one exact prospective assessment target required')
        application = self.record(message['application'], 'lesson-application')
        require(application['scope_ref'] == proposal['scope_ref'], 'application record scope differs from preparation scope')
        observation_raw = self.vault.material(self.routing['observation_binding'])
        observation = self.P.frame_parse(observation_raw)
        require(set(observation) == {'schema_version', 'method_ref', 'scope_ref', 'source_cut', 'application',
                                    'predicted_outcome', 'observed_outcome', 'evidence_bindings', 'counterevidence_bindings',
                                    'causal_claim_ceiling', 'authority_effect'}, 'closed recorded outcome required')
        require(observation['schema_version'] == 'lab-recorded-application-outcome/v1-candidate'
                and observation['method_ref'] == METHOD and observation['authority_effect'] == 'none', 'unknown outcome method')
        require(observation['scope_ref'] == proposal['scope_ref'] and observation['source_cut'] == outer
                and observation['application'] == message['application'], 'recorded application scope/cut/header differs')
        require(observation['causal_claim_ceiling'] == CEILING
                and observation['evidence_bindings'] == message['evidence_bindings']
                and observation['counterevidence_bindings'] == message['counterevidence_bindings'], 'recorded evidence or claim ceiling differs')
        for field in ('predicted_outcome', 'observed_outcome'):
            require(type(observation[field]) is str and bool(observation[field]), 'nonempty recorded outcome statements required')
        for item in [*message['evidence_bindings'], *message['counterevidence_bindings']]:
            self.vault.material(item)
        require(bool(message['evidence_bindings']), 'actual bound recorded outcome evidence required')
        return proposal_raw, proposal, targets[0], observation

    def prepare(self, message, request, outer, key):
        package = type(self.host).__module__.rsplit('.', 1)[0]
        guarded = importlib.import_module(package + '.guarded_candidate')
        failure = None
        with guarded.calculation(self.host) as writer:
            result = None
            raw, proposal, target, observation = self.preflight(message, outer, key)
            validation, details = self.host.candidates.validate(proposal, request, outer, raw, evidence_writer=writer)
            body = self.P.frame_parse(self.vault.material(message['assessment_candidate_binding']))
            payload = body.get('payload', {})
            passed = validation['result'] == 'pass' and all([
                payload.get('lesson_application_ref') == message['application']['version_ref'],
                payload.get('predicted_outcome') == observation['predicted_outcome'],
                payload.get('observed_outcome') == observation['observed_outcome'],
                payload.get('disposition') == 'recorded-outcome-only',
                payload.get('evidence_refs') == [item['ref'] for item in message['evidence_bindings']],
                payload.get('counterevidence_refs') == [item['ref'] for item in message['counterevidence_bindings']],
                payload.get('causal_claim_ceiling') == CEILING,
            ])
            evidence = writer.object(self.P.source.encoded({
                'schema_version': 'lab-recorded-outcome-assessment-check/v1-candidate',
                'result': 'pass' if passed else 'fail', 'method_ref': METHOD,
                'method_binding': self.routing['method_binding'], 'application': message['application'],
                'source_cut': outer, 'assessment_candidate_binding': message['assessment_candidate_binding'],
                'observation_binding': self.routing['observation_binding'],
                'evidence_bindings': message['evidence_bindings'], 'counterevidence_bindings': message['counterevidence_bindings'],
                'causal_claim_ceiling': CEILING, 'candidate_preparation_only': True,
                'interpretation_or_truth_verified': False, 'authority_effect': 'none', 'actual_owner_outcome': None}))
            self.preflight(message, outer, key)
            require(self.host.handlers.current(), 'assessment source changed during preparation')
            if passed:
                result = (copy.deepcopy(proposal), details['evidence'] + [evidence])
            else:
                failure = RuleFailure('conflict', details['evidence'] + [evidence])
        if failure is not None:
            raise failure
        return result
