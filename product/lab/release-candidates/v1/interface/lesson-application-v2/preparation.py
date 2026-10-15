"""Prepare an exact Lesson Application from a current live Session selection."""
import copy
import importlib
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
KIND = 'lab-local-lesson-application-policy/v2-candidate'


def require(value, reason):
    if not value:
        raise ValueError(reason)


class RuleFailure(Exception):
    def __init__(self, evidence):
        self.code = 'conflict'
        self.message = 'Exact application attribution or original prospective core validation did not pass; inspect retained evidence.'
        self.evidence = copy.deepcopy(evidence)
        super().__init__(self.message)


class LessonApplication:
    def __init__(self, host, routing_binding, host_source_binding):
        module = sys.modules.get(type(host).__module__)
        require(module is not None and getattr(module, 'Service', None) is type(host), 'actual selected Service required')
        path = Path(module.__file__).resolve()
        require(path.parent.parent == HERE.parent and path.name == 'service.py', 'foreign host source')
        package = type(host).__module__.rsplit('.', 1)[0]
        self.P = importlib.import_module(package + '.protocol')
        self.M = importlib.import_module(package + '.artifact_model')
        self.H = importlib.import_module(package + '.handlers')
        self.C = importlib.import_module(package + '.custody_context_sessions')
        self.G = importlib.import_module(package + '.guard')
        self.A = importlib.import_module(package + '.auth')
        require(type(host.channel) is self.A.ReaderChannel, 'application preparation requires actual parent operator channel')
        source = path.parent / 'source-manifest.json'
        require(host_source_binding == {'path': str(source.relative_to(ROOT)), 'sha256': self.P.source.sha(source.read_bytes())}, 'host source selection differs')
        manifest = self.G.verify(host_source_binding['sha256'])
        self.method_binding = self.P.binding(str(Path(__file__).resolve().relative_to(ROOT)), Path(__file__).read_bytes())
        require({'path': self.method_binding['ref'], 'sha256': self.method_binding['sha256']} in manifest['files'], 'application method outside host selection')
        self.host = host
        self.vault = host.vault
        self.schemas = host.schemas
        self.host_source_binding = copy.deepcopy(host_source_binding)
        self.routing_binding = copy.deepcopy(routing_binding)
        policy = host.channel.policy_guard()
        require(policy['schema_version'] == KIND and policy['application_control']['routing_binding'] == routing_binding
                and policy['application_control']['method_binding'] == self.method_binding, 'independent application policy absent')
        self.raw = self.vault.object_read(routing_binding)
        self.routing = self.P.frame_parse(self.raw)
        require(set(self.routing) == {'schema_version', 'source_cut', 'scope_ref', 'proposal_binding', 'method_binding',
                                     'selection_binding', 'applicability_binding', 'instruction_precedence_binding',
                                     'intended_influence', 'action_bound_refs', 'override_bindings',
                                     'authorization_basis_binding', 'authority_effect', 'actual_owner_outcome'}, 'closed application routing required')
        require(self.routing['schema_version'] == 'lab-lesson-application-routing/v1-candidate'
                and self.routing['method_binding'] == self.method_binding and self.routing['authority_effect'] == 'none'
                and self.routing['actual_owner_outcome'] is None, 'routing supplies no owner authority')
        authority = ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'
        require(self.routing['authorization_basis_binding'] == self.P.binding(str(authority.relative_to(ROOT)), authority.read_bytes()), 'development authorization differs')

    def live(self, session_ref):
        require(type(self.host.sessions) is self.C.ContextSessions and not self.host.sessions.closed, 'actual parent Session custodian required')
        resource = self.host.sessions.live.get(session_ref)
        require(type(resource) is self.C.LiveReader and resource.source is self.host.sessions.source
                and resource.bridge is self.host.sessions.bridge, 'lost or reconstructed Session cannot prepare application')
        resource.guard()
        row = self.host.sessions.selected(session_ref)
        require(row['posture'] == 'active' and row['source_cut'] == self.H.cut(self.host.handlers.view), 'Session not active at exact source cut')
        require(resource.agent['payload']['accountable_principal_ref'] == self.host.channel.guard()['principal_ref'], 'Session belongs to another Principal')
        return resource, row

    def preflight(self, message, outer, key):
        self.G.verify(self.host_source_binding['sha256'])
        self.schemas.guard()
        context = self.host.channel.guard()
        policy = self.host.channel.policy_guard()
        require(policy['schema_version'] == KIND and 'lesson.apply' in policy['allowed_operations'], 'current application preparation grant absent')
        require(policy['application_control']['routing_binding'] == self.routing_binding
                and policy['application_control']['method_binding'] == self.method_binding
                and self.vault.object_read(self.routing_binding) == self.raw, 'application policy/routing changed')
        actor = {name: context[name] for name in ('principal_ref', 'agent_instance_ref', 'assignment_ref', 'session_ref')}
        actor['role_assignment_refs'] = context['role_assignment_bindings']
        require(message['actor'] == actor, 'application Actor differs from trusted channel')
        require(message['source_cut'] == outer == self.routing['source_cut'] == self.H.cut(self.host.handlers.view), 'application source cut differs')
        require(message['session_ref'] == policy['application_control']['runtime_identities']['session_ref'], 'application must use the independently selected one-use Session identity')
        resource, session = self.live(message['session_ref'])
        require(message['selection_binding'] == self.routing['selection_binding']
                and message['applicability_binding'] == self.routing['applicability_binding'], 'selection/applicability not independently selected')
        selection = self.P.frame_parse(self.vault.object_read(message['selection_binding']))
        require(self.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:lesson-selection:v1-candidate', selection), 'original Lesson Selection contract required')
        require(selection['session_ref'] == message['session_ref'] and selection['assignment'] == session['assignment']
                and selection['source_cut'] == outer, 'selection belongs to another Session/Assignment/cut')
        require(selection['instruction_precedence_binding'] == self.routing['instruction_precedence_binding'], 'instruction precedence differs')
        instruction=self.P.frame_parse(self.vault.material(self.routing['instruction_precedence_binding']))
        require(instruction['session_ref']==message['session_ref'] and instruction['assignment']==session['assignment']
                and instruction['source_cut']==outer and instruction['veto_lesson_influence'] is False,
                'actual instruction precedence vetoes or belongs to another Session/cut')
        items = [item for item in selection['items'] if item['lesson'] == message['lesson']]
        require(len(items) == 1 and not items[0]['expired'], 'exact unexpired selected lesson required')
        item = items[0]
        require(item['applicability_check_binding'] == message['applicability_binding'], 'exact applicability check differs')
        applicability = self.P.frame_parse(self.vault.object_read(message['applicability_binding']))
        require(applicability['lesson'] == message['lesson'] and applicability['source_cut'] == outer,
                'applicability witness belongs to another lesson/cut')
        require(applicability['posture'] == item['posture'] and applicability['expired'] is False
                and applicability['conflict_refs'] == message['conflict_refs'] == item['conflict_refs'], 'applicability posture/conflict set differs')
        require(message['override_basis'] == self.routing['override_bindings'], 'conflict override basis not independently selected')
        if message['conflict_refs']:
            require(item['posture']=='blocked' and item['reason']=='incompatible-influence-with-another-applicable-lesson'
                    and bool(message['override_basis']), 'only explicitly resolved influence conflicts may proceed')
            for selected in message['override_basis']:
                override=self.P.frame_parse(self.vault.material(selected))
                require(set(override)=={'schema_version','principal_ref','session_ref','source_cut','lesson','conflict_refs',
                                      'instruction_precedence_binding','resolution','expires_at','authority_effect'}, 'closed conflict override required')
                require(override['schema_version']=='lab-lesson-conflict-override/v1-candidate'
                        and override['principal_ref']==context['principal_ref'] and override['session_ref']==message['session_ref']
                        and override['source_cut']==outer and override['lesson']==message['lesson']
                        and override['conflict_refs']==message['conflict_refs']
                        and override['instruction_precedence_binding']==selection['instruction_precedence_binding']
                        and override['resolution']=='select-exact-lesson-in-current-session' and override['authority_effect']=='none'
                        and self.A.now()<self.A.instant(override['expires_at'])<=resource.expires,
                        'conflict override differs from actual current private Session/instruction scope')
        else:
            require(item['posture']=='selected' and message['override_basis']==[], 'unconflicted exact selected lesson required')
        subject = self.host.handlers.resolve_exact(message['lesson'])
        require(subject['effective_state'] in ('admitted-current', 'local-admitted-current') and subject['kind'] == 'operational-lesson', 'exact current Lesson unavailable')
        original = self.M.record_bytes(self.host.handlers.view, subject)[0]
        lesson = self.P.frame_parse(original)
        require(lesson['scope_ref'] == self.routing['scope_ref'], 'Lesson record scope differs from preparation scope')
        require(type(self.routing['intended_influence']) is str and bool(self.routing['intended_influence']), 'declared influence required')
        # Reading this record cannot extend the actual resource's permitted actions.
        require(type(self.routing['action_bound_refs']) is list and all(type(ref) is str for ref in self.routing['action_bound_refs']), 'declared action bounds required')
        require(set(self.routing['action_bound_refs']) <= set(resource.bridge.permission().operations), 'lesson influence action bounds exceed actual delegated Session operations')
        raw = self.vault.object_read(self.routing['proposal_binding'])
        proposal = self.P.frame_parse(raw)
        require(self.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:change-proposal:v1-candidate', proposal), 'original ChangeProposal required')
        require(proposal['actor'] == actor and proposal['base_cut'] == outer and proposal['idempotency_key'] == key
                and proposal['scope_ref'] == self.routing['scope_ref'], 'proposal Actor/key/cut/scope differs')
        self.host.candidates.preflight(proposal, outer)
        wanted = message['application_candidate_binding']
        targets = [target for target in proposal['targets'] if target['operation'] != 'withdraw'
                   and target['artifact']['carrier_ref'] == 'cal.artifact-type.lesson-application/v1'
                   and {'ref': target['content']['content_ref'], 'sha256': target['content']['byte_sha256']} == wanted]
        require(len(targets) == 1, 'one exact prospective application target required')
        return raw, proposal, resource

    def prepare(self, message, request, outer, key):
        package = type(self.host).__module__.rsplit('.', 1)[0]
        guarded = importlib.import_module(package + '.guarded_candidate')
        failed = None
        with guarded.calculation(self.host) as writer:
            raw, proposal, resource = self.preflight(message, outer, key)
            validation, details = self.host.candidates.validate(proposal, request, outer, raw, evidence_writer=writer)
            body = self.P.frame_parse(self.vault.material(message['application_candidate_binding']))
            payload = body.get('payload', {})
            passed = validation['result'] == 'pass' and all([
                payload.get('lesson_revision_ref') == message['lesson']['version_ref'],
                payload.get('session_ref') == message['session_ref'],
                payload.get('applicability_assessment_ref') == message['applicability_binding']['ref'],
                payload.get('intended_influence') == self.routing['intended_influence'],
                payload.get('conflict_refs') == [item['version_ref'] for item in message['conflict_refs']],
                payload.get('override_refs') == [item['ref'] for item in message['override_basis']],
                payload.get('application_posture') == 'candidate-attributed-no-tool-dispatch',
            ])
            witness = writer.object(self.P.source.encoded({
                'schema_version': 'lab-lesson-application-preparation-check/v1-candidate',
                'result': 'pass' if passed else 'fail', 'method_binding': self.method_binding,
                'source_cut': outer, 'session_ref': message['session_ref'], 'lesson': message['lesson'],
                'selection_binding': message['selection_binding'], 'applicability_binding': message['applicability_binding'],
                'action_bound_refs': self.routing['action_bound_refs'], 'tool_dispatches': 0,
                'actual_owner_outcome': None, 'authority_effect': 'none'}))
            self.preflight(message, outer, key)
            resource.guard()
            require(self.host.handlers.current(), 'application source changed during preparation')
            if passed:
                result = copy.deepcopy(proposal), details['evidence'] + [witness]
            else:
                failed = RuleFailure(details['evidence'] + [witness])
        if failed is not None:
            raise failed
        return result
