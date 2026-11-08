"""Synthetic no-effect causal checks for local fixture issuer selection."""
import datetime as dt
import os
import unittest
from unittest import mock

import adapter as A

NOW = dt.datetime(2026,10,20,18,30,tzinfo=dt.timezone.utc)
AUTHORITY_ID = 'fixture-inode:authority-1'
STAGE_ID = 'fixture-inode:stage-1'


def signed_facts(selected):
    return {'view_scope':selected['scope_expected'],
            'sources_scope':selected['scope_expected'],
            'selected_basis':{
                'manifest_sha256':selected['reader']['source_package_manifest_sha256'],
                'source_manifest_sha256':selected['reader']['source_manifest_sha256'],
                'adapter_source_sha256':selected['reader']['manifest_sha256']},
            'period_sha256':selected['source_period_sha256'],
            'source_review_sha256':selected['source_effect_review_sha256'],
            'reader_review_sha256':selected['reader_effect_review_sha256'],
            'mapper_review_sha256':selected['mapper_effect_review_sha256'],
            'now_at_close':NOW,'first_guard':True,'final_guard':True,
            'reader_guard':True,'close_ok':True,'current':True}


class AdapterTests(unittest.TestCase):
    def test_current_original_reader_and_unissued_local_identity(self):
        selected = A.select(NOW)
        self.assertEqual(selected['status'],'LOCAL_FIXTURE_ISSUER_SELECTED_AUTH_UNISSUED')
        self.assertEqual(selected['reader']['method'],'SelectedReader.open_signed')
        self.assertEqual(selected['reader']['sha256'],A.READER_CODE_SHA)
        self.assertEqual(selected['scope_actual'],'NOT_OPENED')
        self.assertEqual(selected['issuer']['kind'],'DISPOSABLE_LOCAL_HOST_ONLY')
        self.assertFalse(selected['issuer']['protected_source8_grant'])
        self.assertEqual(selected['issuer']['grant'],'UNISSUED')
        self.assertEqual(selected['auth']['issued_sha256'],'UNMINTED_UNSELECTED')
        self.assertEqual(selected['auth']['final_count_after_issuance'],1571)
        self.assertLessEqual(A.dt.datetime.fromisoformat(selected['auth']['expires_at'])-NOW,
                             dt.timedelta(minutes=20))

    def test_actual_selection_never_opens_private_body(self):
        actual = os.open
        def guarded(path,*args,**kwargs):
            if str(path).endswith('/branch.snapshot'):
                raise AssertionError('private body opened')
            return actual(path,*args,**kwargs)
        with mock.patch.object(os,'open',side_effect=guarded):
            self.assertEqual(A.select(NOW)['effect'],'NOT_RUN')

    def test_reader_or_approval_drift_and_wrong_issuer_refuse(self):
        with mock.patch.object(A,'READER_CODE_SHA','0'*64):
            with self.assertRaises(A.Refused): A.select(NOW)
        with mock.patch.object(A,'SOURCE_APPROVAL_SHA','0'*64):
            with self.assertRaises(A.Refused): A.select(NOW)
        with mock.patch.object(A,'ISSUER_UID',9999):
            with self.assertRaisesRegex(A.Refused,'LOCAL_FIXTURE_ISSUER_IDENTITY'):
                A.select(NOW)

    def test_period_expiry_refuses_before_issuer_selection(self):
        end = dt.datetime(2026,10,21,15,tzinfo=dt.timezone.utc)
        with self.assertRaises((A.Refused,ValueError)):
            A.select(end)

    def test_protocol_claim_before_private_open_and_marker_before_content(self):
        value = A.protocol(A.select(NOW))
        steps = value['steps']
        self.assertLess(steps.index('CLAIM_EXCLUSIVE_AUTHORITY_ATTEMPT_ROOT_CONSUMED'),
                        steps.index('OPEN_EXACT_SELECTED_READER_OPEN_SIGNED_ONCE'))
        self.assertLess(steps.index('DURABLE_AUTHORITY_NO_RETRY_MARKER_BEFORE_PRIVATE_OPEN'),
                        steps.index('OPEN_EXACT_SELECTED_READER_OPEN_SIGNED_ONCE'))
        self.assertLess(steps.index('DURABLE_STAGE_NO_RETRY_MARKER_BEFORE_CONTENT'),
                        steps.index('COPY_REHASH_EXACT_1570_ROWS_WITH_PRIVATE_BODY_CUSTODY'))
        self.assertLess(steps.index('REQUIRE_FINAL_SIGNED_GUARD_READER_GUARD_AND_CLOSE'),
                        steps.index('ISSUE_ONE_0600_AUTH_LEAF_EXCLUSIVE_NOFOLLOW'))
        self.assertLess(steps.index('REQUIRE_FINAL_SIGNED_GUARD_READER_GUARD_AND_CLOSE'),
                        steps.index('PUBLISH_DURABLE_EXTERNAL_SIGNED_SCOPE_ATTESTATION_OR_UNKNOWN'))
        self.assertLess(steps.index('RECHECK_PERIOD_AND_BOUND_SIGNED_SCOPE_ATTESTATION_BEFORE_AUTH_WRITE'),
                        steps.index('ISSUE_ONE_0600_AUTH_LEAF_EXCLUSIVE_NOFOLLOW'))
        self.assertFalse(value['retry_allowed'])

    def test_claim_and_marker_failure_consume_no_retry(self):
        model = A.FixtureOneShotModel(A.select(NOW))
        model.claim(AUTHORITY_ID)
        with self.assertRaisesRegex(A.Refused,'MARKER_UNKNOWN_NO_RETRY'):
            model.marker(False)
        self.assertEqual(model.state,'UNKNOWN_CONSUMED')
        with self.assertRaises(A.Refused): model.marker(True)
        with self.assertRaises(A.Refused): model.claim(AUTHORITY_ID)
        with self.assertRaises(A.Refused): model.begin_signed()
        with self.assertRaises(A.Refused): model.retry()

    def test_wrong_signed_scope_or_failed_close_consumes_no_retry(self):
        selected = A.select(NOW)
        for change in ({'view_scope':'scope:wrong'},
                       {'sources_scope':'scope:wrong'},
                       {'selected_basis':{}},
                       {'period_sha256':'0'*64},
                       {'source_review_sha256':'0'*64},
                       {'reader_review_sha256':'0'*64},
                       {'mapper_review_sha256':'0'*64},
                       {'now_at_close':dt.datetime(2026,10,21,15,
                                                   tzinfo=dt.timezone.utc)},
                       {'first_guard':False}, {'final_guard':False},
                       {'reader_guard':False}, {'close_ok':False},
                       {'current':False}):
            with self.subTest(change=change):
                model = A.FixtureOneShotModel(selected)
                model.claim(AUTHORITY_ID); model.marker(True); model.begin_signed()
                values = signed_facts(selected)
                values.update(change)
                with self.assertRaisesRegex(A.Refused,
                    'SIGNED_SCOPE_OR_CLOSE_UNKNOWN_NO_RETRY'):
                    model.observe_signed_fixture(**values)
                self.assertEqual(model.state,'UNKNOWN_CONSUMED')
                with self.assertRaises(A.Refused): model.marker(True)
                with self.assertRaises(A.Refused): model.begin_signed()
                with self.assertRaises(A.Refused): model.stage_claim(STAGE_ID)
                with self.assertRaises(A.Refused): model.retry()

    def test_fixture_success_reaches_only_prewrite_model(self):
        selected = A.select(NOW)
        model = A.FixtureOneShotModel(selected)
        model.claim(AUTHORITY_ID); model.marker(True); model.begin_signed()
        model.observe_signed_fixture(**signed_facts(selected))
        raw = model.attestation_candidate()
        attested = A.json.loads(raw)
        self.assertEqual(attested['authority_attempt_identity'],AUTHORITY_ID)
        self.assertEqual(attested['selected_basis'],signed_facts(selected)['selected_basis'])
        self.assertEqual(attested['source_period_sha256'],selected['source_period_sha256'])
        digest = model.publish_attestation_fixture(raw,durable=True,
                                                   published_identity=AUTHORITY_ID)
        model.stage_claim(STAGE_ID); model.stage_marker(True)
        model.issuer_ready(rows=1570,current=True,issuer_local=True,
                           scope_rechecked=True,attestation_sha256=digest,
                           authority_attempt_identity=AUTHORITY_ID,
                           stage_attempt_identity=STAGE_ID)
        self.assertEqual(model.state,'AUTH_WRITE_ELIGIBLE_MODEL_ONLY')
        with self.assertRaisesRegex(A.Refused,'EFFECT_DISABLED'):
            model.issue()
        with self.assertRaises(A.Refused): model.retry()

    def test_signed_close_requires_publication_before_stage_claim(self):
        selected = A.select(NOW)
        model = A.FixtureOneShotModel(selected)
        model.claim(AUTHORITY_ID); model.marker(True); model.begin_signed()
        model.observe_signed_fixture(**signed_facts(selected))
        with self.assertRaisesRegex(A.Refused,'PUBLISHED_ATTESTATION_REQUIRED'):
            model.stage_claim(STAGE_ID)
        with self.assertRaisesRegex(A.Refused,'STAGE_MARKER_REQUIRED'):
            model.issuer_ready(rows=1570,current=True,issuer_local=True,
                scope_rechecked=True,attestation_sha256=A.sha(model.attestation_candidate()),
                authority_attempt_identity=AUTHORITY_ID,stage_attempt_identity=STAGE_ID)

    def test_failed_publication_is_absorbing_and_bound_to_identity(self):
        selected = A.select(NOW)
        for changed_raw,durable,identity in ((True,True,AUTHORITY_ID),
                                             (False,False,AUTHORITY_ID),
                                             (False,True,STAGE_ID)):
            with self.subTest(changed_raw=changed_raw,durable=durable,identity=identity):
                model = A.FixtureOneShotModel(selected)
                model.claim(AUTHORITY_ID); model.marker(True); model.begin_signed()
                model.observe_signed_fixture(**signed_facts(selected))
                raw = model.attestation_candidate()
                if changed_raw: raw += b' ' 
                with self.assertRaisesRegex(A.Refused,'ATTESTATION_PUBLICATION_UNKNOWN_NO_RETRY'):
                    model.publish_attestation_fixture(raw,durable=durable,
                                                       published_identity=identity)
                self.assertEqual(model.state,'UNKNOWN_CONSUMED')
                with self.assertRaises(A.Refused):
                    model.publish_attestation_fixture(model._attestation_raw,durable=True,
                                                       published_identity=AUTHORITY_ID)
                with self.assertRaises(A.Refused): model.stage_claim(STAGE_ID)
                with self.assertRaises(A.Refused): model.retry()

    def test_failed_stage_marker_cannot_resume_to_auth(self):
        selected = A.select(NOW)
        model = A.FixtureOneShotModel(selected)
        model.claim(AUTHORITY_ID); model.marker(True); model.begin_signed()
        model.observe_signed_fixture(**signed_facts(selected))
        raw = model.attestation_candidate()
        digest = model.publish_attestation_fixture(raw,durable=True,
                                                   published_identity=AUTHORITY_ID)
        model.stage_claim(STAGE_ID)
        with self.assertRaisesRegex(A.Refused,'STAGE_MARKER_UNKNOWN_NO_RETRY'):
            model.stage_marker(False)
        self.assertEqual(model.state,'UNKNOWN_CONSUMED')
        with self.assertRaises(A.Refused): model.stage_marker(True)
        with self.assertRaises(A.Refused):
            model.issuer_ready(rows=1570,current=True,issuer_local=True,
                scope_rechecked=True,attestation_sha256=digest,
                authority_attempt_identity=AUTHORITY_ID,stage_attempt_identity=STAGE_ID)

    def test_prewrite_rejects_mismatched_publication_identity_or_digest(self):
        selected = A.select(NOW)
        for change in ({'attestation_sha256':'0'*64},
                       {'authority_attempt_identity':STAGE_ID},
                       {'stage_attempt_identity':AUTHORITY_ID}):
            with self.subTest(change=change):
                model = A.FixtureOneShotModel(selected)
                model.claim(AUTHORITY_ID); model.marker(True); model.begin_signed()
                model.observe_signed_fixture(**signed_facts(selected))
                digest = model.publish_attestation_fixture(model.attestation_candidate(),
                    durable=True,published_identity=AUTHORITY_ID)
                model.stage_claim(STAGE_ID); model.stage_marker(True)
                args=dict(rows=1570,current=True,issuer_local=True,scope_rechecked=True,
                          attestation_sha256=digest,authority_attempt_identity=AUTHORITY_ID,
                          stage_attempt_identity=STAGE_ID)
                args.update(change)
                with self.assertRaisesRegex(A.Refused,'AUTH_PREWRITE_UNKNOWN_NO_RETRY'):
                    model.issuer_ready(**args)
                self.assertEqual(model.state,'UNKNOWN_CONSUMED')
                with self.assertRaises(A.Refused): model.issuer_ready(**args)

    def test_bad_prewrite_poisoned_and_every_real_effect_refused(self):
        selected = A.select(NOW)
        model = A.FixtureOneShotModel(selected)
        model.claim(AUTHORITY_ID); model.marker(True); model.begin_signed()
        model.observe_signed_fixture(**signed_facts(selected))
        raw = model.attestation_candidate()
        digest = model.publish_attestation_fixture(raw,durable=True,
                                                   published_identity=AUTHORITY_ID)
        model.stage_claim(STAGE_ID); model.stage_marker(True)
        with self.assertRaisesRegex(A.Refused,'AUTH_PREWRITE_UNKNOWN_NO_RETRY'):
            model.issuer_ready(rows=1569,current=True,issuer_local=True,
                               scope_rechecked=True,attestation_sha256=digest,
                               authority_attempt_identity=AUTHORITY_ID,
                               stage_attempt_identity=STAGE_ID)
        self.assertEqual(model.state,'UNKNOWN_CONSUMED')
        for fn in (A.open_actual_signed_scope,A.issue_actual_auth_or_grant,
                   A.create_stage_or_private_policy,A.launch_context):
            with self.assertRaisesRegex(A.Refused,'EFFECT_DISABLED'):
                fn()


if __name__ == '__main__': unittest.main(verbosity=2)
