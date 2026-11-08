"""Pinned historical source is parsed/rendered only; generated role never imported."""
import ast
import hashlib
from pathlib import Path, PurePosixPath
import unittest

from t35_external_v1 import role_stage
from t35_external_v1.phase_scoped_v2 import mapper_package_adapter_0004 as adapter
from t35_external_v1.phase_scoped_v2 import mapper_package_ipc_model_0004 as ipc

ROOT = Path(__file__).resolve().parents[6]
HISTORICAL = ROOT / 'product/lab/release-candidates/v1/interface/legacy-session-fixture-mapped-v2-action-0148/build.py'
PIN = 'dced09f9432318ef286475081ea5f4f7e6fa633c7cefbd9db76c0ec3c47ecbbb'


def generated():
    raw = HISTORICAL.read_bytes()
    if hashlib.sha256(raw).hexdigest() != PIN:
        raise RuntimeError('HISTORICAL_DRIFT')
    layout = role_stage.DisposableLayout(PurePosixPath('/work/out/legacy-fixture-source'),
                                        PurePosixPath('/work/snapshot'), 'legacy-fixture-source')
    return role_stage.render_python(raw, layout=layout, role='mapped', name='build.py')


class AdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = generated()
        cls.pin = hashlib.sha256(cls.raw).hexdigest()

    def project(self):
        return adapter.adapt(self.raw, expected_preimage_sha256=self.pin)

    def test_five_sites_six_regions_four_spans_two_insertions(self):
        post, record = self.project()
        self.assertEqual([x['id'] for x in record['sites']], ['B1', 'E1', 'E2', 'S1', 'S2', 'C1'])
        self.assertEqual([x['id'] for x in record['grouped_replacements']], ['B1', 'emit', 'seal', 'call'])
        self.assertEqual([x['id'] for x in record['insertions']], ['F1', 'I1'])
        self.assertFalse(record['effect_ready'])
        self.assertEqual(record['authority_effect'], 'none')
        self.assertEqual(adapter.verify_postimage(self.raw, post, expected_preimage_sha256=self.pin), record)
        self.assertEqual(self.project(), (post, record))

    def test_original_15_plus_10_projection_and_all_other_logic_preserved(self):
        post, record = self.project()
        self.assertEqual(record['projection'], {'nodes': 15, 'relations': 10, 'events_per_family': 25,
                                                'leaves': 55, 'manifest_rows': 54})
        before, after = ast.parse(self.raw), ast.parse(post)
        # Independent masking comparison: remove exactly allowed regions and dependency import.
        for tree in (before, after):
            tree.body = [n for n in tree.body if not (isinstance(n, ast.ImportFrom) and n.module == adapter.BRIDGE)]
            for name in ('emit', 'seal', 'call'):
                adapter.function(tree, name).body = []
            build = adapter.function(tree, 'build')
            build.body = [n for n in build.body if ast.unparse(n) not in (
                "require(not out.exists(), 'mapped package already exists')", '_t35_effect_refused()',
                'package_begin(pin, out)', "package_finish(binding(out / 'manifest.json'))")]
        self.assertEqual(adapter.dump(before), adapter.dump(after))
        for name in ('native_bytes', 'guard', '_t35_binding_path'):
            self.assertEqual(adapter.dump(adapter.function(ast.parse(self.raw), name)),
                             adapter.dump(adapter.function(ast.parse(post), name)))

    def test_two_seals_two_cold_calls_and_original_guards(self):
        post, _ = self.project()
        tree = ast.parse(post)
        build = adapter.function(tree, 'build')
        self.assertEqual([len(adapter.calls(build, n)) for n in ('seal', 'call', 'guard', 'emit')], [2, 2, 2, 6])
        self.assertEqual(len(adapter.calls(tree, 'package_begin')), 1)
        self.assertEqual(len(adapter.calls(tree, 'package_finish')), 1)
        self.assertEqual(len(adapter.calls(tree, 'package_seal')), 1)
        self.assertEqual(len(adapter.calls(tree, 'package_cold_read')), 1)
        self.assertEqual(len(adapter.calls(tree, 'run_native')), 0)
        self.assertEqual(len(adapter.calls(tree, '_t35_effect_refused')), 0)
        self.assertEqual(len(adapter.calls(adapter.function(tree, 'call'), 'require')), 2)
        self.assertEqual(ast.unparse(build.body[-3]), "emit(out / 'manifest.json', manifest)")
        self.assertEqual(ast.unparse(build.body[-2]), "package_finish(binding(out / 'manifest.json'))")

    def test_original_and_adapted_control_slice_trace_matches_protocol_order(self):
        post, _ = self.project()
        traces = []
        for raw in (self.raw, post):
            selected = []
            def select(body):
                for node in body:
                    if isinstance(node, ast.With):
                        select(node.body)  # Never enter Source context; only retain selected call sites.
                    elif any(adapter.calls(node, name) for name in
                             ('seal', 'call', 'emit', 'package_begin', 'package_finish')):
                        self.assertIsInstance(node, (ast.Assign, ast.Expr, ast.For))
                        selected.append(node)
            select(adapter.function(ast.parse(raw), 'build').body)
            self.assertEqual(len([n for n in selected if isinstance(n, ast.For)]), 1)
            loop = next(n for n in selected if isinstance(n, ast.For))
            self.assertEqual(ast.unparse(loop.target), '(folder, family, field)')
            self.assertEqual(ast.unparse(loop.iter),
                             "[('semantic', semantic, 'semantic_cursor'), ('governance', governance, 'governance_cursor')]")
            trace = []
            semantic = [{'semantic_cursor': i} for i in range(1, 26)]
            governance = [{'governance_cursor': i} for i in range(1, 26)]
            def seal(body):
                family = 'semantic' if body['semantic'] else 'governance'
                trace.append(('SEAL', family))
                return {'semantic': semantic, 'governance': governance}
            def emit(path, *args, **kwargs):
                trace.append(('EMIT', str(path.relative_to(PurePosixPath('/owned/package')))))
            def cold(args):
                self.assertEqual([str(p) for p in args], ['/owned/package/semantic',
                                 '/owned/package/governance', '/owned/package/request.json'])
                trace.append(('COLD_READ', 2 + sum(x[0] == 'COLD_READ' for x in trace)))
                return b'owned-synthetic-result'
            scope = {'__builtins__': {'str': str}, 'out': PurePosixPath('/owned/package'),
                     'events': semantic, 'semantic': semantic, 'governance': governance,
                     'seal': seal, 'emit': emit, 'call': cold, 'native_bytes': lambda e: b'fixture',
                     'request': {}, 'mapping': {}, 'result': {}, 'manifest': {}, 'pin': 'fixture',
                     'package_begin': lambda *a: trace.append(('BEGIN', '')),
                     'package_finish': lambda *a: trace.append(('FINISH', '')),
                     'binding': lambda p: {}}
            # Exact selected AST control slices with owned synthetic dependencies only.
            # No generated module imports, original Source callbacks, file IO, or native code.
            exec(compile(ast.Module(body=selected, type_ignores=[]), '<original-call-order-slice>', 'exec'), scope)
            traces.append(trace)
        self.assertEqual(traces[0], ipc.schedule()[1:-1])
        self.assertEqual(traces[1], ipc.schedule())
        # Causal wrong-phase oracle: old order cannot be replaced with an early event write.
        m = ipc.ProtocolModel(attempt_id='order-test', selection_sha256='2'*64,
                              begin_pins=dict.fromkeys(('mapper','source','reader','adapter'), '1'*64),
                              peer=(123,456,1000,1000))
        begin = ipc.encode(ipc.envelope(m.attempt_id,m.selection_sha256,0,'BEGIN',m.begin_pins))
        action = m.receive(begin,peer=m.peer);m.complete_synthetic(action['action_id'],success=True)
        wrong = ipc.encode(ipc.envelope(m.attempt_id,m.selection_sha256,1,'BLOB_BEGIN',
                           {'size_bytes':1,'sha256':ipc.sha(b'x'),'purpose':'EMIT','target':'semantic/00000001.json'}))
        with self.assertRaises(ipc.Refusal): m.receive(wrong,peer=m.peer)

    def test_missing_or_wrong_external_pin_and_byte_drift(self):
        with self.assertRaises(TypeError):
            adapter.adapt(self.raw)
        for value in (None, '', self.pin.upper(), '0'*64):
            with self.subTest(value=value), self.assertRaises(adapter.Refusal):
                adapter.adapt(self.raw, expected_preimage_sha256=value)
        for raw in (self.raw+b'\n', self.raw.replace(b'== 15', b'== 14', 1)):
            with self.assertRaisesRegex(adapter.Refusal, 'PREIMAGE_DRIFT'):
                adapter.adapt(raw, expected_preimage_sha256=self.pin)

    def test_coherent_count_repin_does_not_relax_closed_projection(self):
        raw = self.raw.replace(b'== 15', b'== 14', 1)
        self.assertNotEqual(raw, self.raw)
        with self.assertRaisesRegex(adapter.Refusal, 'PROJECTION_COUNTS'):
            adapter.adapt(raw, expected_preimage_sha256=hashlib.sha256(raw).hexdigest())

    def test_each_refusal_site_missing_and_extra_refuse(self):
        for name, index in [('build', 0), ('emit', 0), ('emit', 1), ('seal', 0), ('seal', 1)]:
            tree = ast.parse(self.raw)
            adapter.calls(adapter.function(tree, name), '_t35_effect_refused')[index].func.id = 'other'
            raw = ast.unparse(tree).encode()
            with self.subTest(name=name, index=index), self.assertRaises(adapter.Refusal):
                adapter.adapt(raw, expected_preimage_sha256=hashlib.sha256(raw).hexdigest())
        raw = self.raw + b'\n_t35_effect_refused()\n'
        with self.assertRaisesRegex(adapter.Refusal, 'EXTRA_REFUSAL'):
            adapter.adapt(raw, expected_preimage_sha256=hashlib.sha256(raw).hexdigest())

    def test_postimage_omitted_call_extra_request_and_early_finish_refuse(self):
        post, _ = self.project()
        for mutation in ('call', 'extra', 'finish', 'body', 'import'):
            tree = ast.parse(post)
            if mutation == 'call':
                adapter.function(tree, 'call').body = adapter.function(ast.parse(self.raw), 'call').body
            elif mutation == 'extra':
                adapter.function(tree, 'build').body.append(ast.parse('package_seal(b"x")').body[0])
            elif mutation == 'finish':
                build = adapter.function(tree, 'build')
                build.body.insert(0, build.body.pop(-2))
            elif mutation == 'body':
                adapter.function(tree, 'native_bytes').body = ast.parse('return b"altered"').body
            else:
                tree.body = [n for n in tree.body if not (isinstance(n, ast.ImportFrom) and n.module == adapter.BRIDGE)]
            changed = (ast.unparse(tree)+'\n').encode()
            with self.subTest(mutation=mutation), self.assertRaisesRegex(adapter.Refusal, 'POSTIMAGE_DRIFT'):
                adapter.verify_postimage(self.raw, changed, expected_preimage_sha256=self.pin)

    def test_source_and_syntax_bounds(self):
        for raw in (b'', b'x'*(adapter.MAX_SOURCE+1), b'\xff', b'def :'):
            with self.assertRaises(adapter.Refusal):
                adapter.adapt(raw, expected_preimage_sha256=hashlib.sha256(raw).hexdigest())


if __name__ == '__main__':
    unittest.main()
