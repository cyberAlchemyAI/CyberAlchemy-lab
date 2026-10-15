"""Actual policy/Session composition only; no positive lesson application claim."""
import ast
from contextlib import ExitStack
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
import uuid

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
API = BASE / 'api-v83'
KIND = 'lab-local-lesson-application-policy/v2-candidate'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    source_binding = bind(API / 'source-manifest.json')
    started = time.monotonic()
    name = '_cal_API83_live_application_composition'
    spec = importlib.util.spec_from_file_location(name, API / '__init__.py', submodule_search_locations=[str(API)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    S = __import__(name + '.test_custody_sessions', fromlist=['Sessions'])
    P = __import__(name + '.protocol', fromlist=['Schemas'])
    A = __import__(name + '.auth', fromlist=['ReaderChannel'])
    W = __import__(name + '.workspace', fromlist=['atomic'])
    G = __import__(name + '.guard', fromlist=['verify'])
    G.verify(source_binding['sha256'])
    observations = []

    class Composition(unittest.TestCase):
        setUpClass = classmethod(S.Sessions.setUpClass.__func__)
        invoke = S.Sessions.invoke
        success = S.Sessions.success
        fresh_delivery = S.Sessions.fresh_delivery
        opening = S.Sessions.opening
        opening_success = S.Sessions.opening_success
        inspection = S.Sessions.inspection
        closing = S.Sessions.closing
        tearDown = S.Sessions.tearDown

        def setUp(self):
            self.fixture_stack = ExitStack()
            self.addCleanup(self.fixture_stack.close)
            self.root = Path(self.fixture_stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-API83-live-application-')))
            self.root.chmod(0o700)
            self.key, self.policy, _ = S.provision(self.root, 'custody-participation', self.materials,
                                                self.metadata, principal=S.R.PRINCIPAL,
                                                projection_control=S.projection_control(self.view))
            policy = P.frame_parse(self.policy.read_bytes())
            self.identities = {'session_ref': 'agent-session:R03-live:' + uuid.uuid4().hex,
                               'agent_instance_ref': 'agent-instance:R03-live:' + uuid.uuid4().hex}
            authorization = RUN / 'authorization.json'
            # Opening-only witness; the selected source has no current Lesson.
            # The application handler must still resolve all its own exact inputs.
            method = BASE / 'lesson-application-v2/preparation.py'
            witness = P.source.encoded({'schema_version': 'lab-opening-only-application-routing-witness/v1-candidate',
                                         'scope_ref': policy['scope_refs'][0], 'source_cut': S.cut(self.view),
                                         'application_runtime_qualified': False, 'authority_effect': 'none'})
            digest = P.source.sha(witness)
            W.atomic(self.root / 'workspace/objects' / (digest + '.json'), witness)
            workspace = P.frame_parse((self.root / 'workspace/workspace.json').read_bytes())
            routing = {'ref': 'workspace-object:' + workspace['workspace_ref'] + ':' + digest, 'sha256': digest}
            policy.update(schema_version=KIND, purpose='current-participation-and-exact-lesson-application',
                          development_authorization_binding=P.binding(str(authorization.relative_to(ROOT)), authorization.read_bytes()),
                          allowed_operations=list(P.APPLICATION_SESSION_SUPPORTED),
                          application_control={'routing_binding': routing,
                                               'method_binding': P.binding(str(method.relative_to(ROOT)), method.read_bytes()),
                                               'runtime_identities': self.identities})
            self.assertTrue(self.schemas.valid('reader-authentication', policy))
            no_session = json.loads(json.dumps(policy))
            no_session['session_control'] = None
            self.assertFalse(self.schemas.valid('reader-authentication', no_session))
            extra = json.loads(json.dumps(policy))
            extra['application_control']['runtime_identities']['restore_memory'] = True
            self.assertFalse(self.schemas.valid('reader-authentication', extra))
            malformed = json.loads(json.dumps(policy))
            malformed['application_control']['runtime_identities']['session_ref'] = 'caller:arbitrary'
            self.assertFalse(self.schemas.valid('reader-authentication', malformed))
            raw = P.compact(policy)
            # This is a new owned fixture, before any channel authenticates.
            self.policy.write_bytes(raw)
            self.policy_pin = P.source.sha(raw)
            self.channel = A.ReaderChannel(self.policy, self.policy_pin, self.schemas)
            self.authenticated = self.channel.authenticate(S.proof(self.key, self.channel.challenge))
            self.service = S.Service(self.view, self.channel, self.schemas)
            self.fixture_stack.callback(self.service.close)
            self.delivery_result = None
            self.opened = []
            observations.append({'phase': 'actual-new-policy-authentication-and-closed-schema-refusals', 'result': 'PASS'})

        def test_actual_open_retry_close_and_identity_reuse_refusal(self):
            self.assertIsNotNone(self.service.sessions)
            self.assertEqual(self.service.sessions.live, {})
            self.assertEqual(self.service.sessions.history(), {})
            opened, original_call = self.opening_success()
            self.assertEqual(opened['session_ref'], self.identities['session_ref'])
            self.assertEqual(opened['agent_instance_ref'], self.identities['agent_instance_ref'])
            resource = self.service.sessions.live[opened['session_ref']]
            self.assertLessEqual((resource.expires - A.instant(opened['started_at'])).total_seconds(), 900)
            self.assertIs(resource.source, self.view.custody_signed_sources)
            self.assertEqual(len(list(self.service.sessions.directory.glob('runtime-identity-*.json'))), 2)
            observations.append({'phase': 'original-actual-opening-one-use-reservation-and-900-second-ceiling', 'result': 'PASS'})
            retry = json.loads(json.dumps(original_call))
            retry['call_id'] = 'call:opening-retry:' + uuid.uuid4().hex
            self.assertEqual(self.success(retry), opened)
            self.assertIs(self.service.sessions.live[opened['session_ref']], resource)
            observations.append({'phase': 'exact-original-journal-retry-keeps-same-resource', 'result': 'PASS'})
            closed = self.success(self.closing(opened))
            self.assertTrue(closed['discarded_memory'])
            self.assertFalse(closed['agent_identity_reuse_allowed'])
            self.assertTrue(resource.closed)
            self.assertEqual(resource.memory, [])
            self.assertNotIn(opened['session_ref'], self.service.sessions.live)
            observations.append({'phase': 'original-actual-closing-and-disposal', 'result': 'PASS'})
            second = self.opening(key='open:new-key:' + uuid.uuid4().hex)
            refused = self.invoke(second)
            self.assertEqual(refused['kind'], 'error')
            self.assertEqual(refused['message']['code'], 'indeterminate')
            self.assertEqual(self.service.sessions.live, {})
            self.assertEqual(len(list(self.service.sessions.directory.glob('runtime-identity-*.json'))), 2)
            observations.append({'phase': 'new-key-cannot-reuse-closed-identity-or-reconstruct-resource', 'result': 'PASS'})

    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Composition))
    G.verify(source_binding['sha256'])
    # Only fixed repository frame names are exported, never exception values.
    errors = []
    for test, trace in result.errors + result.failures:
        lines = trace.splitlines()
        frames = [line.strip() for line in lines if line.strip().startswith('File "' + str(ROOT))]
        errors.append({'test_id': test.id(), 'repository_frames': frames,
                       'safe_error_summary': 'Actual composition case failed; inspect original bounded test and phase evidence.'})
    report = {'schema_version': 'lab-live-application-composition-qualification/v1-candidate',
              'result': 'PASS' if result.wasSuccessful() else 'FAIL', 'actual_child_completed': True,
              'cases_run': result.testsRun, 'failure_count': len(result.failures), 'error_count': len(result.errors),
              'phases': observations, 'errors': errors, 'duration_seconds': time.monotonic() - started,
              'files': [source_binding, bind(API / 'contract-profile.json'), bind(Path(__file__).resolve()),
                        bind(BASE / 'lesson-application-v2/DESIGN.md')],
              'actual_clock_and_source_guards_unchanged': True, 'application_runtime_qualified': False,
              'whole_API_qualified': False, 'tool_dispatches': 0, 'actual_owner_outcome': None, 'authority_effect': 'none',
              'claim_ceiling': 'Actual new policy authentication and original Session opening/closing composition only. No positive Lesson Application or outcome qualification.'}
    output = RUN / 'API83-live-application-composition-0001.json'
    with output.open('x') as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': report['result'], 'report_binding': bind(output), 'cases_run': result.testsRun}), flush=True)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':raise SystemExit(main())
