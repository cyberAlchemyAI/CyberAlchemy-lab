import copy
import json
from pathlib import Path
import tempfile
import unittest

import migration_contract_import as importer

PLAN = importer.ROOT / 'evidence/migrations/cyberalchemy-v2-to-lab/executions/0002-contract-checked-sample/plan.json'
SOURCE = importer.ROOT.parent / 'cyberAlchemy-v2'


class ContractImportTests(unittest.TestCase):
    def test_real_source_mapping_and_blockers(self):
        result = importer.prepare(importer.read(PLAN), SOURCE)
        self.assertEqual((result['selected'], result['imported'], result['blocked']), (4, 1, 3))
        product, thesis, capability, team = result['records']
        self.assertEqual(product['record']['name'], product['source_record']['label'])
        self.assertEqual(product['record']['status'], 'candidate-unadmitted')
        self.assertIn('product_ref', thesis['missing_fields'])
        self.assertIn('product_ref', capability['missing_fields'])
        self.assertNotIn('record', team)

    def test_deterministic_store_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            a, b = Path(td) / 'a', Path(td) / 'b'
            importer.run(PLAN, SOURCE, a)
            importer.run(PLAN, SOURCE, b)
            before = (a / 'import.json').read_bytes()
            self.assertEqual(before, (b / 'import.json').read_bytes())
            with self.assertRaisesRegex(ValueError, 'already exists'):
                importer.run(PLAN, SOURCE, a)
            self.assertEqual(before, (a / 'import.json').read_bytes())

    def test_source_drift_creates_no_store(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            plan = importer.read(PLAN)
            path = root / plan['source']['path']
            path.parent.mkdir(parents=True)
            path.write_text('{}')
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                importer.run(PLAN, root, root / 'out')
            self.assertFalse((root / 'out').exists())

    def test_unadmitted_target_and_scope(self):
        for change in ('scope', 'target'):
            plan = importer.read(PLAN)
            if change == 'scope':
                plan['scope'] = 'global'
            else:
                plan['selections'][0]['target'] = 'type.unknown'
            with self.assertRaises(ValueError):
                importer.prepare(plan, SOURCE)

    def test_identity_mismatch_and_duplicate_selection(self):
        plan = importer.read(PLAN)
        plan['selections'][0]['source_id'] = 'wrong'
        with self.assertRaisesRegex(ValueError, 'identity mismatch'):
            importer.prepare(plan, SOURCE)
        plan = importer.read(PLAN)
        plan['selections'].append(copy.deepcopy(plan['selections'][0]))
        with self.assertRaisesRegex(ValueError, 'duplicate selection'):
            importer.prepare(plan, SOURCE)

    def test_missing_product_field_is_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            plan = importer.read(PLAN)
            data = importer.read(SOURCE / plan['source']['path'])
            del data['nodes'][1]['plain_language']
            path = root / plan['source']['path']
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps(data))
            plan['source']['sha256'] = importer.digest(path)
            result = importer.prepare(plan, root)
            self.assertEqual(result['imported'], 0)
            self.assertIn('purpose', result['records'][0]['missing_fields'])


if __name__ == '__main__':
    unittest.main()
