"""W06 negative guards. Unit review/process fixtures are explicitly synthetic.

The separate integration episode supplies the real signature, replay, context
and process evidence; these unit fixtures claim none of those observations.
"""
import copy
from dataclasses import replace
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from application import *
from evaluator import BoundaryFault


class LearningTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='cal-W06-unit-')
        self.e = CandidateSources(Path(self.temp.name)/'unit',host_fixture())
        self.reviews = {}
        self.s = LessonService(self.e,review_reader=lambda r:self.reviews.get(r))
        self.reflection, self.lesson = self.s.draft()
        self.review(self.lesson)
        f = self.e.host
        self.context = CaseContext(f.session.session_ref,SCOPE,'protocol:unit-only',FAMILY,self.e.sources[OLD],
            frozenset({'allow-controlled-source-repair'}),frozenset(),f.status['head'],'protocol:unit-context','protocol:unit-ontology')
        self.app = LessonApplicationService(self.s)

    def tearDown(self):
        self.e.host.session.close();self.temp.cleanup()

    def review(self, ref, **changes):
        value = ReviewedLesson(ref,self.e.records[ref][1],'reviewed-for-controlled-use',self.e.host.status['head'],
            self.e.scope,'protocol:pending-unit-review','local-admitted-current',True)
        value = replace(value,**changes)
        original = encoded({'lesson_ref':value.revision_ref,'lesson_sha256':value.original_sha256,'source_head':value.source_head,
            'scope_ref':value.scope_ref,'disposition':value.disposition,'fixture_only':value.fixture_only,'synthetic_unit_fixture':True})
        token = self.e.blob('unit-review-'+str(len(self.e.blobs))+'.json',original)
        self.reviews[ref] = replace(value,review_original_ref=token)
        return self.reviews[ref]

    def clone(self, **payload):
        value = self.e.get(self.lesson);value['node_id'] += '-unit-'+str(len(self.e.records));value['payload'].update(payload)
        ref = self.e.put(value);self.s.register_rule(ref,self.s.rules[self.lesson]);self.review(ref)
        return ref

    def select(self, ref=None, context=None):
        return self.s.select([ref or self.lesson],context or self.context)

    def reason(self, ref=None, context=None):
        selection = self.select(ref,context)
        return parse(self.e.original(selection.original_ref))['rows'][0]['reason']

    def bad(self, fn, *args, **kwargs):
        with self.assertRaises(BoundaryFault): fn(*args,**kwargs)

    def process(self, posture='completed', count=13, returncode=0):
        return SimpleNamespace(returncode=returncode,stdout=encoded({'controlled':True,
            'source_sha256':byte_sha(repaired_source(OLD.read_bytes())),'preparation_posture':posture,'validated_records':count}),stderr=b'')

    def apply_fixture(self, posture='completed', count=13):
        selected = self.select()
        with patch('application.subprocess.run',return_value=self.process(posture,count)):
            self.app.apply(selected,self.lesson)

    def test_draft_exact_observed_basis(self):
        p = self.e.get(self.lesson)['payload']
        self.assertIn(self.e.W05_refs['assessment'],p['evidence_refs']);self.assertTrue(p['counterevidence_refs'])
        self.assertEqual(p['retention_policy_ref'],RETENTION);self.assertEqual(p['status'],'candidate')

    def test_session_note_cannot_be_lesson(self):
        self.e.host.session.note('temporary unit thought')
        self.bad(self.s.select,['temporary unit thought'],self.context)
        self.assertNotIn(b'temporary unit thought',encoded(self.e.get(self.lesson)))

    def test_selection_is_not_application(self):
        result = self.select();self.assertEqual(result.selected_refs,(self.lesson,))
        self.assertEqual(parse(self.e.original(result.original_ref))['applications_created'],0)
        self.assertFalse(any(self.e.get(r)['kind']=='lesson-application' for r in self.e.records))

    def test_absent_review_excluded(self):
        self.reviews.clear();self.assertEqual(self.reason(),'exact-durable-review-absent-or-changed')

    def test_wrong_original_sha_excluded(self):
        self.review(self.lesson,original_sha256='0'*64);self.assertEqual(self.reason(),'exact-durable-review-absent-or-changed')

    def test_wrong_review_revision_excluded(self):
        self.review(self.lesson,revision_ref='operational-lesson:other@1');self.assertEqual(self.reason(),'exact-durable-review-absent-or-changed')

    def test_unreviewed_disposition_excluded(self):
        self.review(self.lesson,disposition='draft');self.assertEqual(self.reason(),'only-current-exact-owned-fixture-review-supported')

    def test_historical_review_excluded(self):
        self.review(self.lesson,effective_state='local-admitted-historical');self.assertEqual(self.reason(),'only-current-exact-owned-fixture-review-supported')

    def test_nonfixture_authority_not_inferred(self):
        self.review(self.lesson,fixture_only=False);self.assertEqual(self.reason(),'only-current-exact-owned-fixture-review-supported')

    def test_review_scope_cut_excluded(self):
        self.review(self.lesson,scope_ref='scope:other');self.assertEqual(self.reason(),'review-current-cut-or-scope-differs')
        self.review(self.lesson,source_head='cut:other');self.assertEqual(self.reason(),'review-current-cut-or-scope-differs')

    def test_review_original_bytes_cannot_be_token(self):
        self.reviews[self.lesson] = replace(self.reviews[self.lesson],review_original_ref='protocol:invented')
        self.bad(self.select)

    def test_review_original_poison_blocked(self):
        p,_ = self.e.blobs[self.reviews[self.lesson].review_original_ref];p.write_bytes(b'{}\n')
        self.bad(self.select)

    def test_expired_lesson_excluded(self):
        ref = self.clone(expires_at=utc(self.e.host.now[0]-1));self.assertEqual(self.reason(ref),'expired')

    def test_unknown_expiry_excluded(self):
        ref = self.clone(expires_at='owner-defined');self.assertEqual(self.reason(ref),'expiry-unresolved')

    def test_timezone_missing_excluded(self):
        ref = self.clone(expires_at='2026-10-08T12:00:00');self.assertEqual(self.reason(ref),'expiry-unresolved')

    def test_wrong_retention_excluded(self):
        self.assertEqual(self.reason(self.clone(retention_policy_ref='protocol:unknown')),'unsupported-status-or-retention-policy')

    def test_family_excluded(self):
        self.assertEqual(self.reason(context=replace(self.context,family='other')),'family-excluded')

    def test_source_version_excluded(self):
        self.assertEqual(self.reason(context=replace(self.context,source_sha256='0'*64)),'source-version-excluded')

    def test_explicit_exclusion(self):
        self.assertEqual(self.reason(context=replace(self.context,tags=frozenset({'production'}))),'explicit-exclusion')

    def test_instruction_precedes_lesson(self):
        for instructions in [frozenset(),frozenset({'allow-controlled-source-repair','leave-source-unchanged'})]:
            self.assertEqual(self.reason(context=replace(self.context,instruction_effects=instructions)),'current-instruction-precedence')

    def test_contradictory_counterevidence_excluded(self):
        self.s.rules[self.lesson]=replace(self.s.rules[self.lesson],counterevidence_posture='contradicts-this-repair')
        self.assertEqual(self.reason(),'counterevidence-contradicts-use')

    def test_unknown_counterevidence_excluded(self):
        self.s.rules[self.lesson]=replace(self.s.rules[self.lesson],counterevidence_posture='unknown')
        self.assertEqual(self.reason(),'counterevidence-unresolved')

    def test_conflicting_lessons_visible_and_blocked(self):
        other = self.clone();self.s.rules[other]=replace(self.s.rules[other],effect='incompatible-transform')
        selection = self.s.select([self.lesson,other],self.context)
        self.assertEqual(selection.selected_refs,());self.assertEqual(selection.conflicts,((self.lesson,other),))
        rows = parse(self.e.original(selection.original_ref))['rows'];self.assertTrue(all(r['disposition']=='blocked-conflict' for r in rows))
        self.bad(self.app.apply,selection,self.lesson)

    def test_project_session_cut_mismatch_blocked(self):
        for kw in [{'project_ref':'project:other'},{'session_ref':'session:other'},{'source_head':'cut:other'}]:
            self.bad(self.select,context=replace(self.context,**kw))

    def test_duplicate_lesson_selection_blocked(self):
        self.bad(self.s.select,[self.lesson,self.lesson],self.context)

    def test_selection_cannot_be_forged(self):
        forged = Selection('protocol:invented',(self.lesson,),(),self.context)
        self.bad(self.app.apply,forged,self.lesson)

    def test_rule_changed_after_selection_blocked(self):
        selected = self.select();self.s.rules[self.lesson]=replace(self.s.rules[self.lesson],effect='new')
        self.bad(self.app.apply,selected,self.lesson)

    def test_review_revoked_before_application_blocked(self):
        selected = self.select();self.reviews.clear();self.bad(self.app.apply,selected,self.lesson)

    def test_host_revoked_before_application_blocked(self):
        selected = self.select();self.e.host.grant=None;self.bad(self.app.apply,selected,self.lesson)

    def test_profile_output_permission_required(self):
        self.e.host.by_kind['agent-profile']['payload']['allowed_output_kinds']=['agent-action']
        self.e.host.reselect('agent-profile');self.bad(self.select)

    def test_tool_contract_current(self):
        self.e.host.by_kind['tool']['payload']['input_contract_ref']='protocol:other';self.e.host.reselect('tool')
        self.bad(self.select)

    def test_closed_output_kinds(self):
        self.bad(self.e.put,self.e.get(self.e.W05_refs['assessment']))

    def test_original_record_poison(self):
        p,_ = self.e.records[self.lesson];p.write_bytes(b'{}\n');self.bad(self.select)

    def test_original_blob_budget_and_path(self):
        self.bad(self.e.blob,'../escape',b'x');self.bad(self.e.blob,'oversized',b'x'*(self.e.host.grant.max_output_bytes+1))

    def test_expiry_rechecked_before_application(self):
        ref = self.clone(expires_at=utc(self.e.host.now[0]+10));selected=self.select(ref)
        self.e.host.now[0] += 11;self.bad(self.app.apply,selected,ref)

    def test_exact_transform_preserves_other_semantics(self):
        original = OLD.read_bytes();output = repaired_source(original)
        self.assertEqual(output.decode().replace(AFTER,BEFORE).encode(),original)
        self.assertNotEqual(output,CORRECTED.read_bytes())
        self.bad(repaired_source,output)

    def test_actual_application_receipt_separate(self):
        self.apply_fixture();self.assertIsNotNone(self.app.application_ref);self.assertIsNone(self.app.outcome_ref)
        self.assertEqual(parse((self.e.output/'application-completed.json').read_bytes())['outcome_assessed'],False)

    def test_pending_blocks_redispatch(self):
        self.apply_fixture();self.bad(self.app.apply,self.select(),self.lesson)

    def test_uncertain_process_preserves_pending(self):
        selected = self.select()
        with patch('application.subprocess.run',return_value=self.process(returncode=1)):
            self.bad(self.app.apply,selected,self.lesson)
        self.assertTrue((self.e.output/'application-pending.json').exists());self.assertIsNone(self.app.application_ref)
        self.bad(self.app.apply,selected,self.lesson)

    def test_timeout_retains_original_partial_bytes(self):
        selected = self.select()
        with patch('application.subprocess.run',side_effect=subprocess.TimeoutExpired('unit fixture',25,output=b'partial',stderr=b'error')):
            with self.assertRaises(subprocess.TimeoutExpired):self.app.apply(selected,self.lesson)
        self.assertEqual((self.e.output/'application-timeout-stdout.log').read_bytes(),b'partial')
        self.assertIsNone(self.app.application_ref);self.bad(self.app.apply,selected,self.lesson)

    def test_assessment_requires_actual_application(self):
        self.bad(self.app.assess);self.bad(self.app.propose_improvement)

    def test_supported_outcome_keeps_causal_ceiling(self):
        self.apply_fixture();ref = self.app.assess();p=self.e.get(ref)['payload']
        self.assertEqual(p['disposition'],'supported-for-this-controlled-case');self.assertEqual(p['causal_claim_ceiling'],CAUSAL_CEILING)
        self.assertTrue(p['counterevidence_refs'])

    def test_negative_outcome_preserved(self):
        self.apply_fixture('rejected',0);ref = self.app.assess()
        self.assertEqual(self.e.get(ref)['payload']['disposition'],'not-supported-for-this-controlled-case')

    def test_inconclusive_outcome_preserved(self):
        self.apply_fixture('unknown',0);ref = self.app.assess()
        self.assertEqual(self.e.get(ref)['payload']['disposition'],'inconclusive')

    def test_outcome_and_benefit_cannot_be_supplied(self):
        self.apply_fixture();self.bad(self.app.assess,requested_disposition='general-success');self.bad(self.app.assess,claimed_benefit='proven')

    def test_improvement_remains_unapplied(self):
        self.apply_fixture();self.app.assess();self.app.propose_improvement()
        receipt=parse((self.e.output/'unapplied-effect.json').read_bytes())
        self.assertFalse(receipt['applied']);self.assertFalse(receipt['lesson_promoted']);self.assertIsNone(receipt['actual_owner_outcome'])

    def test_close_erases_memory_and_blocks_use(self):
        self.e.host.session.note('temporary');self.e.host.session.close()
        self.assertEqual(self.e.host.session._memory,[]);self.bad(self.select)


if __name__ == '__main__': unittest.main()
