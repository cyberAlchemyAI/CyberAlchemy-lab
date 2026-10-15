"""W05 declared guards. Reuse immutable actual observations; new Session per assessment."""
import copy
from dataclasses import replace
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from failures.episode import *
from evaluator import BoundaryFault


class ServicesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline_temp = tempfile.TemporaryDirectory(prefix='cal-W05-observation-source-')
        cls.baseline, _, cls.refs, cls.contest = prepare_episode(Path(cls.baseline_temp.name)/'episode', finish=False)
        cls.baseline.host.session.close()

    @classmethod
    def tearDownClass(cls):
        cls.baseline_temp.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='cal-W05-guard-')
        self.e = EvidenceService(Path(self.temp.name)/'episode', host_fixture())
        # Historical original observations survive the observing Agent. Current permission is fresh.
        for p in self.baseline.output.iterdir():
            if p.is_file():
                shutil.copyfile(p, self.e.output/p.name)
        self.e.records = {r: (self.e.output/p.name, h) for r, (p, h) in self.baseline.records.items()}
        self.e.record_roles = dict(self.baseline.record_roles)
        self.e.blobs = {r: (self.e.output/p.name, h) for r, (p, h) in self.baseline.blobs.items()}
        self.e.manifest_ref, self.e.subject_ref, self.e.action_ref = self.baseline.manifest_ref, self.baseline.subject_ref, self.baseline.action_ref
        self.f = self.e.host
        self.r = dict(self.refs)
        self.failure = FailureService(self.e)
        self.f.fixture_gate = None
        self.c = ChallengeService(self.e, self.r['challenge_contract'], gate_reader=lambda: self.f.fixture_gate)
        self.c.current_ref = self.contest.current_ref
        self.c.state = 'eligible'

    def tearDown(self):
        self.f.session.close()
        self.temp.cleanup()

    def bad(self, function, *args, **kwargs):
        with self.assertRaises(BoundaryFault):
            function(*args, **kwargs)

    def altered(self, key, field, value):
        v = self.e.get(self.r[key]); v['payload'][field] = value
        v['node_id'] += '-negative-fixture'
        return self.e.put(v)

    def ready_resolution(self):
        self.c.respond('evidence', [self.r['evidence']])
        return declarations(self.e, self.c)

    def assignment(self, scheme=None, value=None, subject=None):
        return self.failure.classify('guard-assignment', subject or self.r['occurrence'], scheme or self.r['scheme'],
            value or self.r['value'], self.r['action'], self.r['observation'], self.r['evidence'], self.r['failure_adapter'])

    def test_actual_observation_and_recovery(self):
        m = parse(self.e.original(self.e.manifest_ref))
        self.assertEqual(m['failed_preparations'], 1)
        self.assertEqual(m['observations'][1]['result']['validated_records'], 13)
        self.assertTrue(m['subject_bytes_unchanged'])

    def test_independent_axes_and_open_cause(self):
        p = self.e.get(self.r['assessment'])['payload']
        self.assertEqual(p['impact_posture'], 'bounded-controlled-preparation')
        self.assertEqual(p['recovery_posture'], 'successor-verified-old-revision-unresolved')
        self.assertEqual(self.e.get(self.r['cause'])['payload']['disposition'], 'open')
        self.assertEqual(self.e.get(self.r['control'])['payload']['effectiveness_evidence_refs'], [])

    def test_mode_not_occurrence(self):
        self.bad(self.failure.assess, 'bad', self.r['mode'], self.r['assignment'], [self.r['cause']])

    def test_cause_not_fact(self):
        self.bad(self.failure.assess, 'bad', self.r['occurrence'], self.r['assignment'], [self.r['cause']], cause_posture='confirmed')

    def test_no_unsupported_impact(self):
        self.bad(self.failure.assess, 'bad', self.r['occurrence'], self.r['assignment'], [self.r['cause']], impact='production-outage')

    def test_no_silent_same_revision_repair(self):
        self.bad(self.failure.assess, 'bad', self.r['occurrence'], self.r['assignment'], [self.r['cause']], recovery='old-revision-fixed')

    def test_wrong_assessment_assignment_subject(self):
        x = self.altered('assignment', 'subject_version_ref', self.r['historical'])
        self.bad(self.failure.assess, 'bad', self.r['occurrence'], x, [self.r['cause']])

    def test_wrong_scheme_value(self):
        value = self.altered('value', 'scheme_ref', 'classification-scheme:unselected@1')
        self.bad(self.assignment, value=value)

    def test_wrong_axis(self):
        value = self.altered('value', 'axis_ref', 'axis:authority')
        self.bad(self.assignment, value=value)

    def test_cardinality_survives_reconstruction(self):
        self.bad(self.assignment)

    def test_assignment_cannot_admit_itself(self):
        x = self.e.get(self.r['assignment']); x['node_id'] += '-bad'; x['authority_effect'] = 'admit'
        self.bad(self.e.put, x)

    def test_production_policy_negative_valid(self):
        incident, disposition = self.failure.incident('negative', self.r['occurrence'], self.r['assessment'], 'protocol:W05-production-threshold@1')
        self.assertIsNone(incident); self.assertFalse(disposition['eligible']); self.assertTrue(disposition['threshold_met'])

    def test_controlled_incident_retains_scope(self):
        x = self.e.get(self.r['incident'])
        self.assertIn('Controlled Incident', x['payload']['impact_summary'])
        self.assertIn('no production', x['payload']['impact_summary'])

    def test_controlled_cannot_be_production(self):
        self.bad(self.failure.incident, 'bad', self.r['occurrence'], self.r['assessment'], 'protocol:W05-controlled-threshold@1', production=True)

    def test_unselected_incident_policy(self):
        self.bad(self.failure.incident, 'bad', self.r['occurrence'], self.r['assessment'], 'policy:caller-body')

    def test_original_observation_chain_drift(self):
        p, h = self.e.blobs[self.e.manifest_ref]; p.write_bytes(p.read_bytes()+b' ')
        self.bad(self.e.original, self.e.manifest_ref)

    def test_original_subject_revision_drift(self):
        p, h = self.e.records[self.r['historical']]; p.write_bytes(p.read_bytes()+b' ')
        self.bad(self.e.get, self.r['historical'])

    def test_challenge_wrong_subject_revision(self):
        self.c.state = 'not-submitted'
        self.bad(self.c.submit, self.r['successor'], self.f.ref('principal'), 'schema-contract-conflict', [self.r['evidence']])

    def test_challenger_must_be_current_principal(self):
        self.c.state = 'not-submitted'
        self.bad(self.c.submit, self.r['historical'], 'principal:caller@1', 'schema-contract-conflict', [self.r['evidence']])

    def test_ground_must_be_declared(self):
        self.c.state = 'not-submitted'
        self.bad(self.c.submit, self.r['historical'], self.f.ref('principal'), 'invented-ground', [self.r['evidence']])

    def test_required_evidence_not_optional(self):
        self.c.state = 'not-submitted'
        self.bad(self.c.submit, self.r['historical'], self.f.ref('principal'), 'schema-contract-conflict', [])

    def test_unrelated_valid_evidence_rejected(self):
        self.c.state = 'not-submitted'
        unrelated = self.altered('evidence', 'source_refs', ['protocol:unrelated'])
        self.bad(self.c.submit, self.r['historical'], self.f.ref('principal'), 'schema-contract-conflict', [unrelated])

    def test_response_mode_closed(self):
        self.bad(self.c.respond, 'automatic-admit', [self.r['evidence']])

    def test_response_window(self):
        self.f.now[0] += 301
        self.bad(self.c.respond, 'evidence', [self.r['evidence']])

    def test_response_without_eligibility(self):
        self.c.state = 'submitted'
        self.bad(self.c.respond, 'evidence', [self.r['evidence']])

    def test_resolution_requires_response(self):
        self.bad(self.c.resolve, 'decision:missing@1', 'effect:missing@1', 'decision-scope:missing@1')

    def test_candidate_declarations_not_host_gate(self):
        d, ef, s = self.ready_resolution(); self.f.fixture_gate = None
        self.bad(self.c.resolve, d, ef, s)

    def test_dict_cannot_supply_gate(self):
        d, ef, s = self.ready_resolution(); self.f.fixture_gate = {'approved': True}
        self.bad(self.c.resolve, d, ef, s)

    def test_expired_gate(self):
        d, ef, s = self.ready_resolution()
        self.f.fixture_gate = replace(self.f.fixture_gate, expires_at=self.f.now[0]-1)
        self.bad(self.c.resolve, d, ef, s)

    def test_gate_wrong_scope_session_and_cut(self):
        d, ef, s = self.ready_resolution(); original = self.f.fixture_gate
        for k, v in [('scope_ref', 'project:elsewhere'), ('session_handle', 'protocol:old-session'), ('head', 'protocol:stale-cut')]:
            with self.subTest(field=k):
                self.f.fixture_gate = replace(original, **{k: v}); self.bad(self.c.resolve, d, ef, s)

    def test_gate_wrong_original_hash(self):
        d, ef, s = self.ready_resolution()
        self.f.fixture_gate = replace(self.f.fixture_gate, decision_sha256='0'*64)
        self.bad(self.c.resolve, d, ef, s)

    def test_gate_original_evidence_drift(self):
        d, ef, s = self.ready_resolution()
        self.f.fixture_gate = replace(self.f.fixture_gate, original=self.f.fixture_gate.original+b' ')
        self.bad(self.c.resolve, d, ef, s)

    def test_decision_outcome_not_owner_admission(self):
        d, ef, s = self.ready_resolution()
        v = self.e.get(d); v['node_id'] += '-bad'; v['payload']['selected_outcome'] = 'admit'
        self.bad(self.c.resolve, self.e.put(v), ef, s)

    def test_effect_cannot_mutate_challenged_subject(self):
        d, ef, s = self.ready_resolution()
        v = self.e.get(ef); v['node_id'] += '-bad'; v['payload']['subject_ref'] = self.r['historical']
        self.bad(self.c.resolve, d, self.e.put(v), s)

    def test_scope_cannot_add_admission(self):
        d, ef, s = self.ready_resolution()
        v = self.e.get(s); v['node_id'] += '-bad'; v['payload']['permitted_effects'].append('canonical-admission')
        self.bad(self.c.resolve, d, ef, self.e.put(v))

    def test_resolution_preserves_subject_and_observations(self):
        d, ef, s = self.ready_resolution(); pin = self.e.records[self.r['historical']][1]
        result = self.c.resolve(d, ef, s)
        self.assertEqual(self.c.state, 'resolved')
        self.assertEqual(self.e.records[self.r['historical']][1], pin)
        self.assertEqual(self.e.get(result)['payload']['resolution_decision_ref'], d)
        self.assertEqual(self.e.get(self.r['challenge_submitted'])['payload']['response_state'], 'submitted')

    def test_repeated_resolution_denied(self):
        d, ef, s = self.ready_resolution(); self.c.resolve(d, ef, s)
        self.bad(self.c.resolve, d, ef, s)

    def test_current_revocation_before_response(self):
        self.f.status['revoked_refs'].append(self.f.ref('delegation'))
        self.bad(self.c.respond, 'evidence', [self.r['evidence']])

    def test_current_revocation_before_resolution(self):
        d, ef, s = self.ready_resolution()
        self.f.status['revoked_refs'].append(self.f.ref('delegation'))
        self.bad(self.c.resolve, d, ef, s)

    def test_profile_must_allow_every_output_kind(self):
        self.f.by_kind['agent-profile']['payload']['allowed_output_kinds'].remove('incident')
        self.f.reselect('agent-profile'); self.bad(self.e.check)

    def test_no_host_grant(self):
        self.f.grant = None; self.bad(self.e.check)

    def test_source_pin_rechecked(self):
        self.e.sources[OLD_BUILDER] = '0'*64; self.bad(self.e.check)

    def test_unknown_relation_signature_and_qualifier(self):
        self.bad(self.e.edge, 'bad', 'relation.imagined', self.r['mode'], self.r['occurrence'], {})
        self.bad(self.e.edge, 'bad2', 'relation.affects', self.r['occurrence'], self.r['historical'],
            {'impact_scope': 'controlled', 'evidence_posture': 'observed', 'authority': 'admit'})

    def test_pending_probe_never_redispatches(self):
        self.bad(self.e.observe)

    def test_synthetic_timeout_keeps_partial_original_bytes(self):
        fresh = EvidenceService(Path(self.temp.name)/'timeout', host_fixture())
        try:
            with patch('evidence.service.subprocess.run', side_effect=subprocess.TimeoutExpired('synthetic-fixture', 20, output=b'partial', stderr=b'diagnostic')):
                with self.assertRaises(subprocess.TimeoutExpired): fresh.observe()
            self.assertEqual((fresh.output/'historical-timeout-stdout.log').read_bytes(), b'partial')
            self.assertIsNone(fresh.manifest_ref)
            self.bad(fresh.observe)
        finally:
            fresh.host.session.close()

    def test_session_end_erases_memory_and_blocks_work(self):
        self.f.session.note('short-lived test note'); self.f.session.close()
        self.assertEqual(self.f.session._memory, [])
        self.bad(self.e.check)

    def test_cold_fresh_process_original_reconstruction(self):
        d, ef, s = self.ready_resolution()
        self.r.update(decision=d, effect=ef, decision_scope=s, challenge_resolved=self.c.resolve(d, ef, s))
        p = finalize(self.e, self.r, self.c)
        result = subprocess.run([sys.executable, str(Path(__file__).with_name('episode.py')), '--cold', str(p), byte_sha(p.read_bytes())], capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assertFalse(parse(result.stdout)['retry_dispatched'])
        self.assertIsNone(parse(result.stdout)['actual_owner_outcome'])

    def test_cold_independent_pin_required(self):
        self.bad(cold_verify, self.e.output/'observation-manifest.json', '0'*64)


if __name__ == '__main__':
    unittest.main()
