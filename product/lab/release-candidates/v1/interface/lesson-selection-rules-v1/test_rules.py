"""Synthetic pure rule checks; no live Session, owner review or public calls."""
import copy
from dataclasses import replace
from datetime import datetime, timezone
import unittest

from rules import *


class Scenario:
    def __init__(self):
        self.blobs = {}
        self.cut = {'store_ref': 'synthetic:store', 'branch_ref': 'synthetic:branch', 'commit_sequence': 1,
                    'commit_sha256': '1'*64, 'source_profile_sha256': '2'*64, 'streams': []}
        self.assignment = {'scope_ref': 'scope:store', 'identity_ref': 'assignment:synthetic',
            'version_ref': 'assignment:synthetic@1', 'carrier_ref': 'cal.artifact-type.agent-assignment/v1', 'byte_sha256': '3'*64}
        self.source = self.put('synthetic:source-code', b'print("original source")\n', raw=True)
        self.instructions = ('instruction:allow-controlled-use',)
        self.tags = ()
        self.veto = False
        self.project = 'scope:project'
        self.family = 'family:controlled'
        self.now = datetime(2026, 10, 11, 12, tzinfo=timezone.utc)
        self.lessons = []
        self.postures = [{'disposition': 'reviewed-for-controlled-use', 'effective_state': 'local-admitted-current', 'fixture_only': True}]
        self.statuses = ['candidate']
        self.retentions = ['synthetic:retention']

    def put(self, ref, value, *, raw=False):
        body = value if raw else encoded(value)
        self.blobs[ref] = body
        return binding(ref, body)

    def add(self, *, payload=None, rule=None, review=None, missing_review=False, missing_rule=False,
            missing_retention=False, exclusions=(False,), influence='influence:A'):
        index = str(len(self.lessons))
        evidence = self.put('synthetic:evidence:' + index, b'original evidence', raw=True)
        counter = self.put('synthetic:counterevidence:' + index, b'original counterevidence', raw=True)
        p = {'lesson_statement': 'Scoped advice only', 'scope_refs': ['scope:project'], 'applicability': 'family:controlled',
             'exclusions': ['Production operation'], 'predicted_benefit': 'Candidate benefit', 'falsifier': 'Candidate falsifier',
             'evidence_refs': [evidence['ref']], 'counterevidence_refs': [counter['ref']],
             'retention_policy_ref': 'synthetic:retention', 'expires_at': '2026-10-11T13:00:00Z',
             'classification_assignment_refs': [], 'status': 'candidate'}
        p.update(payload or {})
        body = {'schema_version': 'cyberalchemy-lab-operational-lesson/v1', 'node_id': 'lesson:synthetic:' + index,
                'kind': 'operational-lesson', 'name': 'Synthetic lesson', 'lifecycle_state': 'candidate', 'authority_effect': 'none',
                'owner_ref': 'synthetic:owner', 'scope_ref': 'scope:domain', 'evidence_refs': [evidence['ref']],
                'challenge_route': 'synthetic:challenge', 'successor_refs': [],
                'relation_refs': [{'relation_kind_ref': 'relation.derives-from', 'direction': 'source',
                                  'counterpart_kind': 'evidence-set', 'counterpart_ref': evidence['ref']}],
                'payload': p, 'claim_ceiling': 'Synthetic pure rule fixture only'}
        raw = encoded(body)
        artifact = {'scope_ref': 'scope:store', 'identity_ref': body['node_id'], 'version_ref': body['node_id'] + '@1',
                    'carrier_ref': 'cal.artifact-type.operational-lesson/v1', 'byte_sha256': sha(raw)}
        r = {'disposition': 'reviewed-for-controlled-use', 'effective_state': 'local-admitted-current', 'fixture_only': True}
        r.update(review or {})
        rb = self.put('synthetic:review:' + index, {'lesson': artifact, 'source_cut': self.cut,
                      'domain_scope_ref': 'scope:domain', **r, 'authority_effect': 'none'})
        reviewed = None if missing_review else ReviewFact(rb, **r)
        assessment = self.put('synthetic:counter-assessment:' + index, {'lesson': artifact, 'source_cut': self.cut,
                   'counterevidence_binding': counter, 'posture': 'limits-claim', 'authority_effect': 'none'})
        a = {'schema_version': 'lab-lesson-applicability/v1-candidate', 'lesson': artifact, 'source_cut': self.cut,
             'project_ref': 'scope:project', 'family': 'family:controlled', 'source_binding': self.source,
             'required_instruction_refs': ['instruction:allow-controlled-use'], 'excluded_tags': ['production'],
             'influence_ref': influence, 'counterevidence': [{'binding': counter, 'posture': 'limits-claim', 'assessment_binding': assessment}],
             'authority_effect': 'none'}
        a.update(rule or {})
        # Independently selected assessment originals track the synthetic test posture.
        for row in a['counterevidence']:
            if row['binding'] == counter:
                row['assessment_binding'] = self.put('synthetic:counter-assessment:' + index, {'lesson': artifact,
                    'source_cut': self.cut, 'counterevidence_binding': counter, 'posture': row['posture'], 'authority_effect': 'none'})
        ab = self.put('synthetic:rule:' + index, a)
        retention = self.put('synthetic:retention-witness:' + index, {'policy_ref': p['retention_policy_ref'],
                              'retain_project_evidence': True, 'exclude_session_memory': True, 'authority_effect': 'none'})
        fact = LessonFact(artifact, raw, 'scope:domain', True, reviewed, None if missing_rule else ab,
                          None if missing_retention else retention, tuple(zip(p['exclusions'], exclusions)), (evidence,), (counter,))
        self.lessons.append(fact)
        return fact

    def build(self):
        session = self.put('synthetic:session-witness', {'session_ref': 'synthetic:session', 'assignment': self.assignment,
                           'source_cut': self.cut, 'authority_effect': 'none'})
        inventory = self.put('synthetic:inventory', {'source_cut': self.cut, 'lessons': [f.artifact for f in self.lessons],
                             'complete': True, 'authority_effect': 'none'})
        context = self.put('synthetic:context', {'session_ref': 'synthetic:session', 'assignment': self.assignment,
            'source_cut': self.cut, 'project_ref': self.project, 'family': self.family, 'source_binding': self.source,
            'tags': list(self.tags), 'authority_effect': 'none'})
        instruction = self.put('synthetic:instruction', {'session_ref': 'synthetic:session', 'assignment': self.assignment,
            'source_cut': self.cut, 'instruction_refs': list(self.instructions), 'veto_lesson_influence': self.veto, 'authority_effect': 'none'})
        profile = self.put('synthetic:profile', {'schema_version': 'lab-lesson-selection-domain/v1-candidate',
            'scope_ref': self.project, 'source_cut': self.cut, 'context_basis_binding': context,
            'selection_method_binding': binding('lesson-selection-rules-v1/rules.py', (HERE/'rules.py').read_bytes()),
            'supported_lesson_statuses': self.statuses, 'supported_retention_policy_refs': self.retentions,
            'reviewed_use_postures': self.postures, 'authority_effect': 'none', 'actual_owner_outcome': None})
        routing = {'schema_version': 'lab-lesson-selection-routing/v1-candidate', 'source_cut': self.cut,
            'assignment': self.assignment, 'session_binding': session, 'instruction_precedence_binding': instruction,
            'inventory_binding': inventory, 'domain_profile_binding': profile,
            'lessons': [{'lesson': f.artifact, 'review_binding': None if f.review is None else f.review.original_binding,
                         'applicability_rule_binding': f.rule_binding} for f in self.lessons],
            'authority_effect': 'none', 'actual_owner_outcome': None}
        facts = ContextFacts('synthetic:selection', 'synthetic:session', self.assignment, self.cut, self.project, self.family,
            self.source, self.instructions, self.tags, self.veto, self.now, session, inventory, context, instruction, tuple(self.lessons))
        return routing, facts

    def read(self, selected):
        return self.blobs[selected['ref']]


class RuleChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules = Rules()

    def setUp(self):
        self.s = Scenario()

    def evaluate(self):
        route, facts = self.s.build()
        return self.rules.select(encoded(route), facts, self.s.read)

    def reason(self, **changes):
        self.s.add(**changes)
        return self.evaluate().result['items'][0]['reason']

    def bad(self, route, facts, read=None):
        with self.assertRaises(SelectionFault):
            self.rules.select(encoded(route), facts, read or self.s.read)

    def test_selected_exact_nonempty(self):
        self.s.add(); row = self.evaluate().result['items'][0]
        self.assertEqual(row['posture'], 'selected'); self.assertFalse(row['expired'])

    def test_empty_complete_inventory(self):
        self.assertEqual(self.evaluate().result['items'], [])

    def test_missing_review_is_blocked(self):
        self.assertEqual(self.reason(missing_review=True), 'exact-durable-review-absent')

    def test_missing_rule_is_blocked(self):
        self.assertEqual(self.reason(missing_rule=True), 'applicability-rule-unresolved')

    def test_unsupported_status(self):
        self.assertEqual(self.reason(payload={'status': 'unreviewed'}), 'unsupported-status-or-retention-policy')

    def test_unsupported_retention(self):
        self.assertEqual(self.reason(payload={'retention_policy_ref': 'other'}), 'unsupported-status-or-retention-policy')

    def test_missing_retention_witness(self):
        self.assertEqual(self.reason(missing_retention=True), 'retention-witness-unresolved')

    def test_expired(self):
        self.assertEqual(self.reason(payload={'expires_at': '2026-10-11T11:00:00Z'}), 'expired')

    def test_expiry_boundary(self):
        self.s.add(payload={'expires_at': '2026-10-11T12:00:00Z'})
        row = self.evaluate().result['items'][0]
        self.assertEqual(row['posture'], 'omitted'); self.assertTrue(row['expired'])

    def test_unresolved_expiry(self):
        self.assertEqual(self.reason(payload={'expires_at': 'owner-defined'}), 'expiry-unresolved')

    def test_naive_expiry(self):
        self.assertEqual(self.reason(payload={'expires_at': '2026-10-11T13:00:00'}), 'expiry-unresolved')

    def test_other_project(self):
        self.assertEqual(self.reason(payload={'scope_refs': ['other']}), 'project-scope-excluded')

    def test_other_family(self):
        self.assertEqual(self.reason(payload={'applicability': 'other'}), 'family-excluded')

    def test_rule_family(self):
        self.assertEqual(self.reason(rule={'family': 'other'}), 'family-excluded')

    def test_other_source(self):
        self.assertEqual(self.reason(rule={'source_binding': {'ref': 'other', 'sha256': '0'*64}}), 'source-version-excluded')

    def test_literal_exclusion(self):
        self.assertEqual(self.reason(exclusions=(True,)), 'explicit-exclusion')

    def test_unresolved_literal_exclusion(self):
        self.assertEqual(self.reason(exclusions=(None,)), 'literal-exclusion-unresolved')

    def test_tag_exclusion(self):
        self.s.tags = ('production',)
        self.assertEqual(self.reason(), 'explicit-exclusion')

    def test_required_instruction(self):
        self.s.instructions = ()
        self.assertEqual(self.reason(), 'current-instruction-precedence')

    def test_veto(self):
        self.s.veto = True
        self.assertEqual(self.reason(), 'current-instruction-precedence')

    def test_original_leave_source_instruction(self):
        self.s.instructions += ('leave-source-unchanged',)
        self.assertEqual(self.reason(), 'current-instruction-precedence')

    def counter_posture(self, posture):
        counter = self.s.put('synthetic:counterevidence:0', b'original counterevidence', raw=True)
        return self.reason(rule={'counterevidence': [{'binding': counter, 'posture': posture,
                                                     'assessment_binding': {'ref': 'placeholder', 'sha256': '0'*64}}]})

    def test_limiting_counterevidence(self):
        self.assertEqual(self.counter_posture('limits-claim'), 'exact-reviewed-current-applicable')

    def test_contradicting_counterevidence(self):
        self.assertEqual(self.counter_posture('contradicts-use'), 'counterevidence-contradicts-use')

    def test_unresolved_counterevidence(self):
        self.assertEqual(self.counter_posture('unresolved'), 'counterevidence-unresolved')

    def test_missing_counterevidence_coverage(self):
        self.s.add(rule={'counterevidence': []}); route, facts = self.s.build(); self.bad(route, facts)

    def test_conflicting_influences_block_both(self):
        self.s.add(); self.s.add(influence='influence:B')
        rows = self.evaluate().result['items']
        self.assertEqual([r['posture'] for r in rows], ['blocked', 'blocked'])
        self.assertEqual(rows[0]['conflict_refs'], [rows[1]['lesson']])

    def test_equal_influences_do_not_conflict(self):
        self.s.add(); self.s.add()
        self.assertEqual([r['posture'] for r in self.evaluate().result['items']], ['selected', 'selected'])

    def test_expired_influence_does_not_block_eligible(self):
        self.s.add(); self.s.add(influence='influence:B', payload={'expires_at': '2026-10-11T11:00:00Z'})
        self.assertEqual([r['posture'] for r in self.evaluate().result['items']], ['selected', 'omitted'])

    def test_three_way_conflicts(self):
        for ref in ('A', 'B', 'C'): self.s.add(influence=ref)
        self.assertTrue(all(len(r['conflict_refs']) == 2 for r in self.evaluate().result['items']))

    def test_duplicate_inventory(self):
        f = self.s.add(); self.s.lessons.append(f); route, facts = self.s.build(); self.bad(route, facts)

    def test_missing_route_cannot_fake_empty(self):
        self.s.add(); route, facts = self.s.build(); route['lessons'] = []; self.bad(route, facts)

    def test_extra_route(self):
        self.s.add(); route, facts = self.s.build(); route['lessons'].append(route['lessons'][0]); self.bad(route, facts)

    def test_noncurrent_inventory(self):
        f = self.s.add(); self.s.lessons[0] = replace(f, current=False)
        route, facts = self.s.build(); self.bad(route, facts)

    def test_lesson_digest(self):
        f = self.s.add(); self.s.lessons[0] = replace(f, original=f.original + b' ')
        route, facts = self.s.build(); self.bad(route, facts)

    def test_original_body_identity(self):
        f = self.s.add(); body = parse(f.original); body['node_id'] = 'different'
        raw = encoded(body); self.s.lessons[0] = replace(f, original=raw, artifact={**f.artifact, 'byte_sha256': sha(raw)})
        route, facts = self.s.build(); self.bad(route, facts)

    def test_review_original_changed(self):
        f = self.s.add(); route, facts = self.s.build(); self.s.blobs[f.review.original_binding['ref']] += b' '
        self.bad(route, facts)

    def test_review_original_disposition_join(self):
        f = self.s.add(); self.s.lessons[0] = replace(f, review=replace(f.review, disposition='invented'))
        route, facts = self.s.build(); self.bad(route, facts)

    def test_fixture_authority_not_inferred(self):
        self.assertEqual(self.reason(review={'fixture_only': False}), 'unsupported-reviewed-use-posture')

    def test_declared_general_status_retention_profile(self):
        self.s.statuses = ['active-advice']; self.s.retentions = ['synthetic:other-retention']
        self.assertEqual(self.reason(payload={'status': 'active-advice', 'retention_policy_ref': 'synthetic:other-retention'}), 'exact-reviewed-current-applicable')

    def test_declared_general_review_profile(self):
        self.s.postures = [{'disposition': 'reviewed-for-scoped-use', 'effective_state': 'admitted-current', 'fixture_only': False}]
        self.assertEqual(self.reason(review=self.s.postures[0]), 'exact-reviewed-current-applicable')

    def test_historical_review(self):
        self.assertEqual(self.reason(review={'effective_state': 'local-admitted-historical'}), 'unsupported-reviewed-use-posture')

    def test_scope_source_cut_change(self):
        self.s.add(); route, facts = self.s.build(); route['source_cut'] = {**self.s.cut, 'commit_sequence': 2}; self.bad(route, facts)

    def test_foreign_session(self):
        self.s.add(); route, facts = self.s.build(); self.bad(route, replace(facts, session_ref='other'))

    def test_foreign_assignment(self):
        self.s.add(); route, facts = self.s.build(); self.bad(route, replace(facts, assignment={**facts.assignment, 'version_ref': 'other'}))

    def test_method_identity(self):
        self.s.add(); route, facts = self.s.build(); value = parse(self.s.blobs['synthetic:profile'])
        value['selection_method_binding']['sha256'] = '0'*64
        route['domain_profile_binding'] = self.s.put('synthetic:profile', value); self.bad(route, facts)

    def test_independent_inventory_complete(self):
        self.s.add(); route, facts = self.s.build(); value = parse(self.s.blobs['synthetic:inventory']); value['complete'] = False
        b = self.s.put('synthetic:inventory', value); route['inventory_binding'] = b; self.bad(route, replace(facts, inventory_binding=b))

    def test_evidence_closure(self):
        f = self.s.add(); self.s.lessons[0] = replace(f, evidence_bindings=())
        route, facts = self.s.build(); self.bad(route, facts)

    def test_missing_original_witness(self):
        f = self.s.add(); route, facts = self.s.build(); del self.s.blobs[f.counterevidence_bindings[0]['ref']]
        self.bad(route, facts)

    def test_duplicate_json(self):
        with self.assertRaises(SelectionFault): parse(b'{"a":1,"a":2}')

    def test_nonfinite_json(self):
        with self.assertRaises(SelectionFault): parse(b'{"a":NaN}')

    def test_input_bound(self):
        with self.assertRaises(SelectionFault): parse(b' ' * (MAX_BYTES+1))

    def test_no_naive_host_clock(self):
        self.s.add(); route, facts = self.s.build(); self.bad(route, replace(facts, now=datetime(2026,10,11)))

    def test_literal_exclusion_coverage(self):
        f = self.s.add(); self.s.lessons[0] = replace(f, exclusions=())
        route, facts = self.s.build(); self.bad(route, facts)

    def test_retention_not_session_memory(self):
        f = self.s.add(); route, facts = self.s.build(); policy = parse(self.s.blobs[f.retention_binding['ref']])
        policy['exclude_session_memory'] = False
        b = self.s.put(f.retention_binding['ref'], policy)
        self.bad(route, replace(facts, lessons=(replace(f, retention_binding=b),)))

    def test_invalid_original_carrier_schema(self):
        f = self.s.add(); body = parse(f.original); del body['payload']['falsifier']; raw = encoded(body)
        self.s.lessons[0] = replace(f, original=raw, artifact={**f.artifact, 'byte_sha256': sha(raw)})
        route, facts = self.s.build(); self.bad(route, facts)

    def test_output_is_bound_and_has_zero_application(self):
        self.s.add(); before = copy.deepcopy(self.s.blobs); out = self.evaluate()
        self.assertEqual(out.applications_created, 0); self.assertEqual(out.authority_effect, 'none')
        for b, raw in out.checks:
            self.assertEqual(sha(raw), b['sha256']); self.assertEqual(parse(raw)['applications_created'], 0)
        # Only fixture build adds the independently supplied context witness bytes.
        for key, raw in before.items(): self.assertEqual(self.s.blobs[key], raw)


if __name__ == '__main__':
    unittest.main(verbosity=2)
