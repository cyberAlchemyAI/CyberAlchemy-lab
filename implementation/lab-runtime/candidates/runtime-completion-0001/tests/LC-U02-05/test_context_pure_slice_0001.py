"""Pure Context phase and exact-AST tests; no builder/native/sandbox effect."""
from __future__ import annotations

import hashlib
import ast
import pathlib
import sys
import unittest
from pathlib import PurePosixPath

ROOT = pathlib.Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT / 'implementation/lab-runtime/candidates/runtime-completion-0001'))

from t35_external_v1 import phase_rebind, role_stage
from t35_external_v1.phase_scoped_v2 import plan as phase_plan
from t35_external_v1.phase_scoped_v2 import context_projection_0001 as projection
from t35_external_v1.phase_scoped_v2 import context_package_adapter_0001 as adapter


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class ContextPureSlice(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        instance = 'legacy-context-pure-0001'
        cls.layout = role_stage.DisposableLayout(
            PurePosixPath('/tmp/' + instance),
            PurePosixPath('/tmp/context-pure-snapshot-0001'), instance)
        cls.rows = role_stage.stage_rows(cls.layout,
                                         lambda path: (ROOT / path).read_bytes())
        cls.plan = phase_plan.plan(cls.layout, cls.rows,
                                   episode_raw=b'{}', role_raw=b'{}')
        cls.held = {name: ('fresh-' + name).encode()
                    for name in phase_rebind.PHASE_PREDECESSORS['context']}
        cls.predecessor = {
            name: {'path': str(cls.layout.family / phase_rebind.PIN_PATHS[name]),
                   'sha256': sha(raw)}
            for name, raw in cls.held.items()}
        cls.by_path = {row['path']: cls.held[name]
                       for name, row in cls.predecessor.items()}

    def test_eleven_held_phase_bindings_and_exact_rewrites(self):
        rows = projection.context_rows(self.plan, self.predecessor,
                                       self.by_path.__getitem__)
        self.assertEqual(len(rows), 11)
        self.assertEqual([r['name'] for r in rows],
                         list(role_stage.ROLE_FILES['context']))
        self.assertEqual(projection.context_bindings(
            self.plan, self.predecessor, self.by_path.__getitem__),
            {r['path']: r['binding'] for r in rows})
        by_name = {r['name']: r['bytes'] for r in rows}
        template = {PurePosixPath(path).relative_to(self.layout.family / 'context').as_posix(): raw
                    for role, path, raw in self.plan.templates if role == 'context'}
        self.assertEqual(set(by_name), set(template))
        for name in ('base.py', 'build.py', 'generation.py'):
            self.assertNotEqual(by_name[name], template[name])
            for predecessor_name in self.predecessor:
                self.assertNotIn(phase_rebind.ORIGINAL_PINS[predecessor_name].encode(),
                                 by_name[name])
        for name in set(template) - {'base.py', 'build.py', 'generation.py'}:
            self.assertEqual(by_name[name], template[name])

    def test_wrong_predecessor_custody_refuses(self):
        bad_bytes = dict(self.by_path)
        path = self.predecessor['mapped_package']['path']
        bad_bytes[path] = b'wrong'
        with self.assertRaisesRegex(ValueError, 'held predecessor bytes differ'):
            projection.context_rows(self.plan, self.predecessor,
                                    bad_bytes.__getitem__)
        wrong_path = {k: dict(v) for k, v in self.predecessor.items()}
        wrong_path['mapped']['path'] = str(self.layout.family / 'mapped/other.json')
        with self.assertRaisesRegex(ValueError, 'held predecessor path differs'):
            projection.context_rows(self.plan, wrong_path, self.by_path.__getitem__)
        missing = dict(self.predecessor)
        del missing['source_package']
        with self.assertRaisesRegex(ValueError, 'exact four Context predecessors'):
            projection.context_rows(self.plan, missing, self.by_path.__getitem__)

    def _selected(self, name):
        rows = projection.context_rows(self.plan, self.predecessor,
                                       self.by_path.__getitem__)
        return next(row['bytes'] for row in rows if row['name'] == name)

    def test_adapter_preserves_inverse_diff_and_leaves_private_root_sealed(self):
        for name, role, remaining in [('build.py', 'build', 2),
                                      ('generation.py', 'generation', 0)]:
            with self.subTest(name=name):
                raw = self._selected(name)
                out, record = adapter.adapt(raw, role=role,
                                            expected_preimage_sha256=sha(raw))
                self.assertEqual(record['remaining_refusals'], remaining)
                self.assertFalse(record['effect_ready'])
                self.assertEqual(record['preimage_sha256'], sha(raw))
                self.assertEqual(record['postimage_sha256'], sha(out))
                self.assertEqual(adapter.verify_postimage(
                    raw, out, role=role, expected_preimage_sha256=sha(raw)), record)
                if role == 'build':
                    self.assertEqual(adapter.count_calls(ast.parse(out),
                                                        '_t35_effect_refused'), 2)
                    self.assertNotIn(b'os.fdopen(', out)
                    self.assertIn(b'return (key, sha(path.read_bytes()))', out)
                else:
                    self.assertNotIn(b'MAPPED.call(', out)
                    self.assertIn(b"(p.parent / 'native-output.json').read_bytes()", out)
                with self.assertRaisesRegex(adapter.Refusal, 'POSTIMAGE_DRIFT'):
                    adapter.verify_postimage(raw, out + b'\n', role=role,
                                             expected_preimage_sha256=sha(raw))

    def test_build_preimage_mutations_refuse_even_when_rehashed(self):
        raw = self._selected('build.py')
        variants = [
            (b"require(not out.exists(), 'refuse delivery package overwrite')",
             b"require(out.exists(), 'refuse delivery package overwrite')"),
            (b"fd = _t35_effect_refused()", b"fd = os.open(p, os.O_WRONLY)"),
            (b"with os.fdopen(fd, 'wb') as f:", b"with open(p, 'wb') as f:"),
            (b'encoded(value) if raw is None else raw',
             b'raw if raw is None else encoded(value)'),
            (b'return (key, sha(path.read_bytes()))', b'return (key, sha(b"fake"))'),
            (b'started = time.monotonic()', b'started = 0'),
        ]
        for before, after in variants:
            with self.subTest(before=before):
                self.assertIn(before, raw)
                changed = raw.replace(before, after, 1)
                with self.assertRaises(adapter.Refusal):
                    adapter.adapt(changed, role='build',
                                  expected_preimage_sha256=sha(changed))
        with self.assertRaisesRegex(adapter.Refusal, 'PREIMAGE_DRIFT'):
            adapter.adapt(raw, role='build', expected_preimage_sha256='0' * 64)

    def test_generation_native_and_parity_mutations_refuse(self):
        raw = self._selected('generation.py')
        for before, after in [
            (b'MAPPED.call([', b'MAPPED.other(['),
            (b"'actual cold native projection differs'",
             b"'accept unverified native output'"),
        ]:
            with self.subTest(before=before):
                self.assertIn(before, raw)
                changed = raw.replace(before, after, 1)
                with self.assertRaises(adapter.Refusal):
                    adapter.adapt(changed, role='generation',
                                  expected_preimage_sha256=sha(changed))


if __name__ == '__main__':
    unittest.main()
