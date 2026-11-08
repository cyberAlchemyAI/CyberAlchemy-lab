"""Pure Mapper 0003 poststate checks; never launch a fixture child."""
from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from t35_external_v1 import scratch_source_probe as source
from t35_external_v1.path_contract import ContractError
from t35_external_v1.phase_scoped_v2 import mapper_prepare_0002 as prepare
from t35_external_v1.phase_scoped_v2 import mapper_readonly_0003 as readonly
from t35_external_v1.phase_scoped_v2 import prefix_probe


class MapperPoststateV3Tests(unittest.TestCase):
    def fixture(self, root: Path):
        contents = {'source/source-manifest.json': b'source\n',
                    'reader/reader-manifest.json': b'reader\n',
                    prepare.MAPPER_MANIFEST: b'mapper\n'}
        contents.update({'mapped/' + name: name.encode() + b'\n'
                         for name in prepare.MAPPER_NAMES})
        for name, raw in contents.items():
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
        self.assertEqual({name for name in contents if name.startswith('mapped/')},
                         prepare.MAPPER_LEAVES | {prepare.MAPPER_MANIFEST})
        return source._tree_files(root), source._tree_dirs(root)

    def test_exact_five_leaf_mapper_poststate_is_allowed(self):
        with tempfile.TemporaryDirectory(prefix='t35-mapper-poststate-v3-') as temp:
            root = Path(temp)
            files, dirs = self.fixture(root)
            with self.assertRaises(ContractError):
                prefix_probe._inventory(root)
            self.assertEqual(readonly._verify_mapper_poststate(
                root, files, dirs, 0, b''), (files, dirs))
            self.assertEqual(readonly.RECEIPT_NAME,
                             'phase-mapper-readonly-result-0003.json')

    def test_mutation_extra_leaf_context_and_package_refuse(self):
        with tempfile.TemporaryDirectory(prefix='t35-mapper-poststate-v3-') as temp:
            root = Path(temp)
            files, dirs = self.fixture(root)
            role = root / next(iter(sorted(prepare.MAPPER_LEAVES)))
            original = role.read_bytes()
            role.write_bytes(original + b'changed')
            with self.assertRaises(ContractError):
                readonly._verify_mapper_poststate(root, files, dirs, 0, b'')
            role.write_bytes(original)
            predecessor = root / 'source/source-manifest.json'
            predecessor_raw = predecessor.read_bytes()
            predecessor.write_bytes(predecessor_raw + b'changed')
            with self.assertRaises(ContractError):
                readonly._verify_mapper_poststate(root, files, dirs, 0, b'')
            predecessor.write_bytes(predecessor_raw)
            extra = root / 'mapped/unselected.txt'
            extra.write_bytes(b'extra')
            with self.assertRaises(ContractError):
                readonly._verify_mapper_poststate(root, files, dirs, 0, b'')
            extra.unlink()
            for name in ('context', 'mapped/packages'):
                directory = root / name
                directory.mkdir()
                with self.assertRaises(ContractError):
                    readonly._verify_mapper_poststate(root, files, dirs, 0, b'')
                directory.rmdir()
            with self.assertRaises(ContractError):
                readonly._verify_mapper_poststate(root, files, dirs, 1, b'')
            with self.assertRaises(ContractError):
                readonly._verify_mapper_poststate(root, files, dirs, 0, b'bad')


if __name__ == '__main__':
    unittest.main()
