"""Exercise API70 single-plan Session and first native Agent challenge call."""

from __future__ import annotations

import base64
import copy
from datetime import datetime, timedelta, timezone
import hashlib
import importlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
import sys
import traceback
import uuid

sys.path.insert(0,str(Path.home()/'.local/share/cyberalchemy-lab/native-install/t22-0001/deps'))

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v70-t15-integrated-local-0001'
SOURCE_SHA = 'dba3969685b1136743921d3fc17bd2bcfe656a826f73b7e535042239716f7316'
PROFILE_SHA = '0fb2b544fb1a523b3eb861972e97b12ceb28f5b2f0524fbcec4baff468e08011'
RECEIPT = HERE / 'LIVE-NATIVE-AGENT-COLD-API70-0001.json'
CALL_OBSERVATION = HERE / 'NATIVE-AGENT-COLD-CALL-API70-0002.json'
DIAGNOSTIC_ROOT = Path.home() / '.local/share/cyberalchemy-lab/t22-native-agent-diagnostics'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def compact(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode()


def journal(vault):
    return {p.relative_to(vault.root).as_posix(): sha(p.read_bytes())
            for p in (vault.root / 'journal').rglob('*') if p.is_file()}


def private_original(directory, name, raw):
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    if directory.stat().st_mode & 0o077:
        raise ValueError('diagnostic custody must be owner-only')
    fd = os.open(directory / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)


def run():
    if not sys.flags.isolated or not sys.dont_write_bytecode or RECEIPT.exists():
        raise ValueError('isolated no-replace native probe required')
    sys.path.insert(0, str(API.parent))
    package = API.name
    guard = importlib.import_module(package + '.guard')
    source = guard.verify(SOURCE_SHA)
    if source['profile_binding']['sha256'] != PROFILE_SHA:
        raise ValueError('selected API70 profile differs')
    test = importlib.import_module(package + '.test_custody_sessions')
    P = importlib.import_module(package + '.protocol')
    M = importlib.import_module(package + '.artifact_model')
    H = importlib.import_module(package + '.handlers')
    F = importlib.import_module(package + '.fixtures')
    A = importlib.import_module(package + '.auth')
    MT = importlib.import_module(package + '.machine_transport')
    CF = importlib.import_module(package + '.challenge_fixture')
    CS = importlib.import_module(package + '.challenge_submission')
    W = importlib.import_module(package + '.workspace')
    G = importlib.import_module(package + '.agent_challenge_grant')
    # Local diagnostic only: retain the original public invalid-contract reply,
    # while recording its underlying exception privately for the next repair.
    original_preflight = CS.ChallengeSubmission.preflight
    diagnostic = DIAGNOSTIC_ROOT / uuid.uuid4().hex
    def traced_preflight(builder, message, outer, key):
        started_at = datetime.now(timezone.utc).isoformat()
        try:
            return original_preflight(builder, message, outer, key)
        except Exception as error:
            private_original(diagnostic, 'preflight-trace.txt',
                             ('started_at=' + started_at + '\nended_at=' +
                              datetime.now(timezone.utc).isoformat() + '\n' +
                              ''.join(traceback.format_exception(error))).encode())
            raise
    CS.ChallengeSubmission.preflight = traced_preflight
    test.PROFILE = PROFILE_SHA
    cls = test.Sessions
    case = cls(methodName='test_01_actual_private_memory_erased')
    class_ready = setup = False
    observations = []
    peer = None
    try:
        print('T22 API70 setup begins=' + datetime.now(timezone.utc).isoformat(),
              file=sys.stderr, flush=True)
        cls.setUpClass(); class_ready = True
        print('T22 API70 source replay complete=' + datetime.now(timezone.utc).isoformat(),
              file=sys.stderr, flush=True)
        view = cls.view
        def pick(kind, identity=None):
            return CF.pick(view, kind, identity)
        work = pick('work', 'work:completion-legacy-local-4636eca980a5d94d')
        contract = pick('challenge-contract',
                        'challenge-contract:completion-legacy-local-4636eca980a5d94d-agent-contest')
        project = CF.pick_endpoint(view, 'project')
        work_header = M.artifact_ref(view, work)
        contract_header = M.artifact_ref(view, contract)
        project_header = M.artifact_ref(view, project)
        work_raw = M.record_bytes(view, work)[0]
        contract_body = P.frame_parse(M.record_bytes(view, contract)[0])
        payload = contract_body['payload']
        work_binding = P.binding(work_header['version_ref'], work_raw)
        validation_path = API / 't22-validation-receipt.json'
        validation_raw = validation_path.read_bytes()
        validation_binding = P.binding(str(validation_path.relative_to(ROOT)), validation_raw)
        cls.materials[work_binding['ref']] = work_raw
        cls.materials[validation_binding['ref']] = validation_raw
        case.setUp(); setup = True
        print('T22 API70 host setup complete=' + A.now().isoformat(),
              file=sys.stderr, flush=True)

        def native(service, call):
            raw = P.compact(call)
            reply = service.call(raw)
            if reply.get('kind') not in ('result', 'error') or not case.schemas.valid('api-reply', reply):
                raise ValueError('native API reply contract refused: ' + str(reply))
            if reply['request_binding']['sha256'] != sha(raw):
                raise ValueError('native API request binding differs')
            W.privacy(reply)
            observations.append({'operation': call['operation'], 'kind': reply['kind'],
                                 'code': reply.get('message', {}).get('code'),
                                 'reply_sha256': sha(P.compact(reply))})
            return reply

        def success(call):
            reply = native(case.service, call)
            if reply['kind'] != 'result':
                raise ValueError('native parent call refused: ' + str(reply['message']))
            return reply['message']

        case.invoke = lambda call: native(case.service, call)
        case.success = success
        status = success(F.call(case.channel.context, 'lab.status', H.cut(view)))
        print('T22 API70 status complete=' + A.now().isoformat(),
              file=sys.stderr, flush=True)
        if 'challenge.submit' not in status['supported_operations']:
            raise ValueError('challenge operation not advertised')
        opened, _ = case.opening_success()
        print('T22 API70 Session opened=' + A.now().isoformat() +
              ' started_at=' + opened['started_at'] +
              ' expires_at=' + opened['expires_at'], file=sys.stderr, flush=True)
        resource = case.service.sessions.live[opened['session_ref']]
        cut = H.cut(view)
        if opened['source_cut'] != G.native_cut():
            raise ValueError('Session selected another source cut')
        now = A.now()
        issuer = Ed25519PrivateKey.generate()
        issuer_public = issuer.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
        live = {'agent_record': resource.agent, 'session_record': resource.session,
                'session_result': opened,
                'context_view_header': case.delivery_result['context_view'],
                'context_delivery_binding': opened['context_delivery_binding']}
        grant_payload = G.project_live(live, cut, now, os.getuid(),
                                       case.channel.policy['expires_at'],
                                       'grant:R03-0005:' + uuid.uuid4().hex,
                                       issuer_public, resource.guard)
        grant_envelope = G.sign(grant_payload, issuer)
        del issuer
        G.verify(grant_envelope, issuer_public, grant_payload, A.now())
        agent = resource.agent
        agent_header = {'scope_ref': agent['scope_ref'], 'identity_ref': agent['node_id'],
                        'version_ref': agent['node_id'] + '@ephemeral.1',
                        'carrier_ref': 'cal.artifact-type.agent-instance/v1',
                        'byte_sha256': sha(P.compact(agent))}
        # The route must stay inside both the signed technical grant and the
        # actual live Session. A shorter arbitrary lease expired during the
        # source-backed native preflight on the previous diagnostic attempt.
        expires = min(A.instant(grant_payload['expires_at']), resource.expires)
        if not A.now() < expires:
            raise ValueError('no live Agent challenge lease remains')
        ground = 'scope-error'
        accepted = [
            {'kind': 'source', 'binding': work_binding, 'artifact': work_header,
             'receipt_binding': None, 'original_binding': None,
             'source_posture': 'signed-source'},
            {'kind': 'validation-receipt', 'binding': validation_binding, 'artifact': None,
             'receipt_binding': {'path': str(validation_path.relative_to(ROOT)),
                                 'sha256': sha(validation_raw)},
             'original_binding': None, 'source_posture': 'completed-validation'},
        ]
        routing = {
            'schema_version': 'lab-independent-challenge-submit-routing/v1-candidate',
            'principal_ref': case.channel.context['principal_ref'],
            'storage_scope_ref': view.data['config']['scope_ref'],
            'candidate_scope_ref': view.data['config']['scope_ref'],
            'challenge_contract': contract_header,
            'challenger': agent_header,
            'evidence_project': project_header,
            'source_cut': cut,
            'subjects': [work_header],
            'grounds': [ground],
            'accepted_evidence': accepted,
            'policy_ref': payload['policy_ref'],
            'owner_route': payload['owner_route'],
            'resolution_gate_ref': payload['resolution_gate_ref'],
            'residue_route_ref': payload['unresolved_residue_route'],
            'response_mode': 'evidence',
            'not_before': (now - timedelta(seconds=60)).isoformat(),
            'expires_at': expires.isoformat(),
            'revoked': False,
            'development_authorization_binding': P.binding(
                'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json',
                (ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json').read_bytes()),
            'actual_owner_outcome': None,
            'authority_effect': 'none',
        }
        routing_binding = case.service.vault.object(P.compact(routing))
        print('T22 route expires_at=' + routing['expires_at'] +
              ' created_at=' + A.now().isoformat(), file=sys.stderr, flush=True)
        expired_route = copy.deepcopy(routing)
        expired_route['not_before'] = (A.now() - timedelta(minutes=2)).isoformat()
        expired_route['expires_at'] = (A.now() - timedelta(minutes=1)).isoformat()
        expired_binding = case.service.vault.object(P.compact(expired_route))
        expired_policy = copy.deepcopy(case.channel.policy)
        expired_policy['schema_version'] = 'lab-local-challenge-candidate-policy/v1-candidate'
        expired_policy['challenge_control'] = {'routing_binding': expired_binding}
        expired_before = journal(case.service.vault)
        try:
            CS.validate_control(expired_policy, case.schemas)
        except ValueError as error:
            if 'challenge routing expired' not in str(error):
                raise
        else:
            raise ValueError('expired route was not causally refused')
        if journal(case.service.vault) != expired_before:
            raise ValueError('expired route changed challenge journal')
        selection = {
            'envelope': grant_envelope,
            'issuer_public': base64.b64encode(issuer_public).decode(),
            'challenge_control': {'routing_binding': routing_binding},
        }
        source_binding = {'path': str((API / 'source-manifest.json').relative_to(ROOT)),
                          'sha256': SOURCE_SHA}
        peer = MT.select(case.service, opened['session_ref'], source_binding,
                         agent_challenge=selection)
        machine_context = peer.authenticate(peer.proof())
        if machine_context['agent_instance_ref'] != agent['node_id']:
            raise ValueError('authenticated Machine Actor differs')

        event = P.frame_parse((ROOT / 'authority/artifact-types/challenge-event/v1/fixtures/valid/record.json').read_bytes())
        event.update(node_id='challenge-event:R03-agent:' + uuid.uuid4().hex,
                     name='Agent challenge of exact API30 Work revision',
                     owner_ref=contract_body['owner_ref'],
                     scope_ref=routing['candidate_scope_ref'],
                     lifecycle_state='candidate',
                     evidence_refs=[r['binding']['ref'] for r in accepted],
                     relation_refs=[{'relation_kind_ref': 'relation.challenges',
                                     'counterpart_kind': view.handle.operations.endpoint_kind(work, view.data['projection']),
                                     'counterpart_ref': work_header['version_ref'],
                                     'direction': 'source'}],
                     successor_refs=[],
                     challenge_route=payload['owner_route'],
                     claim_ceiling='Local Agent challenge candidate; no factual ground decision or admission.')
        event['payload'].update(challenge_contract_ref=contract_header['version_ref'],
                                subject_ref=work_header['identity_ref'],
                                subject_version_ref=work_header['version_ref'],
                                challenger_ref=agent['node_id'],
                                ground=ground,
                                evidence_refs=event['evidence_refs'],
                                response_state='open',
                                resolution_decision_ref='none',
                                residue_refs=[],
                                submitted_at=A.now().isoformat())
        candidate_raw = (json.dumps(event, indent=3, ensure_ascii=False) + '\n').encode()
        candidate_binding = case.service.vault.object(candidate_raw)
        actor = {k: machine_context[k] for k in
                 ('principal_ref', 'agent_instance_ref', 'assignment_ref', 'session_ref')}
        actor['role_assignment_refs'] = machine_context['role_assignment_bindings']
        routes = {k: routing[k] for k in
                  ('policy_ref', 'owner_route', 'resolution_gate_ref', 'residue_route_ref', 'response_mode')}
        routes['response_period'] = payload['response_period']
        validator = P.binding(str((API / 'challenge_submission.py').relative_to(ROOT)),
                              (API / 'challenge_submission.py').read_bytes())
        eligibility_raw = CS.eligibility_bytes(
            actor=actor, subject=work_header, contract=contract_header,
            challenger=agent_header, ground=ground,
            evidence=[{'kind': r['kind'], 'binding': r['binding'],
                       'source_posture': r['source_posture']} for r in accepted],
            source_cut=cut, routes=routes, validator_binding=validator)
        eligibility_binding = case.service.vault.object(eligibility_raw)
        message = {
            'schema_version': 'lab-challenge-request/v1-candidate',
            'request_ref': 'request:R03-agent:' + uuid.uuid4().hex,
            'actor': actor,
            'subject': work_header,
            'challenge_contract': contract_header,
            'ground': ground,
            'evidence_bindings': [r['binding'] for r in accepted],
            'eligibility_evaluation_binding': eligibility_binding,
            'challenge_candidate_binding': candidate_binding,
            'source_cut': cut,
            'authority_effect': 'none',
        }
        for name, raw in (('routing.json', P.compact(routing)),
                          ('candidate.json', candidate_raw),
                          ('eligibility.json', eligibility_raw),
                          ('request.json', P.compact(message))):
            private_original(diagnostic, name, raw)
        call = F.call(machine_context, 'lab.status', cut)
        call.update(operation='challenge.submit',
                    idempotency_key='fixture:R03-agent-challenge:' + uuid.uuid4().hex,
                    message=message)
        before = journal(case.service.vault)
        print('T22 positive call at=' + A.now().isoformat(), file=sys.stderr, flush=True)
        reply = peer.call(P.compact(call))
        print('T22 positive reply at=' + A.now().isoformat(), file=sys.stderr, flush=True)
        call_observation = {
            'schema_version': 'lab-T22-API70-challenge-call-observation/v1-candidate',
            'api_source_sha256': SOURCE_SHA, 'api_profile_sha256': PROFILE_SHA,
            'source_cut': cut, 'session_ref': opened['session_ref'],
            'session_expires_at': opened['expires_at'],
            'reply_kind': reply.get('kind'),
            'reply_code': reply.get('message', {}).get('code'),
            'reply_sha256': sha(P.compact(reply)),
            'journal_before': before,
            'journal_after': journal(case.service.vault),
            'authority_effect': 'none',
        }
        private_original(diagnostic, 'call-observation.json', P.compact(call_observation))
        raw_observation = json.dumps(call_observation, sort_keys=True, indent=2).encode() + b'\n'
        fd = os.open(CALL_OBSERVATION, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw_observation)
        if reply.get('kind') not in ('result', 'error') or not case.schemas.valid('api-reply', reply):
            raise ValueError('native Agent challenge reply contract differs: ' + str(reply))
        observations.append({'operation': 'challenge.submit', 'kind': reply['kind'],
                             'code': reply.get('message', {}).get('code'),
                             'reply_sha256': sha(P.compact(reply))})
        if reply['kind'] != 'result':
            raise ValueError('native Agent challenge refused: ' + str(reply['message']))
        proposal = reply['message']
        if proposal['schema_version'] != 'lab-change-proposal/v1-candidate' or proposal['base_cut'] != cut:
            raise ValueError('native Agent challenge proposal differs')
        # A fresh Vault instance and then a new interpreter reopen the actual
        # completed claim/result and candidate original bytes before cleanup.
        delta = set(journal(case.service.vault)) - set(before)
        results = [name for name in delta if name.endswith('.result.json')]
        if len(results) != 1:
            raise ValueError('one new completed challenge result required')
        namespace = Path(results[0]).name.removesuffix('.result.json')
        cold = W.Vault(peer)
        claim, completed = cold.state(namespace)
        if (claim['operation'] != 'challenge.submit' or completed['posture'] != 'completed'
                or P.frame_parse(cold.object_read(completed['domain_binding'])) != proposal):
            raise ValueError('fresh Vault did not reopen exact completed proposal')
        cold_script = HERE / 'cold_challenge_api70.py'
        with tempfile.TemporaryDirectory(prefix='cal-T22-challenge-cold-copy-') as scratch:
            scratch = Path(scratch); scratch.chmod(0o700)
            root_copy = scratch / 'vault'
            shutil.copytree(case.service.vault.root, root_copy)
            private_policy = copy.deepcopy(peer.policy)
            private_policy['workspace']['root'] = str(root_copy)
            policy_file = scratch / 'policy.json'
            policy_file.write_bytes(P.compact(private_policy)); policy_file.chmod(0o600)
            command = [sys.executable, '-I', '-B', str(cold_script), str(policy_file),
                       namespace, sha(candidate_raw)]
            child = subprocess.run(command, capture_output=True, check=False,
                                   env={**os.environ, 'PYTHONDONTWRITEBYTECODE':'1'})
            if child.returncode != 0:
                raise ValueError('fresh-process native journal cold read refused: ' + child.stdout.decode())
            cold_result = json.loads(child.stdout)
            # Corrupt only the isolated copy, never selected source or live journal.
            result_path = root_copy / 'journal' / (namespace + '.result.json')
            original_result = result_path.read_bytes()
            changed = json.loads(original_result); changed['claim_sha256'] = '0' * 64
            result_path.write_bytes(P.compact(changed))
            bad_claim = subprocess.run(command, capture_output=True, check=False,
                                       env={**os.environ, 'PYTHONDONTWRITEBYTECODE':'1'})
            result_path.write_bytes(original_result)
            if bad_claim.returncode != 2:
                raise ValueError('changed isolated journal claim was accepted')
            candidate_object = root_copy / 'objects' / (sha(candidate_raw) + '.json')
            original_candidate = candidate_object.read_bytes()
            candidate_object.write_bytes(original_candidate + b' ')
            bad_body = subprocess.run(command, capture_output=True, check=False,
                                      env={**os.environ, 'PYTHONDONTWRITEBYTECODE':'1'})
            candidate_object.write_bytes(original_candidate)
            if bad_body.returncode != 2:
                raise ValueError('changed isolated candidate bytes were accepted')
            restored = subprocess.run(command, capture_output=True, check=False,
                                      env={**os.environ, 'PYTHONDONTWRITEBYTECODE':'1'})
            if restored.returncode != 0 or json.loads(restored.stdout) != cold_result:
                raise ValueError('restored isolated cold journal differs')
        peer.close(); peer = None
        inspected = success(case.inspection(opened['session_ref']))
        closed = success(case.closing(opened, inspected))
        if not resource.closed or not closed['discarded_memory']:
            raise ValueError('Agent Session was not disposed')
        result = {
            'schema_version': 'lab-T22-native-Agent-challenge/v1-candidate',
            'result': 'PASS',
            'api_source_binding': source_binding,
            'api_profile_binding': {'path': str((API / 'contract-profile.json').relative_to(ROOT)),
                                    'sha256': PROFILE_SHA},
            'source_cut': cut,
            'agent_instance_ref': agent['node_id'],
            'session_ref': opened['session_ref'],
            'technical_grant_payload_sha256': sha(G.compact(grant_payload)),
            'challenge_response_sha256': sha(P.compact(reply)),
            'fresh_process_cold_journal': cold_result,
            'cold_checker_sha256': sha(cold_script.read_bytes()),
            'isolated_changed_claim_refused': True,
            'isolated_changed_candidate_refused': True,
            'isolated_restored_cold_read_equal': True,
            'challenge_proposal_ref': proposal.get('proposal_ref'),
            'wrong_actor_refused_in_this_run': False,
            'wrong_actor_prior_API56_observation_only': False,
            'expired_route_preflight_refused': True,
            'expired_route_journal_unchanged': True,
            'session_closed': True,
            'native_operations': observations,
            'challenge_submitted': True,
            'challenge_resolved': False,
            'contest_outcome': None,
            'owner_decision': None,
            'authority_effect': 'none',
        }
    finally:
        if peer is not None:
            peer.close()
        if setup:
            try: case.tearDown()
            finally: case.doCleanups()
        if class_ready:
            cls.doClassCleanups()
    guard.verify(SOURCE_SHA)
    raw = json.dumps(result, sort_keys=True, indent=2).encode() + b'\n'
    fd = os.open(RECEIPT, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    return {'result': 'PASS', 'sha256': sha(raw), 'proposal': result['challenge_proposal_ref']}


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True))
