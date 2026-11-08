"""Disposable current signed Source agent-context instance fixture.

The local grant is a test-owned private input. It does not imply an owner
decision, canonical admission, or completed Work. A caller may attach an
independently selected output plan before calling workflow.transition.
"""

import base64
import copy
from contextlib import contextmanager
from datetime import datetime, timezone, timedelta
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
API = BASE / 'api-integration-v51-t31-agent-context-instance-0002'
SOURCE_SHA = '59667101ce45d09c45b2cf91ca2d36edd65b28316e4657b7dde46b7ba654b1c2'
PROFILE_SHA = '46461dac621009d145b1b9a7904bafe6dcf1e9240dabc1ca79d77a69e4d865a4'
PREFIX = 'completion-legacy-local-ce4d53a6479188a5'
PRINCIPAL = 'principal:owned-t31-workflow-operator'
AUTHORIZATION = ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'
BRIDGE_CODE_SHA = 'a7e4a6a4bc01f235ca35f4acb2ca6e90272d581de44f004dd091caf513a1f0cd'


def selected_bridge_installer():
    path = Path(__file__).with_name('install_bridge.py')
    if sha(path) != BRIDGE_CODE_SHA:
        raise ValueError('private output bridge installer changed')
    spec = importlib.util.spec_from_file_location('_cal_t31_private_bridge_installer_0001', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if sha(path) != BRIDGE_CODE_SHA:
        raise ValueError('private output bridge installer changed during import')
    return module


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def install(name, path):
    spec = importlib.util.spec_from_file_location(name, path / '__init__.py', submodule_search_locations=[str(path)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def public_binding(path):
    return {'ref': path.relative_to(ROOT).as_posix(), 'sha256': sha(path)}


def owned_snapshot(root):
    return {p.relative_to(root).as_posix(): sha(p) for p in root.rglob('*') if p.is_file()}


@contextmanager
def current_fixture():
    name = '_cal_t31_api49_owned_workflow_0002'
    install(name, API)
    P = __import__(name + '.protocol', fromlist=['Schemas'])
    A = __import__(name + '.auth', fromlist=['ReaderChannel'])
    S = __import__(name + '.service', fromlist=['Service'])
    H = __import__(name + '.handlers', fromlist=['cut'])
    M = __import__(name + '.artifact_model', fromlist=['artifact_ref'])
    W = __import__(name + '.workspace', fromlist=['atomic'])
    F = __import__(name + '.fixtures', fromlist=['proof'])
    J = __import__(name + '.workflow_output_journal', fromlist=['Journal'])
    G = __import__(name + '.guard', fromlist=['verify'])
    G.verify(SOURCE_SHA)
    schemas = P.Schemas(PROFILE_SHA)
    component = '_cal_t31_workflow_component_0001'
    install(component, BASE / 'workflow-transition-v1')
    T = __import__(component + '.fixtures', fromlist=['build'])
    with P.source.replay_source(P.source.CURRENT_LEGACY_NAME) as view, tempfile.TemporaryDirectory(prefix='cal-t31-api50-context-') as temporary:
        owned = Path(temporary)
        owned.chmod(0o700)
        workspace = owned / 'workspace'
        workspace.mkdir(mode=0o700)
        for part in ('inputs', 'objects', 'journal', 'workflows'):
            (workspace / part).mkdir(mode=0o700)
        cut = H.cut(view)
        message, facts = T.build()
        actor = {'principal_ref': PRINCIPAL, 'agent_instance_ref': None, 'assignment_ref': None,
                 'session_ref': None, 'role_assignment_refs': []}

        def selected(identity, kind):
            rows = [r for r in view.subjects.values() if r['identity'] == identity and r['kind'] == kind
                    and r['effective_state'] in ('admitted-current', 'local-admitted-current')]
            if len(rows) != 1:
                raise ValueError('exact current workflow subject missing/ambiguous: ' + kind + ':' + identity)
            return M.artifact_ref(view, rows[0])

        with M.model_read_batch(view):
            headers = {
                'intent': selected('intent:' + PREFIX, 'intent'),
                'work': selected('work:' + PREFIX, 'work'),
                'coordination_context': selected('coordination:' + PREFIX, 'coordination-context'),
                'intent_resolution': selected('intent-resolution:' + PREFIX + ':workflow', 'intent-resolution'),
                'decision_profile': selected('workflow-decision-profile:lab-governance-single-checkpoint', 'workflow-decision-profile'),
            }
        definition = json.loads((ROOT / 'docs/proposals/0007-lab-integrated-schema-package/workflows/agent-context.json').read_bytes())
        run = json.loads(facts['run_raw'])
        definition['decision_profile'] = headers['decision_profile']
        transition = definition['transitions'][0]
        transition['input_carriers'] = ['cal.artifact-type.work/v1']
        run.update(run_ref='workflow-run:owned-t31-agent-context', state='requested')
        run.update(actor=actor, source_cut=cut, **{key: headers[key] for key in
                   ('intent', 'intent_resolution', 'work', 'coordination_context')})
        grant = copy.deepcopy(facts['host_grant'])
        start = datetime.now(timezone.utc)
        end = min(start + timedelta(minutes=30), datetime.fromisoformat(view.data['config']['expires_at'])) if 'expires_at' in view.data['config'] else start + timedelta(minutes=30)
        grant.update(principal_ref=PRINCIPAL, scope_ref=view.data['config']['scope_ref'], source_cut=cut,
                     actor_role_refs=transition['actor_role_refs'], not_before=(start - timedelta(seconds=1)).isoformat(),
                     expires_at=end.isoformat())
        materials = {}

        def original(ref, value):
            raw = P.compact(value)
            materials[ref] = raw
            return P.binding(ref, raw)

        core = original('authority-core:owned-t31-source-inspection', {
            'schema_version': 'lab-isolated-operator-workflow-core/v1-candidate',
            'principal_ref': PRINCIPAL, 'scope_ref': grant['scope_ref'], 'source_cut': cut,
            'actor_role_refs': grant['actor_role_refs'], 'permitted_effects': grant['permitted_effects'],
            'not_before': grant['not_before'], 'expires_at': grant['expires_at'],
            'role_scope': 'Test-owned current coordination only; no canonical governing role or owner outcome.',
            'authority_effect': 'none'})
        observed = original('evidence:owned-t31-signed-source-inspection', {
            'schema_version': 'lab-actual-workflow-source-inspection/v1-candidate',
            'source_cut': cut, 'headers': headers,
            'signed_source_binding': P.source.current_workflow_bindings()['source_binding'],
            'signed_package_binding': P.source.current_workflow_bindings()['package_binding'],
            'actual_signed_transactions': view.data['head']['sequence'], 'result': 'PASS',
            'authority_effect': 'none',
            'claim_ceiling': 'Current signed Source and selected headers only; no owner decision or Work completion.'})
        obligations = {ref: [core] if ref in transition['authority_requirement_refs'] else [observed]
                       for ref in [*transition['authority_requirement_refs'], *transition['precondition_refs'],
                                   *transition['satisfaction_check_refs'], *transition['relation_requirement_refs']]}

        def check(ref):
            return {'check_ref': 'check:' + ref, 'obligation_ref': ref, 'result': 'pass',
                    'evidence_bindings': obligations[ref],
                    'claim_ceiling': 'Actual owned grant/source selection; semantic closure is rechecked before any effect.'}

        definition_binding = original('workflow-definition:owned-t31-agent-context', definition)
        run['definition_binding'] = definition_binding
        run_binding = original('workflow-run:owned-t31-agent-context:before', run)
        authority = json.loads(facts['authority_raw'])
        authority.update(source_cut=cut, evaluated_at=start.isoformat(), expires_at=end.isoformat(),
                         authority_envelope_binding=core,
                         checks=[check(ref) for ref in transition['authority_requirement_refs']],
                         evidence_bindings=[core])
        satisfaction = json.loads(facts['satisfaction_raw'])
        satisfaction.update(subject_binding=run_binding, source_cut=cut,
                            checks=[check(ref) for ref in [*transition['precondition_refs'],
                                                            *transition['satisfaction_check_refs'],
                                                            *transition['relation_requirement_refs']]])
        authority_binding = original('authority-evaluation:owned-t31-source-inspection', authority)
        satisfaction_binding = original('satisfaction:owned-t31-source-inspection', satisfaction)
        message.update(actor=actor, source_cut=cut, run_binding=run_binding,
                       transition_ref=transition['transition_ref'], expected_state='requested',
                       definition_binding=definition_binding, input_artifacts=[headers['work']],
                       authority_evaluation_binding=authority_binding,
                       satisfaction_report_binding=satisfaction_binding)
        grant.update(run_binding=run_binding, definition_binding=definition_binding,
                     permitted_transitions=[transition['transition_ref']],
                     authority_evaluation_binding=authority_binding,
                     satisfaction_report_binding=satisfaction_binding, obligation_bindings=obligations)
        store = J.Journal.initialize(workspace / 'workflows/agent-context', materials[run_binding['ref']],
                                     grant['scope_ref'], PRINCIPAL)
        grant_binding = original('grant:owned-t31-agent-context', grant)
        routing_binding = original('routing:owned-t31-agent-context', {
            'schema_version': 'lab-owned-workflow-routing/v1-candidate', 'grant_binding': grant_binding,
            'journal_root': 'workflows/agent-context', 'journal_config_sha256': store.config_sha256})
        producer_root = owned / 'producer'
        producer_root.mkdir(mode=0o700)
        producer_key, producer_policy_path, producer_policy_sha = F.provision(
            producer_root, source_name=P.source.CURRENT_LEGACY_NAME,
            principal=PRINCIPAL, max_actions=64)
        producer_channel = A.ReaderChannel(producer_policy_path, producer_policy_sha, schemas)
        producer_channel.authenticate(F.proof(producer_key, producer_channel.challenge))
        producer_key = None
        producer_service = S.Service(view, producer_channel, schemas)
        bridge_installer = selected_bridge_installer()
        bridge_materials, bridge_binding, output_plan_binding = bridge_installer.prepare_materials(
            owned_root=owned, principal_ref=PRINCIPAL, scope_ref=grant['scope_ref'],
            source_cut=cut, first_api_custody=producer_service.vault.root)
        if set(materials) & set(bridge_materials):
            raise ValueError('private output bridge input reference collision')
        materials.update(bridge_materials)
        rows = []
        for index, (ref, raw) in enumerate(materials.items()):
            path = 'inputs/' + str(index) + '.json'
            W.atomic(workspace / path, raw)
            rows.append({'ref': ref, 'path': path, 'sha256': P.source.sha(raw)})
        manifest = {'schema_version': 'lab-owned-candidate-workspace/v1-candidate',
                    'workspace_ref': 'T31-workflow-' + os.urandom(12).hex(),
                    'principal_ref': PRINCIPAL, 'scope_refs': [grant['scope_ref']],
                    'materials': rows, 'target_metadata': {}, 'authority_effect': 'none',
                    'actual_owner_outcome': None}
        manifest_raw = P.source.encoded(manifest)
        W.atomic(workspace / 'workspace.json', manifest_raw)
        key = Ed25519PrivateKey.generate()
        component_path = BASE / 'workflow-transition-v1'
        policy = {
            'schema_version': 'lab-local-workflow-transition-policy/v1-candidate',
            'principal_ref': PRINCIPAL,
            'reader_public_key': base64.b64encode(key.public_key().public_bytes_raw()).decode(),
            'host_uid': os.getuid(), 'source_name': P.source.CURRENT_LEGACY_NAME,
            'scope_refs': [grant['scope_ref']], 'expires_at': end.isoformat(),
            'max_request_bytes': 1048576, 'max_response_bytes': 4194304, 'max_calls': 128,
            'allowed_operations': list(P.WORKFLOW_TRANSITION_SUPPORTED), 'revoked': False,
            'scope_posture': 'isolated-candidate-preparation', 'authority_effect': 'none',
            'actual_owner_outcome': None,
            'workspace': {'root': str(workspace), 'manifest_sha256': P.source.sha(manifest_raw), 'max_actions': 8},
            'session_control': None, 'projection_control': None,
            'purpose': 'durable-metadata-and-exact-workflow-transition',
            'development_authorization_binding': public_binding(AUTHORIZATION), 'scope_control': None,
            'workflow_source_control': P.source.current_workflow_bindings(),
            'workflow_control': {'routing_binding': routing_binding,
                                 'kernel_binding': public_binding(component_path / 'kernel.py'),
                                 'journal_binding': public_binding(API / 'workflow_output_journal.py')},
        }
        policy_path = owned / 'reader-policy.json'
        policy_raw = P.compact(policy)
        W.atomic(policy_path, policy_raw)
        if not schemas.valid('reader-authentication', policy):
            reasons = [(list(e.path), e.message[:180]) for e in schemas.validators['reader-authentication'].iter_errors(policy)]
            raise ValueError('new private T31 policy schema refused: ' + repr(reasons[:3]))
        channel = A.ReaderChannel(policy_path, P.source.sha(policy_raw), schemas)
        service = None
        try:
            context = channel.authenticate(F.proof(key, channel.challenge))['context']
            key = None
            service = S.Service(view, channel, schemas)
            selected_output_plan = bridge_installer.bind_service(service, P, bridge_binding)
            call = F.call(context, 'lab.status', cut)
            call.update(operation='workflow.transition', idempotency_key=message['idempotency_key'],
                        message=copy.deepcopy(message), max_response_bytes=4194304,
                        deadline=end.isoformat())
            yield {'service': service, 'channel': channel, 'view': view, 'schemas': schemas,
                   'workspace': workspace, 'store': store, 'call': call, 'message': message,
                   'source_cut': cut, 'policy': policy, 'context': context, 'protocol': P,
                   'fixtures': F, 'journal': J, 'headers': headers, 'grant': grant,
                   'output_plan': selected_output_plan,
                   'output_plan_binding': output_plan_binding,
                   'bridge_binding': bridge_binding,
                   'bridge_installer': bridge_installer,
                   'producer_service': producer_service,
                   'producer_channel': producer_channel,
                   'producer_policy_path': producer_policy_path,
                   'producer_policy_sha': producer_policy_sha,
                   'producer_context': producer_channel.context,
                   'owned_root': owned,
                   'materials': materials,
                   'run_binding': run_binding,
                   'definition_binding': definition_binding}
        finally:
            if service is not None:
                service.close()
            channel.close()
            producer_service.close()
            producer_channel.close()
            G.verify(SOURCE_SHA)

