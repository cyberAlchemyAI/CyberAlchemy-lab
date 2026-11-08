"""Offline closure negatives against the retained failed API76 installation."""
import ast
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import tempfile
from types import SimpleNamespace
import unittest


SOURCE = Path(__file__).resolve().parents[4] / 'product/lab/release-candidates/v1/interface/api-integration-v76-current-repairs-0001/guard.py'
INSTALL = Path(os.environ['CAL_FAILED_API76_ROOT']).resolve()
API = INSTALL / 'product/lab/release-candidates/v1/interface/api-integration-v76-current-repairs-0001'
tree = ast.parse(SOURCE.read_bytes())
names = {'_capture_exact', '_governance_external_rows', '_check_external_rows',
         'verify'}
selected = ast.Module(body=[node for node in tree.body
                            if isinstance(node, ast.FunctionDef) and node.name in names],
                      type_ignores=[])
ns = {'Path': Path, 'PurePosixPath': PurePosixPath, 'os': os, 'stat': stat,
      're': re, 'json': json, 'hashlib': hashlib}
exec(compile(selected, str(SOURCE), 'exec'), ns)
capture = ns['_capture_exact']
governance_rows = ns['_governance_external_rows']
check = ns['_check_external_rows']


class ClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = json.loads((API / 'source-manifest.json').read_bytes())['files']
        cls.package = API.relative_to(INSTALL).as_posix() + '/'
        cls.governance = governance_rows(INSTALL, API, cls.rows)
        cls.helpers = {r['path'] for r in cls.rows
                       if not r['path'].startswith(cls.package)
                       and r['path'] not in cls.governance}
        cls.member_path = (API / 'integration-members.json').relative_to(INSTALL).as_posix()

    def test_retained_manifest_has_exact_selected_closure(self):
        self.assertEqual(len(self.governance), 987)
        self.assertEqual(len(self.helpers), 30)
        check(self.rows, self.helpers, self.governance, self.package)

    def test_repaired_guard_reaches_exact_file_verification(self):
        source = (API / 'source-manifest.json').read_bytes()
        binding = {'path': (API / 'source-manifest.json').relative_to(INSTALL).as_posix(),
                   'sha256': hashlib.sha256(source).hexdigest()}
        environment = json.loads(source)['environment']
        globals_for_verify = ns.copy()
        globals_for_verify.update({
            'ROOT': INSTALL, 'HERE': API,
            'PORTABLE': SimpleNamespace(guard=lambda: None,
                                        binding=lambda name: binding),
            'platform': SimpleNamespace(python_version=lambda: environment['python']),
            'importlib': SimpleNamespace(metadata=SimpleNamespace(
                version=lambda name: environment[name])),
            '_verify_files': lambda root, rows: {'verified_files': len(rows)},
        })
        function = ast.Module(body=[node for node in tree.body
                                   if isinstance(node, ast.FunctionDef) and node.name == 'verify'],
                              type_ignores=[])
        exec(compile(function, str(SOURCE), 'exec'), globals_for_verify)
        self.assertEqual(len(globals_for_verify['verify'](binding['sha256'])['files']),
                         len(self.rows))

    def test_foreign_row_refused(self):
        with self.assertRaisesRegex(ValueError, 'foreign successor'):
            check(self.rows + [{'path': 'unrelated/foreign.json', 'sha256': '0' * 64}],
                  self.helpers, self.governance, self.package)

    def test_missing_governance_row_refused(self):
        path = next(iter(self.governance))
        with self.assertRaisesRegex(ValueError, 'closure incomplete'):
            check([r for r in self.rows if r['path'] != path],
                  self.helpers, self.governance, self.package)

    def test_changed_governance_digest_refused(self):
        path = next(iter(self.governance))
        changed = [dict(r, sha256='0' * 64) if r['path'] == path else r
                   for r in self.rows]
        with self.assertRaisesRegex(ValueError, 'governance byte row differs'):
            check(changed, self.helpers, self.governance, self.package)

    def test_changed_member_binding_refused(self):
        changed = [dict(r, sha256='0' * 64) if r['path'] == self.member_path
                   else r for r in self.rows]
        with self.assertRaisesRegex(ValueError, 'capture digest differs'):
            governance_rows(INSTALL, API, changed)

    def test_foreign_governance_member_refused(self):
        member = json.loads((API / 'integration-members.json').read_bytes())
        member['members']['governance']['directory'] = 'api-governance-integration-v4'
        with tempfile.TemporaryDirectory(prefix='cal-api76-closure-test-') as temp:
            root = Path(temp)
            local = root / self.member_path
            local.parent.mkdir(parents=True)
            raw = (json.dumps(member, sort_keys=True) + '\n').encode()
            local.write_bytes(raw)
            rows = [dict(r, sha256=hashlib.sha256(raw).hexdigest())
                    if r['path'] == self.member_path else r for r in self.rows]
            with self.assertRaisesRegex(ValueError, 'member differs'):
                governance_rows(root, local.parent, rows)


if __name__ == '__main__':
    unittest.main(verbosity=2)
