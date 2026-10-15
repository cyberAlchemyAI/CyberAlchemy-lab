"""UNSCORED memory-only I12 rejection and coverage tests; no files/events published."""
import builtins
import copy
import hashlib
import io
import json
import unittest
from pathlib import Path
from unittest.mock import patch

import composition_i12_runtime_v1 as m


def source_pack():
    s, r = m.make_schedule()
    return {'schedule': s, 'reviews': r,
        'contract': m.read(m.R / 'generation-review-contract.v2.json'),
        'criteria': m.read(m.R / 'criteria-generation.v2.json'),
        'archives': m.read(m.R / 'archives/case-archives.json'),
        'cases': {c: m.read(m.R / f'cases/{c}.json') for c in m.CASES},
        'prompts': {j['prompt_ref']: m.prompt_text(j['operation']) for j in s['jobs']}}


def native(prepared, ordinal=1, payload=None):
    start = {k: prepared[k] for k in ('job_id', 'study_id', 'case_id', 'phase', 'prompt_ref',
        'prompt_sha256', 'source_freeze_sha256', 'output_ref')}
    start.update(agent_handle='memory-handle-' + str(ordinal), native_call_id='memory-call-' + str(ordinal),
        turn=1, native_start_observed=True, fresh_context=True)
    final = {k: v for k, v in start.items() if k not in ('native_start_observed', 'fresh_context')}
    final.update(native_final_observed=True, terminal_witness='parent_received_NATIVE_FINAL_ANSWER',
        output_sha256=hashlib.sha256(payload).hexdigest() if payload is not None else None)
    return start, final


def encode(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False).encode()


class MemoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack = source_pack()
        cls.fixture = m.maximal_fixture_pack(cls.pack)
        cls.raw = cls.fixture['raw_packet']
        cls.post = cls.fixture['post_packet']
        cls.jobs = {j['job_id']: j for j in cls.pack['schedule']['jobs']}
        cls.fjobs = {j['job_id']: j for j in cls.fixture['input_pack']['schedule']['jobs']}
        cls.original = m.read(m.R / m.PACK)['assigned_source_bindings']
        cls.before = {x['path']: m.sha(m.R / x['path']) for x in cls.original}
        cls.global_objects = {('base', k): id(v) for k, v in vars(m.base).items()}
        cls.global_objects.update({('raw', k): id(v) for k, v in vars(m.raw).items()})

    @classmethod
    def tearDownClass(cls):
        assert cls.before == {x['path']: m.sha(m.R / x['path']) for x in cls.original}
        assert cls.global_objects == {**{('base', k): id(v) for k, v in vars(m.base).items()},
            **{('raw', k): id(v) for k, v in vars(m.raw).items()}}

    def setUp(self):
        real_builtin, real_io = builtins.open, io.open
        def guard(original):
            def wrapped(file, mode='r', *args, **kwargs):
                if any(x in mode for x in 'wax+'):
                    raise AssertionError('Memory tests forbid real filesystem writes: ' + str(file))
                return original(file, mode, *args, **kwargs)
            return wrapped
        self.patches = [patch('builtins.open', guard(real_builtin)), patch('io.open', guard(real_io)),
            patch.object(Path, 'mkdir', side_effect=AssertionError('Memory tests forbid mkdir')),
            patch.object(m.audited.g, 'event', side_effect=AssertionError('No events'))]
        for p in self.patches:
            p.start()
        self.addCleanup(lambda: [p.stop() for p in reversed(self.patches)])

    def reject(self, packet, review, post=False):
        result = m.validate_review(packet, review, self.raw if post else None, self.fixture['raw_lock'] if post else None)
        self.assertFalse(result['valid'], result)
        self.assertTrue(result['errors'])

    def context(self, job):
        return {'output_exists': False, 'prompt_exists': False, 'admission_valid': True,
            'source_bound_phase_readiness': True, 'confirmation_allowed': True,
            'source_hashes': {p: 'a' * 64 for p in job.get('input_refs', [])},
            'template': m.prompt_text(job['operation']), 'assigned_prompt_ref': 'prompts/future/' + job['job_id'] + '.txt',
            'source_freeze_sha256': 'b' * 64}

    def first_job(self, operation):
        return next(j for j in self.jobs.values() if j['operation'] == operation)

    def test_01_all_114_and_24(self):
        self.assertEqual(m.validate_schedule(*m.make_schedule())['G_D'], 114)
        for case in m.CASES:
            js = [j for j in self.jobs.values() if j['case_id'] == case]
            self.assertEqual((len(js), sum(j['role'] == 'compression' for j in js)), (19, 5))
        self.assertEqual(len(self.pack['reviews']['jobs']), 24)

    def test_02_shared_read_identity(self):
        for case in m.CASES:
            js = [j for j in self.jobs.values() if j['case_id'] == case]
            shared = js[:4]
            self.assertTrue(all(j['input_refs'] == [f'cases/{case}.json'] and not j['depends_on'] for j in shared))
            for arm in m.ARMS:
                challenger, convergence, compressor = [j for j in js if j['arm'] == arm]
                self.assertEqual(challenger['depends_on'], [shared[0]['job_id']])
                self.assertEqual(convergence['depends_on'][:4], [j['job_id'] for j in shared])
                self.assertEqual(convergence['depends_on'][-1], challenger['job_id'])
                self.assertEqual(compressor['depends_on'], [convergence['job_id']])

    def test_03_budgets_exact_and_nontransferable(self):
        self.assertEqual(self.pack['schedule']['phase_budgets']['pilot'], {'G_D': 38, 'raw_post_reviews': 8, 'base': 46, 'maximum': 48})
        self.assertEqual(self.pack['schedule']['phase_budgets']['confirmation'], {'G_D': 76, 'raw_post_reviews': 16, 'base': 92, 'maximum': 96})
        for j in self.jobs.values():
            self.assertEqual(j['soft_saved_word_limit'], 350 if j['role'] == 'compression' else 420)
        self.assertTrue(all(j['soft_saved_word_limit'] == 20000 for j in self.pack['reviews']['jobs']))

    def test_04_full_exact_730_855(self):
        self.assertEqual(self.raw['core_packet']['matrix_counts'], m.RAW_COUNTS)
        self.assertEqual(self.post['core_packet']['matrix_counts'], m.POST_COUNTS)
        self.assertEqual((self.raw['expected_total_rows'], self.post['expected_total_rows']), (730, 855))
        for packet in (self.raw, self.post):
            independently = m.rederive_core_identities(packet['core_packet'])
            for table, ids in independently.items():
                self.assertEqual({m.canonical_hash(x) for x in ids},
                    {m.canonical_hash(x['identity']) for x in packet['core_packet']['expected_matrix'][table]})

    def test_05_all_60_pairs_even_undeclared(self):
        rows = self.post['expected_source_pairs']
        self.assertEqual(len(rows), 60)
        self.assertEqual(rows, m.expected_source_pairs(self.post['core_packet']))
        self.assertEqual(len({(r['identity']['post_card_id'], r['identity']['source_card_id']) for r in rows}), 60)
        for u in self.post['core_packet']['units']:
            if u['content_kind'] == 'summary':
                self.assertEqual(sum(r['identity']['post_card_id'] in {p['id'] for p in u['artifact']['openings']} for r in rows), 12)

    def test_06_all_artifacts_schema_valid(self):
        for job in self.fjobs.values():
            result = m.validate_generation(job, self.fixture['artifacts'][job['job_id']], self.pack['cases']['H-P'],
                {p: self.fixture['artifacts'][p] for p in job['depends_on']})
            self.assertTrue(result['valid'], result)

    def test_07_complete_prompt_schemas(self):
        for op in m.OPERATIONS:
            text = m.prompt_text(op)
            schema = m.json_text(text.split('Return exactly this complete nested JSON Schema; no other keys:\n')[1])
            self.assertEqual(schema, m.role_schema(op))
            self.assertFalse(schema['additionalProperties'])
        for op in ('ordinary', 'generic'):
            text = m.prompt_text(op)
            for forbidden in ('factorial', 'Robot Talks', 'hypothesis', 'OC', 'IC', 'OD', 'GC'):
                # schema's kind=hypothesis is a required card enum, not treatment hypothesis.
                if forbidden != 'hypothesis':
                    self.assertNotIn(forbidden, text)

    def test_08_strict_json_duplicate_and_constants(self):
        for text in ('{"a":1,"a":2}', '{"x":NaN}', '{"x":Infinity}', '{bad'):
            with self.assertRaises(ValueError):
                m.json_text(text)

    def test_09_strict_normalized_paths(self):
        for path in ('../a', '/a', 'a/../b', 'a//b', './a', 'a\\b', 'C:/a', 'a/', ''):
            self.assertFalse(m.relative(path), path)
        self.assertTrue(m.relative('a/b.json'))

    def test_10_boolean_integer_and_unknown_keys(self):
        job = next(j for j in self.fjobs.values() if j['role'] == 'convergence')
        body = copy.deepcopy(self.fixture['artifacts'][job['job_id']]); body['contradiction_count'] = False
        priors = {p: self.fixture['artifacts'][p] for p in job['depends_on']}
        self.assertFalse(m.validate_generation(job, body, self.pack['cases']['H-P'], priors)['valid'])
        body = copy.deepcopy(self.fixture['artifacts'][job['job_id']]); body['unknown'] = 1
        self.assertFalse(m.validate_generation(job, body, self.pack['cases']['H-P'], priors)['valid'])

    def test_11_lineage_full_unknown_and_duplicates(self):
        job = next(j for j in self.fjobs.values() if j['semantic_role'] == 'challenger')
        priors = {p: self.fixture['artifacts'][p] for p in job['depends_on']}
        for mutation in ('missing', 'duplicate', 'unknown', 'targets'):
            body = copy.deepcopy(self.fixture['artifacts'][job['job_id']])
            if mutation == 'missing': body['lineage'] = []
            elif mutation == 'duplicate': body['lineage'].append(copy.deepcopy(body['lineage'][0]))
            elif mutation == 'unknown': body['openings'][0]['source_refs'].append('G9999:R1')
            else: body['lineage'][0]['target_ids'] = ['R3']
            self.assertFalse(m.validate_generation(job, body, self.pack['cases']['H-P'], priors)['valid'], mutation)

    def test_12_prediction_pairs_all_and_duplicate_unordered(self):
        unit = next(u for u in self.raw['core_packet']['units'] if 'prediction_commitment_pairs' in u)
        self.assertEqual(len(unit['prediction_commitment_pairs']), 36)
        job = next(j for j in self.fjobs.values() if j['role'] == 'convergence')
        body = copy.deepcopy(self.fixture['artifacts'][job['job_id']])
        priors = {p: self.fixture['artifacts'][p] for p in job['depends_on']}
        ids = [p + ':' + c['id'] + ':prediction' for p, a in priors.items() for c in a['openings']]
        body['contradictions'] = [{'pair': ids[:2], 'evidence': 'Fictional opposed predictions.'}, {'pair': list(reversed(ids[:2])), 'evidence': 'Duplicate.'}]
        body['contradiction_count'] = 2
        self.assertFalse(m.validate_generation(job, body, self.pack['cases']['H-P'], priors)['valid'])
        body['contradictions'][1]['pair'] = ['G9999:R1:prediction', ids[0]]
        self.assertFalse(m.validate_generation(job, body, self.pack['cases']['H-P'], priors)['valid'])

    def test_13_seed_exact_one_or_none(self):
        job = next(j for j in self.fjobs.values() if j['operation'] == 'seed')
        body = copy.deepcopy(self.fixture['artifacts'][job['job_id']])
        body['openings'] = []; body['seed_status'] = 'no_viable_seed'
        self.assertTrue(m.validate_generation(job, body, self.pack['cases']['H-P'], {})['valid'])
        body['seed_status'] = 'viable'
        self.assertFalse(m.validate_generation(job, body, self.pack['cases']['H-P'], {})['valid'])

    def test_14_no_seed_skips_dependents_concerns_independent(self):
        challenger = self.first_job('ordinary'); seed = self.jobs[challenger['depends_on'][0]]
        states = {k: 'pending' for k in self.jobs}; states[seed['job_id']] = 'valid'
        body = {'seed_status': 'no_viable_seed', 'openings': []}
        plan = m.prepare_job(challenger, self.jobs, states, {seed['job_id']: body}, self.context(challenger))
        self.assertEqual(plan['cause'], 'no_viable_shared_seed')
        concern = self.first_job('concern-evidence')
        self.assertEqual(m.prepare_job(concern, self.jobs, states, {}, self.context(concern))['event_kind'], 'job_prepared')

    def test_15_invalid_missing_skipped_preserve_denominator(self):
        job = self.first_job('ordinary')
        for failure in ('invalid', 'missing', 'skipped'):
            states = {k: 'pending' for k in self.jobs}; states[job['depends_on'][0]] = failure
            plan = m.prepare_job(job, self.jobs, states, {}, self.context(job))
            self.assertEqual(plan['status'], 'skipped')
            self.assertIsNone(plan['semantic_assessment'])
            coverage = m.coverage(self.jobs, [plan])
            self.assertEqual((coverage['planned'], coverage['skipped'], coverage['actual_native_starts']), (114, 1, 0))

    def test_16_raw_before_D_preparation_and_start(self):
        job = self.first_job('compression'); states = {k: 'valid' for k in self.jobs}; states[job['job_id']] = 'pending'
        context = self.context(job)
        with self.assertRaises((KeyError, TypeError, ValueError)):
            m.prepare_job(job, self.jobs, states, {}, context)
        context.update(raw_packet=self.raw, raw_lock=self.fixture['raw_lock'], dual_raw_final_observed=True, raw_lock_source_binding_valid=True)
        with self.assertRaises(ValueError):
            m.prepare_job(job, self.jobs, states, {}, context)
        with self.assertRaises(ValueError):
            m.check_D_ready(job, context)

    def test_17_D_current_local_source_ids(self):
        job = next(j for j in self.fjobs.values() if j['role'] == 'compression')
        priors = {p: self.fixture['artifacts'][p] for p in job['depends_on']}
        body = copy.deepcopy(self.fixture['artifacts'][job['job_id']])
        body['openings'][0]['source_ids'] = [job['depends_on'][0] + ':R1']
        self.assertFalse(m.validate_generation(job, body, self.pack['cases']['H-P'], priors)['valid'])
        body = copy.deepcopy(self.fixture['artifacts'][job['job_id']]); body['lineage'][0]['target_ids'] = ['D1']
        self.assertFalse(m.validate_generation(job, body, self.pack['cases']['H-P'], priors)['valid'])

    def test_18_D_optional_caps_and_unknown_keys(self):
        job = next(j for j in self.fjobs.values() if j['role'] == 'compression')
        priors = {p: self.fixture['artifacts'][p] for p in job['depends_on']}
        body = copy.deepcopy(self.fixture['artifacts'][job['job_id']]); body['proposals'].append(copy.deepcopy(body['proposals'][0]))
        self.assertFalse(m.validate_generation(job, body, self.pack['cases']['H-P'], priors)['valid'])
        body = copy.deepcopy(self.fixture['artifacts'][job['job_id']]); body['openings'][0]['extra'] = 0
        self.assertFalse(m.validate_generation(job, body, self.pack['cases']['H-P'], priors)['valid'])

    def test_19_valid_raw_and_post_review(self):
        self.assertTrue(m.validate_review(self.raw, m.fixture_review(self.raw))['valid'])
        result = m.validate_review(self.post, m.fixture_review(self.post), self.raw, self.fixture['raw_lock'])
        self.assertTrue(result['valid'], result)
        self.assertEqual((result['carried_rows'], result['fresh_rows']), (730, 125))

    def test_20_exact_carry_values_evidence_status(self):
        carried = self.post['core_packet']['raw_first']['carried_rows']
        self.assertEqual(carried, m.raw.locked_rows(self.raw['core_packet'], self.fixture['raw_lock']['core_lock']))
        for field in ('values', 'field_status'):
            packet = copy.deepcopy(self.post)
            row = packet['core_packet']['raw_first']['carried_rows'][0]
            if field == 'values': row[field]['evidence'] += ' drift'
            else: row[field][next(iter(row[field]))] = 'agreed'
            packet['core_packet_sha256'] = m.canonical_hash(packet['core_packet'])
            self.reject(packet, m.fixture_review(packet), True)

    def test_21_carried_review_evidence_change(self):
        review = m.fixture_review(self.post); review['core_review']['raw_rows'][0][-1] += ' drift'
        self.reject(self.post, review, True)

    def test_22_protected_raw_source_drift(self):
        for field in ('claim', 'delta', 'prediction', 'probe', 'fit', 'assumptions'):
            packet = copy.deepcopy(self.post)
            source = next(u for u in packet['core_packet']['units'] if u['content_kind'] == 'source')
            card = source['artifact']['openings'][0]
            card[field] = ['drift'] if field == 'assumptions' else 'violates' if field == 'fit' else card[field] + ' drift'
            packet['core_packet_sha256'] = m.canonical_hash(packet['core_packet'])
            packet['raw_core_context_sha256'] = m.raw.raw_context_hash(packet['core_packet'])
            self.reject(packet, m.fixture_review(packet), True)

    def test_23_stripping_wrapper(self):
        self.reject(self.raw['core_packet'], m.fixture_review(self.raw)['core_review'])
        review = m.fixture_review(self.raw); review['extra'] = 0
        self.reject(self.raw, review)

    def test_24_truncation_core_packet_even_recount_rehash(self):
        packet = copy.deepcopy(self.raw)
        packet['core_packet']['expected_matrix']['candidate_pairs'].pop()
        packet['core_packet']['matrix_counts']['candidate_pairs'] -= 1
        packet['core_packet']['expected_total_rows'] -= 1
        packet['core_packet_sha256'] = m.canonical_hash(packet['core_packet'])
        packet['raw_core_context_sha256'] = m.raw.raw_context_hash(packet['core_packet'])
        packet['matrix_counts']['candidate_pairs'] -= 1; packet['expected_total_rows'] -= 1
        self.reject(packet, m.fixture_review(packet))

    def test_25_truncation_review_core(self):
        review = m.fixture_review(self.raw); review['core_review']['contradiction_rows'].pop()
        self.reject(self.raw, review)

    def test_26_source_extension_truncation_and_duplicates(self):
        for change in ('missing', 'duplicate', 'unknown', 'enum', 'blank', 'width'):
            review = m.fixture_review(self.post)
            if change == 'missing': review['source_pairs'].pop()
            elif change == 'duplicate': review['source_pairs'].append(copy.deepcopy(review['source_pairs'][0]))
            elif change == 'unknown': review['source_pairs'][0][1] = 'unknown-source'
            elif change == 'enum': review['source_pairs'][0][2] = 'retained'
            elif change == 'blank': review['source_pairs'][0][3] = ' '
            else: review['source_pairs'][0].append('extra')
            self.reject(self.post, review, True)

    def test_27_source_extension_packet_recount_hides_nothing(self):
        packet = copy.deepcopy(self.post); packet['expected_source_pairs'].pop()
        packet['matrix_counts']['source_pairs'] -= 1; packet['expected_total_rows'] -= 1
        self.reject(packet, m.fixture_review(packet), True)

    def test_28_boolean_as_integer_review(self):
        review = m.fixture_review(self.raw); review['core_review']['raw_rows'][0][2] = False
        self.reject(self.raw, review)

    def test_29_reviewer_and_columns_identity(self):
        for change in ('wrong', 'mismatch', 'columns'):
            review = m.fixture_review(self.raw)
            if change == 'wrong': review['reviewer_id'] = review['core_review']['reviewer_id'] = 'unknown'
            elif change == 'mismatch': review['core_review']['reviewer_id'] = self.raw['core_packet']['review_job_ids'][1]
            else: review['core_review']['columns']['raw_rows'].pop()
            self.reject(self.raw, review)

    def test_30_full_map_and_schedule_hashes(self):
        self.assertEqual(self.raw['opaque_map_sha256'], m.canonical_hash(self.fixture['raw_opaque_map']))
        self.assertEqual(self.post['opaque_map_sha256'], m.canonical_hash(self.fixture['post_opaque_map']))
        self.assertEqual(self.raw['custom_schedule_sha256'], m.canonical_hash(self.fixture['input_pack']['schedule']))
        packet = copy.deepcopy(self.post); packet['raw_opaque_map_sha256'] = '0' * 64
        self.reject(packet, m.fixture_review(packet), True)

    def test_31_start_all_binding_errors(self):
        job = self.first_job('seed'); states = {k: 'pending' for k in self.jobs}; ctx = self.context(job)
        prepared = m.prepare_job(job, self.jobs, states, {}, ctx)
        start, _ = native(prepared)
        m.start_valid(job['job_id'], start['agent_handle'], start, prepared, [])
        for field in ('agent_handle', 'native_call_id', 'turn', 'prompt_sha256', 'source_freeze_sha256', 'output_ref', 'case_id', 'phase', 'study_id', 'job_id'):
            bad = dict(start); bad[field] = False if field == 'turn' else ''
            with self.assertRaises(ValueError, msg=field):
                m.start_valid(job['job_id'], start['agent_handle'], bad, prepared, [])

    def test_32_final_all_binding_errors(self):
        job = self.first_job('seed'); ctx = self.context(job)
        prepared = m.prepare_job(job, self.jobs, {k: 'pending' for k in self.jobs}, {}, ctx)
        start, final = native(prepared, payload=b'{}')
        m.final_valid(job['job_id'], start['agent_handle'], final, prepared, start, final['output_sha256'])
        for field in ('agent_handle', 'native_call_id', 'turn', 'prompt_sha256', 'source_freeze_sha256', 'output_ref', 'output_sha256', 'terminal_witness', 'native_final_observed'):
            bad = dict(final); bad[field] = False if field in ('turn', 'native_final_observed') else ''
            with self.assertRaises(ValueError, msg=field):
                m.final_valid(job['job_id'], start['agent_handle'], bad, prepared, start, final['output_sha256'])

    def test_33_first_save_zero_retry_state_machine(self):
        job = self.first_job('seed'); prepared = m.prepare_job(job, self.jobs, {k: 'pending' for k in self.jobs}, {}, self.context(job))
        start, final = native(prepared)
        e = dict(start, runtime_version=m.VERSION, event_kind='native_spawn')
        f = dict(final, runtime_version=m.VERSION, event_kind='native_terminal_join', execution='missing')
        self.assertEqual(m.state_from_events({job['job_id']: job}, [prepared,e,f])[job['job_id']], 'missing')
        for events in ([prepared,prepared], [prepared,e,e], [prepared,e,f,f], [e], [prepared,f]):
            with self.assertRaises(ValueError): m.state_from_events({job['job_id']: job}, events)

    def test_34_spawn_first_output_and_prompt_drift(self):
        job = self.first_job('seed'); ctx = self.context(job)
        prepared = m.prepare_job(job, self.jobs, {k: 'pending' for k in self.jobs}, {}, ctx)
        start, _ = native(prepared)
        ctx['actual_prompt_bytes'] = prepared['prompt_text'].encode()
        self.assertEqual(m.spawn_job(job, prepared, start, [prepared], ctx)['event_kind'], 'native_spawn')
        ctx['output_exists'] = True
        with self.assertRaises(ValueError): m.spawn_job(job, prepared, start, [prepared], ctx)
        ctx['output_exists'] = False; ctx['actual_prompt_bytes'] += b'drift'
        with self.assertRaises(ValueError): m.spawn_job(job, prepared, start, [prepared], ctx)

    def test_35_join_strict_actual_bytes_missing_and_invalid(self):
        job = self.first_job('seed'); ctx = self.context(job)
        prepared = m.prepare_job(job, self.jobs, {k: 'pending' for k in self.jobs}, {}, ctx)
        for payload, expected in ((None, 'missing'), (b'{"case_id":1,"case_id":2}', 'invalid'), (b'[]', 'invalid')):
            start, final = native(prepared, payload=payload)
            result = m.join_job(job, prepared, start, final, payload, self.pack['cases']['H-P'], {})
            self.assertEqual(result['execution'], expected)
            self.assertIsNone(result['validation']['saved_words'] if payload is None else None)

    def test_36_fresh_handles_and_no_automatic_scalar(self):
        job = self.first_job('seed'); prepared = m.prepare_job(job, self.jobs, {k: 'pending' for k in self.jobs}, {}, self.context(job))
        start, _ = native(prepared)
        with self.assertRaises(ValueError):
            m.start_valid(job['job_id'], start['agent_handle'], start, prepared, [dict(start, event_kind='native_spawn')])
        self.assertIn('never automatic', self.pack['schedule']['optional_scalar_turn'])

    def test_37_exact_source_union_no_hash_cycle(self):
        union = m.source_paths(self.original)
        self.assertIn(m.INDEPENDENT, union); self.assertIn(m.INDEPENDENT_OUTPUT, union)
        self.assertFalse({m.FREEZE,m.ADMISSION,m.EVENTS} & union)
        self.assertEqual(union - m.source_paths(self.original,False), {m.INDEPENDENT,m.INDEPENDENT_OUTPUT})
        for cap in m.CAPACITY.values(): self.assertIn(cap['validation_ref'], union)

    def test_38_fictional_lock_never_live(self):
        lock = self.fixture['raw_lock']
        self.assertTrue(lock['fixture_only']); self.assertEqual(lock['native_witnesses'], [])
        self.assertFalse(lock['core_lock']['independent_review_complete'])
        self.assertEqual(len(lock['core_lock']['rows']), 730)
        self.assertTrue(all(v is None for r in lock['core_lock']['rows'] for k,v in r['values'].items() if k in r['field_status']))

    def test_39_old_globals_unchanged_after_builders(self):
        before = {k:id(v) for k,v in vars(m.base).items()}
        f = m.maximal_fixture_pack(self.pack)
        self.assertEqual(before, {k:id(v) for k,v in vars(m.base).items()})
        self.assertEqual(f['raw_packet'], self.raw); self.assertEqual(f['post_packet'], self.post)

    def test_40_memory_writer_guard(self):
        with self.assertRaises(AssertionError): m.save_new('/UNSCORED-never-write.json', {})

    def test_41_saved_fixture_inputs_rebuild(self):
        rebuilt = m.maximal_fixture_pack(self.fixture['input_pack'])
        self.assertEqual(rebuilt['raw_packet'], self.raw)
        self.assertEqual(rebuilt['post_packet'], self.post)
        self.assertEqual(rebuilt['raw_lock'], self.fixture['raw_lock'])

    def test_42_invalid_source_nulls_and_missing_units_retained(self):
        pack = self.fixture['input_pack']; artifacts = copy.deepcopy(self.fixture['artifacts']); disp = copy.deepcopy(self.fixture['dispositions'])
        raw_jobs = [j for j in pack['schedule']['jobs'] if j['role'] != 'compression']
        seed = raw_jobs[0]['job_id']; missing = raw_jobs[1]['job_id']
        disp[seed] = {'execution':'invalid','cause':'UNSCORED invalid readable seed'}
        disp[missing] = {'execution':'missing','cause':'UNSCORED missing source'}; artifacts.pop(missing)
        raw_ids = {j['job_id'] for j in raw_jobs}
        packet,_ = m.build_raw_case('H-P',{k:v for k,v in artifacts.items() if k in raw_ids},{k:v for k,v in disp.items() if k in raw_ids},pack)
        self.assertEqual(len(packet['core_packet']['units']),14)
        self.assertTrue(any(x['null_semantics'] for x in packet['core_packet']['expected_matrix']['raw_rows']))
        review = m.fixture_review(packet)
        self.assertTrue(m.validate_review(packet,review)['valid'])

    def test_43_optional_proposals_separate_from_pairs(self):
        self.assertEqual(len(self.post['core_packet']['expected_matrix']['addition_rows']),10)
        post_ids = {r['identity']['card_id'] for r in self.post['core_packet']['expected_matrix']['post_rows']}
        self.assertTrue(all(r['identity']['post_card_id'] in post_ids for r in self.post['expected_source_pairs']))

    def test_44_preparation_and_live_gate_separate(self):
        job = self.first_job('seed'); ctx = self.context(job); ctx['admission_valid'] = False
        with self.assertRaises(ValueError): m.prepare_job(job,self.jobs,{k:'pending' for k in self.jobs},{},ctx)
        ctx['admission_valid'] = True; ctx['source_bound_phase_readiness'] = False
        with self.assertRaises(ValueError): m.prepare_job(job,self.jobs,{k:'pending' for k in self.jobs},{},ctx)

    def test_45_duplicate_core_identity_and_unknown_null_type(self):
        review = m.fixture_review(self.raw); review['core_review']['raw_rows'].append(copy.deepcopy(review['core_review']['raw_rows'][0]))
        self.reject(self.raw,review)
        packet = copy.deepcopy(self.raw); packet['matrix_counts']['raw_rows'] = True
        self.reject(packet,m.fixture_review(packet))

    def test_46_equal_27_raw_and_19_units_protected_in_saved_post(self):
        self.assertEqual(len(self.post['core_packet']['units']),19)
        self.assertEqual(m.raw.raw_context_hash(self.raw['core_packet']),m.raw.raw_context_hash(self.post['core_packet']))
        self.assertEqual(len(self.post['core_packet']['expected_matrix']['raw_rows']),27)

    def test_47_failure_raw_review_preserves_planned_null_rows(self):
        core = self.raw['core_packet']
        prepared=[];starts=[];finals=[]
        for n in (1,2):
            p={'job_id':f'RF-R-I12-H-P-{n}','study_id':'I12','case_id':'H-P','phase':'pilot',
                'prompt_ref':f'prompts/future/r{n}.txt','prompt_sha256':'a'*64,'source_freeze_sha256':'b'*64,
                'output_ref':f'reviews/future/r{n}.json'}
            s,f=native(p,n,None);prepared.append(p);starts.append(s);finals.append(f)
        lock=m.reconcile_reviews(self.raw,[None,None],prepared,starts,finals,[None,None],
            [{'path':'fixtures/future/raw.json','sha256':'c'*64}])
        self.assertFalse(lock['independent_review_complete'])
        self.assertEqual(len(lock['core_lock']['rows']),730)
        m.validate_raw_lock(self.raw,lock)
        self.assertTrue(all(v is None for r in lock['core_lock']['rows'] for k,v in r['values'].items() if k in r['field_status']))

    def test_48_extension_family_dispute_stays_separate(self):
        prepared=[];starts=[];finals=[];reviews=[];payloads=[]
        for n in (1,2):
            r=m.fixture_review(self.post,self.post['core_packet']['review_job_ids'][n-1])
            if n==2:r['source_pairs'][0][2]='distinct'
            payload=encode(r);payloads.append(payload);reviews.append(r)
            p={'job_id':f'RF-P-I12-H-P-{n}','study_id':'I12','case_id':'H-P','phase':'pilot',
                'prompt_ref':f'prompts/future/p{n}.txt','prompt_sha256':'a'*64,'source_freeze_sha256':'b'*64,'output_ref':f'reviews/future/p{n}.json'}
            s,f=native(p,n,payload);prepared.append(p);starts.append(s);finals.append(f)
        lock=m.reconcile_reviews(self.post,reviews,prepared,starts,finals,payloads,
            [{'path':'fixtures/future/post.json','sha256':'c'*64}],self.raw,self.fixture['raw_lock'])
        row=next(r for r in lock['source_pairs'] if r['field_status']['relation']=='family_unresolved')
        self.assertIsNone(row['values']['relation'])
        self.assertEqual(lock['extension_family_merge_credit'],0)
        self.assertEqual([r for r in lock['core_lock']['rows'] if (r['table'],r['row_id']) in
            {(r['table'],r['row_id']) for r in self.fixture['raw_lock']['core_lock']['rows']}],
            self.fixture['raw_lock']['core_lock']['rows'])



    def readiness_bundle(self):
        # Fictional parent receipts exist only in memory; no native event is written.
        hashes={p:hashlib.sha256(('UNSCORED '+p).encode()).hexdigest() for p in
            m.source_paths(self.original)|{m.FREEZE,m.ADMISSION}}
        hashes.update(self.before)
        bundle={'fixture_inputs':copy.deepcopy(self.fixture)}
        events=[]
        def binds(paths):return [{'path':p,'sha256':hashes[p]} for p in sorted(paths)]
        def validator(items):
            self.assertEqual(len({x['path'] for x in items}),len(items))
            for x in items:
                m.require(set(x)=={'path','sha256'} and m.relative(x['path']) and hashes.get(x['path'])==x['sha256'],'memory-bound source hash')
        for n,phase in enumerate(('raw','post'),1):
            spec=m.CAPACITY[phase];packet=self.raw if phase=='raw' else self.post
            review=m.fixture_review(packet);bundle[phase+'_capacity_review']=review
            hashes[spec['output_ref']]=hashlib.sha256(encode(review)).hexdigest()
            sources=binds(m.capacity_source_paths(phase))
            snapshot=[x for x in sources if x['path']!=spec['output_ref']]
            p={'job_id':spec['job_id'],'study_id':'I12','case_id':'UNSCORED-MAXIMAL','phase':'preparation',
                'prompt_ref':spec['prompt_ref'],'prompt_sha256':hashes[spec['prompt_ref']],
                'source_freeze_sha256':m.canonical_hash(snapshot),'output_ref':spec['output_ref']}
            start,final=native(p,n,encode(review))
            cap={'classification':'pass','study_id':'I12','capacity_phase':phase,'expected_rows':spec['expected_rows'],
                'actual_native_starts':1,'actual_native_terminal_joins':1,'native_start':start,'native_final':final,
                'structural_validation':{'valid':True,'output_sha256':hashes[spec['output_ref']],
                    'expected_rows':spec['expected_rows'],'core_rows':730 if phase=='raw' else 795,'source_pair_rows':0 if phase=='raw' else 60},
                'saved_word_soft_limit':20000,'saved_words':100,'overage_words':0,'source_bindings':sources,
                'wrapper_sha256':m.canonical_hash(packet),'core_sha256':packet['core_packet_sha256'],
                'opaque_map_sha256':packet['opaque_map_sha256'],'custom_schedule_sha256':packet['custom_schedule_sha256'],
                'raw_core_context_sha256':packet['raw_core_context_sha256'],'assigned_reviewer_id':review['reviewer_id'],
                'claim_ceiling':'structure_and_size_only'}
            bundle[phase+'_capacity']=cap
            hashes[spec['validation_ref']]=hashlib.sha256(encode(cap)).hexdigest()
            events.extend([{'event_kind':'native_spawn','job_id':spec['job_id'],'witness':start},
                {'event_kind':'preparation_terminal_join','job_id':spec['job_id'],'witness':final}])
        sources=binds(m.source_paths(self.original,False))
        p={'job_id':'PREP-I12-INDEPENDENT-PRELAUNCH','study_id':'I12','case_id':'PRELAUNCH','phase':'preparation',
            'prompt_ref':m.PROMPT_DIR+'/independent-prelaunch.txt','prompt_sha256':hashes[m.PROMPT_DIR+'/independent-prelaunch.txt'],
            'source_freeze_sha256':m.canonical_hash(sources),'output_ref':m.INDEPENDENT_OUTPUT}
        start,final=native(p,3);final['output_sha256']=hashes[m.INDEPENDENT_OUTPUT]
        independent={'classification':'independent_prelaunch_pass','study_id':'I12','source_bindings':sources,
            'native_start':start,'native_final':final,'independent_from_author_and_capacity':True,
            'runtime_source_audit_pass':True,'independent_native_final_observed':True}
        bundle['independent']=independent;hashes[m.INDEPENDENT]=hashlib.sha256(encode(independent)).hexdigest()
        events.extend([{'event_kind':'native_spawn','job_id':p['job_id'],'witness':start},
            {'event_kind':'preparation_terminal_join','job_id':p['job_id'],'witness':final}])
        bundle['freeze']={'study_id':'I12','classification':'exact_native_source_freeze','files':binds(m.source_paths(self.original))}
        hashes[m.FREEZE]=hashlib.sha256(encode(bundle['freeze'])).hexdigest()
        bundle['admission']={'status':'pass','study_id':'I12','freeze_sha256':hashes[m.FREEZE],
            'independent_prelaunch_sha256':hashes[m.INDEPENDENT],
            'raw_capacity_validation_sha256':hashes[m.CAPACITY['raw']['validation_ref']],
            'post_capacity_validation_sha256':hashes[m.CAPACITY['post']['validation_ref']],
            'parent_observed_receipts_complete':True}
        return bundle,validator,lambda p:hashes[p],events

    def test_49_complete_fictional_readiness_structure_only(self):
        bundle,validate,file_hash,events=self.readiness_bundle()
        self.assertTrue(m.validate_readiness(bundle,self.original,validate,file_hash,events)['ready'])

    def test_50_both_capacity_receipts_needed(self):
        for phase in ('raw','post'):
            bundle,validate,file_hash,events=self.readiness_bundle();bundle.pop(phase+'_capacity')
            with self.assertRaises(ValueError):m.validate_readiness(bundle,self.original,validate,file_hash,events)

    def test_51_actual_starts_and_FINALs_needed(self):
        for kind in ('native_spawn','preparation_terminal_join'):
            for phase in ('raw','post'):
                bundle,validate,file_hash,events=self.readiness_bundle()
                events=[e for e in events if not(e['job_id']==m.CAPACITY[phase]['job_id'] and e['event_kind']==kind)]
                with self.assertRaises(ValueError):m.validate_readiness(bundle,self.original,validate,file_hash,events)

    def test_52_actual_full_parent_capacity_validator_needed(self):
        bundle,validate,file_hash,events=self.readiness_bundle()
        bundle['post_capacity_review']['source_pairs'].pop()
        with self.assertRaises(ValueError):m.validate_readiness(bundle,self.original,validate,file_hash,events)

    def test_53_exact_future_freeze_union(self):
        for mutate in ('missing','extra'):
            bundle,validate,file_hash,events=self.readiness_bundle()
            if mutate=='missing':bundle['freeze']['files'].pop()
            else:bundle['freeze']['files'].append(copy.deepcopy(bundle['freeze']['files'][0]))
            with self.assertRaises((ValueError,AssertionError)):m.validate_readiness(bundle,self.original,validate,file_hash,events)

    def test_54_exact_independent_union_and_native_FINAL(self):
        for mutate in ('missing','final','hash'):
            bundle,validate,file_hash,events=self.readiness_bundle()
            if mutate=='missing':bundle['independent']['source_bindings'].pop()
            elif mutate=='final':bundle['independent']['native_final']['native_final_observed']=False
            else:bundle['independent']['native_final']['output_sha256']='0'*64
            with self.assertRaises(ValueError):m.validate_readiness(bundle,self.original,validate,file_hash,events)

    def test_55_capacity_unique_fresh_reviewers_and_explicit_assignment(self):
        bundle,validate,file_hash,events=self.readiness_bundle()
        bundle['raw_capacity']['assigned_reviewer_id']='unknown'
        with self.assertRaises(ValueError):m.validate_readiness(bundle,self.original,validate,file_hash,events)
        bundle,validate,file_hash,events=self.readiness_bundle()
        bundle['post_capacity']['native_start']['agent_handle']=bundle['raw_capacity']['native_start']['agent_handle']
        bundle['post_capacity']['native_final']['agent_handle']=bundle['raw_capacity']['native_start']['agent_handle']
        with self.assertRaises(ValueError):m.validate_readiness(bundle,self.original,validate,file_hash,events)

    def test_56_capacity_map_schedule_context_drift(self):
        for field in ('wrapper_sha256','core_sha256','opaque_map_sha256','custom_schedule_sha256','raw_core_context_sha256'):
            bundle,validate,file_hash,events=self.readiness_bundle();bundle['raw_capacity'][field]='0'*64
            with self.assertRaises(ValueError):m.validate_readiness(bundle,self.original,validate,file_hash,events)

    def test_57_capacity_bool_turn_and_counter(self):
        for field in ('expected_rows','actual_native_starts'):
            bundle,validate,file_hash,events=self.readiness_bundle();bundle['raw_capacity'][field]=True
            with self.assertRaises(ValueError):m.validate_readiness(bundle,self.original,validate,file_hash,events)

    def test_58_separate_exact_admission_gate(self):
        bundle,validate,file_hash,events=self.readiness_bundle();bundle['admission']['post_capacity_validation_sha256']='0'*64
        with self.assertRaises(ValueError):m.validate_readiness(bundle,self.original,validate,file_hash,events)

    def test_59_convergence_pairs_cannot_be_erased_and_recounted(self):
        packet=copy.deepcopy(self.raw)
        for u in packet['core_packet']['units']:u.pop('prediction_commitment_pairs',None)
        packet['core_packet']['expected_matrix']['contradiction_rows']=[]
        packet['core_packet']['matrix_counts']['contradiction_rows']=0
        packet['core_packet']['expected_total_rows']-=180
        packet['core_packet_sha256']=m.canonical_hash(packet['core_packet'])
        packet['raw_core_context_sha256']=m.raw.raw_context_hash(packet['core_packet'])
        packet['matrix_counts']['contradiction_rows']=0;packet['expected_total_rows']-=180
        self.reject(packet,m.fixture_review(packet))

    def test_60_planned_source_graph_cannot_be_changed(self):
        packet=copy.deepcopy(self.raw)
        u=next(u for u in packet['core_packet']['units'] if len(u['source_unit_ids'])==5)
        u['source_unit_ids']=u['source_unit_ids'][:1]
        packet['planned_units']=[{'unit_id':u['unit_id'],'content_kind':u['content_kind'],'source_unit_ids':u['source_unit_ids']} for u in packet['core_packet']['units']]
        packet['core_packet_sha256']=m.canonical_hash(packet['core_packet']);packet['raw_core_context_sha256']=m.raw.raw_context_hash(packet['core_packet'])
        self.reject(packet,m.fixture_review(packet))

    def test_61_separate_parent_phase_readiness_required(self):
        job=self.first_job('seed')
        receipt={'study_id':'I12','phase':'pilot','status':'pass','policy_source_sha256':'a'*64,
            'upstream':{k:{'status':'pass','native_terminals_observed':True,'complete_dual_assessments':True,
                'locked_decision':True,**({'fidelity_ready':True} if k=='I09' else {}),'source_bindings':[{'path':'future/'+k+'.json','sha256':'b'*64}]} for k in ('I05','I08','I09')}}
        self.assertTrue(m.phase_gate(job,receipt,'a'*64,lambda _:None))
        receipt['upstream']['I09']['fidelity_ready']=False
        with self.assertRaises(ValueError):m.phase_gate(job,receipt,'a'*64,lambda _:None)

    def test_62_extension_invalid_source_pair_null_semantics(self):
        pack=self.fixture['input_pack'];artifacts=copy.deepcopy(self.fixture['artifacts']);disp=copy.deepcopy(self.fixture['dispositions'])
        D=next(j for j in pack['schedule']['jobs'] if j['role']=='compression')
        disp[D['job_id']]={'execution':'invalid','cause':'UNSCORED invalid D'}
        packet,_=m.build_post_case('H-P',artifacts,disp,self.raw,self.fixture['raw_lock'],pack)
        self.assertEqual(sum(x['null_semantics'] for x in packet['expected_source_pairs']),12)
        review=m.fixture_review(packet)
        self.assertTrue(m.validate_review(packet,review,self.raw,self.fixture['raw_lock'])['valid'])
        index=next(i for i,x in enumerate(packet['expected_source_pairs']) if x['null_semantics'])
        review['source_pairs'][index][2]='uncertain'
        self.reject(packet,review,True)



    def test_63_actual_budget_separate_no_transfer(self):
        budget=m.read(m.R/m.BUDGET)
        starts=[{'event_kind':'native_spawn','study_id':'I12','phase':'preparation',
            'agent_handle':'UNSCORED-'+str(i),'native_call_id':'UNSCORED-call-'+str(i)} for i in range(6)]
        self.assertEqual(m.validate_budget(budget,starts)['preparation'],6)
        starts.append({'event_kind':'native_spawn','study_id':'I12','phase':'preparation',
            'agent_handle':'UNSCORED-extra','native_call_id':'UNSCORED-extra-call'})
        with self.assertRaises(ValueError):m.validate_budget(budget,starts)
        starts[-1]['phase']='completion_audit'
        self.assertEqual(m.validate_budget(budget,starts)['completion_audit'],1)
        starts.append({'event_kind':'native_spawn','study_id':'I12','phase':'completion_audit',
            'agent_handle':'UNSCORED-audit2','native_call_id':'UNSCORED-auditcall2'})
        with self.assertRaises(ValueError):m.validate_budget(budget,starts)

    def test_64_prompt_capacity_has_explicit_assigned_reviewer(self):
        for phase in ('raw','post'):
            text=m.capacity_prompt(phase,self.fixture)
            self.assertIn(self.fixture['capacity_assignments'][phase]['assigned_reviewer_id'],text)
            self.assertIn(m.CAPACITY[phase]['output_ref'],text)
            self.assertNotIn('Read only this prompt, '+str(m.R/m.FIXTURE_INPUTS),text)



    def test_65_factorial_interaction_uses_only_four_cells(self):
        cells={'OC':[0,0],'IC':[1,1],'OD':[2,2],'ID':[4,4],'GC':[100,100]}
        result=m.factorial_contrasts(cells)
        self.assertEqual(result['interaction'],[1,1])
        cells['GC']=[200,200]
        self.assertEqual(m.factorial_contrasts(cells)['interaction'],[1,1])
        cells['IC']=None
        self.assertIsNone(m.factorial_contrasts(cells)['interaction'])

    def test_66_metrics_unavailable_remains_null(self):
        post_lock={'raw_wrapper_sha256':m.canonical_hash(self.post),'core_lock':{'independent_review_complete':False,
            'rows':[{'table':t,'row_id':ob['row_id'],'identity':ob['identity'],
                'values':{**{k:copy.deepcopy(ob['identity'].get(k,ob['fixed_values'].get(k))) for k in self.post['core_packet']['contract']['columns'][t]},'evidence':'UNSCORED failed post review planned null row.'},
                'field_status':{k:'unobservable' for k in self.post['core_packet']['contract']['columns'][t] if k not in ob['identity'] and k not in ob['fixed_values'] and k!='evidence'}} for t,rows in self.post['core_packet']['expected_matrix'].items() for ob in rows]},
            'source_pairs':[{'row_id':ob['row_id']} for ob in self.post['expected_source_pairs']]}
        prior={(r['table'],r['row_id']):r for r in self.fixture['raw_lock']['core_lock']['rows']}
        post_lock['core_lock']['rows']=[copy.deepcopy(prior.get((r['table'],r['row_id']),r)) for r in post_lock['core_lock']['rows']]
        result=m.case_metrics(self.raw,self.fixture['raw_lock'],self.post,post_lock,
            self.fixture['raw_opaque_map'],self.fixture['post_opaque_map'],self.fixture['input_pack'],[])
        self.assertFalse(result['raw_comparison_evaluable'])
        self.assertIsNone(result['qualified_family_contrasts']['interaction'])
        self.assertEqual(result['denominators']['planned_G_D_roles'],19)
        self.assertEqual(result['denominators']['raw_cards'],27)
        self.assertEqual(result['shared_convergence_creation_credit'],0)


def run_tests():
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(MemoryTests)
    result=unittest.TextTestRunner(verbosity=1).run(suite)
    return {'valid':result.wasSuccessful(),'tests_run':result.testsRun,
        'failures':len(result.failures),'errors':len(result.errors),'filesystem_writes':0,'native_calls':0}


if __name__=='__main__':
    result=run_tests()
    print(json.dumps(result,sort_keys=True))
    raise SystemExit(0 if result['valid'] else 1)
