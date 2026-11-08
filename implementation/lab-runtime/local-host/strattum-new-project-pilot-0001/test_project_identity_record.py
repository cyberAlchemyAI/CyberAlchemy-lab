"""Offline selected-schema, route, and retained-evidence checks."""
import ast
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest
from types import SimpleNamespace

from jsonschema import Draft202012Validator, FormatChecker


SOURCE = Path(__file__).with_name('pilot.py')
INSTALL = Path(os.environ['CAL_FAILED_API76_ROOT']).resolve()
tree = ast.parse(SOURCE.read_bytes())
functions = ast.Module(body=[node for node in tree.body
                             if isinstance(node, ast.FunctionDef) and node.name in
                             {'digest', 'write_raw_new', 'project_identity_record'}],
                       type_ignores=[])
namespace = {'Path': Path, 'os': os, 'hashlib': hashlib,
             'PROJECT': 'project:lab-strattum-feature-gap-pilot',
             'G': SimpleNamespace(Draft202012Validator=Draft202012Validator,
                                  FormatChecker=FormatChecker, parse=json.loads)}
exec(compile(functions, str(SOURCE), 'exec'), namespace)


class ProjectIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema_path = INSTALL / 'authority/artifact-types/project-identity/v1/schema.json'
        cls.schema_raw = cls.schema_path.read_bytes()
        manifest = json.loads((INSTALL / '.cal-package-manifest.json').read_bytes())
        row = next(item for item in manifest['members']
                   if item['path'] == 'authority/artifact-types/project-identity/v1/schema.json')
        assert hashlib.sha256(cls.schema_raw).hexdigest() == row['sha256']
        proposal = json.loads((Path('/home/vlad_/projects/CyberAlchemy-lab') /
                               'implementation/lab-runtime/local-host/t03-long-local-fixture-0001/instances/legacy-local-fb234116c28181e8/source/packages/0001/project-setup-proposal.json').read_bytes())
        cls.route = proposal['challenge_route']

    def test_literal_project_identity_follows_exact_native_route(self):
        record = namespace['project_identity_record']('project:baseline', 'role:operator',
                                                       self.route, 'evidence:scope', self.schema_raw)
        self.assertEqual(len(record), 13)
        self.assertEqual(record['challenge_route'], self.route)
        self.assertEqual(record['project_id'], namespace['PROJECT'])
        Draft202012Validator(json.loads(self.schema_raw),
                             format_checker=FormatChecker()).validate(record)

    def test_missing_route_refused(self):
        with self.assertRaisesRegex(ValueError, 'challenge route missing'):
            namespace['project_identity_record']('project:baseline', 'role:operator',
                                                 '', 'evidence:scope', self.schema_raw)

    def test_exact_scope_evidence_retained_without_overwrite(self):
        raw = b'{"authority_effect":"none","project_id":"project:pilot"}'
        with tempfile.TemporaryDirectory(prefix='cal-pilot-evidence-test-') as directory:
            target = Path(directory) / 'SCOPE-EVIDENCE.json'
            digest = namespace['write_raw_new'](target, raw)
            self.assertEqual(digest, hashlib.sha256(raw).hexdigest())
            self.assertEqual(target.read_bytes(), raw)
            self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o600)
            with self.assertRaises(FileExistsError):
                namespace['write_raw_new'](target, raw)


if __name__ == '__main__':
    unittest.main(verbosity=2)
