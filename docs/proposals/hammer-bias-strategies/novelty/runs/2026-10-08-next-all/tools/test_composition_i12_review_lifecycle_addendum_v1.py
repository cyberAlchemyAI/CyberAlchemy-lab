"""Memory-only guard regression tests; fictional fixtures give no trial credit."""
import copy
import unittest
import composition_i12_runtime_v2 as base
import composition_i12_review_lifecycle_addendum_v1 as fix
from test_composition_i12_runtime_v2 import source_pack


class ReviewGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack = source_pack()
        cls.fixture = base.maximal_fixture_pack(cls.pack)

    def setUp(self):
        pack = copy.deepcopy(self.fixture['input_pack'])
        original = [j for j in self.pack['schedule']['jobs'] if j['case_id'] == 'H-P']
        remap = {old['job_id']: new['job_id'] for old, new in zip(original, pack['schedule']['jobs'])}
        for review in pack['reviews']['jobs']:
            review['depends_on'] = [remap[k] for k in review['depends_on']]
        self.memory_pack = pack
        self.jobs = {j['job_id']: j for j in pack['schedule']['jobs'] + pack['reviews']['jobs']}
        self.job = next(j for j in pack['reviews']['jobs'] if j['review_phase'] == 'raw')
        self.states = {k: 'valid' for k in self.jobs}
        self.states[self.job['job_id']] = 'pending'
        self.packet = copy.deepcopy(self.fixture['raw_packet'])
        self.admin = copy.deepcopy(self.fixture['raw_opaque_map'])
        self.context = {'admission_valid': True, 'source_bound_phase_readiness': True,
            'confirmation_allowed': True, 'output_exists': False, 'prompt_exists': False,
            'source_freeze_sha256': 'a' * 64, 'source_hashes': {'memory/raw.json': 'b' * 64},
            'template': base.review_prompt('raw'), 'assigned_prompt_ref': 'memory/review.txt',
            'review_input_refs': ['memory/raw.json'], 'review_packet': self.packet,
            'review_admin_map': self.admin,
            'assigned_reviewer_id': next(x['opaque_job_id'] for x in self.admin['review_job_bindings']
                                         if x['job_id'] == self.job['job_id'])}

    def prepare(self):
        return fix.prepare_review(self.job, self.jobs, self.states, {}, self.context)

    def test_01_successful_dependencies_keep_exact_original_prompt(self):
        self.assertEqual(self.prepare(), base.prepare_job(self.job, self.jobs, self.states, {}, self.context))

    def test_02_pending_dependency_is_rejected(self):
        self.states[self.job['depends_on'][0]] = 'pending'
        with self.assertRaises(ValueError): self.prepare()

    def test_03_running_dependency_is_rejected(self):
        self.states[self.job['depends_on'][0]] = 'running'
        with self.assertRaises(ValueError): self.prepare()

    def test_04_state_and_packet_disposition_drift_is_rejected(self):
        self.states[self.job['depends_on'][0]] = 'missing'
        with self.assertRaises(ValueError): self.prepare()

    def test_05_no_input_mutation(self):
        before = copy.deepcopy((self.job, self.jobs, self.states, self.packet, self.admin, self.context))
        self.prepare()
        self.assertEqual(before, (self.job, self.jobs, self.states, self.packet, self.admin, self.context))

    def test_06_generation_role_cannot_use_review_adapter(self):
        self.job = next(j for j in self.jobs.values() if 'review_phase' not in j)
        with self.assertRaises(ValueError): self.prepare()

    def test_07_graph_truncation_is_rejected(self):
        self.job['depends_on'].pop()
        with self.assertRaises(ValueError): self.prepare()

    def test_08_map_byte_meaning_drift_is_rejected(self):
        self.admin['case_id'] = 'changed'
        with self.assertRaises(ValueError): self.prepare()

    def test_09_wrong_reviewer_is_rejected(self):
        self.context['assigned_reviewer_id'] = 'other-reviewer'
        with self.assertRaises(ValueError): self.prepare()

    def test_10_missing_admission_is_rejected(self):
        self.context['admission_valid'] = False
        with self.assertRaises(ValueError): self.prepare()

    def test_11_missing_phase_readiness_is_rejected(self):
        self.context['source_bound_phase_readiness'] = False
        with self.assertRaises(ValueError): self.prepare()

    def test_12_existing_output_is_rejected(self):
        self.context['output_exists'] = True
        with self.assertRaises(ValueError): self.prepare()

    def test_13_existing_prompt_is_rejected(self):
        self.context['prompt_exists'] = True
        with self.assertRaises(ValueError): self.prepare()

    def test_14_already_prepared_review_is_rejected(self):
        self.states[self.job['job_id']] = 'ready'
        with self.assertRaises(ValueError): self.prepare()

    def test_15_post_review_still_requires_actual_raw_lock(self):
        self.job = next(j for j in self.jobs.values() if j.get('review_phase') == 'post')
        self.states[self.job['job_id']] = 'pending'
        self.packet = copy.deepcopy(self.fixture['post_packet'])
        self.admin = copy.deepcopy(self.fixture['post_opaque_map'])
        self.context.update(review_packet=self.packet, review_admin_map=self.admin,
            template=base.review_prompt('post'), raw_packet=self.fixture['raw_packet'],
            raw_lock=self.fixture['raw_lock'], assigned_reviewer_id=next(m['opaque_job_id']
                for m in self.admin['review_job_bindings'] if m['job_id'] == self.job['job_id']))
        with self.assertRaises(ValueError): self.prepare()

    def test_16_failed_terminal_sources_are_assessed_with_full_unchanged_denominators(self):
        for failure in ('invalid', 'missing', 'skipped'):
            key = self.job['depends_on'][0]
            self.states[key] = failure
            raw_ids = set(self.job['depends_on'])
            artifacts = {k: copy.deepcopy(v) for k, v in self.fixture['artifacts'].items() if k in raw_ids}
            if failure != 'invalid': artifacts.pop(key)
            dispositions = {k: {'execution': self.states[k], 'cause': 'UNSCORED explicit memory terminal.'} for k in raw_ids}
            packet, admin = base.build_raw_case('H-P', artifacts, dispositions, self.memory_pack)
            self.context.update(review_packet=packet, review_admin_map=admin,
                assigned_reviewer_id=next(x['opaque_job_id'] for x in admin['review_job_bindings']
                                         if x['job_id'] == self.job['job_id']))
            before = copy.deepcopy(packet)
            self.assertEqual(base.prepare_job(self.job, self.jobs, self.states, artifacts, self.context)['status'], 'skipped')
            self.assertEqual(self.prepare()['event_kind'], 'job_prepared')
            self.assertEqual(before, packet)
            self.assertEqual(len(packet['core_packet']['units']), 14)
            mapping = next(x for x in admin['mapping'] if x.get('job_id') == key and 'unit_id' in x)
            unit = next(u for u in packet['core_packet']['units'] if u['unit_id'] == mapping['unit_id'])
            self.assertEqual(unit['execution'], failure)
            if failure == 'invalid':
                raw_card_ids = {c['id'] for c in unit['artifact']['openings']}
                obligations = [o for o in packet['core_packet']['expected_matrix']['raw_rows']
                               if o['identity']['card_id'] in raw_card_ids]
                self.assertTrue(obligations)
                self.assertTrue(all(o['null_semantics'] for o in obligations))


if __name__ == '__main__':
    unittest.main(verbosity=2)
