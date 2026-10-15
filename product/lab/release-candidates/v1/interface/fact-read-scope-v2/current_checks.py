"""Actual API33 host policy, dispatch and boundary observations."""
import base64
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

from . import scope as K

HERE = Path(__file__).resolve().parent
API = HERE.parent / 'api-v33'
NAME = '_cal_boundary_scope_actual_api33'
spec = importlib.util.spec_from_file_location(NAME, API / '__init__.py',
                                            submodule_search_locations=[str(API)])
package = importlib.util.module_from_spec(spec)
sys.modules[NAME] = package
spec.loader.exec_module(package)
def imported(name):
    return __import__(NAME + '.' + name, fromlist=['*'])
P, F, EF, A, S, H = [imported(n) for n in
                     ['protocol', 'fixtures', 'example_fixture', 'auth', 'service', 'handlers']]
D = imported('custody_context_sessions').D
PIN = '2908afb3d739d92d403c3f4035fe5742d626899a23b401103065b21e9314b5f3'
PROFILE = 'b3ad5b5a94c05fe68e087eb16e6de5b574131b30981c0b56035af974c8b2f112'

class CurrentChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        imported('guard').verify('d240d0d47f83b2dfeb9b5cccdba824d22986b37a690cb2318f8a77782e09487a')
        cls.manager = P.source.replay_source('custody-participation')
        cls.view = cls.manager.__enter__()
        cls.parent = cls.view.custody_signed_sources
        cls.schemas = P.Schemas(PROFILE)
        cls.materials, cls.metadata, cls.target = EF.materials_for(cls.view)
    @classmethod
    def tearDownClass(cls):
        cls.manager.__exit__(None, None, None)
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='cal-R03-boundary-policy-')
        self.root = Path(self.temporary.name)
        self.root.chmod(0o700)
        self.key, self.path, self.pin = F.provision(
            self.root, 'custody-participation', self.materials, self.metadata,
            principal=D.records.PRINCIPAL)
        self.channel = A.ReaderChannel(self.path, self.pin, self.schemas)
        self.channel.authenticate(F.proof(self.key, self.channel.challenge))
        self.service = S.Service(self.view, self.channel, self.schemas)
        self.bridge = self.service.sessions.bridge
        self.callback = self.parent.sources.current_guard
    def tearDown(self):
        self.assertEqual(self.parent.sources.current_guard, self.callback)
        self.assertIsNone(K.active_scope())
        self.service.close()
        self.key = None
        self.temporary.cleanup()
        self.assertFalse(self.root.exists())
    def capture(self):
        return K.read_scope(self.parent, D.EL, self.bridge, producer=D,
                            package_checks=[(D.verify_source, PIN)])
    def test_19_actual_boundary_policy_reads_use_only_guarded_source_facts(self):
        counts = {'policy_reads': 0, 'source_selector_calls': 0}
        def observe(frame, event, arg):
            if event != 'call':
                return
            if frame.f_code.co_filename == str(API / 'auth.py') and frame.f_code.co_name == 'policy_guard':
                counts['policy_reads'] += 1
            if frame.f_code.co_filename == str(API / 'source_bridge.py') and frame.f_code.co_name == 'custody_delivery':
                counts['source_selector_calls'] += 1
        self.assertIsNone(sys.getprofile())
        try:
            sys.setprofile(observe)
            with self.capture() as facts:
                self.assertIs(K.policy_scope(self.channel).producer, D)
                self.assertIs(type(facts), D.EL.ExactSources)
                self.bridge.permission()
                self.bridge.permission()
        finally:
            sys.setprofile(None)
        self.assertGreaterEqual(counts['policy_reads'], 4)
        self.assertEqual(counts['source_selector_calls'], 0)
        self.assertEqual(self.parent.sources.current_guard, self.callback)
    def test_20_actual_policy_revocation_cannot_be_hidden_by_copy(self):
        original = self.path.read_bytes()
        try:
            with self.assertRaises(ValueError):
                with self.capture():
                    self.path.write_bytes(original + b' ')
                    self.bridge.permission()
        finally:
            self.path.write_bytes(original)
        self.channel.guard()
    def test_21_actual_nested_dispatch_is_refused_without_workspace_effect(self):
        call = F.call(self.channel.context, 'lab.status', H.cut(self.view))
        before = {p.relative_to(self.root).as_posix(): p.read_bytes()
                  for p in self.root.rglob('*') if p.is_file()}
        with self.capture():
            reply = self.service.call(P.compact(call))
            self.assertEqual(reply['code'], 'unauthenticated-channel')
        after = {p.relative_to(self.root).as_posix(): p.read_bytes()
                 for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(after, before)
    def test_22_real_revoked_entry_never_yields_copied_facts(self):
        original = self.path.read_bytes()
        reached = False
        try:
            self.path.write_bytes(original + b' ')
            with self.assertRaises(ValueError):
                with self.capture():
                    reached = True
        finally:
            self.path.write_bytes(original)
        self.assertFalse(reached)
        self.assertIsNone(K.active_scope())
        self.channel.guard()
