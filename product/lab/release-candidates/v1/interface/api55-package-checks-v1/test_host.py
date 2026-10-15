"""Real authenticated import and native source/target checks on one owned fixture."""
import copy
from contextlib import ExitStack
from datetime import timedelta
import importlib
from pathlib import Path
import tempfile
import unittest
import uuid

PACKAGE = None
PROFILE = None


class PackageChecks(unittest.TestCase):
    events = []
    source_exit_completed = False
    owned_cleanup_completed = False
    positive_import_completed = False

    @classmethod
    def setUpClass(cls):
        cls.stack = ExitStack()
        cls.P = importlib.import_module(PACKAGE + '.protocol')
        cls.A = importlib.import_module(PACKAGE + '.auth')
        cls.S = importlib.import_module(PACKAGE + '.service')
        cls.F = importlib.import_module(PACKAGE + '.fixtures')
        cls.PF = importlib.import_module(PACKAGE + '.package_fixture')
        cls.H = importlib.import_module(PACKAGE + '.handlers')
        try:
            cls.view = cls.stack.enter_context(cls.P.source.replay_source('custody-participation'))
            cls.before = cls.view.handle.common.digest(cls.view.data['projection'])
            cls.schemas = cls.P.Schemas(PROFILE)
            cls.root = Path(cls.stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-API53-owned-package-')))
            cls.root.chmod(0o700)
            key, path, pin, cls.message, cls.expected, cls.plan, cls.archive = cls.PF.provision(cls.root, cls.view)
            cls.channel = cls.A.ReaderChannel(path, pin, cls.schemas)
            authenticated = cls.channel.authenticate(cls.F.proof(key, cls.channel.challenge))
            cls.context = authenticated['context']
            assert cls.context['agent_instance_ref'] is cls.context['assignment_ref'] is cls.context['session_ref'] is None
            cls.host = cls.S.Service(cls.view, cls.channel, cls.schemas)
            cls.stack.callback(cls.host.close)
            cls.original = cls.F.call(cls.context, 'lab.status', cls.H.cut(cls.view))
            cls.original.update(operation='package.import', idempotency_key=cls.PF.KEY,
                                message=copy.deepcopy(cls.message))
        except BaseException:
            cls.stack.close()
            cls.owned_cleanup_completed = not cls.root.exists() if hasattr(cls, 'root') else False
            raise

    @classmethod
    def tearDownClass(cls):
        try:
            cls.view.custody_signed_sources.guard()
            assert cls.before == cls.view.handle.common.digest(cls.view.data['projection'])
        finally:
            cls.stack.close()
        cls.source_exit_completed = True
        cls.owned_cleanup_completed = not cls.root.exists()

    def invoke(self, value):
        raw = self.P.compact(value)
        reply = self.host.call(raw)
        self.events.append({'original_call': copy.deepcopy(value), 'request_byte_sha256': self.P.source.sha(raw),
                            'reply': copy.deepcopy(reply)})
        return reply

    def fresh(self):
        value = copy.deepcopy(self.original)
        value['call_id'] = 'call:R03-package:' + uuid.uuid4().hex
        return value

    def attributes(self):
        return {p.relative_to(self.host.vault.root).as_posix():
                (p.stat().st_ino, p.stat().st_size, p.stat().st_mtime_ns, p.stat().st_ctime_ns)
                for p in self.host.vault.root.rglob('*')}

    def test_01_actual_import_returns_exact_validated_candidate(self):
        reply = self.invoke(self.original)
        self.assertEqual(reply['kind'], 'result', reply)
        self.assertEqual(reply['message'], self.expected)
        self.assertEqual(reply['handler_binding'], self.P.binding(
            str((Path(self.S.__file__).parent / 'package_import.py').relative_to(self.P.ROOT)),
            (Path(self.S.__file__).parent / 'package_import.py').read_bytes()))
        claim, result = self.host.vault.lookup({'operation': 'package.import', 'idempotency_key': self.PF.KEY}, self.context)
        self.assertIsNotNone(claim)
        self.assertEqual(result['posture'], 'completed')
        proofs = [self.P.source.parse(self.host.vault.object_read(b)) for b in result['evidence_bindings']]
        reports = [p for p in proofs if p.get('schema_version') == 'lab-validation-report/v1-candidate']
        self.assertEqual(len(reports), 2)
        self.assertTrue(all(p['result'] == 'pass' and not p['gaps'] for p in reports))
        self.assertTrue(all(c['result'] == 'pass' for p in reports for c in p['checks']))
        accounts = [p for p in proofs if 'accounted_source_artifacts' in p]
        self.assertEqual(len(accounts), 1)
        self.assertEqual(accounts[0]['accounted_source_artifacts'], 4)
        self.assertEqual(accounts[0]['accounted_source_materials'], 10)
        self.assertFalse(accounts[0]['target_model_validation_pending'])
        self.assertFalse(accounts[0]['automatic_admission'])
        self.assertFalse(accounts[0]['source_retirement'])
        inspect = self.F.call(self.context, 'operation.inspect', self.H.cut(self.view))
        inspect['message']['lookup'] = {'operation': 'package.import', 'idempotency_key': self.PF.KEY}
        checked = self.invoke(inspect)
        self.assertEqual(checked['kind'], 'result', checked)
        self.assertEqual(checked['message']['posture'], 'completed')
        self.assertFalse(checked['message']['retry_allowed'])
        type(self).positive_import_completed = True

    def test_02_actual_actor_control_cut_deadline_and_conflict_refusals(self):
        self.assertTrue(type(self).positive_import_completed, 'positive case must complete first')
        before = self.attributes()
        actor = self.fresh()
        actor['message']['actor']['principal_ref'] = 'principal:forged-package-caller'
        selected = self.fresh()
        selected['idempotency_key'] += ':different-control'
        selected['message']['mapping_binding']['sha256'] = '0' * 64
        stale = self.fresh()
        stale['idempotency_key'] += ':stale-cut'
        stale['message']['target_base_cut']['commit_sequence'] += 1
        stale['expected_source_cut'] = copy.deepcopy(stale['message']['target_base_cut'])
        expired = self.fresh()
        expired['deadline'] = (self.A.now() - timedelta(seconds=1)).isoformat()
        conflict = self.fresh()
        conflict['message']['request_ref'] += ':changed'
        for value, expected in [(actor, 'unauthorized'), (selected, 'unauthorized'), (stale, 'stale-cut'),
                                (expired, 'deadline-exceeded'), (conflict, 'idempotency-conflict')]:
            with self.subTest(expected=expected):
                reply = self.invoke(value)
                self.assertEqual(reply['kind'], 'error', reply)
                self.assertEqual(reply['message']['code'], expected, reply)
        self.assertEqual(before, self.attributes())

    def test_03_exact_retry_is_readonly_and_tampering_requires_recovery(self):
        self.assertTrue(type(self).positive_import_completed, 'positive case must complete first')
        before = self.attributes()
        reply = self.invoke(self.fresh())
        self.assertEqual(reply['kind'], 'result', reply)
        self.assertEqual(reply['message'], self.expected)
        self.assertEqual(before, self.attributes())
        directories = list(Path(self.plan['output_root']).glob('pkg-*'))
        self.assertEqual(len(directories), 1)
        path = directories[0] / 'package.json'
        path.write_bytes(b'{}')
        changed = self.attributes()
        refused = self.invoke(self.fresh())
        self.assertEqual(refused['kind'], 'error', refused)
        self.assertEqual(refused['message']['code'], 'recovery-required', refused)
        self.assertEqual(changed, self.attributes())
        self.assertEqual(path.read_bytes(), b'{}')
