"""Fast, causal checks for the T08 bridge-root schema successor."""

import json
from pathlib import Path
import unittest

import jsonschema


ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
PACKAGE = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v33-t08-mixed-0002'


class RootModeSchema(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        schema = json.loads((PACKAGE / 'host-bridge.schema.json').read_bytes())
        jsonschema.Draft202012Validator.check_schema(schema)
        cls.item = schema['properties']['protected_inputs']['anyOf'][1]['properties']['control_roots']['items']

    def root(self, identifier, mode):
        return {'id': identifier, 'path': '/bounded/root', 'device': 1,
                'inode': 1, 'uid': 1, 'mode': mode}

    def test_private_requires_0700(self):
        jsonschema.validate(self.root('private', 0o700), self.item)
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(self.root('private', 0o755), self.item)

    def test_selected_read_only_roots(self):
        for identifier in ('repo', 'absolute:' + 'a' * 20):
            for mode in (0o700, 0o755):
                with self.subTest(identifier=identifier, mode=mode):
                    jsonschema.validate(self.root(identifier, mode), self.item)

    def test_foreign_or_writable_roots_refused(self):
        for identifier, mode in (('other', 0o755), ('absolute:bad', 0o755),
                                 ('repo', 0o777), ('repo', 0o775),
                                 ('absolute:' + 'a' * 20, 0o777)):
            with self.subTest(identifier=identifier, mode=mode):
                with self.assertRaises(jsonschema.ValidationError):
                    jsonschema.validate(self.root(identifier, mode), self.item)


if __name__ == '__main__':
    unittest.main()
