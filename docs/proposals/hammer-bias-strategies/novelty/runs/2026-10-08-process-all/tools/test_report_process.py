import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('report_process', Path(__file__).with_name('report_process.py'))
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)


class ReportingTests(unittest.TestCase):
    def row(self):
        return {'raw_id': 'A1', 'family_id': 'new', 'intelligible': True, 'novelty': 'new',
                'usefulness': 1, 'fit': 'preserves', 'observability': 2, 'support': 'speculative',
                'contract': 'met', 'judgment_resolved': True, 'retention': 'lost'}

    def data(self):
        units = []
        for condition in ['ordinary', 'creative', 'P01']:
            row = self.row()
            if condition != 'P01':
                row.update(family_id='familiar', novelty='equivalent')
            units.append({'unit_id': condition, 'condition': condition, 'repetition': 1,
                          'raw_execution_valid': True, 'raw_assessment_complete': True,
                          'execution_valid': False, 'post_assessment_complete': False,
                          'raw': [row], 'post_only': []})
        return {'case_id': 'test', 'units': units, 'families': {
            'new': {'equivalence_status': 'confirmed', 'uncertain_equivalence_with': []},
            'familiar': {'equivalence_status': 'confirmed', 'uncertain_equivalence_with': []}}}

    def test_compression_failure_does_not_erase_raw_gain(self):
        finding = report.main_case(self.data())['P01'][0]
        self.assertEqual(finding['exclusive_raw_families'], ['new'])
        self.assertIsNone(finding['exclusive_retained_families'])

    def test_uncertain_link_blocks_exclusivity(self):
        data = self.data()
        data['families']['new']['uncertain_equivalence_with'] = ['familiar']
        self.assertEqual(report.main_case(data)['P01'][0]['exclusive_raw_families'], [])

    def test_missing_control_is_gate_not_zero(self):
        data = self.data()
        data['units'][1]['raw_execution_valid'] = False
        self.assertIsNone(report.main_case(data)['P01'][0]['exclusive_raw_families'])

    def test_form_without_semantic_contract_does_not_qualify(self):
        row = self.row()
        row['contract'] = 'not_met'
        self.assertFalse(report.qualified(row, {'equivalence_status': 'confirmed'}))

    def test_retention_dispute_does_not_block_raw_qualification(self):
        row = self.row()
        row.update(judgment_resolved=False, raw_judgment_resolved=True, retention=None)
        self.assertTrue(report.qualified(row, {'equivalence_status': 'confirmed'}))


if __name__ == '__main__':
    unittest.main()
