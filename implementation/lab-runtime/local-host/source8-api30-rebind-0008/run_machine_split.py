"""Exact MachineTransport successor with seven reads across two real Sessions."""
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE = Path(__file__).resolve().parent
V4 = HERE.with_name('source8-api30-rebind-0004')
V5 = HERE.with_name('source8-api30-rebind-0005')
V6 = HERE.with_name('source8-api30-rebind-0006')
V6_RESULT_SHA = '076565b442d47bfa431b8ec228da4ac5f5243250f4bf9c2829acdb8b49797ecd'
V6_RUNNER_SHA = 'caf8af0a0994ce936f606d5fcc39930ad7deafef1cba72b3fbc2d8458d60fe92'
V5_RESULT_SHA = '20b649f019253210123a4b345d9a6a8305a6cc5e7b11b158345e341ac307e143'
V5_RUNNER_SHA = '0511ceca71d145c4753a469e56a8ac99655d1565b65ef91e57c35593421a02ea'
V4_RESULT_SHA = '90c3c6ca270031930351485ff9a70660240d55b2186393abe46c32f55d26427f'
METHOD_SHA = '4b6d15ea0127148c9a3ecc92225a11bf4635246f9f0c427928c7da7278587b2e'
SPLIT = []


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def need(ok, why):
    if not ok:
        raise ValueError(why)


def select():
    for path, expected in ((V6/'working/machine-result-0001.json', V6_RESULT_SHA),
                           (V6/'run_machine.py', V6_RUNNER_SHA),
                           (V5/'working/remainder-result-0001.json', V5_RESULT_SHA),
                           (V5/'run_remainder.py', V5_RUNNER_SHA),
                           (V4/'working/whole-classes-result-0001.json', V4_RESULT_SHA)):
        need(path.is_file() and not path.is_symlink() and sha(path) == expected,
             'frozen T02 predecessor byte differs')
    failed = json.loads((V6/'working/machine-result-0001.json').read_bytes())
    need(failed['result'] == 'FAIL' and failed['tests_run'] == 2 and
         [r['result'] for r in failed['case_rows']] == ['PASS', 'ERROR'] and
         len(failed['errors']) == 1 and
         "'NoneType' object has no attribute 'vault'" in failed['errors'][0][1] and
         failed['source_unchanged_during_run'] is True,
         'v6 causal predecessor differs')
    sys.path.insert(0, str(V5))
    import run_remainder as prior
    name, old, manifest = prior.select()
    need(failed['selected_case_ids'] == old['selected_case_ids'][85:],
         'v6 selected Machine suffix differs')
    custody = __import__(name + '.test_custody_sessions', fromlist=['Sessions'])
    module = __import__(name + '.test_machine_transport', fromlist=['MachineTransport'])
    custody.PROFILE = prior.PROFILE_SHA
    module.PROFILE = prior.PROFILE_SHA
    original = module.MachineTransport
    methods = unittest.defaultTestLoader.getTestCaseNames(original)
    need(len(methods) == 14 and hashlib.sha256(
        json.dumps(methods, separators=(',', ':')).encode()).hexdigest() == METHOD_SHA,
        'original 14 Machine method inventory differs')
    return prior, module, original, failed, manifest


def make_class(original, module):
    package = module.__package__
    MT = __import__(package + '.machine_transport', fromlist=['select'])
    F = __import__(package + '.example_fixture', fromlist=['call'])
    M = __import__(package + '.artifact_model', fromlist=['artifact_ref'])
    D = __import__(package + '.current_legacy_context_sessions', fromlist=['D']).D
    source = __import__(package + '.protocol', fromlist=['source']).source
    compact = __import__(package + '.protocol', fromlist=['compact']).compact
    cut = __import__(package + '.handlers', fromlist=['cut']).cut
    record = __import__(package + '.fixture_observation', fromlist=['record']).record

    def test_02_all_seven_public_read_operations_with_actual_Actor(self):
        # A retained Service reference lets the observation record the exact
        # transport refusal even when MachinePeer disposal clears .service.
        def machine_call(request):
            service = self.peer.service
            raw = compact(request)
            reply = self.peer.call(raw)
            if service is not None:
                record(self.id(), service, raw, reply)
            self.machine_events.append({'operation': request['operation'],
                                        'request_sha256': source.sha(raw),
                                        'reply': copy.deepcopy(reply)})
            self.assertTrue(self.schemas.valid('api-reply', reply), reply)
            self.assertEqual(reply['request_binding']['sha256'], source.sha(raw))
            self.assertEqual(reply['trusted_context_binding'],
                             __import__(package + '.protocol', fromlist=['binding']).binding(
                                 self.peer.context['context_ref'], compact(self.peer.context)))
            self.assertEqual(reply['kind'], 'result', reply)
            return reply

        first, _ = self.authenticated()
        first_ref = first['session_ref']
        first_expiry = self.resource.expires
        first_delivery = copy.deepcopy(self.opened_result['context_delivery_binding'])
        current = cut(self.view)
        for op in ('lab.status', 'catalog.get', 'artifact.query'):
            machine_call(F.call(first, op, current))
        subject = next(s for s in self.view.subjects.values()
                       if s['identity'] == self.resource.agent['payload']['profile_ref'].split('@')[0])
        machine_call(F.call(first, 'artifact.inspect', current,
                            artifact=M.artifact_ref(self.view, subject),
                            include=['body', 'contract', 'gaps']))
        need(tuple(e['operation'] for e in self.machine_events) ==
             ('lab.status', 'catalog.get', 'artifact.query', 'artifact.inspect'),
             'first live Machine operation half differs')

        self.peer.close()
        self.assertFalse(self.resource.closed)
        self.assertEqual(self.resource.expires, first_expiry)
        # Make a real new Context delivery before opening the second Session;
        # reusing the prior delivery can retain its earlier host deadline.
        self.delivery_result = None
        self.opened_result, self.opening_call = self.opening_success()
        self.assertNotEqual(self.opened_result['context_delivery_binding'], first_delivery)
        self.resource = self.service.sessions.live[self.opened_result['session_ref']]
        self.peer = MT.select(self.service, self.opened_result['session_ref'], self.selection)
        self.addCleanup(self.peer.close)
        second, _ = self.authenticated()
        self.assertNotEqual(first_ref, second['session_ref'])
        self.assertEqual(self.service.sessions.live[first_ref].expires, first_expiry)
        message = D.query(self.view.custody_signed_sources, self.peer.service.sessions.bridge)
        message['budget'].update(max_input_bytes=65536, max_output_bytes=1048576)
        request = F.call(second, 'lab.status', current)
        request.update(operation='context.get', message=message)
        machine_call(request)
        request = self.inspection(second['session_ref'])
        request['caller_context_ref'] = second['context_ref']
        request['message']['actor'] = {k: second[k] for k in
                                       ('principal_ref', 'agent_instance_ref',
                                        'assignment_ref', 'session_ref')}
        request['message']['actor']['role_assignment_refs'] = []
        machine_call(request)
        machine_call(F.call(second, 'operation.inspect', None,
                            lookup={'operation': 'session.open',
                                    'idempotency_key': self.opening_call['idempotency_key']}))
        self.assertEqual({e['operation'] for e in self.machine_events}, set(MT.READ_OPERATIONS))
        SPLIT.append({'first_session_ref_sha256': source.sha(first_ref.encode()),
                      'second_session_ref_sha256': source.sha(second['session_ref'].encode()),
                      'first_session_expires_at': first_expiry.isoformat(),
                      'second_session_expires_at': self.resource.expires.isoformat(),
                      'fresh_second_context_delivery': True,
                      'first_operations': [e['operation'] for e in self.machine_events[:4]],
                      'second_operations': [e['operation'] for e in self.machine_events[4:]],
                      'original_session_expiry_unchanged': True})

    cls = type(original.__name__, (original,),
               {'test_02_all_seven_public_read_operations_with_actual_Actor':
                test_02_all_seven_public_read_operations_with_actual_Actor})
    cls.__module__ = module.__name__
    cls.__qualname__ = original.__qualname__
    return cls


def main():
    prior, module, original, failed, manifest = select()
    cls = make_class(original, module)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(cls)
    ids = [case.id() for case in suite]
    need(len(ids) == 14 and len(set(ids)) == 14 and
         ids == failed['selected_case_ids'], 'v8 exact Machine IDs differ')
    started = datetime.now(timezone.utc).isoformat()
    result = unittest.TextTestRunner(verbosity=2, failfast=True,
                                     resultclass=prior.Outcome).run(suite)
    unchanged = (sha(prior.API/'source-manifest.json') == prior.API_SHA and
                 all(sha(ROOT/row['path']) == row['sha256'] for row in manifest['files']))
    verdict = {'result': 'PASS' if result.wasSuccessful() and result.testsRun == 14 and
               unchanged and len(SPLIT) == 1 else 'FAIL',
               'predecessor_v6_result_sha256': V6_RESULT_SHA,
               'source_manifest_sha256': prior.API_SHA,
               'profile_sha256': prior.PROFILE_SHA,
               'selected_case_ids': ids, 'started_at_utc': started,
               'completed_at_utc': datetime.now(timezone.utc).isoformat(),
               'tests_run': result.testsRun, 'case_rows': result.rows,
               'failures': [(case.id(), value[-1600:]) for case, value in result.failures],
               'errors': [(case.id(), value[-1600:]) for case, value in result.errors],
               'split_seven_read_evidence': SPLIT,
               'source_unchanged_during_run': unchanged,
               'runner_sha256': sha(Path(__file__).resolve())}
    out = HERE/'working'
    out.mkdir(mode=0o700, exist_ok=True)
    target = out/'machine-split-result-0001.json'
    need(not target.exists(), 'versioned Machine result already exists')
    target.write_text(json.dumps(verdict, sort_keys=True, indent=2) + '\n')
    print(json.dumps({'result': verdict['result'], 'tests_run': result.testsRun,
                      'failures': len(result.failures), 'errors': len(result.errors)}))


if __name__ == '__main__':
    main()
