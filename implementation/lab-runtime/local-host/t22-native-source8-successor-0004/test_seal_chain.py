"""Causal negatives for the native Source→Context terminal receipt."""
import json
import unittest

import seal_chain as S


def selected():
    return (
        {name: json.loads(S.work_check.read(S.FAMILY + '/' + name + '-result.json', pin)) for name, pin in S.PHASE.items()},
        json.loads(S.work_check.read(S.MAPPING, S.MAPPING_SHA)),
        json.loads(S.work_check.read(S.DELIVERY, S.DELIVERY_SHA)),
        json.loads(S.work_check.read(S.PERIOD, S.PERIOD_SHA)),
        S.work_check.verify(),
    )


class ChainTests(unittest.TestCase):
    def test_sealed_replay(self):
        self.assertEqual(S.calculate()['status'], 'PASS-native-family-construction')
        self.assertEqual(S.RESULT.read_bytes(), S.canonical(S.calculate()))

    def test_changed_cold_source_refused(self):
        args = selected()
        args[0]['cold']['source_binding']['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'cold Source does not match'):
            S.assess(*args)

    def test_changed_native_cut_refused(self):
        args = selected()
        args[1]['source_cut']['commit_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'Context/native source cut differs'):
            S.assess(*args)

    def test_substituted_work_in_delivery_refused(self):
        args = selected()
        for row in args[2]['included_refs']:
            if row['carrier_ref'] == 'cal.artifact-type.work/v1':
                row['byte_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'omits selected API30 Work'):
            S.assess(*args)

    def test_false_session_completion_refused(self):
        args = selected()
        args[4]['native_session_consumed'] = True
        with self.assertRaisesRegex(ValueError, 'Work assertion differs'):
            S.assess(*args)


if __name__ == '__main__': unittest.main()
