"""Causal cold checks for the selected T22 Agent-contest construction cut."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).absolute().parent
SPEC = importlib.util.spec_from_file_location('t22_agent_chain', HERE / 'seal_chain.py')
CHAIN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHAIN)


def inputs():
    phases = {name: json.loads(CHAIN.read(CHAIN.FAMILY + '/' + name + '-result.json', pin))
              for name, pin in CHAIN.PINS.items()}
    mapping = json.loads(CHAIN.read(CHAIN.FAMILY + '/mapped/packages/0001/mapping.json', CHAIN.MAPPING))
    delivery = json.loads(CHAIN.read(CHAIN.FAMILY + '/context/packages/0001/delivery.json', CHAIN.DELIVERY))
    period = json.loads(CHAIN.read(CHAIN.FAMILY + '/source/packages/0001/period.json', CHAIN.PERIOD))
    index = json.loads(CHAIN.read(CHAIN.FAMILY + '/source/packages/0001/record-index.json', CHAIN.INDEX))
    return phases, mapping, delivery, period, index


class ChainTests(unittest.TestCase):
    def test_exact_receipt_replays_without_write(self):
        raw = CHAIN.canonical(CHAIN.calculate())
        self.assertEqual(raw, CHAIN.RESULT.read_bytes())
        self.assertEqual(CHAIN.sha(raw), 'ff1ae2eb4e6745f7f47592387538a5f6c4fcced21525812a95d0670e1f5cf4d5')

    def test_changed_source_cut_refused(self):
        phases, mapping, delivery, period, index = inputs()
        mapping['source_cut']['commit_sha256'] = 'a' * 64
        with self.assertRaisesRegex(ValueError, 'native Source cut differs'):
            CHAIN.assess(phases, mapping, delivery, period, index)

    def test_missing_work_and_changed_contract_refused(self):
        phases, mapping, delivery, period, index = inputs()
        delivery['included_refs'] = [r for r in delivery['included_refs']
                                     if r['carrier_ref'] != 'cal.artifact-type.work/v1']
        with self.assertRaisesRegex(ValueError, 'Context delivery closure differs'):
            CHAIN.assess(phases, mapping, delivery, period, index)
        phases, mapping, delivery, period, index = inputs()
        contract = next(r for r in index if r['kind'] == 'challenge-contract')
        contract['original_binding']['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'selected Work or Contract original differs'):
            CHAIN.assess(phases, mapping, delivery, period, index)

    def test_changed_bytes_and_linked_ancestor_refused(self):
        with tempfile.TemporaryDirectory(dir=CHAIN.ROOT) as home:
            base = Path(home)
            real = base / 'real'
            real.mkdir()
            file = real / 'input.json'
            file.write_bytes(b'{}')
            relative = file.relative_to(CHAIN.ROOT).as_posix()
            self.assertEqual(CHAIN.read(relative, CHAIN.sha(b'{}')), b'{}')
            with self.assertRaisesRegex(ValueError, 'selected bytes changed'):
                CHAIN.read(relative, '0' * 64)
            linked = base / 'linked'
            linked.symlink_to(real, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'selected path missing or linked'):
                CHAIN.read((linked / 'input.json').relative_to(CHAIN.ROOT).as_posix(),
                           CHAIN.sha(b'{}'))


if __name__ == '__main__':
    unittest.main()
