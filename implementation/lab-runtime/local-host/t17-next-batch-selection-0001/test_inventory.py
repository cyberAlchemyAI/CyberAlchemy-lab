"""Causal checks for the pinned T17 operation selection."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


MODULE_PATH = Path(__file__).with_name('inventory.py')
SPEC = importlib.util.spec_from_file_location('t17_inventory', MODULE_PATH)
INVENTORY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INVENTORY)


class InventoryTests(unittest.TestCase):
    def test_selected_result_has_no_live_credit(self):
        result = INVENTORY.build()
        self.assertEqual(json.loads(Path(__file__).with_name('RESULT.json').read_bytes()), result)
        self.assertEqual(result['all34_count'], 34)
        self.assertEqual(set(result['operation_coverage']), set(result['all34_operations']))
        self.assertEqual(result['next_positive_negative_batch'], ['session.open', 'session.close'])
        self.assertFalse(result['fresh_family_selected'])
        self.assertTrue(all(not any(row.values()) for row in result['operation_coverage'].values()))

    def test_changed_selected_input_refuses(self):
        with tempfile.TemporaryDirectory(prefix='cal-t17-pin-') as temporary:
            root = Path(temporary)
            path = root / INVENTORY.PLAN[0]
            path.parent.mkdir(parents=True)
            path.write_bytes(INVENTORY.pinned(INVENTORY.PLAN) + b' ')
            with patch.object(INVENTORY, 'ROOT', root):
                with self.assertRaisesRegex(ValueError, 'selected T17 input changed'):
                    INVENTORY.pinned(INVENTORY.PLAN)

    def test_duplicate_or_missing_operation_refuses(self):
        original = INVENTORY.pinned
        plan = json.loads(original(INVENTORY.PLAN))
        plan['operations'][1] = plan['operations'][0]

        def changed(binding):
            if binding == INVENTORY.PLAN:
                return json.dumps(plan).encode()
            return original(binding)

        with patch.object(INVENTORY, 'pinned', side_effect=changed):
            with self.assertRaisesRegex(ValueError, 'operation inventory differs'):
                INVENTORY.build()

    def test_unselected_protocol_expression_refuses(self):
        with self.assertRaisesRegex(ValueError, 'unselected operation expression'):
            INVENTORY.supported(b"SUPPORTED = tuple(['session.open'])\n")


if __name__ == '__main__':
    unittest.main()
