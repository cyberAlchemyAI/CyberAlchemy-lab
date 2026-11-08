"""Pure causal guard checks; separate actual-Source probes remain required."""
import ast
import base64
import copy
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import types
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v71-t15-integrated-closure-0001'
compact = lambda value: json.dumps(value, sort_keys=True, separators=(',', ':')).encode()
sha = lambda raw: hashlib.sha256(raw).hexdigest()


def require(value, reason):
    if not value:
        raise ValueError(reason)


class MachineSeal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('final_machine_seal_delta', HERE / 'final_machine_seal.py')
        delta = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(delta)
        cls.postimage = delta.apply((API / 'machine_transport.py').read_text())
        tree = ast.parse(cls.postimage)
        parent = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == 'MachinePeer')
        nodes = [copy.deepcopy(node) for node in parent.body if isinstance(node, ast.FunctionDef)
                 and node.name in ('_peer_basis_guard', 'live', 'dispatch_current')]
        model = ast.ClassDef(name='MachinePeer', bases=[], keywords=[], body=nodes, decorator_list=[], type_params=[])
        unit = ast.Module(body=[model], type_ignores=[])
        ast.fix_missing_locations(unit)
        cls.helper_name = '_cal_T15_machine_seal_test.session_source_freshness'
        cls.previous_helper = sys.modules.get(cls.helper_name)
        helper = types.ModuleType(cls.helper_name)
        helper.captured_source_basis = lambda selected: copy.deepcopy(selected.private_basis)
        sys.modules[cls.helper_name] = helper
        cls.ns = {'__package__':'_cal_T15_machine_seal_test', 'require':require,
                  'base64':base64, 'copy':copy,
                  'fresh_selected_source':lambda selected, family: None}
        exec(compile(unit, str(API / 'machine_transport.py'), 'exec'), cls.ns)
        cls.Peer = cls.ns['MachinePeer']

    @classmethod
    def tearDownClass(cls):
        if cls.previous_helper is None:
            sys.modules.pop(cls.helper_name, None)
        else:
            sys.modules[cls.helper_name] = cls.previous_helper

    def setUp(self):
        self.full = 0
        selected = types.SimpleNamespace(private_basis={'cut':'actual-cut','baseline':'original-baseline'}, guard=self.full_guard)
        bridge = object()
        resource = types.SimpleNamespace(source=selected, bridge=bridge, closed=False,
                                         guard=lambda: True, expires=datetime.now(timezone.utc)+timedelta(minutes=10))
        owner = types.SimpleNamespace(sessions=types.SimpleNamespace(source=selected, bridge=bridge, live={'session:actual':resource}),
                                      channel=types.SimpleNamespace(termination_guard=lambda: {}))
        peer = self.Peer()
        peer.owner = peer._peer_owner = owner
        peer.resource = peer._peer_resource = resource
        peer.row = {'session_ref':'session:actual','agent_instance_ref':'agent:actual','source_cut':'actual-cut'}
        peer.connection = 'connection:actual'
        peer.public_key_bytes = b'actual-generated-public-key'
        peer.P = types.SimpleNamespace(source=types.SimpleNamespace(sha=sha), compact=compact)
        peer.context = None
        peer._authenticated_context_basis = None
        peer._peer_binding_basis = sha(compact({'row':peer.row,'connection':peer.connection,
            'public_key':base64.b64encode(peer.public_key_bytes).decode()}))
        peer._source_memory_basis = copy.deepcopy(selected.private_basis)
        peer._dispatch_scope = True
        peer.closed = False
        peer.expires = resource.expires
        peer.A = types.SimpleNamespace(now=lambda: datetime.now(timezone.utc))
        peer.schemas = types.SimpleNamespace(guard=lambda: None)
        peer.policy = {'allowed_operations':['artifact.inspect']}
        peer.narrow_policy = lambda **kwargs: copy.deepcopy(peer.policy)
        peer._family_bindings = {'actual-source-manifest':'independent-code-pin'}
        peer.close = lambda: setattr(peer, 'closed', True)
        self.peer = peer

    def full_guard(self):
        self.full += 1

    def test_selected_peer_and_source_pass(self):
        self.peer._peer_basis_guard()
        self.peer.dispatch_current()

    def test_outer_live_keeps_full_semantic_proof(self):
        self.peer.live()
        self.peer.live()
        self.assertEqual(self.full, 2)

    def test_each_inner_boundary_checks_captured_source(self):
        self.peer.dispatch_current()
        self.peer.resource.source.private_basis['baseline'] = 'matching-owned-file-retarget'
        with self.assertRaisesRegex(ValueError, 'Machine captured source facts changed'):
            self.peer.dispatch_current()

    def test_row_actor_cut_and_connection_are_sealed(self):
        for change in ('agent_instance_ref', 'source_cut'):
            with self.subTest(field=change):
                original = self.peer.row[change]
                self.peer.row[change] = 'substituted'
                with self.assertRaisesRegex(ValueError, 'Actor, cut, connection or signer'):
                    self.peer._peer_basis_guard()
                self.peer.row[change] = original
        self.peer.connection = 'connection:other'
        with self.assertRaises(ValueError):
            self.peer._peer_basis_guard()

    def test_cross_peer_owner_is_refused(self):
        self.peer.owner = copy.copy(self.peer.owner)
        with self.assertRaisesRegex(ValueError, 'selected owner or actual Session'):
            self.peer._peer_basis_guard()

    def test_cross_peer_resource_is_refused(self):
        self.peer.resource = copy.copy(self.peer.resource)
        with self.assertRaisesRegex(ValueError, 'selected owner or actual Session'):
            self.peer._peer_basis_guard()

    def test_authenticated_opaque_context_is_sealed(self):
        self.peer.context = {'context_ref':'opaque:actual','session_ref':'session:actual'}
        self.peer._authenticated_context_basis = sha(compact(self.peer.context))
        self.peer.dispatch_current()
        self.peer.context['context_ref'] = 'opaque:substituted'
        with self.assertRaisesRegex(ValueError, 'authenticated opaque context'):
            self.peer.dispatch_current()

    def test_context_requires_real_authentication(self):
        self.peer.context = {'context_ref':'unissued'}
        with self.assertRaisesRegex(ValueError, 'predates actual authentication'):
            self.peer._peer_basis_guard()


if __name__ == '__main__':
    unittest.main(verbosity=2)
